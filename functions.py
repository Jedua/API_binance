import pandas as pd #en versiones despues de 2.0 append ya no existe usar concat() en su lugar
import json
from collections import defaultdict
import time


# Almacenar datos de velas
data = defaultdict(lambda: pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']))


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
# Obtener datos históricos paginados (REST API) para 4 meses
def get_historical_data_paginated(exchange, symbol, timeframe='5m', since=None, limit=1000):
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

# Procesar los mensajes recibidos del WebSocket
def on_message(ws, message):
    json_message = json.loads(message)
    symbol = json_message['s']  # Ejemplo: 'ETHUSDT', 'BTCUSDT', etc.
    candle = json_message['k']   # Datos de la vela

    # Datos de la vela en formato legible
    timestamp = pd.to_datetime(candle['t'], unit='ms')
    open_price = float(candle['o'])
    high_price = float(candle['h'])
    low_price = float(candle['l'])
    close_price = float(candle['c'])
    volume = float(candle['v'])

    # Crear un nuevo DataFrame con la nueva vela
    new_row = pd.DataFrame({
        'timestamp': [timestamp],
        'open': [open_price],
        'high': [high_price],
        'low': [low_price],
        'close': [close_price],
        'volume': [volume]
    })

    # Concatenar la nueva vela al DataFrame existente
    df = data[symbol]
    df = pd.concat([df, new_row], ignore_index=True)

    # Mantener un número razonable de filas (por ejemplo, últimas 4 meses de datos + tiempo real)
    if len(df) > 34560 + 4:  # Máximo 4 meses + tiempo real
        df = df.tail(34560 + 4)  # Mantener las últimas filas de datos

    data[symbol] = df

    # Mostrar los últimos datos del símbolo
    print(f"Últimos datos de {symbol} (actualizado):")
    print(data[symbol].tail())
    print("\n")

# Manejar errores del WebSocket
def on_error(ws, error):
    print(error)

# Manejar el cierre de la conexión del WebSocket
def on_close(ws):
    print("Conexión cerrada")

# Iniciar el WebSocket y suscribirse a los pares deseados
def on_open(ws):
    params = {
        "method": "SUBSCRIBE",
        "params": [
            "ethusdt@kline_5m",
            "adausdt@kline_5m",
            "btcusdt@kline_5m"
        ],
        "id": 1
    }
    ws.send(json.dumps(params))

# Iniciar el WebSocket
def iniciar_websocket():
    import websocket
    socket = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(socket, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()