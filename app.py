from flask import Flask, render_template
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

VALID_CATEGORIES = {
    "major":   "Majors_tbl",
    "minor":   "Minors_tbl",
    "exotic":  "Exotics_tbl",
    "metal":   "Metals_tbl",
    "crypto":  "Cryptos_tbl",
    "other":   "other_tbl",
}

@app.route('/spread/<category>')
def show_spread(category):
    # 銘柄とスプレッドのテーブルを取得
    con = sqlite3.connect("spread_data.db")
    cur = con.cursor()
    tbl = VALID_CATEGORIES[category]
    page_title = f"{category} table"
        
    cur.execute(f"""
    SELECT b.brand, b.standard_spread, b.kiwami_spread, b.zero_spread
    FROM  {tbl} AS b
    JOIN (
        SELECT brand, MAX(rowid) AS max_rowid
        FROM {tbl}
        GROUP BY brand
    ) latest
    ON  b.brand = latest.brand
    AND b.rowid = latest.max_rowid
""")
    SpreadData = cur.fetchall()
    con.close()            

    return render_template(f"{category}.html", SpreadData = SpreadData, page_title = page_title)


if __name__ == '__main__':

   app.run(debug=False, host='0.0.0.0', port=5000)