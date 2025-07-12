import sqlite3
import MetaTrader5 as mt5
import logging, os
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# ❶ ログを書きたい場所（Wine から見える Z: パス）
LOG_PATH = r"Z:\home\trader\my_project\sh_folder\logger.log"

# ❷ ルートロガーを取得してレベルを決める
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ❸ FileHandler を作成 ―― encoding='utf-8' がポイント
fh = logging.FileHandler(LOG_PATH, encoding='utf-8')
fh.setFormatter(logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

# ❹ ロガーにハンドラを登録
logger.addHandler(fh)

# --- 通貨ペア分類マップ ---
category_map = {
    "Majors": [
        "GBPUSD", "USDCHF", "USDJPY", "USDCAD", "CHFJPY",
        "EURGBP", "EURUSD", "EURCHF", "GBPCAD", "EURJPY",
        "EURCAD", "GBPCHF", "GBPJPY", "CADCHF", "CADJPY"
    ],
    "Minors": [
        "AUDNZD", "AUDCAD", "AUDCHF", "AUDJPY", "EURAUD",
        "AUDUSD", "EURNZD", "NZDUSD", "GBPAUD", "GBPNZD",
        "NZDCAD", "NZDCHF", "NZDJPY"
    ],
    "Exotics": [
        "EURDKK", "EURHKD", "EURHUF", "EURNOK", "EURPLN",
        "EURSEK", "EURSGD", "EURTRY", "EURZAR", "GBPDKK",
        "GBPNOK", "GBPSEK", "CHFSGD", "GBPSGD", "USDZAR",
        "NZDSGD", "SGDJPY", "USDCNH", "USDDKK", "USDHKD",
        "USDHUF", "USDMXN", "USDNOK", "USDPLN", "USDSEK",
        "USDSGD", "USDTRY"
    ],
    "Metals": [
        "SILVER", "GOLD", "XAUEUR", "XPTUSD", "XPDUSD"
    ],
    "Cryptos": [
        "AAVEUSD", "ADAUSD", "ALGOUSD", "APEUSD", "APTUSD",
        "ARBUSDT", "ATOMUSD", "AVAXUSD", "AXSUSD", "BATUSD",
        "BCHUSD", "BTCEUR", "BTCGBP", "BTCUSD"
    ],
    "Other": []
}

# 収納データ
categorized = {key: {} for key in category_map.keys()}

# --- スプレッド取得・カテゴリ分け ---
def get_categorized_spreads(path,filterd_txt):
    if not mt5.initialize(path):
        print("MT5初期化エラー:", mt5.last_error())
        return {}

    for symbol in mt5.symbols_get():
        raw_name = symbol.name
        
        # フィルターされたテキストのみ通す
        if not raw_name.endswith(filterd_txt):
            continue

        name = symbol.name.split(f"{filterd_txt}")[0]

        tick = mt5.symbol_info_tick(symbol.name)

        if tick and symbol.point > 0:
            spread = round((tick.ask - tick.bid) / (10 * symbol.point), 2)

            found = False
            for category, pairs in category_map.items():
                if name in pairs:
                    categorized[category][name] = []
                    categorized[category][name].append(spread)
                    found = True
                    break
            if not found:
                categorized[category][name] = []
                categorized["Other"][name].append(spread)

    mt5.shutdown()

standard_path = "/home/trader/.wine/drive_c/Program Files/XMTrading MT5/terminal64.exe"
kiwami_path = "/home/trader/.wine/drive_c/Program Files/XMTrading MT5/KIWAMI/terminal64.exe"
zero_path = "/home/trader/.wine/drive_c/Program Files/XMTrading MT5/Zero/terminal64.exe"

# --- 実行 ---
xm_mt5_path = [standard_path, kiwami_path]

for path in xm_mt5_path:
    get_categorized_spreads(path)


# --- データベース保存 ---

conn = sqlite3.connect(r"Z:\home\trader\my_project\spread_data.db")
cur = conn.cursor()

# ---- テーブル作成（ループ処理）----            
for key in category_map:
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {key}_tbl (
    brand TEXT,
    standard_spread REAL,
    kiwami_spread REAL
    
    ); 
    """)

#銘柄とpipsのデータ登録

for key,row in categorized.items():
    for item in row:
            cur.execute(
                f"INSERT INTO {key}_tbl (brand, standard_spread, kiwami_spread) VALUES(?,?);",
                (item[0],item[1],item[2])
            )

logging.info("INSERT完了")
conn.commit()
conn.close()