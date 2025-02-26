from flask import Flask,request,render_template
import sys
sys.path.append('/app/grpc')
import grpc
import Dvrpc_pb2
import Dvrpc_pb2_grpc
import os
import sqlite3
import init_config


## 数据库
DB_PATH=r"/app/data/database.db"
app = Flask(__name__)

def send2manager(url):
    count=0
    timeout_restrict=5
    while count<=5:
        try:
            channel = grpc.insecure_channel('url-manager:8001')
            stub = Dvrpc_pb2_grpc.URLManagerStub(channel)
            response = stub.PushURL(Dvrpc_pb2.PushURLRequest(url=url),timeout=timeout_restrict)
            if response.reply=="True":
                print(f'URL:{url}发送成功,正在等待下一操作')
                return
            else:
                print(f'URL:{url}发送失败，正在重试')
                count+=1
                continue
        except grpc.RpcError as e:
            # 捕获超时异常或其他 gRPC 错误
            print(f'{url} 发送失败，错误信息: {e}')
            count += 1
    print('重试失败，请检查节点是否可以访问')
    return 



def write_data(url):
    # 对传入的url进行剔除空白，并去数据库查找url对应的记录的数量
    url=url.strip()
    conn = sqlite3.connect('/app/data/database.db')
    cur=conn.cursor()
    count=cur.execute(f"select count(ID) from URL where URL='{url}'").fetchone()[0]
    # 如果数据库中有记录，则跳过，没记录，则写入数据库，并发送给到任务池。
    if count>=1:
        print(1)
    else:
        send2manager(url=url)
        cur.execute(f"INSERT INTO URL (URL) VALUES ('{url}')")
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