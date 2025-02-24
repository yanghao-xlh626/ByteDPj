from flask import Flask,request,render_template
import os
import sqlite3
import init_config
## 数据库
DB_PATH=r"/app/data/database.db"
app = Flask(__name__)

def write_data(url):
    # 对传入的url进行剔除空白，并去数据库查找url对应的记录的数量
    url=url.strip()
    conn = sqlite3.connect('/app/data/database.db')
    cur=conn.cursor()
    count=cur.execute(f"select count(ID) from URL where URL='{url}'").fetchone()[0]
    # 如果数据库中有记录，则跳过，没记录，则写入数据库，并发送给到任务池。
    if count>=1:
        pass
    else:
        cur.execute(f"INSERT INTO URL (ID, URL) VALUES (1, '{url}')")
        pass # NOTE 这里需要调用一个函数来进行url的分发
    conn.commit()
    conn.close()
    return 



@app.route('/',methods=['POST','GET'])
def add_url():
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        url = request.form['url']
        write_data(url)
    return render_template('index.html')

if __name__ == '__main__':
    init_config.init_db(DB_PATH)
    app.run(host='0.0.0.0', port=8000)