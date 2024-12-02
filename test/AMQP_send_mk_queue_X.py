# 큐 생성 코드
# chatGPT 코드 실제 생성자를 따라가면
# queue_name => address

from proton import Message
from proton.reactor import Container
from proton.handlers import MessagingHandler
import time

class QueueCreator(MessagingHandler):
    def __init__(self, url, queue_name):
        super(QueueCreator, self).__init__()
        self.url = url
        self.queue_name = queue_name
        self.conn = None  # 연결 객체를 저장하기 위한 변수

    def on_start(self, event):
        # 브로커에 연결
        self.conn = event.container.connect(self.url)
        # 큐에 메시지를 보내면서 큐를 생성
        event.container.create_sender(self.conn, self.queue_name)

    def on_sendable(self, event):
        # 큐 생성 요청 메시지 전송
        msg = Message(body="Create queue")
        event.sender.send(msg)
        print(f"Queue '{self.queue_name}' created on {self.url}")

        # 송신자 닫기
        event.sender.close()

        # 연결 종료 예약
        event.reactor.schedule(0.1, self)  # 0.1초 후 연결 종료 스케줄링

    def on_timer_task(self, event):
        if self.conn:
            print("Closing the connection.")
            self.conn.close()

if __name__ == "__main__":
    broker_url = "amqp://192.168.0.32:5672"  # 브로커 주소
    queue_name = "testQQ"                    # 생성할 큐 이름

    container = Container(QueueCreator(broker_url, queue_name))
    container.run()  # 이벤트 루프 실행
