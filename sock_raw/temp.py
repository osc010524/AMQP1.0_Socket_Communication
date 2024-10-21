# # def protocol_header_metadata():
# #     # Length 자동 계산
# #     Doff = 2
# #     Type = 1
# #     Channel = 0
# #     SASL_Methode = 64 # 0x40
# #     Arguments_header = b"\xc0\x15\x01" # 분석 x
# #     Mechanisms_haeder = b"\xe0\x12\x02\xa3\05" # 분석 x
# #     Mechanisms = []
# #
# #     Mechanisms.append(b"PLAIN")
# #     Mechanisms.append(b"ANONYMOUS")
# #
# #     Mechanisms_bytes = Mechanisms_haeder
# #     Mechanisms_bytes += (b"\x09".join(Mechanisms)) # 분석 x
# #
# #     Arguments = Arguments_header
# #     Arguments += Mechanisms_bytes
# #
# #     Metadata = b""
# #     Metadata += Doff.to_bytes(1, byteorder="big")
# #     Metadata += Type.to_bytes(1, byteorder="big")
# #     Metadata += Channel.to_bytes(2, byteorder="big")
# #     Metadata += b"\x00\x53" # 분석 x
# #     Metadata += SASL_Methode.to_bytes(1, byteorder="big")
# #     Metadata += Arguments
# #
# #     Length = len(Metadata) + 4  # Add 4 bytes for the length field itself
# #     Metadata = Length.to_bytes(4, byteorder="big") + Metadata
# #
# #     return Metadata
#
#
# import socket
# import sys
#
# host = "192.168.0.47"
# port = 5672
#
#
# def hex_print(data):
#     print("Length: ", len(data))
#     print("Hex: ", end="")
#     print(" ".join("{:02x}".format(c) for c in data))
#     print("ASCII: ", end="")
#     print("".join(chr(c) if 32 <= c <= 126 else "." for c in data))
#
#
# def protocol_header_1_0_0(sock):
#     Protocol = b"AMQP"
#     Protocol_ID = 3
#     Version_Major = 1
#     Version_Minor = 0
#     Version_Revision = 0
#
#     Protocol_header = Protocol
#     Protocol_header += bytes([Protocol_ID, Version_Major, Version_Minor, Version_Revision])
#
#     sock.sendall(Protocol_header)
#     sasl_mechanisms = sock.recv(4096)
#
#     hex_print(sasl_mechanisms)
#     return sasl_mechanisms
#
#
# def sasl_mechanisms(sock, recv_message):
#     # SASL mechanisms
#     Lenght = 0
#     Doff = 2
#     Type = 1
#     Channel = 0
#     SASL_Methode = 64  # 0x40
#     Arguments_header = b"\xc0\x15\x01"  # 분석 x
#     Mechanisms_haeder = b"\xe0\x12\x02\xa3\05"  # 분석 x
#     Mechanisms = []
#
#     if recv_message[:4] == b"AMQP":
#         pass
#
#
# def socker_create(host, port):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect((host, port))
#     return sock
#
#
# if __name__ == '__main__':
#     # sock = socker_create(host, port)
#     sock = "1"
#     # recv_data = protocol_header(sock)
#     recv_data = b"AMQP.......\".....S@........PLAIN.ANONYMOUS"
#
#     sasl_mechanisms(sock, recv_data)
#
# # protocol check
#
# # if recv_message[:4] == b"AMQP":
# # if recv_message[:4] == self.protocol_header.Protocol:
# #     recv_message = recv_message[4:]
# #     self.Protocol_ID = recv_message[0]
# #     recv_message = recv_message[1:]
# #     self.Version_Major = recv_message[0]
# #     recv_message = recv_message[1:]
# #     self.Version_Minor = recv_message[0]
# #     recv_message = recv_message[1:]
# #     self.Version_Revision = recv_message[0]
# #     recv_message = recv_message[1:]
# #
# #     if protocol_version_check:
# #         if self.Protocol_ID != self.protocol_header.Protocol_ID:
# #             print("Protocol ID is not matched")
# #             return
# #         if self.Version_Major != self.protocol_header.Version_Major:
# #             print("Version Major is not matched")
# #             return
# #         if self.Version_Minor != self.protocol_header.Version_Minor:
# #             print("Version Minor is not matched")
# #             return
# #         if self.Version_Revision != self.protocol_header.Version_Revision:
# #             print("Version Revision is not matched")
# #             return
#
#

from sock_raw.AMQP_type import AMQPTypeHelper

hostname: str = "192.168.0.47"
test = AMQPTypeHelper()
hostname = test.add_delimiter_size(hostname.encode(), "str8_utf8")
print(hostname)
