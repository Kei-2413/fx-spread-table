import sqlite3
import MetaTrader5 as mt5
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

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

# --- スプレッド取得・カテゴリ分け ---
def get_categorized_spreads():
    xm_path = "/home/trader/.wine/drive_c/Program Files/XMTrading MT5/terminal64.exe"
    if not mt5.initialize(path=xm_path):
        print("MT5初期化エラー:", mt5.last_error())
        return {}

    categorized = {key: [] for key in category_map.keys()}

    for symbol in mt5.symbols_get():
        name = symbol.name.split(".")[0]
        if not name.isalpha():
            continue

        tick = mt5.symbol_info_tick(symbol.name)
        if tick and symbol.point > 0:
            spread = (tick.ask - tick.bid) / (10 * symbol.point)
            row = [name, round(spread, 2)]

            found = False
            for category, pairs in category_map.items():
                if name in pairs:
                    categorized[category].append(row)
                    found = True
                    break
            if not found:
                categorized["Other"].append(row)

    mt5.shutdown()
    return categorized


# --- 実行 ---
spread_data = get_categorized_spreads()

# --- データベース保存 ---

conn = sqlite3.connect(r"Z:\home\trader\my_project\spread_data.db")
cur = conn.cursor()

print("spread_data.dbに接続しました")

sql = (
"CREATE TABLE IF NOT EXISTS spread_usdjpy ("
"time TEXT,"
"spread real"
")"
)
cur.execute(sql)

#登録データに追加

for row in spread_data["Majors"]:
    if row[0] == "USDJPY":
        usdjpy_spread = row[1]
        dt_now = datetime.now()

        #データベースにINSERT
        #if dt_now.minute in [0,30]:
        cur.execute(
            "INSERT INTO spread_usdjpy (time, spread) VALUES (?,?)",
             (dt_now, usdjpy_spread)
            )
            
brand_and_pips = (
    "CREATE TABLE IF NOT EXISTS Brand_And_Pips("
    "brand TEXT,"
    "spread real"
    ")"
)
cur.execute(brand_and_pips)

#銘柄とpipsのデータ登録

for key,row in spread_data.items():
    for item in row:
            print(f"保存中: {item[0]}, {item[1]}")
            cur.execute(
                "INSERT INTO Brand_And_Pips (brand, spread) VALUES(?,?)",
                (item[0],item[1])
                )
print("INSERT完了:", spread_data)

conn.commit()
conn.close()
