import paho.mqtt.client as mqtt

# 브로커 및 토픽 설정
BROKER = "192.168.0.64"
PORT = 1883
TOPIC = "test/topic"

# 메시지 수신 콜백 함수
def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload.decode()}")

# 클라이언트 생성
# client = mqtt.Client("MQTTConsumer", protocol=mqtt.MQTTv311)
client = mqtt.Client("MQTTConsumer")
# 콜백 함수 설정
client.on_message = on_message
# 브로커 연결
client.connect(BROKER, PORT, 60)
print("Connected to broker.")
# 토픽 구독
client.subscribe(TOPIC)
print(f"Subscribed to topic: {TOPIC}")
# 메시지 수신 대기
client.loop_forever()
