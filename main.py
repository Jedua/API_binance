from connect import get_binance_connection
from functions import get_historical_data_paginated, iniciar_websocket, data

def main():
    # Conectar a Binance
    exchange = get_binance_connection()

    # Obtener datos históricos de los últimos 4 meses de ETH, ADA y BTC
    symbols = ['ETH/USDT', 'ADA/USDT', 'BTC/USDT']
    for symbol in symbols:
        print(f"Obteniendo datos históricos de {symbol} (últimos 4 meses)...")
        historical_data = get_historical_data_paginated(exchange, symbol, timeframe='5m')
        data[symbol] = historical_data
        print(f"Datos históricos de {symbol} (últimos 5 registros):")
        print(data[symbol].tail())

    # Iniciar el WebSocket para recibir datos en tiempo real
    iniciar_websocket()

if __name__ == '__main__':
    main()
