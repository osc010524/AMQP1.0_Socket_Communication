import socket
import sys
import base64
import uuid
from types import AMQPTypeHelper

#option
protocol_version_check = True
Type = 1 # SASL
contianer_id = str(uuid.uuid4())
address = "queue.example"

#default
SASL_header = b"\x00\x53"
Performatives_header = b"\x00\x53"

host = "192.168.0.47"
port = 5672


def hex_print(data):
    print("Length: ", len(data))
    print("Hex: ", end="")
    print(" ".join("{:02x}".format(c) for c in data))
    print("ASCII: ", end="")
    print("".join(chr(c) if 32 <= c <= 126 else "." for c in data))




class ProtocolHeader:
    def __init__(self):
        self.Protocol = b"AMQP"
        self.Protocol_ID = 3
        self.Version_Major = 1
        self.Version_Minor = 0
        self.Version_Revision = 0

    def create_header(self):
        Protocol_header = self.Protocol
        Protocol_header += bytes([self.Protocol_ID, self.Version_Major, self.Version_Minor, self.Version_Revision])
        return Protocol_header

    def msg_send_header(self, sock):
        self.Protocol_ID = 0
        Protocol_header = self.Protocol
        Protocol_header += bytes([self.Protocol_ID, self.Version_Major, self.Version_Minor, self.Version_Revision])
        return Protocol_header


class SASLMechanisms:
    def __init__(self, protocol_header: ProtocolHeader):
        self.Length: int
        self.Doff: int
        self.Type: int
        self.Channel: int
        # self.SASL_header: bytes = b"\x00\x53"  # 분석 x
        self.SASL_header: bytes = SASL_header  # 분석 x
        self.SASL_Methode: int = 64  # 0x40 SASL_MECHANISMS

        self.Arguments_header: bytes = b"\xc0\x15\x01"  # 분석 x
        self.Arguments_header = AMQPTypeHelper().LIST8_DELIMITER


        self.Arguments_data: bytes
        self.Mechanisms_haeder: bytes = b"\xe0\x12\x02\xa3\05"  # 분석 x
        self.Mechanisms: list = []
        # self.protocol_header = protocol_header
        self.protocol_header = protocol_header.create_header()

    def process_mechanisms(self, recv_message):
        if recv_message[:len(self.protocol_header)] != self.protocol_header:
            print("Protocol header is not matched")
            return
        else:
            recv_message = recv_message[len(self.protocol_header):]

        self.Length = int.from_bytes(recv_message[:4], byteorder="big")
        if self.Length != len(recv_message):
            print("Length is not matched")
            return
        else:
            recv_message = recv_message[4:]

        self.Doff = int.from_bytes(recv_message[:1], byteorder="big")
        recv_message = recv_message[1:]

        self.Type = int.from_bytes(recv_message[:1], byteorder="big")
        recv_message = recv_message[1:]
        if self.Type != Type:
            print("Type is not matched")
            return

        self.Channel = int.from_bytes(recv_message[:2], byteorder="big")
        recv_message = recv_message[2:]

        if self.SASL_header != recv_message[:2]:
            print("SASL header is not matched")
            return
        else:
            recv_message = recv_message[2:]

        SASL_Methode = int.from_bytes(recv_message[:1], byteorder="big")
        if SASL_Methode != self.SASL_Methode:
            print("SASL Methode is not matched")
            return
        else:
            recv_message = recv_message[1:]


        if recv_message[:len(self.Arguments_header)] != self.Arguments_header:
            print("Arguments header is not matched")
            return
        else:
            recv_message = recv_message[len(self.Arguments_header):]
            self.Arguments_data = recv_message

        if recv_message[:len(self.Mechanisms_haeder)] != self.Mechanisms_haeder:
            print("Mechanisms header is not matched")
            return
        else:
            recv_message = recv_message[len(self.Mechanisms_haeder):]
            self.Mechanisms = recv_message

        self.delimiter = b"\x09"
        self.Mechanisms = self.Mechanisms.split(self.delimiter)
        # self.Mechanisms = [mechanism.decode() for mechanism in self.Mechanisms]

        return 0

