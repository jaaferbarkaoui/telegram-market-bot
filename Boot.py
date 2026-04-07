import requests
import time

# ===== إعدادات Telegram =====
TOKEN = "8728131545:AAH66qpkZ1lNweD_Ard0RcFwioUKKOIidh0"
CHAT_ID = "8022505118"

# ===== دالة إرسال الرسائل =====
def send_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ===== دالة جلب بيانات السوق من Binance =====
def get_market_data(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    data = requests.get(url).json()
    close = float(data["lastPrice"])
    volume = float(data["volume"])
    return close, volume

# ===== إعدادات الاستراتيجية =====
PUMP_PERC = 20.0
DROP_PERC = 15.0
VOL_MULT  = 1.5

# ===== العملات المراد مراقبتها =====
symbols = [
"OGUSDT","2ZUSDT","A2ZUSDT","ACHUSDT","ACTUSDT","ADAUSDT","ADXUSDT","AEURUSDT",
"AIXBTUSDT","ALGOUSDT","ALICEUSDT","ALPINEUSDT","ALTUSDT","AMPUSDT","ANKRUSDT","APEUSDT",
"AP13USDT","APTUSDT","ARUSDT","ARBUSDT","ARDRUSDT","ARKUSDT","ARKMUSDT","ARPAUSDT","ASRUSDT",
"ASTRUSDT","ATUSDT","ATAUSDT","ATMUSDT","ATOMUSDT","AVAUSDT","AVAXUSDT","AWEUSDT","AXLUSDT",
"BANANAUSDT","BANDUSDT","BARUSDT","BATUSDT","BCHUSDT","BEAMXUSDT","BICOUSDT","BIOUSDT","BLURUSDT",
"BMTUSDT","BREVUSDT","BTCUSDT","BTTCUSDT","CUSDT","CELOUSDT","CELRUSDT","CFXUSDT","CGPTUSDT","CHRUSDT",
"CHZUSDT","CITYUSDT","CKBUSDT","COOKIEUSDT","COSUSDT","CTKUSDT","CTSIUSDT","CVCUSDT","CYBERUSDT","DUSDT",
"DASHUSDT","DCRUSDT","DENTUSDT","DEXEUSDT","DGBUSDT","DIAUSDT","DOGEUSDT","DOTUSDT","DUSKUSDT","EDUUSDT",
"EGLDUSDT","EIGENUSDT","ENJUSDT","ENSUSDT","ENSOUSDT","EPICUSDT","ERAUSDT","ESPUSDT","ETCUSDT","ETHUSDT",
"EURIUSDT","FDUSDUSDT","FETUSDT","FIDAUSDT","FILUSDT","FIOUSDT","FLOWUSDT","FLUXUSDT","GUSDT","GALAUSDT",
"GASUSDT","GLMUSDT","GLMRUSDT","GMTUSDT","GPSUSDT","GRTUSDT","GTCUSDT","HBARUSDT","HEIUSDT","HIGHUSDT",
"HIVEUSDT","HOLOUSDT","HOOKUSDT","HOTUSDT","HYPERUSDT","ICPUSDT","ICXUSDT","IDUSDT","IMXUSDT","INITUSDT",
"IOUSDT","IOSTUSDT","IOTAUSDT","IOTXUSDT","IQUSDT","JASMYUSDT","JUVUSDT","KAIAUSDT","KAITOUSDT","KGSTUSDT",
"KITEUSDT","KSMUSDT","LAUSDT","LAZIOUSDT","LINKUSDT","LPTUSDT","LRCUSDT","LSKUSDT","LTCUSDT","LUMIAUSDT",
"LUNAUSDT","MAGICUSDT","MANAUSDT","MANTAUSDT","MASKUSDT","MDTUSDT","MEUSDT","METISUSDT","MINAUSDT","MIRAUSDT",
"MOVEUSDT","MOVRUSDT","MTLUSDT","NEARUSDT","NEWTUSDT","NFPUSDT","NIGHTUSDT","NILUSDT","NTRNUSDT","ONEUSDT",
"ONGUSDT","OPUSDT","OPENUSDT","ORDIUSDT","OXTUSDT","PARTIUSDT","PAXGUSDT","PHAUSDT","PHBUSDT","PIVXUSDT",
"PIXELUSDT","PLUMEUSDT","POLUSDT","POLYXUSDT","PONDUSDT","PORTALUSDT","PORTOUSDT","POWRUSDT","PROMUSDT",
"PROVEUSDT","PSGUSDT","PUNDIXUSDT","PYTHUSDT","QKCUSDT","QNTUSDT","QTUMUSDT","RADUSDT","RAREUSDT","RENDERUSDT",
"REQUSDT","RIFUSDT","RLCUSDT","RONINUSDT","ROSEUSDT","RSRUSDT","RVNUSDT","SUSDT","SAGAUSDT","SAHARAUSDT",
"SANDUSDT","SANTOSUSDT","SAPIENUSDT","SCUSDT","SCRUSDT","SCRTUSDT","SEIUSDT","SENTUSDT","SFPUSDT","SHELLUSDT",
"SIGNUSDT","SKLUSDT","SOLUSDT","SOMIUSDT","SOPHUSDT","SSVUSDT","STEEMUSDT","STORJUSDT","STRAXUSDT","STXUSDT",
"SUIUSDT","SXTUSDT","SYSUSDT","TAOUSDT","TFUELUSDT","THETAUSDT","TIAUSDT","TNSRUSDT","TONUSDT","TOWNSUSDT",
"TRBUSDT","TRXUSDT","TUSDUSDT","TWTUSDT","UUSDT","USDCUSDT","USDPUSDT","USDTUSD","UTKUSDT","VANAUSDT","VANRYUSDT",
"VETUSDT","VICUSDT","VIRTUALUSDT","VTHOUSDT","WUSDT","WALUSDT","WAXPUSDT","WCTUSDT","WINUSDT","WLDUSDT","XAIUSDT",
"XECUSDT","XLMUSDT","XNOUSDT","XPLUSUSDT","XRPUSDT","XTZUSDT","XUSDUSDT","XVGUSDT","ZAMAUSDT","ZECUSDT","ZENUSDT","ZILUSDT"
]

# ===== إعدادات متابعة كل عملة =====
market_data = {}
for s in symbols:
    market_data[s] = {
        "base_close": None,
        "top_close": None,
        "bottom_close": None,
        "neckline": None,
        "pump_done": False,
        "drop_done": False,
        "break_done": False,
        "fib_hit": {"1.272": False, "1.5": False, "1.618": False, "2.0": False}
    }

# ===== دالة تحقق استراتيجية لكل عملة =====
def check_market(symbol):
    data = market_data[symbol]
    close, volume = get_market_data(symbol)
    vol_ma = volume
    high_volume = volume > vol_ma * VOL_MULT

    # ===== Pump =====
    if data["base_close"] is None:
        data["base_close"] = close
    pump = (close - data["base_close"]) / data["base_close"] * 100
    if pump >= PUMP_PERC and high_volume:
        data["top_close"] = close
        data["pump_done"] = True
        data["bottom_close"] = None

    # ===== Drop =====
    if data["pump_done"]:
        data["bottom_close"] = close if data["bottom_close"] is None else min(data["bottom_close"], close)
        drop = (data["top_close"] - data["bottom_close"]) / data["top_close"] * 100
        if drop >= DROP_PERC:
            data["drop_done"] = True
            data["neckline"] = data["bottom_close"]

    # ===== Break =====
    if data["drop_done"] and close < data["neckline"] and high_volume and not data["break_done"]:
        data["break_done"] = True
        send_message(f"🚨 BREAK: {symbol} Neckline Broken\nPrice: {close}")

    # ===== Fibonacci =====
    if data["break_done"]:
        range_ = data["top_close"] - data["neckline"]
        fibs = {
            "1.272": data["neckline"] - range_ * 1.272,
            "1.5": data["neckline"] - range_ * 1.5,
            "1.618": data["neckline"] - range_ * 1.618,
            "2.0": data["neckline"] - range_ * 2.0
        }
        for k, v in fibs.items():
            if close <= v and not data["fib_hit"][k]:
                send_message(f"🎯 {symbol} Hit Fib {k}\nPrice: {close}")
                data["fib_hit"][k] = True

# ===== التشغيل الدوري لكل العملات =====
while True:
    for s in symbols:
        try:
            check_market(s)
        except Exception as e:
            send_message(f"⚠️ Error with {s}: {e}")
    time.sleep(60)  # كل دقيقة