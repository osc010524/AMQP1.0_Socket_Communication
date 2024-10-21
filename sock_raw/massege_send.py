import socket
import sys
import base64
import uuid
from AMQP_type import AMQPTypeHelper
import AMQP_type

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

    def msg_send_header(self):
        self.Protocol_ID = 0 # AMQP
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

        self.Arguments_data: bytes
        self.Mechanisms_haeder: bytes = b"\xe0\x12\x02\xa3\05"  # 분석 x
        self.Mechanisms: list = []
        # self.protocol_header = protocol_header
        self.protocol_header = protocol_header.create_header()

    def process_mechanisms(self, recv_message):
        if recv_message[:len(self.protocol_header)] != self.protocol_header:
            ValueError("Protocol header is not matched")
            return
        else:
            recv_message = recv_message[len(self.protocol_header):]

        self.Length = int.from_bytes(recv_message[:4], byteorder="big")
        if self.Length != len(recv_message):
            ValueError("Length is not matched")
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
        Arguments_header = AMQPTypeHelper().delimiter_list_header("list8", len(self.Arguments_data), 1)
        self.Arguments = Arguments_header + self.Arguments_data
        SASL_Init += self.Arguments

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
            ValueError("Length is not matched")
            return
        else:
            recv_message = recv_message[4:]

        self.Doff = int.from_bytes(recv_message[:1], byteorder="big")
        recv_message = recv_message[1:]
        self.Type = int.from_bytes(recv_message[:1], byteorder="big")
        if self.Type != Type:
            TypeError("Type is not matched")
            return
        else:
            recv_message = recv_message[1:]
        self.Channel = int.from_bytes(recv_message[:2], byteorder="big")
        recv_message = recv_message[2:]

        if self.SASL_header != recv_message[:2]:
            ValueError("SASL header is not matched")
            return
        else:
            recv_message = recv_message[2:]

        SASL_Methode = int.from_bytes(recv_message[:1], byteorder="big")
        if SASL_Methode != self.SASL_Methode:
            ValueError("SASL Methode is not matched")
            return
        else:
            recv_message = recv_message[1:]

        if recv_message[:len(self.Arguments)] != self.Arguments:
            ValueError("Arguments is not matched")
            return
        else:
            recv_message = recv_message[len(self.Arguments):]

        self.Arguments_data = recv_message
        self.code = int.from_bytes(recv_message[:1], byteorder="big")

        if self.code == 0:
            # print("SASL outcome is success")
            return True

        return 0

