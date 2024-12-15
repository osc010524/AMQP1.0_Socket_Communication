from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
from proton import Connection


class AMQPSender(MessagingHandler):
    def __init__(self, url, user, password, target_address, session_id):
        super(AMQPSender, self).__init__()
        self.url = url
        self.user = user
        self.password = password
        self.target_address = target_address
        self.session_id = session_id
        self.message_body = "Hello, this is a test message"

    def on_start(self, event):
        print("Starting connection with session ID: {}".format(self.session_id))
        conn = event.container.connect(url=self.url, user=self.user, password=self.password, virtual_host=self.session_id)
        event.container.create_sender(conn, target=self.target_address)

    def on_sendable(self, event):
        msg = Message(body=self.message_body)
        print(f"Sending message to {self.target_address} with session ID: {self.session_id}")
        event.sender.send(msg)
        print(f"Message sent: {self.message_body}")
        event.connection.close()

    def on_connection_opened(self, event: Connection):
        print(f"Connection opened for session ID: {self.session_id}")

    def on_connection_closed(self, event: Connection):
        print(f"Connection closed for session ID: {self.session_id}")

    def on_transport_error(self, event):
        print(f"Transport error: {event.transport.condition.description}")
        print(f"Transport error occurred for session ID: {self.session_id}")


if __name__ == "__main__":
    # Configuration
    # amqp_url = "amqp://192.168.0.47:61616"  # Replace with your broker URL
    amqp_url = "amqp://192.168.0.64:5672"  # Replace with your broker URL
    # user = "ACTIVEMQ.CLUSTER.ADMIN.USER"    # Replace with your username
    user = "test_user"    # Replace with your username
    # password = "CHANGE ME!!"                # Replace with your password
    password = "tes_passwd"                # Replace with your password
    target_address = "queue.example"        # Replace with your target address
    session_id = "exampleSessionId"         # Replace with your session ID

    handler = AMQPSender(amqp_url, user, password, target_address, session_id)
    container = Container(handler)
    container.run()
