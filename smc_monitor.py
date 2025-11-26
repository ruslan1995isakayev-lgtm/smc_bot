import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import aiohttp

TELEGRAM_TOKEN = "8268878810:AAGeOoNod10X4ErKFESJZSbmSCuZ8Qa3jP0"
CHAT_ID = "1780455285"
SYMBOLS = [
    "BTC/USDT","ETH/USDT","ZEC/USDT","ZBCN/USDT","SOL/USDT",
    "ASTER/USDT","ADA/USDT","VIRTUAL/USDT","XRP/USDT"
]
TIMEFRAMES = ["15m","1h"]
POLL_INTERVAL = 30

async def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode":"HTML"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            await resp.text()

async def fetch_ohlcv(exchange, symbol, timeframe, limit=100):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('datetime', inplace=True)
        return df
    except:
        return None

def detect_signal(df):
    if len(df) < 10:
        return None
    if df['close'].iloc[-1] > df['high'].iloc[-2]:
        return "BOS_UP"
    if df['close'].iloc[-1] < df['low'].iloc[-2]:
        return "BOS_DOWN"
    return None

async def monitor():
    exchange = ccxt.binance({"enableRateLimit": True})
    while True:
        for tf in TIMEFRAMES:
            for sym in SYMBOLS:
                df = await fetch_ohlcv(exchange, sym, tf)
                if df is None:
                    continue
                sig = detect_signal(df)
                if sig:
                    msg = f"<b>{sym}</b>\\nTF: {tf}\\nSignal: {sig}\\nPrice: {df['close'].iloc[-1]:.2f}"
                    await send_telegram(msg)
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(monitor())
