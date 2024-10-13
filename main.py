# main.py
from connect import get_binance_connection
from functions import get_balance, get_historical_data

def main():
    # Conectar a Binance
    exchange = get_binance_connection()

    balance = get_balance(exchange)
    print("Balance de la cuenta:")
    print(balance)

    # Obtener datos históricos de un par (por ejemplo ETH/USDT)
    symbol = 'ETH/USDT'
    historical_data = get_historical_data(exchange, symbol)
    print(f"Datos históricos de {symbol}:")
    print(historical_data.tail())

if __name__ == '__main__':
    main()
