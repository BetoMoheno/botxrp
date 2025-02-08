import os
import threading
import time
import pandas as pd
import schedule
from flask import Flask
from binance.client import Client

# 🔐 1. Cargar claves de API de Binance desde variables de entorno
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

if not api_key or not api_secret:
    print(f"🔴 ERROR: Claves de API no encontradas. API_KEY={api_key}, API_SECRET={api_secret}")
    exit(1)

# 🔗 2. Conectar con Binance
try:
    client = Client(api_key, api_secret)
    print("✅ Conexión con Binance establecida correctamente")
except Exception as e:
    print(f"❌ ERROR al conectar con Binance: {e}")
    exit(1)

# 📈 3. Obtener precios de velas (candlestick) en formato DataFrame
def get_candles(symbol, interval='1d', limit=100):
    try:
        candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(candles, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'num_trades', 
            'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
        ])
        df = df[['time', 'open', 'high', 'low', 'close', 'volume']].astype(float)
        return df
    except Exception as e:
        print(f"❌ ERROR al obtener datos de {symbol}: {e}")
        return None

# 📊 4. Implementar UT Bot Alerts (estrategia de trading)
def calculate_ut_bot(data, key_value=1, atr_period=10):
    if data is None:
        return None
    
    df = data.copy()
    df['atr'] = df['high'] - df['low']
    df['n_loss'] = key_value * df['atr']
    df['xATRStop'] = df['close']
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

# 🔍 5. Seleccionar el mejor activo para invertir (XRP o PAXG)
def select_best_asset(xrp_df, paxg_df):
    if xrp_df is not None and xrp_df['pos'].iloc[-1] == 1:
        return "XRPUSDT"
    elif paxg_df is not None and paxg_df['pos'].iloc[-1] == 1:
        return "PAXGUSDT"
    else:
        return "USDT"

# 🏦 6. Colocar orden de compra o venta en Binance
def place_order(symbol, side, amount):
    try:
        if side.upper() == "BUY":
            order = client.order_market_buy(symbol=symbol, quantity=amount)
        else:
            order = client.order_market_sell(symbol=symbol, quantity=amount)

        print(f"✅ Orden ejecutada: {side} {amount} de {symbol}")
        return order
    except Exception as e:
        print(f"❌ ERROR al ejecutar orden: {e}")

# 🤖 7. Función principal del bot
def run_bot():
    print("🚀 Ejecutando bot de trading...")

    xrp_data = get_candles("XRPUSDT")
    paxg_data = get_candles("PAXGUSDT")

    xrp_df = calculate_ut_bot(xrp_data)
    paxg_df = calculate_ut_bot(paxg_data)

    selected_asset = select_best_asset(xrp_df, paxg_df)
    print(f"📊 Mejor activo para invertir: {selected_asset}")

    if selected_asset == "XRPUSDT":
        place_order("XRPUSDT", "BUY", 10)
    elif selected_asset == "PAXGUSDT":
        place_order("PAXGUSDT", "BUY", 0.01)
    else:
        print("🔍 No hay oportunidades, mantener en USDT")

# ⏳ 8. Automatizar el bot para que corra todos los días a medianoche
schedule.every().day.at("00:00").do(run_bot)

# 🔥 9. Servidor Flask para Cloud Run
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot de trading en ejecución 🚀"

@app.route("/health")
def health():
    return "✅ OK", 200

# 🔄 10. Hilos separados para ejecutar Flask y el bot
def start_bot():
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            print(f"⚠️ ERROR en el bot: {e}")

def start_flask():
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Iniciando Flask en el puerto: {port}")
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"❌ ERROR iniciando Flask: {e}")
        exit(1)

if __name__ == "__main__":
    print("🔄 Iniciando servicio...")

    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()

    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    flask_thread.join()


