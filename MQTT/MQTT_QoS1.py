import paho.mqtt.client as mqtt

# MQTT 브로커 정보
BROKER_ADDRESS = "192.168.0.64"  # 브로커 주소
BROKER_PORT = 1883  # 브로커 포트
TOPIC = "test/topic"  # 메시지를 보낼 토픽
MESSAGE = "Hello, QoS 1 Message!"  # 전송할 메시지

# 클라이언트 생성
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully.")
        # QoS 1 레벨로 메시지 전송
        client.publish(TOPIC, MESSAGE, qos=1)
        print(f"Message published to topic '{TOPIC}': {MESSAGE}")
    else:
        print(f"Failed to connect. Return code: {rc}")

def on_publish(client, userdata, mid):
    print(f"Message ID {mid} published successfully.")

# 콜백 함수 등록
client.on_connect = on_connect
client.on_publish = on_publish

try:
    # 브로커 연결
    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    # 네트워크 루프 시작
    client.loop_start()
except Exception as e:
    print(f"An error occurred: {e}")
