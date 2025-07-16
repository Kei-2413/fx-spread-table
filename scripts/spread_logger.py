import sqlite3
import MetaTrader5 as mt5
import logging, os
from datetime import datetime, timedelta

# ログを書きたい場所（Wine から見える Z: パス）
LOG_PATH = r"Z:\home\trader\my_project\sh_folder\logger.log"

# ルートロガーを取得してレベルを決める
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# FileHandler を作成 
fh = logging.FileHandler(LOG_PATH, encoding='utf-8')
fh.setFormatter(logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

# ロガーにハンドラを登録
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
        "ATOMUSD", "AVAXUSD", "AXSUSD", "BATUSD",
        "BCHUSD", "BTCEUR", "BTCGBP", "BTCUSD"
    ],
    "Other": []
}

# 収納データ
spread_data = {}

# --- スプレッド取得・カテゴリ分け ---
def get_categorized_spreads(path,filterd_txt,i):
    if not mt5.initialize(path):
        print("MT5初期化エラー:", mt5.last_error())
        return {}
   
    for symbol in mt5.symbols_get():
        tick = mt5.symbol_info_tick(symbol.name)    
        raw_name = symbol.name

        # USDJPY# → USDJPY に透過する
        symbol_name = raw_name.split(filterd_txt)[0] if filterd_txt else raw_name
        
        # ----------------通行許可の条件--------------
        if filterd_txt is not None:
            if not raw_name.endswith(filterd_txt):continue
        if not tick and symbol.point > 0:continue
        # -------------------------------------------

        spread = round((tick.ask - tick.bid) / (10 * symbol.point), 2)

        if symbol_name not in spread_data.keys():
            spread_data[symbol_name] = ["-"] * 3
        
        spread_data[symbol_name][i] = spread

    mt5.shutdown()

standard_path = "/home/trader/.wine/drive_c/Program Files/XMTrading MT5/terminal64.exe"
kiwami_path = "/home/trader/.wine/drive_c/Program Files/XMTrading MT5/KIWAMI/terminal64.exe"
zero_path = "/home/trader/.wine/drive_c/Program Files/XMTrading MT5/Zero/terminal64.exe"

# --- 実行 ---
xm_mt5_path = [standard_path,kiwami_path, zero_path]
filter_list = [None,"#", "."]

for i in range(len(xm_mt5_path)):
    get_categorized_spreads(xm_mt5_path[i],filter_list[i],i)


categorized_sp_data = {key: {} for key in category_map.keys()}

# --- 2次元辞書の作成 ---

for cat, sp_list in category_map.items():
    for symbol in spread_data.keys():
        if symbol in sp_list:
            categorized_sp_data[cat][symbol] = spread_data[symbol]

        else:
            categorized_sp_data["Other"][symbol] = spread_data[symbol]
        

print(categorized_sp_data)

# --- データベース保存 ---

conn = sqlite3.connect(r"Z:\home\trader\my_project\spread_data.db")
cur = conn.cursor()

# ---- テーブル作成（ループ処理）----            
for key in category_map:
    cur.execute(f"DROP TABLE IF EXISTS {key}_tbl;") #テーブルを消去
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {key}_tbl (
    brand TEXT,
    standard_spread REAL,
    kiwami_spread REAL,
    zero_spread REAL
    ); 
    """)

#銘柄とpipsのデータ登録

for cat,sp_dict in categorized_sp_data.items():
    for pair,sp_list in sp_dict.items():
        cur.execute(
            f"INSERT INTO {cat}_tbl (brand, standard_spread, kiwami_spread, zero_spread) VALUES(?,?,?,?);",
            (pair, sp_list[0], sp_list[1], sp_list[2])
        )

logging.info("INSERT完了")
conn.commit()
conn.close()
