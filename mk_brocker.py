import time
from proton import Message
from proton.reactor import Container

class QueueCreator:
    def __init__(self, address):
        self.address = address

    def create_queue(self, queue_name):
        # 큐 생성 요청 메시지 작성
        message = Message(body=f'CreateQueue:{queue_name}')
        message.address = self.address

        # 메시지 전송
        self.send_message(message)

    def send_message(self, message):
        def on_send(sender):
            sender.send(message)
            print(f'Sent message: {message.body}')

        Container(on_send).run()

if __name__ == '__main__':
    broker_address = 'amqp://username:password@remote-broker-host:5672'  # 브로커 주소
    queue_name = 'testQueue'  # 생성할 큐 이름

    queue_creator = QueueCreator(broker_address)
    queue_creator.create_queue(queue_name)

    # 잠시 대기 (메시지가 처리될 시간을 주기 위해)
    time.sleep(5)
