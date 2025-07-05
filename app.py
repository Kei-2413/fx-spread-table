from flask import Flask, render_template
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/minor')
def show_tbl_and_img():
    # 銘柄とスプレッドのテーブルを取得
    con = sqlite3.connect("spread_data.db")
    cur = con.cursor()
        
    cur.execute("""
    SELECT b.brand, b.spread
    FROM Minors_tbl AS b
    JOIN (
        SELECT brand, MAX(rowid) AS max_rowid   -- brand ごとに最新 rowid
        FROM Minors_tbl
        GROUP BY brand
    ) latest
    ON  b.brand = latest.brand
    AND b.rowid = latest.max_rowid
""")
    SpreadData = cur.fetchall()
    con.close()            

    return render_template('minor.html', SpreadData = SpreadData)


if __name__ == '__main__':

   app.run(debug=False, host='0.0.0.0', port=5000)



