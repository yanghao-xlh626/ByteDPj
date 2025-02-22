import grpc
import hello_bilibili_pb2_grpc as pb2_grpc
import hello_bilibili_pb2 as pb2

def run():
    conn =grpc.insecure_channel('0.0.0.0:5000')
    client = pb2_grpc.BilibiliStub(channel=conn)
    response = client.HelloYanghao(pb2.HelloYanghaoReq(
        name='yanghao',
        age=25
    ))
    print(response.result)

if __name__== '__main__':
    run()