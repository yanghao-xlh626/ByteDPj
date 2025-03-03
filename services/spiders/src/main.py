import os
import time
import sys
sys.path.append('/app/grpc')
# sys.path.append('/home/os/Docker/academyrepos/services/grpc')
from concurrent import futures
import Dvrpc_pb2_grpc
import Dvrpc_pb2
import grpc
import socket
import animate
import config
import threading

manager_ip=None
def send_ip():
    count=0
    timeout_restrict=5
    while count<5:
        try:
            channel = grpc.insecure_channel('url-manager:8001')
            stub = Dvrpc_pb2_grpc.URLManagerStub(channel)
            my_ip = socket.gethostbyname(socket.gethostname())
            print('正在向主控进行注册')
            request = Dvrpc_pb2.RegisteRequest(node_ip=f"{my_ip}")
            response = stub.Registe(request,timeout=timeout_restrict)
            if response.core_ip:
                global manager_ip
                manager_ip= response.core_ip
                print(f'得到主控{manager_ip}授权，注册完毕，等待任务')
                return my_ip
            else:
                print('注册失败，正在重试')
                count+=1
                continue
        except grpc.RpcError as e:
            count +=1
            print(f'第{count}次注册尝试超时,再次尝试注册，错误信息:{e}')
    print('重试失败，请检查节点是否可以访问')
    return my_ip



class SpidersNode(Dvrpc_pb2_grpc.SpidersNodeServicer):
    def __init__(self,my_ip):
        self.my_ip=my_ip
    def Heartbeat(self,request,context):
        print(f"收到来自主控的heartbeat")
        response = Dvrpc_pb2.HeartbeatReply(reply="True")
        print('正在回传数据')
        return response
    def DistributeURL(self,request,context):
        print(f'正在接收来自主控的URL{request.url}')
        response = Dvrpc_pb2.DistributeURLResponse(reply=True)
        print('正在爬取数据')
        # NOTE:爬虫的逻辑,需要启动一个线程，当线程启动增加
        if config.thread_current<config.tread_max:
            config.thread_current+=1
            print(f'爬虫线程{config.thread_current}已经启动')
            th=threading.Thread(target=animate.main,args=(my_ip,request.url))
            th.start()
            return response
        else:
            response = Dvrpc_pb2.DistributeURLResponse(reply=False)
            return response


def serve(my_ip):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    Dvrpc_pb2_grpc.add_SpidersNodeServicer_to_server(SpidersNode(my_ip=my_ip),server)
    server.add_insecure_port("0.0.0.0:8001")
    server.start()
    print('爬虫启动完毕，正在监听8001')
    server.wait_for_termination()

if __name__ == "__main__":
    my_ip=send_ip()
    serve(my_ip)
