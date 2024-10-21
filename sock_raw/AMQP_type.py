# AMQP 타입별 Delimiter(구분자) 값 정의

# Null
NULL_DELIMITER = 0x40

# Boolean
BOOLEAN_TRUE_DELIMITER = 0x41
BOOLEAN_FALSE_DELIMITER = 0x42
BOOLEAN_DELIMITER = 0x56

# Unsigned Byte (ubyte)
UBYTE_DELIMITER = 0x50

# Unsigned Short (ushort)
USHORT_DELIMITER = 0x60

# Unsigned Integer (uint)
UINT_DELIMITER = 0x70
SMALL_UINT_DELIMITER = 0x52
UINT0_DELIMITER = 0x43

# Unsigned Long (ulong)
ULONG_DELIMITER = 0x80
SMALL_ULONG_DELIMITER = 0x53
ULONG0_DELIMITER = 0x44

# Byte (byte)
BYTE_DELIMITER = 0x51

# Short (short)
SHORT_DELIMITER = 0x61

# Integer (int)
INT_DELIMITER = 0x71
SMALL_INT_DELIMITER = 0x54

# Long (long)
LONG_DELIMITER = 0x81
SMALL_LONG_DELIMITER = 0x55

# Float (float)
FLOAT_DELIMITER = 0x72  # IEEE-754

# Double (double)
DOUBLE_DELIMITER = 0x82  # IEEE-754

# Decimal
DECIMAL32_DELIMITER = 0x74  # IEEE-754
DECIMAL64_DELIMITER = 0x84  # IEEE-754
DECIMAL128_DELIMITER = 0x94  # IEEE-754

# Char (char)
CHAR_DELIMITER = 0x73  # UTF-32

# Timestamp (timestamp)
TIMESTAMP_DELIMITER = 0x83  # Milliseconds (64-bit)

# UUID (uuid)
UUID_DELIMITER = 0x98

# Binary (binary)
VBIN8_DELIMITER = 0xa0
VBIN32_DELIMITER = 0xb0

# String (string)
STR8_UTF8_DELIMITER = 0xa1
STR32_UTF8_DELIMITER = 0xb1

# Symbol (symbol)
SYM8_DELIMITER = 0xa3
SYM32_DELIMITER = 0xb3

# List (list)
LIST0_DELIMITER = 0x45
LIST8_DELIMITER = 0xc0
LIST32_DELIMITER = 0xd0

# Map (map)
MAP8_DELIMITER = 0xc1
MAP32_DELIMITER = 0xd1

# Array (array)
ARRAY8_DELIMITER = 0xe0
ARRAY32_DELIMITER = 0xf0

