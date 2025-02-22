import grpc
import hello_bilibili_pb2_grpc as pb2
import hello_bilibili_pb2_grpc as pb2_grpc

from concurrent import futures
import time

class Bilibili(pb2_grpc.BilibiliServicer):
    def HelloYanghao(self,request,context):
        name = request.name
        age = request.age
        result= f'my name is {name},i am {age} years old'
        return pb2.HelloYanghaoReply(result=result)
    

def run():
    grpc_server =grpc.server(
        futures.ThreadPoolExecutor(max_workers=4)
    )
    pb2_grpc.add_BilibiliServicer_to_server(Bilibili(),grpc_server)
    grpc_server.add_insecure_port('0.0.0.0:5000')
    print('server will start at 0.0.0.0:5000')
    grpc_server.start() 

    try:
        while 1:
            time.sleep(3600)
    except KeyboardInterrupt:
        grpc_server.stop(0)

if __name__ == '__main__':
    run()