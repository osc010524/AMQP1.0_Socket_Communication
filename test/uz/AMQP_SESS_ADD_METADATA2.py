from proton import Message
from proton.reactor import Container
from proton.handlers import MessagingHandler

class MetaDataAMQPClient(MessagingHandler):
    def __init__(self, server_url, metadata):
        super(MetaDataAMQPClient, self).__init__()
        self.server_url = server_url
        self.metadata = metadata

    def on_start(self, event):
        # Open a connection to the AMQP server
        self.connection = event.container.connect(self.server_url)
        # Create a sender link to initiate communication
        self.sender = event.container.create_sender(self.connection, target=None)
        print("Connection started with AMQP broker.")

    def on_sendable(self, event):
        # Attach metadata to a message
        message = Message()
        message.body = "Metadata initialization"
        message.properties = {
            "_AMQ_Session_AddMetaDataKey": self.metadata["key"],
            "_AMQ_Session_AddMetaDataValue": self.metadata["value"],
            "_AMQ_Session_RequiresConfirmations": True  # To trigger the `SESS_ADD_METADATA2` case
        }

        # Send the message to the server
        event.sender.send(message)
        print(f"Sent message with metadata: {self.metadata}")
        event.sender.close()
        event.connection.close()

    def on_connection_closed(self, event):
        print("Connection closed.")

if __name__ == "__main__":
    # Define the server URL and metadata to be added
    server_url = "amqp://192.168.0.64:5672"
    metadata = {
        "key": "example_key",
        "value": "example_value"
    }

    # Start the AMQP client
    try:
        client = MetaDataAMQPClient(server_url, metadata)
        Container(client).run()
    except Exception as e:
        print(f"Error: {e}")