class AMQPTypeHelper:
    def __init__(self):
        self.delimiters = {
            # Null
            "null": NULL_DELIMITER,

            # Boolean
            "boolean_true": BOOLEAN_TRUE_DELIMITER,
            "boolean_false": BOOLEAN_FALSE_DELIMITER,
            "boolean": BOOLEAN_DELIMITER,

            # Unsigned Byte (ubyte)
            "ubyte": UBYTE_DELIMITER,

            # Unsigned Short (ushort)
            "ushort": USHORT_DELIMITER,

            # Unsigned Integer (uint)
            "uint": UINT_DELIMITER,
            "smalluint": SMALL_UINT_DELIMITER,
            "uint0": UINT0_DELIMITER,

            # Unsigned Long (ulong)
            "ulong": ULONG_DELIMITER,
            "smallulong": SMALL_ULONG_DELIMITER,
            "ulong0": ULONG0_DELIMITER,

            # Byte (byte)
            "byte": BYTE_DELIMITER,

            # Short (short)
            "short": SHORT_DELIMITER,

            # Integer (int)
            "int": INT_DELIMITER,
            "smallint": SMALL_INT_DELIMITER,

            # Long (long)
            "long": LONG_DELIMITER,
            "smalllong": SMALL_LONG_DELIMITER,

            # Float (float)
            "float": FLOAT_DELIMITER,

            # Double (double)
            "double": DOUBLE_DELIMITER,

            # Decimal
            "decimal32": DECIMAL32_DELIMITER,
            "decimal64": DECIMAL64_DELIMITER,
            "decimal128": DECIMAL128_DELIMITER,

            # Char (char)
            "char": CHAR_DELIMITER,

            # Timestamp (timestamp)
            "timestamp": TIMESTAMP_DELIMITER,

            # UUID (uuid)
            "uuid": UUID_DELIMITER,

            # Binary (binary)
            "vbin8": VBIN8_DELIMITER,
            "vbin32": VBIN32_DELIMITER,

            # String (string)
            "str8_utf8": STR8_UTF8_DELIMITER,
            "str32_utf8": STR32_UTF8_DELIMITER,

            # Symbol (symbol)
            "sym8": SYM8_DELIMITER,
            "sym32": SYM32_DELIMITER,

            # List (list)
            "list0": LIST0_DELIMITER,
            "list8": LIST8_DELIMITER,
            "list32": LIST32_DELIMITER,

            # Map (map)
            "map8": MAP8_DELIMITER,
            "map32": MAP32_DELIMITER,

            # Array (array)
            "array8": ARRAY8_DELIMITER,
            "array32": ARRAY32_DELIMITER,
        }

        self.reverse_delimiters = {v: k for k, v in self.delimiters.items()}

    def add_delimiter(self, value:bytes, value_type):
        """
        해당 값에 맞는 구분자를 추가

        Args:
            value (bytes): 값
            value_type (str): 값의 타입 ( document 참조 )

        Returns:
            bytes: bytes([value_type]) + value
        """
        try:
            value_type = self.delimiters[value_type]
        except KeyError:
            raise KeyError("Invalid value type")

        result = bytes([value_type]) + value

        return result  # 구분자가 없는 경우 그대로 반환

    def add_delimiter_size(self, value:bytes, value_type:bytes) -> bytes :
        """
        해당 값에 맞는 구분자와 사이즈를 추가
        :param value: 값 (bytes)
        :param value_type: 값의 타입 (str) ( doc 참조 )
        :return: bytes([value_type]) + len(value).to_bytes(byteorder='big') + value
        """
        try:
            value_type = self.delimiters[value_type]
        except KeyError:
            raise KeyError("Invalid value type")

        result = bytes([value_type]) + len(value).to_bytes(byteorder='big') + value

        return result  # 구분자가 없는 경우 그대로 반환

    def re_delimiter_valu(self, value:bytes):
        """
        해당 값에 맞는 구분자와 사이즈를 제거
        :param value: 값 (bytes)
        :return: value, value_size, value_type
        """
        value_type = value[0]
        value_size = value[1]
        value = value[2:]

        try:
            value_type = self.reverse_delimiters[value_type]
        except KeyError:
            raise KeyError(f"Invalid value type | value_type = {hex(value_type)} | value = {value}")

        try:
            value = value[:value_size]
            return value, value_size, value_type
        except:
            return Exception("Invalid value size")

    def delimiter_list_header(self, type:str, values_size:int, element:int) -> bytes:
        """
        array 타입의 값 생성
        :param type: array 타입 (str)
        :param values_size: array 사이즈 (int)
        :param element: array 개수 (int)
        :return:

        type:
            - "list0": LIST0_DELIMITER,
            - "list8": LIST8_DELIMITER,
            - "list32": LIST32_DELIMITER
        """
        try:
            type_byte = self.delimiters[type]
        except KeyError:
            raise KeyError("Invalid value type")

        result = type_byte.to_bytes() + values_size.to_bytes() + element.to_bytes()
        return result

    def de_delimiter_list_header(self, value:bytes):
        """
        list 타입의 값 분해
        :param type: list 타입 (str)
        :param values_size: list 사이즈 (int)
        :param element: list 개수 (int)
        :return:

        type:
            - "list0": LIST0_DELIMITER,
            - "list8": LIST8_DELIMITER,
            - "list32": LIST32_DELIMITER
        """
        try:
            type_byte = self.reverse_delimiters[value[0]]
        except KeyError:
            raise KeyError(f"Invalid value type | value_type = {hex(value[0])}")
        # values_size = int.from_bytes(value[1], byteorder='big')
        values_size = value[1]
        element = int.from_bytes(value[2:], byteorder='big')

        return type_byte, values_size, element

    def de_delimiter_array_header(self, value: bytes):
        """
        array 타입의 header 분해
        :param value: raw data (bytes)
        :return:
        """
        type_byte = value[0]
        try:
            type_str = self.reverse_delimiters[type_byte]
        except KeyError:
            raise KeyError("Invalid value type")

        values_size = value[1]
        element = value[2]
        values_type = value[3]
        value = value[4:]
        value = value[:values_size]

        return type_str, values_size, element, values_type, value

    def de_constructor_array(self, value: bytes):
        type_str, array_size, element, values_type, value = self.de_delimiter_array_header(value)

        array_result = []
        for i in range(element):
            length = value[0]
            value = value[1:]
            val = value[:length]
            value = value[length:]
            array_result.append(val)

        return array_result , type_str, array_size, element, values_type

    def de_delimiter_map_header(self, value:bytes):
        """
        map 타입의 header 분해
        :param type: map 타입 (str)
        :param values_size: map 사이즈 (int)
        :param element: map 개수 (int)
        :return: type_str, values_size, element

        type:
            - "map8": MAP8_DELIMITER,
            - "map32": MAP32_DELIMITER
        """
        type_byte = value[0]
        try:
            type_str = self.reverse_delimiters[type_byte]
        except KeyError:
            raise KeyError(f"Invalid value type | value_type = {hex(type_byte)}")

        values_size = value[1]
        element = value[2]

        return type_str, values_size, element

    def de_constructor_map (self, value:bytes):
        """
        map 타입의 값 분해
        :param value: map 타입 값 (bytes)
        :return:
        """
        type_str, dic_size, element = self.de_delimiter_map_header(value)
        value = value[3:]

        dic = {}
        for i in range(element//2):
            key, key_size, key_type = self.re_delimiter_valu(value)
            value = value[2:]
            value = value[key_size:]
            val, val_size, val_type = self.re_delimiter_valu(value)
            value = value[2:]
            value = value[val_size:]
            dic[key] = val

        return dic , dic_size


if __name__ == '__main__':
#     #b'sole-connection-for-container' 29 sym8
#     data = bytes.fromhex("a3 1d 73 6f 6c 65 2d 63 6f 6e 6e 65 63 74 69 6f 6e 2d 66 6f 72 2d 63 6f 6e 74 61 69 6e 65 72 80 80 80")
#     data = bytes.fromhex("c1 34 04 a3 07 70 72 6f 64 75 63 74 a1 17 61 70 61 63 68 65 2d 61 63 74 69 76 65 6d 71 2d 61 72 74 65 6d 69 73 a3 07 76 65 72 73 69 6f 6e a1 06 32 2e 33 37 2e 30")
    data = bytes.fromhex("e04d04a31d736f6c652d636f6e6e656374696f6e2d666f722d636f6e7461696e65721044454c415945445f44454c49564552590b5348415245442d535542530f414e4f4e594d4f55532d52454c4159")
    # print(data)
    amqp = AMQPTypeHelper()
    # print(amqp.de_constructor_array(data))
# 0xe0 0x4d 0x04 0xa3 0x1d