from connect import get_binance_connection
from functions import get_historical_data, iniciar_websocket

# Conectar a Binance
exchange = get_binance_connection()

# Diccionario para almacenar datos históricos y en tiempo real
data = {
    'BTC/USDT': None,
    'ETH/USDT': None,
    'ADA/USDT': None
}

if __name__ == "__main__":
    # Obtener datos históricos de los últimos 4 meses
    symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT']
    for symbol in symbols:
        print(f"Obteniendo datos históricos de {symbol}...")
        data[symbol] = get_historical_data(exchange, symbol)

    # Iniciar WebSocket para obtener datos en tiempo real
    print("\nIniciando WebSocket para obtener datos en tiempo real...")
    iniciar_websocket(data)
