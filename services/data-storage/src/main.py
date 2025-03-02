import os
# from services.grpc import Dvrpc_pb2_grpc, Dvrpc_pb2
import shutil
import sys
sys.path.append('/app/grpc/')
from concurrent import futures
import Dvrpc_pb2_grpc
import Dvrpc_pb2
import grpc
import time
import threading

class FileTransfer(Dvrpc_pb2_grpc.FileTransferServicer):
    def __init__(self):
        self.PATH='/app/binary_data'
    def UploadFolder(self, request_iterator, context):
        try:
            print('接收到写入请求。')
            os.makedirs(self.PATH, exist_ok=True)
            print(f"完成生成路径: {self.PATH}")
            for chunk in request_iterator:
                if chunk.is_dir:
                    dir_path=os.path.join(self.PATH,chunk.file_path)
                    print(f'正在创建文件夹:{dir_path}')
                    os.makedirs(dir_path, exist_ok=True)
                else:
                    directory = os.path.dirname(chunk.file_path)
                    os.makedirs(os.path.join(self.PATH,directory),exist_ok=True)
                    file=os.path.join(self.PATH,chunk.file_path)
                    print(f'正在下载文件：{file}')
                    with open(file,'ab') as f:
                        f.write(chunk.data)
            response = Dvrpc_pb2.UploadStatus(success=True,message='正在输出')
            return response
        except Exception as e:
            # 打印完整的错误信息
            print(f"Error in UploadFolder: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return Dvrpc_pb2.UploadResponse(message="Upload failed")




def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Dvrpc_pb2_grpc.add_FileTransferServicer_to_server(FileTransfer(), server)
    server.add_insecure_port('[::]:8001')
    server.start()
    print("服务已经启动，正在监听8001端口")
    server.wait_for_termination()

if "__main__" == __name__:
    server()