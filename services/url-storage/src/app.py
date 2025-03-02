from flask import Flask,request,render_template
import sys
sys.path.append('/app/grpc')
import grpc
import Dvrpc_pb2
import Dvrpc_pb2_grpc
import os
import sqlite3
import init_config
import time


## 数据库
DB_PATH=r"/app/data/database.db"
app = Flask(__name__)


class GrpcClient:
    def __init__(self, target, timeout=5):
        self.target = target
        self.timeout = timeout

    def send_url(self, url):
        try:
            with grpc.insecure_channel(self.target) as channel:
                stub = Dvrpc_pb2_grpc.URLManagerStub(channel)
                response = stub.PushURL(Dvrpc_pb2.PushURLRequest(url=url), timeout=self.timeout)
                return response.reply == "True"
        except grpc.RpcError as e:
            print(f"GRPC Error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return False

# 主页面路由
@app.route('/', methods=['POST', 'GET'])
def add_url():
    message = None
    if request.method == 'POST':
        urls = request.form['urls'].strip()
        if urls:
            urls = [i.strip() for i in urls.split('\n') if i !='']
            for url in urls:
                client = GrpcClient('url-manager:8001')
                if client.send_url(url):
                    message = f"URL: {url} 发送成功！"
                    time.sleep(0.3)
                else:
                    message = f"URL: {url} 发送失败！"
    return render_template('index.html', message=message)

# 主函数
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)