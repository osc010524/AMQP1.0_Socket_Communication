from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

broker_url = "amqp://192.168.0.47:5672"
address = "queue.example"

class ReceiveMessage(MessagingHandler):
    def __init__(self, broker_url, address):
        super(ReceiveMessage, self).__init__()
        self.broker_url = broker_url
        self.address = address
        self.container_id = "test"

    def on_start(self, event):
        conn = event.container.connect(self.broker_url)
        event.container.create_receiver(conn, self.address)

    def on_message(self, event):
        print(f"Received message: {event.message.body}")
        # 연결을 닫지 않고 계속 수신할 수 있도록 함.

def receive_message(broker_url, address):
    handler = ReceiveMessage(broker_url, address)
    container = Container(handler)
    container.run()

# Example usage:

receive_message(broker_url, address)
