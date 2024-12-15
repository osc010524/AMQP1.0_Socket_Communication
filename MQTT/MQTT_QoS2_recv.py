import paho.mqtt.client as mqtt

# MQTT 브로커 정보
BROKER_ADDRESS = "192.168.0.64"  # 브로커 주소
BROKER_PORT = 1883  # 브로커 포트
TOPIC = "example/qos2"  # 구독할 토픽

# 메시지 수신 콜백 함수
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic} with QoS {msg.qos}")

# 브로커 연결 시 호출되는 콜백 함수
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to broker.")
        # QoS 2 레벨로 토픽 구독
        client.subscribe(TOPIC, qos=2)
        print(f"Subscribed to topic '{TOPIC}' with QoS 2")
    else:
        print(f"Failed to connect. Return code: {rc}")

# 클라이언트 생성
client = mqtt.Client()

# 콜백 함수 등록
client.on_connect = on_connect
client.on_message = on_message

try:
    # 브로커 연결
    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    # 네트워크 루프 실행
    client.loop_forever()
except Exception as e:
    print(f"An error occurred: {e}")
