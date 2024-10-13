# connect.py
import ccxt
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_binance_connection():
    api_key = os.getenv('API_KEY')
    secret_key = os.getenv('SECRET_KEY')

    # Configuración de la API de Binance
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
    })
    return exchange
