from flask import Flask, render_template
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')

def show_tbl_and_img():

    #グラフ用のデータ作成

    con = sqlite3.connect("spread_data.db")
    cur = con.cursor()
    cur.execute("SELECT time, spread FROM spread_usdjpy") 
    query = "SELECT time, spread FROM spread_usdjpy"
    cur.execute(query)  
    data = cur.fetchall()



    #グラフデータの保存

    x = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f") for row in data]
    y = [row[1] for row in data]
    plt.xlabel('time')
    plt.ylabel('spread(USJPY)')
    plt.title('usdjpy_spread_graph')
    plt.xlim(min(x),max(x))
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.ylim(0,max(y)+0.5)
    plt.plot(x,y)
    plt.savefig("static/usdjpy_spread_graph.png")

    table_data = data[-30:]

    # 銘柄とスプレッドのテーブルを取得

    cur.execute("""
    SELECT b.brand, b.spread
    FROM Brand_and_Pips AS b
    JOIN (
        SELECT brand, MAX(rowid) AS max_rowid   -- brand ごとに最新 rowid
        FROM Brand_and_Pips
        GROUP BY brand
    ) latest
    ON  b.brand = latest.brand
    AND b.rowid = latest.max_rowid
""")
    SpreadData = cur.fetchall()
    con.close()            

    return render_template("index.html", table_data=table_data, SpreadData = SpreadData)


if __name__ == '__main__':

   app.run(debug=False, host='0.0.0.0', port=5000)



