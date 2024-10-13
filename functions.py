import pandas as pd
import time

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

# 1m: 1 minuto.     15m: 15 minutos.    1w: 1 semana.
# 3m: 3 minutos.    30m: 30 minutos.
# 5m: 5 minutos.    1h: 1 hora.
# 4h: 4 horas.      1d: 1 día.

def get_multiple_symbols_data(exchange, symbols, timeframe='1h', limit=100):
    data = {}
    for symbol in symbols:
        df = get_historical_data(exchange, symbol, timeframe, limit)
        data[symbol] = df
    return data


# Un día tiene 288 velas de 5 minutos (porque hay 12 velas de 5 minutos por hora y 24 horas en un día).
# 4 meses son aproximadamente 120 días.
# Por lo tanto, 120 días × 288 velas por día = 34,560 velas para cubrir 4 meses.
def get_historical_data_paginated(exchange, symbol, timeframe='5m', since=None, limit=1000):
    """
    Obtiene datos históricos paginados debido al límite de 1000 velas por solicitud en Binance.
    El parámetro 'since' es opcional, si no se proporciona, traerá datos desde el punto más reciente.
    """
    all_data = []
    while True:
        # Obtener los datos en fragmentos de 'limit' velas
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if len(ohlcv) == 0:
            break
        all_data.extend(ohlcv)  # Agregar los datos obtenidos
        since = ohlcv[-1][0] + 1  # Continuar desde el último timestamp
        time.sleep(1)  # Para evitar ser bloqueados por la API

        # Verificación: Si ya obtenemos 34,560 velas (4 meses), podemos detenernos
        if len(all_data) >= 34560:
            break

    # Convertir los datos a DataFrame
    df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df