class Open_begin_attach_send:
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
        self.Contianer_id = AMQPTypeHelper().add_delimiter_size(self.Contianer_id.encode(), "str8_utf8")
        self.hostname: str = host
        self.hostname = AMQPTypeHelper().add_delimiter_size(self.hostname.encode(), "str8_utf8")
        self.Max_Frame_Size: int = 32768  # 4 byte
        self.Max_Frame_Size = AMQP_type.UINT_DELIMITER.to_bytes() + self.Max_Frame_Size.to_bytes(4, byteorder="big")
        self.Channel_Max: int = 32768  # 2 byte
        self.Channel_Max = AMQP_type.USHORT_DELIMITER.to_bytes() + self.Channel_Max.to_bytes(2, byteorder="big")


        Open = self.Doff.to_bytes(1, byteorder="big")
        Open += self.Type.to_bytes(1, byteorder="big")
        Open += self.Channel.to_bytes(2, byteorder="big")
        Open += self.Performatives_header
        Open += Performatives.to_bytes(1, byteorder="big")

        Arguments = self.Contianer_id
        Arguments += self.hostname
        Arguments += self.Max_Frame_Size
        Arguments += self.Channel_Max
        self.Arguments_data = AMQPTypeHelper().delimiter_list_header("list8", len(Arguments), 4) + Arguments
        Open += self.Arguments_data

        length = len(Open) + 4  # Add 4 bytes for the length field itself
        Open = length.to_bytes(4, byteorder="big") + Open

        return Open

    def begin(self):
        Performatives: int = 17  # 0x10 Open
        self.Next_Outgoing_Id = 0x43
        self.Next_Outgoing_Id = AMQP_type.NULL_DELIMITER.to_bytes() + self.Next_Outgoing_Id.to_bytes(1, byteorder="big")
        self.Incoming_Window = 2147483647
        self.Incoming_Window = AMQP_type.UINT_DELIMITER.to_bytes() + self.Incoming_Window.to_bytes(4, byteorder="big")
        self.Outgoing_Window = 2147483647
        self.Outgoing_Window = AMQP_type.UINT_DELIMITER.to_bytes() + self.Outgoing_Window.to_bytes(4, byteorder="big")
        self.Handle_Max = 2147483647
        self.Handle_Max = AMQP_type.UINT_DELIMITER.to_bytes() + self.Handle_Max.to_bytes(4, byteorder="big")

        begin = self.Doff.to_bytes(1, byteorder="big")
        begin += self.Type.to_bytes(1, byteorder="big")
        begin += self.Channel.to_bytes(2, byteorder="big")
        begin += self.Performatives_header
        begin += Performatives.to_bytes(1, byteorder="big")

        Arguments = self.Next_Outgoing_Id
        Arguments += self.Incoming_Window
        Arguments += self.Outgoing_Window
        Arguments += self.Handle_Max
        self.Arguments_data = AMQPTypeHelper().delimiter_list_header("list8", len(Arguments), 5) + Arguments
        begin += self.Arguments_data

        length = len(begin) + 4  # Add 4 bytes for the length field itself
        begin = length.to_bytes(4, byteorder="big") + begin

        return begin

    def attach(self):
        Performatives: int = 18 # 0x12 Attach

        self.Name_header: bytes = b"\xc0\x63\x0b \xa1\x32"
        # self.Name: str = contianer_id + address # todo attach name = container_id + address
        self.Name: str = f"{contianer_id}-{address}" # todo attach name = container_id + address
        self.Name = AMQPTypeHelper().add_delimiter_size(self.Name.encode(), "str8_utf8")
        self.Handle: bytes = b"\x43" # todo Handle = 0
        self.Role: bytes = b"\x42" # todo Role = sender

        # todo Send_Settle_Mode = mixed(2)
        self.Send_Settle_Mode: bytes = b"\x02"
        self.Send_Settle_Mode = AMQP_type.UBYTE_DELIMITER.to_bytes() + self.Send_Settle_Mode
        # todo Receive_Settle_Mode = first(0)
        self.Receive_Settle_Mode: bytes = b"\x00"
        self.Receive_Settle_Mode = AMQP_type.UBYTE_DELIMITER.to_bytes() + self.Receive_Settle_Mode

        # Source mack
        delimiter: bytes = b"\x00\x53\x28"
        # todo Terminus_Durable = none(0)
        self.Terminus_Durable: bytes = b"\x43"
        self.Terminus_Durable = AMQP_type.NULL_DELIMITER.to_bytes() + self.Terminus_Durable
        # todo Timeout = 0
        self.Timeout: bytes = b"\x43"
        self.Timeout = AMQP_type.NULL_DELIMITER.to_bytes() + self.Timeout
        # todo Dynamic = False
        self.Dynamic: bytes = b"\x42"
        # test mack
        self.Source = self.Terminus_Durable + self.Timeout + self.Dynamic
        self.Source = AMQPTypeHelper().delimiter_list_header("list8", len(self.Source), 5) + self.Source
        self.Source = delimiter + self.Source


        # Target mack
        delimiter: bytes = b"\x00\x53\x29"

        self.Address: str = address
        self.Address = AMQPTypeHelper().add_delimiter_size(self.Address.encode(), "str8_utf8")
        self.Terminus_Durable: bytes = b"\x43" # todo Terminus_Durable = none(0)
        self.Timeout: bytes = b"\x43"
        self.Timeout = AMQP_type.NULL_DELIMITER.to_bytes() + self.Timeout
        self.Dynamic: bytes = b"\x42"

        Target_data = self.Address + self.Terminus_Durable + self.Timeout + self.Dynamic
        #todo Target mack ???
        # org : 53 29 |c0 14 05| a1 0d 71
        # self.Target = 53 29 |c0 13 05| a1 0d 71
        self.Target = AMQPTypeHelper().delimiter_list_header("list8", len(Target_data), 5) + Target_data
        self.Target = delimiter + self.Target

        self.Initial_Delivery_Count: bytes = b"\x43" # todo Initial_Delivery_Count = 0 (UINT0_DELIMITER)
        self.Initial_Delivery_Count = AMQP_type.NULL_DELIMITER.to_bytes() + self.Initial_Delivery_Count
        self.Max_Message_Size: bytes = b"\x44"

        attach = self.Doff.to_bytes(1, byteorder="big")
        attach += self.Type.to_bytes(1, byteorder="big")
        attach += self.Channel.to_bytes(2, byteorder="big")
        attach += self.Performatives_header
        attach += Performatives.to_bytes(1, byteorder="big")

        Arguments = self.Name
        Arguments += self.Handle
        Arguments += self.Role
        Arguments += self.Send_Settle_Mode
        Arguments += self.Receive_Settle_Mode
        Arguments += self.Source
        Arguments += self.Target
        Arguments += AMQP_type.NULL_DELIMITER.to_bytes()
        Arguments += self.Initial_Delivery_Count
        Arguments += self.Max_Message_Size
        Arguments = AMQPTypeHelper().delimiter_list_header("list8", len(Arguments), 0x0b) + Arguments
        attach += Arguments



        length = len(attach) + 4  # Add 4 bytes for the length field itself

        attach = length.to_bytes(4, byteorder="big") + attach

        return attach

    def open_begin_attach(self):
        result = self.protocol_header
        result += self.open()
        result += self.begin()
        result += self.attach()

        return result

