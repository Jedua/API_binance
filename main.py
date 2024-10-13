from connect import get_binance_connection
from functions import *

def main():
    # Conectar a Binance
    exchange = get_binance_connection()

    balance = get_balance(exchange)
    print("Balance de la cuenta:")
    print(balance)

    # Obtener datos históricos de un par (por ejemplo ETH/USDT)
    symbols = ['ETH/USDT', 'ADA/USDT', 'BTC/USDT']
    # historical_data = get_multiple_symbols_data(exchange, symbols)

    for symbol in symbols:
        print(f"Obteniendo datos históricos de {symbol}...")
        historical_data = get_historical_data_paginated(exchange, symbol, timeframe='5m')
        print(f"Datos históricos de {symbol} (últimas 5 filas):")
        print(historical_data.tail())

if __name__ == '__main__':
    main()
