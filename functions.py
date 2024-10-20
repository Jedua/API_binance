import pandas as pd
import time
import pandas_ta as ta
import json

def get_historical_data(exchange, symbol, timeframe='1h', days=120, limit=1000):
    """Obtener datos históricos paginados de los últimos 'days' días con velas de 1 hora"""
    all_data = []
    since = exchange.parse8601((pd.Timestamp.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    total_candles = 0

    while True:
        # Obtener datos paginados con el límite de 1000 por cada solicitud
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if not ohlcv:
            print("No se obtuvieron más datos.")
            break
        
        # Convertir los datos en un DataFrame y añadir a la lista de all_data
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        all_data.append(df)

        # Actualizar el contador de velas totales obtenidas
        total_candles += len(ohlcv)

        # Actualizar el punto desde donde empezar la siguiente solicitud
        since = ohlcv[-1][0] + 1

        # Pausar un poco para no hacer demasiadas solicitudes seguidas
        time.sleep(1)

        # Si hemos obtenido más de los registros esperados para el rango de días solicitado, salir
        if total_candles >= (24 * days):  # 24 velas por día para velas de 1 hora
            print(f"Se alcanzó el límite de {total_candles} registros, equivalente a {days} días de datos.")
            break

        # Si el número de registros se detiene alrededor de 3000, es probable que Binance esté limitando
        if total_candles >= 3000:
            print("Se alcanzó el límite de 3000 registros debido a la limitación de la API de Binance.")
            break

    # Concatenar todos los DataFrames obtenidos
    return pd.concat(all_data).reset_index(drop=True)

def calcular_indicadores(df):
    if len(df) >= 50:
        df['SMA_50'] = ta.sma(df['close'], length=50)
    else:
        df['SMA_50'] = None

    if len(df) >= 200:
        df['SMA_200'] = ta.sma(df['close'], length=200)
    else:
        df['SMA_200'] = None

    if len(df) >= 14:
        df['RSI'] = ta.rsi(df['close'], length=14)
    else:
        df['RSI'] = None

    if len(df) >= 26:
        macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_signal'] = macd['MACDs_12_26_9']
        df['MACD_histogram'] = macd['MACDh_12_26_9']
    else:
        df['MACD'] = df['MACD_signal'] = df['MACD_histogram'] = None

    return df

def confirmar_volumen(df):
    df['average_volume'] = df['volume'].rolling(window=20).mean()
    df['volumen_confirmado'] = df['volume'] > 1.5 * df['average_volume']
    return df

def generar_senales(df):
    if len(df) >= 200:
        df['buy_signal'] = (
            (df['SMA_50'] > df['SMA_200']) &
            (df['SMA_50'].shift(1) <= df['SMA_200'].shift(1)) &
            (df['RSI'] < 30) &
            (df['MACD'] > df['MACD_signal'])
        )
        df['sell_signal'] = (
            (df['SMA_50'] < df['SMA_200']) &
            (df['SMA_50'].shift(1) >= df['SMA_200'].shift(1)) &
            (df['RSI'] > 70) &
            (df['MACD'] < df['MACD_signal'])
        )
        df = confirmar_volumen(df)
        df['buy_signal'] = df['buy_signal'] & df['volumen_confirmado']
        df['sell_signal'] = df['sell_signal'] & df['volumen_confirmado']
    else:
        df['buy_signal'] = df['sell_signal'] = False

    if df['buy_signal'].iloc[-1]:
        print(f"🚀 Señal de COMPRA detectada: {df['timestamp'].iloc[-1]}")
    elif df['sell_signal'].iloc[-1]:
        print(f"🔻 Señal de VENTA detectada: {df['timestamp'].iloc[-1]}")

    return df

def on_message(ws, message, data):
    import json
    json_message = json.loads(message)
    symbol = json_message['s'].replace("USDT", "/USDT")
    candle = json_message['k']

    timestamp = pd.to_datetime(candle['t'], unit='ms')
    open_price = float(candle['o'])
    high_price = float(candle['h'])
    low_price = float(candle['l'])
    close_price = float(candle['c'])
    volume = float(candle['v'])

    new_row = pd.DataFrame({
        'timestamp': [timestamp],
        'open': [open_price],
        'high': [high_price],
        'low': [low_price],
        'close': [close_price],
        'volume': [volume]
    })

    # Concatenar los datos en tiempo real
    data[symbol] = pd.concat([data[symbol], new_row], ignore_index=True)

    # Mostrar el número de registros actuales
    print(f"\nCantidad de datos actuales para {symbol}: {len(data[symbol])}")

    # Calcular indicadores técnicos (SMA, RSI, MACD)
    data[symbol] = calcular_indicadores(data[symbol])

    # Generar señales de compra/venta
    data[symbol] = generar_senales(data[symbol])

    # Mostrar los últimos 5 registros para verificar la actualización
    print("Datos actualizados con análisis:")
    print(data[symbol].tail())

def on_open(ws):
    params = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@kline_15m",
            "ethusdt@kline_15m",
            "adausdt@kline_15m"
        ],
        "id": 1
    }
    ws.send(json.dumps(params))

def iniciar_websocket(data):
    import websocket
    socket = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(socket, on_message=lambda ws, msg: on_message(ws, msg, data), on_open=on_open)
    ws.run_forever()
