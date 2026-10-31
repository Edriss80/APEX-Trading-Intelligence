import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from analysis_engine import analyze_market

st.set_page_config(
    page_title="APEX Intelligence",
    layout="wide"
)

st.title("APEX | Trading Intelligence")
st.caption("Multi-Market AI Analysis System")

MARKETS = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Gold": "GC=F",
    "EUR/USD": "EURUSD=X",
    "Apple": "AAPL",
    "S&P 500": "SPY"
}

asset = st.sidebar.selectbox(
    "Select Market",
    list(MARKETS.keys())
)

period = st.sidebar.selectbox(
    "Period",
    ["1mo", "3mo", "6mo", "1y", "2y"]
)

if st.button("ANALYZE MARKET"):

    with st.spinner("APEX analyzing..."):

        try:
            df = yf.download(
                MARKETS[asset],
                period=period,
                interval="1d",
                auto_adjust=True,
                progress=False
            )

            if df.empty:
                st.error("No market data available")
                st.stop()

            if hasattr(df.columns, "nlevels"):
                if df.columns.nlevels > 1:
                    df.columns = df.columns.get_level_values(0)

            result = analyze_market(df)

            st.header(asset)

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Latest Price",
                f"{float(df['Close'].iloc[-1]):.4f}"
            )

            c2.metric(
                "Market Trend",
                result["trend"]
            )

            c3.metric(
                "RSI",
                f"{result['rsi']:.2f}"
                if result["rsi"] is not None
                else "N/A"
            )

            st.subheader("Breakout Detection")
            st.write(result["breakout"])

            st.subheader("Volume Analysis")
            st.write(result["volume_signal"])

            st.subheader("Technical Signals")

            if result["signals"]:
                for signal in result["signals"]:
                    st.write("- " + signal)
            else:
                st.write("No additional signals")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["Close"],
                name="Market Price"
            ))

            fig.update_layout(
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.caption(
                "Research prototype. "
                "Signals are experimental, not trade recommendations."
            )

        except Exception as e:
            st.error(str(e))

else:
    st.info("Select a market and start analysis.")
