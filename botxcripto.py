import os
import pandas as pd
from binance.client import Client

# 🔐 1. Cargar claves de API de Binance desde variables de entorno (Ejemplo con claves falsas)
api_key = os.getenv("SB9riIpm8RMgw36NDvHVoHPWDt41DU16NJbcLw7EdOurws15jdMJLSxQeBoYgtbfHDDuvOW6Njy17QpwzuYjMnV8i1ujS7RCUM7BzrG2lBDeOIkFEwk0HoPqtWyILajT")
api_secret = os.getenv("SB9riIpm8RMgw36NDvHVoHPWDt41DU16NJbcLw7EdOurws15jdMJLSxQeBoYgtbfHDDuvOW6Njy17QpwzuYjMnV8i1ujS7RCUM7BzrG2lBDeOIkFEwk0HoPqtWyILajT")

if not api_key or not api_secret:
    print("🔴 ERROR: Claves de API no encontradas.")
    exit(1)

# 🔗 2. Conectar con Binance
try:
    client = Client(api_key, api_secret)
    print("✅ Conexión con Binance establecida correctamente")
except Exception as e:
    print(f"❌ ERROR al conectar con Binance: {e}")
    exit(1)

# 📈 3. Obtener datos de velas (candlestick) en formato DataFrame
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

# 📊 4. Implementar UT Bot Alerts
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

# 🔍 5. Seleccionar el mejor activo para invertir
def select_best_asset():
    assets = ["BTCUSDT", "ADAUSDT", "XRPUSDT", "PAXGUSDT"]
    best_asset = "USDT"

    for asset in assets:
        data = get_candles(asset)
        df = calculate_ut_bot(data)

        if df is not None and df['pos'].iloc[-1] == 1:
            best_asset = asset  # Se elige el último activo con señal de compra

    return best_asset

# 🏦 6. Obtener saldo disponible en USDT
def get_balance():
    try:
        balance = client.get_asset_balance(asset="USDT")
        return float(balance['free'])
    except Exception as e:
        print(f"❌ ERROR al obtener balance: {e}")
        return 0

# 🏦 7. Colocar orden de compra o venta en Binance
def place_order(symbol, side, amount):
    try:
        if amount <= 0:
            print("⚠️ No hay suficiente saldo para operar.")
            return

        if side.upper() == "BUY":
            order = client.order_market_buy(symbol=symbol, quantity=amount)
        else:
            order = client.order_market_sell(symbol=symbol, quantity=amount)

        print(f"✅ Orden ejecutada: {side} {amount} de {symbol}")
        return order
    except Exception as e:
        print(f"❌ ERROR al ejecutar orden: {e}")

# 🤖 8. Ejecutar el bot
def run_bot():
    print("🚀 Ejecutando BotCripto...")

    # Verificar saldo disponible
    balance = get_balance()
    if balance < 10:  # Se establece un mínimo de 10 USDT para operar
        print("⚠️ Saldo insuficiente para operar.")
        return

    # Seleccionar el mejor activo para invertir
    best_asset = select_best_asset()
    if best_asset == "USDT":
        print("🔍 No hay señales de compra, manteniendo USDT.")
        return

    # Definir cantidad a invertir (Ejemplo: 20% del saldo disponible)
    investment_amount = round(balance * 0.2, 5)  

    # Ejecutar compra
    place_order(best_asset, "BUY", investment_amount)

# 🔄 9. Configurar ejecución automática
if __name__ == "__main__":
    run_bot()


