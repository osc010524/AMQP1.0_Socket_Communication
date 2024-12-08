from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

broker_url = "amqp://192.168.0.64:61616" #ALL port
# broker_url = "amqp://192.168.0.32:5672" # AMQP port
address = "queue.example"

class SendMessage(MessagingHandler):
    def __init__(self, broker_url, address):
        super(SendMessage, self).__init__()
        self.broker_url = broker_url
        self.address = address
        self.user = "admin"
        self.password = "admin"
        self.sender = None

    def on_start(self, event):
        self.conn = event.container.connect(self.broker_url)
        self.sender = event.container.create_sender(self.conn, self.address)

    def on_sendable(self, event):
        # 메시지를 보낼 준비가 되었을 때 호출되므로 여기는 빈 상태로 둡니다.
        pass

    def send_message(self, message_body):
        if self.sender.credit > 0:  # 송신자의 신용(credit)이 있어야 메시지 전송 가능
            message = Message(body=message_body, ttl=300000)
            self.sender.send(message)

    def on_connection_closed(self, event):
        event.container.stop()

def send_message(broker_url, address):
    handler = SendMessage(broker_url, address)
    container = Container(handler)

    # 별도의 쓰레드에서 컨테이너를 실행
    from threading import Thread
    thread = Thread(target=container.run)
    thread.start()

    # 사용자 입력을 받는 루프
    while True:
        message_body = input("Enter a message to send (or 'exit' to quit): ")
        if message_body.lower() == 'exit':
            handler.conn.close()  # 연결을 종료하고 루프 탈출
            break
        handler.send_message(message_body)
        handler.conn.close()
        break


# Example usage:
send_message(broker_url, address)
