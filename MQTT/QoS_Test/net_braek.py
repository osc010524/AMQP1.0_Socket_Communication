import time
import paho.mqtt.client as mqtt

# 브로커 정보
BROKER_ADDRESS = "192.168.0.64"  # 브로커 주소
PORT = 1883                    # MQTT 기본 포트
TOPIC = "test/topic"          # 테스트용 토픽
QOS = 1                        # QoS 레벨 설정

# 메시지 수신 콜백 함수
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic} with QoS {msg.qos}")

# 연결 콜백 함수
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        client.subscribe(TOPIC, qos=QOS)
    else:
        print(f"Failed to connect with result code {rc}")

# 연결 끊김 콜백 함수
def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")

# 클라이언트 초기화
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# 브로커 연결
print("Connecting to broker...")
client.connect(BROKER_ADDRESS, PORT, keepalive=60)

# 별도의 쓰레드에서 네트워크 루프 실행
client.loop_start()

# 메시지 발행
print("Publishing initial message...")
client.publish(TOPIC, payload="Initial Message", qos=QOS)

# 네트워크 연결 끊김 시뮬레이션
print("Simulating disconnect...")
client.disconnect()  # 클라이언트 연결 강제 종료

# 대기
time.sleep(5)

# 다시 연결
print("Reconnecting to broker...")
client.reconnect()

# 대기
time.sleep(5)

# 메시지 발행 확인
print("Publishing message after reconnect...")
client.publish(TOPIC, payload="Message after reconnect", qos=QOS)

# 종료
client.loop_stop()
client.disconnect()
print("Test completed")