class Open_begin_attach_flow_recv:
    def __init__(self, protocol_header: ProtocolHeader):
        self.Length: int
        self.Doff: int = 2
        self.Type: int = 0 # AMQP
        self.Channel: int = 0

        self.Performatives_header: bytes = Performatives_header

        self.protocol_header = protocol_header.msg_send_header()

        self.Arguments_data: bytes

    def open(self, recv_message):
        result_dic = {}

        Length = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Length"] = Length
        recv_message = recv_message[4:]

        Doff = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Doff"] = Doff
        recv_message = recv_message[1:]
        _Type = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Type"] = _Type
        recv_message = recv_message[1:]
        if _Type != 0: # todo AMQP type
            ValueError("Type is not AMQP matched")
            return

        Channel = int.from_bytes(recv_message[:2], byteorder="big")
        result_dic["Channel"] = Channel
        recv_message = recv_message[2:]

        if self.Performatives_header != recv_message[:2]:
            ValueError("Performatives header is not matched")
            return
        else:
            recv_message = recv_message[2:]

        _Performatives = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Performatives"] = _Performatives
        if _Performatives != 16: # todo open
            ValueError("Performatives is not open matched")
            return
        else:
            result_dic["Performatives"] = _Performatives
            recv_message = recv_message[1:]

        if recv_message[0] != 0xc0: # not array
            ValueError("not found Arguments")
            return

        result_dic["Arguments"] = {}
        type_byte, values_size, element = AMQPTypeHelper().de_delimiter_list_header(recv_message[:3])
        recv_message = recv_message[3:]

        Container_Id , data_size, data_type = AMQPTypeHelper().re_delimiter_valu(recv_message)
        result_dic["Arguments"]["Container_Id"] = Container_Id
        recv_message = recv_message[2:]
        recv_message = recv_message[data_size:]

        recv_message = recv_message[1:] # todo Null_delimiter

        #todo UINT_DELIMITER
        recv_message = recv_message[1:]
        Max_Frame_Size = recv_message[:4]
        result_dic["Arguments"]["Max_Frame_Size"] = Max_Frame_Size
        # result_dic["Arguments"]["Max_Frame_Size"] = int.from_bytes(self.Max_Frame_Size, byteorder="big")
        recv_message = recv_message[4:]

        # todo USHORT_DELIMITER
        recv_message = recv_message[1:]
        Channel_Max = recv_message[:2]
        result_dic["Arguments"]["Channel_Max"] = Channel_Max
        recv_message = recv_message[2:]

        # todo UINT_DELIMITER
        recv_message = recv_message[1:]
        Idle_Timeout = recv_message[:4]
        result_dic["Arguments"]["Idle_Timeout"] = Idle_Timeout
        recv_message = recv_message[4:]

        # todo Null_delimiter
        recv_message = recv_message[1:]
        recv_message = recv_message[1:]

        # todo str8_utf8 array
        array_data, type_str, array_size, element, values_type = AMQPTypeHelper().de_constructor_array(recv_message)
        result_dic["Arguments"]["offeredCapabilities"] = array_data
        recv_message = recv_message[3:]
        recv_message = recv_message[array_size:]

        # todo error??
        # # Null_delimiter
        # recv_message = recv_message[1:]

        # todo map
        dic_data, dic_size = AMQPTypeHelper().de_constructor_map(recv_message)
        result_dic["Arguments"]["properties"] = dic_data
        recv_message = recv_message[2:]
        recv_message = recv_message[dic_size:]

        self.open_dic = result_dic

        return recv_message

    def begin(self, recv_message):
        result_dic = {}

        Length = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Length"] = Length
        recv_message = recv_message[4:]

        Doff = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Doff"] = Doff
        recv_message = recv_message[1:]
        _Type = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Type"] = _Type
        recv_message = recv_message[1:]

        if _Type != 0:
            ValueError("Type is not AMQP matched")
            return

        Channel = int.from_bytes(recv_message[:2], byteorder="big")
        result_dic["Channel"] = Channel
        recv_message = recv_message[2:]

        if self.Performatives_header != recv_message[:2]:
            ValueError("Performatives header is not matched")
            return
        else:
            recv_message = recv_message[2:]

        _Performatives = int.from_bytes(recv_message[:1], byteorder="big")
        if _Performatives != 17: # todo begin
            ValueError(f"Performatives is not begin matched | Performatives = {_Performatives}")
            return
        else:
            result_dic["Performatives"] = _Performatives
            recv_message = recv_message[1:]

        #Arguments
        type_byte, values_size, element = AMQPTypeHelper().de_delimiter_list_header(recv_message[:3])
        result_dic["Arguments"] = {}
        recv_message = recv_message[3:]

        # USHORT_DELIMITER
        recv_message = recv_message[1:]
        Remort_Channel = int.from_bytes(recv_message[:2], byteorder="big")
        result_dic["Arguments"]["Remort_Channel"] = Remort_Channel
        recv_message = recv_message[2:]

        # SMALL_UINT_DELIMITER
        recv_message = recv_message[1:]
        Next_Outgoing_Id = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Next_Outgoing_Id"] = Next_Outgoing_Id
        recv_message = recv_message[1:]

        # UINT_DELIMITER
        recv_message = recv_message[1:]
        Incoming_Window = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Arguments"]["Incoming_Window"] = Incoming_Window
        recv_message = recv_message[4:]

        # UINT_DELIMITER
        recv_message = recv_message[1:]
        Outgoing_Window = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Arguments"]["Outgoing_Window"] = Outgoing_Window
        recv_message = recv_message[4:]

        # UINT_DELIMITER
        recv_message = recv_message[1:]
        Handle_Max = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Arguments"]["Handle_Max"] = Handle_Max
        recv_message = recv_message[4:]

        self.begin_dic = result_dic

        return recv_message


    def attach(self, recv_message):
        result_dic = {}

        performatives = 18  # 0x12 Attach

        Length = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Length"] = Length
        recv_message = recv_message[4:]

        Doff = recv_message[1]
        result_dic["Doff"] = Doff
        recv_message = recv_message[1:]

        _Type = int.from_bytes(recv_message[:1], byteorder="big")
        if _Type != 0: # todo AMQP type
            print("Type is not AMQP matched")
            return
        else:
            recv_message = recv_message[1:]

        Channel = int.from_bytes(recv_message[:2], byteorder="big")
        result_dic["Channel"] = Channel
        recv_message = recv_message[2:]

        if self.Performatives_header != recv_message[:2]:
            print("Performatives is not attach matched")
            return
        else:
            recv_message = recv_message[2:]

        _Performatives = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Performatives"] = _Performatives
        if _Performatives != performatives:
            print("Performatives is not attach matched")
            return
        else:
            recv_message = recv_message[1:]

        # Arguments
        type_byte, values_size, element = AMQPTypeHelper().de_delimiter_list_header(recv_message[:3])
        result_dic["Arguments"] = {}
        recv_message = recv_message[3:]

        value, value_size, value_type = AMQPTypeHelper().re_delimiter_valu(recv_message)
        Name = value
        result_dic["Arguments"]["Name"] = Name
        recv_message = recv_message[2:]
        recv_message = recv_message[value_size:]

        # Handle
        Handle = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Handle"] = Handle
        recv_message = recv_message[1:]

        # Role
        Role = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Role"] = Role
        recv_message = recv_message[1:]

        # Send_Settle_Mode
        # UBYTE_DELIMITER
        recv_message = recv_message[1:]
        Send_Settle_Mode = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Send_Settle_Mode"] = Send_Settle_Mode
        recv_message = recv_message[1:]

        # Receive_Settle_Mode
        # UBYTE_DELIMITER
        recv_message = recv_message[1:]
        Receive_Settle_Mode = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Receive_Settle_Mode"] = Receive_Settle_Mode
        recv_message = recv_message[1:]

        # Source Header
        recv_message = recv_message[3:]  # 0x00 0x53 0x28
        Source = recv_message[:1]
        result_dic["Arguments"]["Source"] = [Source]
        recv_message = recv_message[1:]

        # Target Header
        recv_message = recv_message[3:]  # 0x00 0x53 0x29
        type_byte, values_size, element = AMQPTypeHelper().de_delimiter_list_header(recv_message)
        result_dic["Arguments"]["Target"] = {}
        recv_message = recv_message[3:]

        value, value_size, value_type = AMQPTypeHelper().re_delimiter_valu(recv_message)
        Address = value
        result_dic["Arguments"]["Target"]["Address"] = Address
        recv_message = recv_message[2:]
        recv_message = recv_message[value_size:]

        self.attach_dic = result_dic

        return recv_message

    def flow(self, recv_message):
        result_dic = {}

        performatives = 19  # 0x13 19 Flow

        Length = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Length"] = Length
        recv_message = recv_message[4:]

        Doff = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Doff"] = Doff
        recv_message = recv_message[1:]

        _Type = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Type"] = _Type
        if _Type != 0: # todo AMQP type
            print("Type is not AMQP matched")
            return
        else:
            recv_message = recv_message[1:]

        Channel = int.from_bytes(recv_message[:2], byteorder="big")
        result_dic["Channel"] = Channel
        recv_message = recv_message[2:]

        if self.Performatives_header != recv_message[:2]:
            print("Performatives is not flow matched")
            return
        else:
            recv_message = recv_message[2:]

        Performatives = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Performatives"] = Performatives
        recv_message = recv_message[1:]

        # Arguments
        type_byte, values_size, element = AMQPTypeHelper().de_delimiter_list_header(recv_message[:3])
        result_dic["Arguments"] = {}
        recv_message = recv_message[3:]

        # Next_Incoming_Id
        next_incoming_id = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Next_Incoming_Id"] = next_incoming_id
        recv_message = recv_message[1:]

        # Incoming_Window
        # UINT_DELIMITER
        recv_message = recv_message[1:]
        incoming_window = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Arguments"]["Incoming_Window"] = incoming_window
        recv_message = recv_message[4:]

        # Next_Outgoing_Id
        # SMALL_UINT_DELIMITER
        recv_message = recv_message[1:]
        next_outgoing_id = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Next_Outgoing_Id"] = next_outgoing_id
        recv_message = recv_message[1:]

        # Outgoing_Window
        # UINT_DELIMITER
        recv_message = recv_message[1:]
        outgoing_window = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Arguments"]["Outgoing_Window"] = outgoing_window
        recv_message = recv_message[4:]

        # Handle
        handle = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Handle"] = handle
        recv_message = recv_message[1:]

        # Delivery_Count
        delivery_count = int.from_bytes(recv_message[:1], byteorder="big")
        result_dic["Arguments"]["Delivery_Count"] = delivery_count
        recv_message = recv_message[1:]

        # Link_Credit
        # UINT_DELIMITER
        recv_message = recv_message[1:]
        link_credit = int.from_bytes(recv_message[:4], byteorder="big")
        result_dic["Arguments"]["Link_Credit"] = link_credit
        recv_message = recv_message[4:]

        self.flow_dic = result_dic

        return recv_message


    def open_begin_attach_flow(self, recv_message):
        open_result = self.open(recv_message)
        begin_result = self.begin(open_result)
        attach_result = self.attach(begin_result)
        flow_result = self.flow(attach_result)

        return True