class SASLInit:
    def __init__(self, SASL_Mechanisms: SASLMechanisms):
        self.Length: int
        self.Doff: int = 2
        self.Type: int = Type
        self.Channel: int = 0
        # self.SASL_header: bytes = b"\x00\x53"  # 분석 x
        self.SASL_header: bytes = SASL_header  # 분석 x
        self.SASL_Methode: int = 65  # 0x41 SASL_INIT

        self.Arguments :bytes
        self.Arguments_data: bytes

        self.SASL_Mechanisms = SASL_Mechanisms

    def auth_data(self):
        #todo 임시 제작
        # SASL PLAIN
        # auth_str = f"\0{username}\0{password}"
        Mechanisms = [mechanism.decode() for mechanism in self.SASL_Mechanisms.Mechanisms]
        if Mechanisms[0] == "PLAIN":
            id = Mechanisms[1] # ANONYMOUS
            pw = Mechanisms[1].lower()
            data = b"\xa3\x09" + id.encode() + b"\xa0\x09" + pw.encode()
        return data

    def create_sasl_init(self):
        SASL_Init = self.Doff.to_bytes(1, byteorder="big")
        SASL_Init += self.Type.to_bytes(1, byteorder="big")
        SASL_Init += self.Channel.to_bytes(2, byteorder="big")
        SASL_Init += self.SASL_header
        SASL_Init += self.SASL_Methode.to_bytes(1, byteorder="big")

        self.Arguments_data = self.auth_data()
        Arguments_header = AMQPTypeHelper().constructor_list_header("list8", len(self.Arguments_data), 1)
        self.Arguments = Arguments_header + self.Arguments_data

        self.Length = len(SASL_Init) + 4  # Add 4 bytes for the length field itself
        SASL_Init = self.Length.to_bytes(4, byteorder="big") + SASL_Init

        return SASL_Init

class SASLOutcome:
    def __init__(self,SASLInit: SASLInit):
        self.Length: int
        self.Doff: int = 2
        self.Type: int = Type
        self.Channel: int = 0
        # self.SASL_header: bytes = b"\x00\x53"  # 분석 x
        self.SASL_header: bytes = SASL_header  # 분석 x
        self.SASL_Methode: int = 68  # 0x44 SASL_OUTCOME
        self.Arguments: bytes = SASLInit.Arguments
        self.Arguments_data: bytes
        self.code : int

    def sasl_outcome(self,recv_message):
        self.Length = int.from_bytes(recv_message[:4], byteorder="big")
        if len(recv_message) != self.Length:
            print("Length is not matched")
            return
        else:
            recv_message = recv_message[4:]

        self.Doff = int.from_bytes(recv_message[:1], byteorder="big")
        recv_message = recv_message[1:]
        self.Type = int.from_bytes(recv_message[:1], byteorder="big")
        if self.Type != Type:
            print("Type is not matched")
            return
        else:
            recv_message = recv_message[1:]
        self.Channel = int.from_bytes(recv_message[:2], byteorder="big")
        recv_message = recv_message[2:]

        if self.SASL_header != recv_message[:2]:
            print("SASL header is not matched")
            return
        else:
            recv_message = recv_message[2:]

        SASL_Methode = int.from_bytes(recv_message[:1], byteorder="big")
        if SASL_Methode != self.SASL_Methode:
            print("SASL Methode is not matched")
            return
        else:
            recv_message = recv_message[1:]

        if recv_message[:len(self.Arguments)] != self.Arguments:
            print("Arguments is not matched")
            return
        else:
            recv_message = recv_message[len(self.Arguments):]

        self.Arguments_data = recv_message
        self.code = int.from_bytes(recv_message[:1], byteorder="big")

        if self.code == 0:
            # print("SASL outcome is success")
            return True

        return 0

