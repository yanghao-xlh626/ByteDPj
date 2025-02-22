import os
import time
from kafka import KafkaProducer, KafkaConsumer

def test_kafka_connection():
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        producer.send('test-topic', b'ping')
        producer.flush()
        print("✅ Kafka连接成功")
        return True
    except Exception as e:
        print(f"❌ Kafka连接失败: {str(e)}")
        return False

if __name__ == '__main__':
    print("等待Kafka服务启动...")
    time.sleep(10)  # 给Kafka留出启动时间
    if test_kafka_connection():
        print("爬虫节点准备就绪")
        while True:
            time.sleep(1)  # 保持容器运行