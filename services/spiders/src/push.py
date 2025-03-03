import os
# from services.grpc import Dvrpc_pb2_grpc, Dvrpc_pb2
import sys
sys.path.append('/app/grpc/')
import Dvrpc_pb2_grpc
import Dvrpc_pb2
import grpc
current_working_directory = os.getcwd()



def generate_chunk(PATH):
    folders_name=os.listdir(PATH)
    for folder_name in folders_name:
        absolute_path=os.path.join(current_working_directory,PATH,folder_name)
        relative_path = os.path.relpath(absolute_path, current_working_directory)
        if os.path.isdir(absolute_path):
            chunk = Dvrpc_pb2.FolderChunk(
                file_path=relative_path,
                is_dir= True
            )
            print(f"Sending directory chunk: {relative_path}")
            yield chunk
        else :
            with open(absolute_path, "rb") as file:
                chunk_size = 4096  # 每个数据块的大小，按需调整
                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break  # 文件读取完毕
                    file_chunk = Dvrpc_pb2.FolderChunk(
                        data=data,
                        file_path = relative_path,
                        is_dir = False
                    )
                    print(f"Sending file chunk: {relative_path}, size: {len(data)} bytes")
                    yield file_chunk

def upload_folder(stub,PATH):
    chunks = generate_chunk(PATH)
    response = stub.UploadFolder(chunks)
    print(response.message)
    return response

def push(PATH):
    channel = grpc.insecure_channel('down_disk:8001')
    stub = Dvrpc_pb2_grpc.FileTransferStub(channel)
    response=upload_folder(stub,PATH)
    return response