class Open_begin_attach:
    def __init__(self, protocol_header: ProtocolHeader):
        self.Length: int
        self.Doff: int = 2
        self.Type: int = 0 # AMQP
        self.Channel: int = 0

        self.Performatives_header: bytes = Performatives_header

        self.protocol_header = protocol_header.msg_send_header()

        self.Arguments_data: bytes


    def open(self):
        Performatives: int = 16  # 0x10 Open

        self.Contianer_id: str = contianer_id
        self.Contianer_id = AMQPTypeHelper.add_delimiter_size(self.Contianer_id.encode(), "str8_utf8")
        self.hostname: str = host
        self.hostname = AMQPTypeHelper.add_delimiter_size(self.hostname.encode(), "str8_utf8")
        self.Max_Frame_Size: int = 32768  # todo 임시 제작 분석 x
        self.Max_Frame_Size = AMQPTypeHelper().UINT_DELIMITER + self.Max_Frame_Size
        self.Channel_Max: int = 32768  # todo 임시 제작 분석 x
        self.Channel_Max = AMQPTypeHelper().USHORT_DELIMITER + self.Channel_Max


        Open = self.Doff.to_bytes(1, byteorder="big")
        Open += self.Type.to_bytes(1, byteorder="big")
        Open += self.Channel.to_bytes(2, byteorder="big")
        Open += self.Performatives_header
        Open += Performatives.to_bytes(1, byteorder="big")

        Arguments = self.Contianer_id
        Arguments += self.hostname
        Arguments += self.Max_Frame_Size
        Arguments += self.Channel_Max
        self.Arguments_data = AMQPTypeHelper().constructor_list_header("list8", len(Arguments), 4) + Arguments
        Open += Arguments

        length = len(Open) + 4  # Add 4 bytes for the length field itself
        Open = length.to_bytes(4, byteorder="big") + Open

        return Open

    def begin(self):
        Performatives: int = 11  # 0x10 Open
        self.Next_Outgoing_Id_header: bytes = b"\x12\x05\x40" #todo 임시 제작 분석 x 0x40 => 1 byte
        self.Next_Outgoing_Id = 0
        self.Incoming_Window_header: bytes = b"\x70"  # todo 임시 제작 분석 x
        self.Incoming_Window = 2147483647
        self.Outgoing_Window_header: bytes = b"\x70"
        self.Outgoing_Window = 2147483647
        self.Handle_Max_header: bytes = b"\x70"
        self.Handle_Max = 2147483647

        begin = self.Doff.to_bytes(1, byteorder="big")
        begin += self.Type.to_bytes(1, byteorder="big")
        begin += self.Channel.to_bytes(2, byteorder="big")
        begin += self.Performatives_header
        begin += Performatives.to_bytes(1, byteorder="big")

        begin += self.Arguments_header
        begin += self.Next_Outgoing_Id_header
        begin += self.Next_Outgoing_Id.to_bytes(4, byteorder="big")
        begin += self.Incoming_Window_header
        begin += self.Incoming_Window.to_bytes(4, byteorder="big")
        begin += self.Outgoing_Window_header
        begin += self.Outgoing_Window.to_bytes(4, byteorder="big")
        begin += self.Handle_Max_header
        begin += self.Handle_Max.to_bytes(4, byteorder="big")

        length = len(begin) + 4  # Add 4 bytes for the length field itself
        begin = length.to_bytes(4, byteorder="big") + begin

        return begin

    def attach(self):
        Performatives: int = 18 # 0x12 Attach

        self.Name_header: bytes = b"\x63\x0b\xa1\x32"
        self.Name: str = self.Contianer_id + address # todo attach name = container_id + address
        self.Handle: bytes = b"\x43" # todo Handle = 0
        self.Role: bytes = b"\x42" # todo Role = sender

        # todo Send_Settle_Mode = mixed(2)
        self.Send_Settle_Mode: bytes = b"\x02"
        self.Send_Settle_Mode = AMQPTypeHelper().UBYTE_DELIMITER + self.Send_Settle_Mode
        # todo Receive_Settle_Mode = first(0)
        self.Receive_Settle_Mode: bytes = b"\x00"
        self.Receive_Settle_Mode = AMQPTypeHelper().UBYTE_DELIMITER + self.Receive_Settle_Mode

        # Source mack
        delimiter: bytes = b"\x00\x53\x28"
        self.Source_header: bytes = b"\xc0\x06\x05\x40"
        self.Source = delimiter + self.Source_header
        # todo Terminus_Durable = none(0)
        self.Terminus_Durable: bytes = b"\x00"
        self.Terminus_Durable = AMQPTypeHelper().UINT0_DELIMITER + self.Terminus_Durable
        # todo Timeout = 0
        self.Timeout: bytes = b"\x00"
        self.Timeout = AMQPTypeHelper().UINT0_DELIMITER + self.Timeout
        # todo Dynamic = False
        self.Dynamic: bytes = b"\x42"
        # source mack
        self.Source = self.Source + self.Terminus_Durable + self.Timeout + self.Dynamic

        # Target mack
        delimiter: bytes = b"\x00\x53\x29"
        self.Target_header: bytes = b"\xc0\x14\x05"
        self.Target = delimiter + self.Target_Target_header
        self.Address_header: bytes = b"\xa1\x0d"
        self.Address: str = address
        self.Terminus_Durable: bytes = b"\x43" # todo Terminus_Durable = none(0)
        self.Timeout: bytes = b"\x00"
        self.Timeout = AMQPTypeHelper().UINT0_DELIMITER + self.Timeout
        self.Dynamic: bytes = b"\x42"
        self.Dynamic = AMQPTypeHelper().UINT0_DELIMITER + self.Dynamic

        self.Target = self.Target + self.Address_header + self.Address + self.Terminus_Durable + self.Timeout + self.Dynamic

        self.Initial_Delivery_Count: bytes = b"\x43" # todo Initial_Delivery_Count = 0 (UINT0_DELIMITER)
        self.Initial_Delivery_Count = AMQPTypeHelper().UINT0_DELIMITER + self.Initial_Delivery_Count
        self.Max_Message_Size: bytes = b"\x43"

        attach = self.Doff.to_bytes(1, byteorder="big")
        attach += self.Type.to_bytes(1, byteorder="big")
        attach += self.Channel.to_bytes(2, byteorder="big")
        attach += self.Performatives_header
        attach += Performatives.to_bytes(1, byteorder="big")
        attach += self.Arguments_header
        attach += self.Name_header
        attach += self.Name.encode()
        attach += self.Handle
        attach += self.Role

        attach += self.Send_Settle_Mode
        attach += self.Receive_Settle_Mode

        attach += self.Source
        attach += self.Target

        attach += AMQPTypeHelper().UINT0_DELIMITER
        attach += self.Initial_Delivery_Count
        attach += self.Max_Message_Size

        length = len(attach) + 4  # Add 4 bytes for the length field itself

        attach = length.to_bytes(4, byteorder="big") + attach

        return attach

    def open_begin_attach(self):
        open = self.open()
        begin = self.begin()
        attach = self.attach()

        return open + begin + attach



class SocketHandler:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_protocol_header(self, data):
        self.sock.sendall(data)

    def send_packet(self, data):
        self.sock.sendall(data)

    def receive_packet(self):
        return self.sock.recv(4096)


def main():
    socket_handler = SocketHandler(host, port)
    socket_handler.create_socket()

    protocol_header = ProtocolHeader()
    header = protocol_header.create_header()
    socket_handler.send_protocol_header(header)

    # recv_data = socket_handler.receive_sasl_mechanisms()
    recv_data = socket_handler.receive_packet()

    sasl_mechanisms = SASLMechanisms(protocol_header)
    sasl_mechanisms.process_mechanisms(recv_data)

    SASL_init = SASLInit(sasl_mechanisms)
    sasl_init_packet = SASL_init.create_sasl_init()
    socket_handler.send_packet(sasl_init_packet)

    recv_data = socket_handler.receive_packet()
    sasl_outcome = SASLOutcome()
    sasl_outcome.sasl_outcome(recv_data)

    open_begin_attach = Open_begin_attach(protocol_header)
    open_begin_attach_packet = open_begin_attach.open_begin_attach()
    socket_handler.send_packet(open_begin_attach_packet)

if __name__ == '__main__':
    main()