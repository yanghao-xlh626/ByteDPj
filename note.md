# 基于compose配置启动5个节点。
docker-compose up -d --build --pull never


```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. hello_bilibili.proto
# -I 指定.proto文件的搜素路径，
# --python_out= 指定当前路径
# hello_bilibili.proto 指定生成后的文件名
```