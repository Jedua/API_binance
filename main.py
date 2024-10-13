from connect import get_binance_connection
from functions import get_balance, get_multiple_symbols_data

def main():
    # Conectar a Binance
    exchange = get_binance_connection()

    balance = get_balance(exchange)
    print("Balance de la cuenta:")
    print(balance)

    # Obtener datos históricos de un par (por ejemplo ETH/USDT)
    symbols = ['ETH/USDT', 'ADA/USDT', 'BTC/USDT']
    historical_data = get_multiple_symbols_data(exchange, symbols)
    
    for symbol, data in historical_data.items():
        print(f"\nDatos históricos de {symbol}:")
        print(data.tail())

if __name__ == '__main__':
    main()
