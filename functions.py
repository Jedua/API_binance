import pandas as pd

def get_balance(exchange):
    balance = exchange.fetch_balance()
    return balance

def get_historical_data(exchange, symbol, timeframe='1h', limit=100):
    # Obtener datos históricos
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    # Convertir a DataFrame para mejor manejo
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def get_multiple_symbols_data(exchange, symbols, timeframe='1h', limit=100):
    data = {}
    for symbol in symbols:
        df = get_historical_data(exchange, symbol, timeframe, limit)
        data[symbol] = df
    return data