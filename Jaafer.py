import requests
import time

# ===== إعدادات Telegram =====
TOKEN = "PUT_TOKEN_HERE"
CHAT_ID = "PUT_CHAT_ID"

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ===== أفضل العملات (Top Volume) =====
def get_top_symbols():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    data = requests.get(url).json()

    usdt = [x for x in data if x["symbol"].endswith("USDT")]
    sorted_pairs = sorted(usdt, key=lambda x: float(x["quoteVolume"]), reverse=True)

    return [x["symbol"] for x in sorted_pairs[:30]]

# ===== الفريمات الاحترافية =====
timeframes = ["5m","15m","1h","4h"]

# ===== جلب البيانات =====
def get_klines(symbol, tf):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=120"
    data = requests.get(url).json()

    closes = [float(x[4]) for x in data]
    volumes = [float(x[5]) for x in data]

    return closes, volumes

# ===== تخزين الحالة =====
store = {}

def process(symbol, tf):
    closes, volumes = get_klines(symbol, tf)

    base = closes[0]
    top = max(closes)
    top_index = closes.index(top)

    pump = (top - base) / base * 100
    if pump < 20:
        return

    bottom = min(closes[top_index:])
    drop = (top - bottom) / top * 100
    if drop < 15:
        return

    # قمة ثانية داخل النطاق
    second_top = max(closes[top_index:])
    if not (bottom < second_top < top):
        return

    # فوليوم
    vol_avg = sum(volumes) / len(volumes)
    if volumes[-1] < vol_avg * 1.5:
        return

    key = f"{symbol}_{tf}"

    if key not in store:
        store[key] = {"break": False}

    last = closes[-1]
    neckline = bottom

    # ===== كسر =====
    if last < neckline and not store[key]["break"]:
        store[key]["break"] = True

        send(f"🚨 BREAK {symbol} [{tf}]\nPrice: {last}")

        r = top - neckline

        store[key]["fibs"] = {
            "1.272": neckline - r * 1.272,
            "1.5": neckline - r * 1.5,
            "1.618": neckline - r * 1.618,
            "2.0": neckline - r * 2
        }

        store[key]["hits"] = {k: False for k in store[key]["fibs"]}

    # ===== فيبوناتشي =====
    if key in store and "fibs" in store[key]:
        for k, v in store[key]["fibs"].items():
            if last <= v and not store[key]["hits"][k]:
                send(f"🎯 {symbol} [{tf}] Hit Fib {k}\nPrice: {last}")
                store[key]["hits"][k] = True

# ===== التشغيل =====
while True:
    try:
        symbols = get_top_symbols()

        for tf in timeframes:
            for s in symbols:
                process(s, tf)

    except:
        pass

    time.sleep(60)