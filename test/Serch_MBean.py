from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

class AddressListReceiver(MessagingHandler):
    def __init__(self, broker_url):
        super(AddressListReceiver, self).__init__()
        self.broker_url = broker_url
        self.receiver = None

    def on_start(self, event):
        conn = event.container.connect(self.broker_url)
        self.receiver = event.container.create_receiver(conn, "$management")  # Management address

    def on_link_opened(self, event):
        # Management message to request address list
        msg = Message(address="$management")
        msg.properties = {
            "operation": "getAddressNames"
        }
        event.sender.send(msg)

    def on_message(self, event):
        # 출력된 주소 리스트를 받음
        print("Received address list:", event.message.body)

        # 연결 종료
        event.connection.close()

def get_address_list(broker_url):
    handler = AddressListReceiver(broker_url)
    container = Container(handler)
    container.run()

# Example usage
broker_url = "amqp://192.168.0.30:5672"  # 브로커 URL 설정
get_address_list(broker_url)
