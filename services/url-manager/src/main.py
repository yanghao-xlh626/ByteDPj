import sys
sys.path.append('/app/grpc')
from concurrent import futures
import Dvrpc_pb2_grpc
import Dvrpc_pb2
import grpc
import time
import threading
import socket
import config
# 整体大概是这样，grpc服务端负责三件事，
# 第一件，接受爬虫节点启动后的注册请求，
# 第二件，接受来自flask推过来的url，并载入队列
# 多线程函数负责将队列中的url异步分发。会先调用heartbeat确定节点的存活，再根据节点状态对元数据进行维护，在节点正常的时候发送url


class URLManager(Dvrpc_pb2_grpc.URLManagerServicer):
    def __init__(self):
        self.max_url_restric=7
        self.urlpool=list()
        self.registers=list() #回头注册的节点要会用字符串的形式写入此处，id:{ip/容器名:端口}
        self.container_index=0
    def __ipadd__(self,ip):
        if ip in self.registers:
            return
        else:
            self.registers.append(ip)
    def PushURL(self,request,context):
        print(f'已经成功接收到URL:{request.url}')
        response = Dvrpc_pb2.PushURLReply(reply="True")
        self.urlpool.append(request.url)
        print(f"URL:{request.url}已转储成功")
        # NOTE:这里需要调用一个函数进行对url的数据池进行判断，如果达到设定的阈值就启动新的节点
        if config.status==0:#第一次收到url的时候基本register已经注册，此时直接创建线程
            thread(self.urlpool,self.registers) # NOTE:这里需要有一个函数进行url的分发
        return response
    def Registe(self,request,context):
        print(f'已接受到节点{request.node_ip}的注册请求')
        self.__ipadd__(request.node_ip)
        ip = socket.gethostbyname(socket.gethostname())
        response = Dvrpc_pb2.RegisteResponse(core_ip=f'{ip}')
        print(self.registers)
        print(f'已注册完成，正在知会{request.node_ip}')
        return response

def url_send__(url,registers):
    print(f'正在分发url，共有{len(url)}条')
    while True:
        while url and registers:
            i=0
            register_size=len(registers)
            send_url=url.pop(0)
            i=(i+1)%register_size
            send_register=registers[i]
            ret = heartbeat(send_register,registers)
            if ret ==1:
                url_send__client(send_register,send_url,urlpool=url)
            elif ret==4:
                url.insert(0, send_url)
        time.sleep(5)        

def heartbeat(ip,registers):
    # 发送heartbeat，
    timeout_restric=5
    try:
        channel =grpc.insecure_channel(f"{ip}:8001")
        stub = Dvrpc_pb2_grpc.SpidersNodeStub(channel)
        print(f'正在确认是否{ip}节点存活')
        request=Dvrpc_pb2.HeartbeatQuery(query="True")
        response=stub.Heartbeat(request,timeout=timeout_restric)
        if response.reply =="True":
            print('节点存活')
            return 1
        else:
            print(f'节点{ip}无响应，正在移除')
            registers.remove(ip)
            return 4
    except grpc.RpcError as e:
        print(f'与 {ip} 节点通信失败: {e}')
        registers.remove(ip)  # 移除该节点IP
        return 4
    except Exception as e:
        # 捕获其他异常
        print(f'检查 {ip} 节点时发生错误: {e}')
        registers.remove(ip)  # 移除该节点IP
        return 4
    
def url_send__client(ip,url,urlpool):
    timeout_restrict=5
    # 发送url，等收到了返回值，就将url记录到database里
    channel = grpc.insecure_channel(f'{ip}:8001')
    stub = Dvrpc_pb2_grpc.SpidersNodeStub(channel)
    print(f'正在向节点{ip}发送url:{url}')
    request = Dvrpc_pb2.DistributeURLRequest(url=f'{url}')
    print('正在等待节点接受任务')
    response =stub.DistributeURL(request)
    if response.reply==True:
        print(f'已经得到{ip}的响应，等待它的爬取。')
    else:
        urlpool.insert(0,url)
        print(f'节点忙，正在尝试下一个节点')
    
def thread(url,registers):
    config.status=1
    print('分发url服务正在启动')
    th=threading.Thread(target=url_send__,args=(url,registers,))
    th.start()
    print('url分发服务启动完成,欢迎访问,主人')

def serve():
    # 创建服务器gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 注册服务
    urlmanager=URLManager()
    Dvrpc_pb2_grpc.add_URLManagerServicer_to_server(urlmanager,server)
    server.add_insecure_port("[::]:8001")
    server.start()
    print("主控正在运行. 监听端口 8001")
    # 等待服务器终止
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