class Transfer_send:
    def __init__(self):
        pass
    def transfer(self,send_msg_data, send_msg_type="str8_utf8"):
        Doff: int = 2
        Doff = Doff.to_bytes(1, byteorder="big")
        _Type: int = 0
        _Type = _Type.to_bytes(1, byteorder="big")
        Channel: int = 0
        Channel = Channel.to_bytes(2, byteorder="big")
        _Performatives_header: bytes = Performatives_header
        Performatives = b"\x14"  # 0x14 Transfer
        Performatives = Performatives_header + Performatives

        #Arguments
        Handle:bytes = b"\x43" # todo Handle = 0
        Delivery_Id:bytes = b"\x43" # todo Delivery-Id = 0
        Delivery_Tag:bytes = b"\x31" # todo Delivery-Tag = 31
        Delivery_Tag = AMQPTypeHelper().add_delimiter_size(Delivery_Tag, "vbin8")
        Message_Format:bytes = b"\x43" # todo Message-Format = 0
        Arguments = Handle + Delivery_Id + Delivery_Tag + Message_Format
        Arguments = AMQPTypeHelper().delimiter_list_header("list8", len(Arguments), 0x04) + Arguments

        Message_Haeder = b"\x00\x53\x70" + b"\x45"
        Message_Properties = b"\x00\x53\x73" + b"\x45"
        # todo 메세지 내용 작성
        AMQP_Value = b"\x00\x53\x77"
        AMQP_Value += AMQPTypeHelper().add_delimiter_size(send_msg_data.encode(), send_msg_type)

        result = Doff + _Type + Channel + Performatives + Arguments + Message_Haeder + Message_Properties + AMQP_Value

        length = len(result) + 4  # Add 4 bytes for the length field itself
        result = length.to_bytes(4, byteorder="big") + result

        return result

    def disposition(self,received_data):
        result_dic = {}
        Length = int.from_bytes(received_data[:4], byteorder="big")
        result_dic["Length"] = Length
        received_data = received_data[4:]

        Doff = int.from_bytes(received_data[:1], byteorder="big")
        result_dic["Doff"] = Doff
        received_data = received_data[1:]

        _Type = int.from_bytes(received_data[:1], byteorder="big")
        result_dic["Type"] = _Type
        received_data = received_data[1:]

        Channel = int.from_bytes(received_data[:2], byteorder="big")
        result_dic["Channel"] = Channel
        received_data = received_data[2:]

        if received_data[:2] != Performatives_header:
            print("Performatives header is not matched")
            return
        else:
            received_data = received_data[2:]

        Performatives = int.from_bytes(received_data[:1], byteorder="big")
        result_dic["Performatives"] = Performatives
        received_data = received_data[1:]

        # Arguments
        type_byte, values_size, element = AMQPTypeHelper().de_delimiter_list_header(received_data[:3])
        result_dic["Arguments"] = {}
        received_data = received_data[3:]

        # Role
        Role = received_data[:1]
        result_dic["Arguments"]["Role"] = Role
        received_data = received_data[1:]

        # First
        First = received_data[:1]
        result_dic["Arguments"]["First"] = First
        received_data = received_data[1:]

        # Last
        Last = received_data[:1]
        result_dic["Arguments"]["Last"] = Last
        received_data = received_data[1:]

        # Settled
        Settled = received_data[:1]
        result_dic["Arguments"]["Settled"] = Settled
        received_data = received_data[1:]

        # Accepted
        # AMQPTypeHelper().de_constructor_list(received_data)
        Accepted_haeder = received_data[:3] # 0x00 0x53 0x24
        result_dic["Arguments"]["Accepted"] = {}
        received_data = received_data[3:]

        return result_dic


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
    sasl_outcome = SASLOutcome(SASL_init)
    sasl_outcome.sasl_outcome(recv_data)

    recv_data = socket_handler.receive_packet()

    open_begin_attach = Open_begin_attach_send(protocol_header)
    open_begin_attach_packet = open_begin_attach.open_begin_attach()
    socket_handler.send_packet(open_begin_attach_packet)

    recv_data = socket_handler.receive_packet()
    open_begin_attach_flow = Open_begin_attach_flow_recv(protocol_header)
    open_begin_attach_flow.open_begin_attach_flow(recv_data)

    transfer = Transfer_send()
    transfer_packet = transfer.transfer("Hello World")
    socket_handler.send_packet(transfer_packet)

    recv_data = socket_handler.receive_packet()
    disposition = transfer.disposition(recv_data)
    print(disposition)

if __name__ == '__main__':
    main()