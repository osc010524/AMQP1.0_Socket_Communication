import paho.mqtt.client as mqtt

# MQTT 브로커 정보
BROKER = "192.168.0.64"
PORT = 1883
TOPIC = "test/topic"
MESSAGE = "Hello, ActiveMQ with MQTT!"

# 메시지 전송 완료 콜백
def on_publish(client, userdata, mid):
    print(f"Message ID {mid} published successfully!")

# 클라이언트 생성
client = mqtt.Client("MQTTProducer")
client.on_publish = on_publish

# 브로커 연결
client.connect(BROKER, PORT, 60)

# 메시지 전송
result = client.publish(TOPIC, MESSAGE)
result.wait_for_publish()  # 전송 대기

# 연결 종료
client.disconnect()
