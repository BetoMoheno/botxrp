import os
import pandas as pd
import numpy as np
import schedule
import time
from binance.client import Client

# 🔐 Cargar claves de Binance desde variables de entorno
api_key = os.getenv("SB9riIpm8RMgw36NDvHVoHPWDt41DU16NJbcLw7EdOurws15jdMJLSxQeBoYgtbf")
api_secret = os.getenv("HDDuvOW6Njy17QpwzuYjMnV8i1ujS7RCUM7BzrG2lBDeOIkFEwk0HoPqtWyILajT")

if not api_key or not api_secret:
    raise ValueError("🔴 Error: Claves de API no encontradas en las variables de entorno.")

# Conectar con Binance
client = Client(api_key, api_secret)

# 📈 Obtener precios de velas (1 día)
def get_candles(symbol, interval='1d', limit=100):
    candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(candles, columns=['time', 'open', 'high', 'low', 'close', 'volume', 
                                        'close_time', 'quote_asset_volume', 'num_trades', 
                                        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'])
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

# 📊 Implementar UT Bot Alerts
def calculate_ut_bot(data, key_value=1, atr_period=10):
    df = data.copy()
    df['atr'] = df['high'] - df['low']  # ATR aproximado
    df['n_loss'] = key_value * df['atr']
    df['xATRStop'] = df['close']  # Inicializa con valores de cierre para evitar NaN
    df['pos'] = 0

    for i in range(1, len(df)):
        if df['close'][i] > df['xATRStop'][i-1]:
            df.at[i, 'xATRStop'] = df['close'][i] - df['n_loss'][i]
            df.at[i, 'pos'] = 1
        elif df['close'][i] < df['xATRStop'][i-1]:
            df.at[i, 'xATRStop'] = df['close'][i] + df['n_loss'][i]
            df.at[i, 'pos'] = -1
        else:
            df.at[i, 'xATRStop'] = df.at[i-1, 'xATRStop']
            df.at[i, 'pos'] = df.at[i-1, 'pos']

    return df

# 🔍 Seleccionar el mejor activo para invertir
def select_best_asset(xrp_df, paxg_df):
    if xrp_df['pos'].iloc[-1] == 1:
        return "XRPUSDT"
    elif paxg_df['pos'].iloc[-1] == 1:
        return "PAXGUSDT"
    else:
        return "USDT"

# 🏦 Colocar orden en Binance
def place_order(symbol, side, amount):
    try:
        if side.upper() == "BUY":
            order = client.order_market_buy(symbol=symbol, quantity=amount)
        else:
            order = client.order_market_sell(symbol=symbol, quantity=amount)

        print(f"✅ Orden ejecutada: {side} {amount} de {symbol}")
        return order
    except Exception as e:
        print(f"❌ Error al ejecutar orden: {e}")

# 🤖 Función principal del bot
def run_bot():
    print("🚀 Ejecutando bot de trading...")
    
    # Obtener datos de XRP y PAXGOLD
    xrp_data = get_candles("XRPUSDT")
    paxg_data = get_candles("PAXGUSDT")

    # Calcular señales de trading
    xrp_df = calculate_ut_bot(xrp_data)
    paxg_df = calculate_ut_bot(paxg_data)

    # Decidir en qué activo invertir
    selected_asset = select_best_asset(xrp_df, paxg_df)
    print(f"📊 Mejor activo para invertir: {selected_asset}")

    # Ejecutar compra según el activo en tendencia
    if selected_asset == "XRPUSDT":
        place_order("XRPUSDT", "BUY", 10)  # Compra 10 XRP
    elif selected_asset == "PAXGUSDT":
        place_order("PAXGUSDT", "BUY", 0.01)  # Compra 0.01 PAXG
    else:
        print("🔍 No hay oportunidades, mantener en USDT")

# ⏳ Automatizar el bot para que corra todos los días a medianoche
schedule.every().day.at("00:00").do(run_bot)

print("🤖 Bot en ejecución...")

# Mantener el bot corriendo con manejo de errores
while True:
    try:
        schedule.run_pending()
    except Exception as e:
        print(f"⚠️ Error en el bot: {e}")
    
    time.sleep(60)  # Espera 60 segundos antes de volver a verificar

from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot de trading en ejecución 🚀"

def start_bot():
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            print(f"⚠️ Error en el bot: {e}")

if __name__ == "__main__":
    # Iniciar el bot en un hilo aparte
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # Iniciar el servidor Flask
    app.run(host="0.0.0.0", port=8080)



