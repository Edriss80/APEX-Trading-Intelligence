import pandas as pd


def analyze_market(df):

    result = {
        "trend": "UNKNOWN",
        "breakout": "NONE",
        "rsi": None,
        "volume_signal": "NORMAL",
        "signals": []
    }

    if df is None or len(df) < 50:
        return result

    df = df.copy()

    close = df["Close"]
    volume = df["Volume"]

    df["EMA20"] = close.ewm(span=20).mean()
    df["EMA50"] = close.ewm(span=50).mean()

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))

    df["RSI"] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]

    result["rsi"] = (
        float(latest["RSI"])
        if pd.notna(latest["RSI"])
        else None
    )

    if latest["EMA20"] > latest["EMA50"]:
        result["trend"] = "BULLISH"
    else:
        result["trend"] = "BEARISH"

    previous_high = df["High"].iloc[-21:-1].max()
    previous_low = df["Low"].iloc[-21:-1].min()

    if latest["Close"] > previous_high:
        result["breakout"] = "BULLISH BREAKOUT"

    elif latest["Close"] < previous_low:
        result["breakout"] = "BEARISH BREAKDOWN"

    average_volume = volume.iloc[-21:-1].mean()

    if pd.notna(average_volume) and average_volume > 0:
        if latest["Volume"] > average_volume * 1.5:
            result["volume_signal"] = "HIGH VOLUME"

    if result["rsi"] is not None:
        if result["rsi"] > 70:
            result["signals"].append("OVERBOUGHT")

        elif result["rsi"] < 30:
            result["signals"].append("OVERSOLD")

    return result
