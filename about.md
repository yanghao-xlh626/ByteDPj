# 整体结构
url-storage
- flask获取url并进行比对是否爬过(X),再将url转发到url-manager
- url-manager部署有两个服务端,并维护了一些数据
    - 数据：
        - urlpol的限制长度，超过该长度就会尝试启动一个docker容器
        - urlpool，用来维护来自flask的url
        - registers列表，用来维护来自spider节点的注册信息，存放着spider节点的ip
        - container_index：不记得干啥了，应该是废弃了
    - PushURL服务。允许flask发送url
    - Registe服务，允许spider节点向自己注册ip到registers中
    - 分发线程，在首次发送url的时候会创建一个循环线程，间歇性通过轮询的方式发送urlpool中的数据到spider节点。每次回先发一个heartbeat，确认是否存活，不存活则回滚本次操作，
- spiders部署有两个服务端：
    - Heartbeat;允许url-manager发送heartbeat信息
    - DistributeURL,允许分发线程发送url到本机，每次调用回启动一个线程，达到限制个数后回等待其他线程的爬虫释放资源
    - 注册函数：在启动的时候回尝试向url-manager注册自己

# 问题1
这个系统通过flask获取用户发送的url，进行一轮检查后，直接发送到url-manager，这不好，因为flask并不知道这个url是否被爬取过了。它只知道自己接收过没。
# 思路1
将flask的数据库放到url-manager去维护，让flask作为一个代理，可以发送到多个url-manager

# 问题2
当前的url-manager发送一个url后，收到的只是spider是否get到这个url，并不知道spider是否完成了爬取，
# 思路2
添加一个新的服务，让爬虫节点完成后，能发送url到url-manager，并让url-manager向数据库写入一条记录。

# 问题3
系统worker的扩展性很差，需要增加扩展能力。
# 思路3
url-manager需要作为grpc的客户端访问另一台机器上的服务端，并在节点数量不足的时候通过python docker创建一个节点。

# 问题4
什么时候回收一个节点呢？？没想好。
# 思路4 
不知道