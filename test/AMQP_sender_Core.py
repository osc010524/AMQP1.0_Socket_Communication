import json
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

# ActiveMQ Artemis 서버 정보
BROKER_URL = "amqp://192.168.0.47:5672"  # ActiveMQ 브로커 주소
ADDRESS = "queue.example"  # ActiveMQ에 생성된 주소

# 전송할 Core 정보
core_info = {
    "message_id": "12345",
    "priority": 4,
    "user_property": "custom_value",
    "content": "Hello, this is a Core message!"
}

# 메시지 핸들러 정의
class CoreMessageSender(MessagingHandler):
    def __init__(self, broker_url, address, core_info):
        super(CoreMessageSender, self).__init__()
        self.broker_url = broker_url
        self.address = address
        self.core_info = core_info

    def on_start(self, event):
        # 브로커와 연결하고 송신자 생성
        conn = event.container.connect(self.broker_url)
        event.container.create_sender(conn, self.address)

    def on_sendable(self, event):
        # 메시지 생성 및 Core 정보 설정
        message = Message()
        message.id = self.core_info["message_id"]
        message.priority = self.core_info["priority"]

        # Core 정보를 application_properties에 설정
        message.application_properties = {
            "user_property": self.core_info["user_property"]
        }

        # 메시지 본문을 JSON 형식으로 설정
        message.body = json.dumps({
            "content": self.core_info["content"]
        })

        # 메시지 전송
        event.sender.send(message)
        print(f"Message with Core info sent to {self.address}")
        event.connection.close()

# 메시지 전송 실행
try:
    Container(CoreMessageSender(BROKER_URL, ADDRESS, core_info)).run()
except KeyboardInterrupt:
    print("Message sending interrupted")
