import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="APEX Trading Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("APEX | Trading Intelligence")
st.caption("Multi-Market Analysis System - Version 1.0")

MARKETS = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Gold": "GC=F",
    "EUR/USD": "EURUSD=X",
    "Apple": "AAPL",
    "S&P 500": "SPY"
}

st.sidebar.title("APEX Control Center")

asset = st.sidebar.selectbox(
    "Select Market",
    list(MARKETS.keys())
)

period = st.sidebar.selectbox(
    "Analysis Period",
    ["1mo", "3mo", "6mo", "1y", "2y"]
)

if st.button("Analyze Market"):
    ticker = MARKETS[asset]

    with st.spinner("Analyzing market data..."):
        try:
            df = yf.download(
                ticker,
                period=period,
                interval="1d",
                auto_adjust=True,
                progress=False
            )

            if df.empty:
                st.error("Market data unavailable.")
                st.stop()

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df["EMA20"] = df["Close"].ewm(
                span=20, adjust=False
            ).mean()

            df["EMA50"] = df["Close"].ewm(
                span=50, adjust=False
            ).mean()

            delta = df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss.replace(0, float("nan"))
            df["RSI"] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]

            st.subheader(f"{asset} Market Analysis")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Latest Price",
                f"{latest['Close']:.4f}"
            )

            c2.metric(
                "EMA 20",
                f"{latest['EMA20']:.4f}"
            )

            c3.metric(
                "RSI 14",
                f"{latest['RSI']:.2f}"
                if pd.notna(latest["RSI"])
                else "N/A"
            )

            if latest["EMA20"] > latest["EMA50"]:
                trend = "BULLISH"
            else:
                trend = "BEARISH"

            st.subheader("Trend Analysis")
            st.write(f"Market Trend: **{trend}**")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["Close"],
                name="Price"
            ))

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["EMA20"],
                name="EMA 20"
            ))

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["EMA50"],
                name="EMA 50"
            ))

            fig.update_layout(
                template="plotly_dark",
                height=550,
                title=f"{asset} Price Analysis"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("APEX Intelligence")

            if trend == "BULLISH":
                st.info("Positive trend detected. Further confirmation required.")
            else:
                st.warning("Negative trend detected. Further confirmation required.")

            st.caption(
                "Educational analysis only. "
                "Not a trading recommendation."
            )

        except Exception as e:
            st.error(f"Analysis error: {e}")

else:
    st.info("Select a market and press Analyze Market.")

    st.subheader("System Modules")

    col1, col2, col3 = st.columns(3)

    col1.write("Technical Analysis")
    col2.write("Market Intelligence")
    col3.write("Strategy Research")

    st.caption("APEX V1.0 | Development Mode")
