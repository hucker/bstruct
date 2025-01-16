"""
Wrapper around the struct module to provide a better developer experience.

The speed of this code should be ever so slightly slower because

"""

import struct

from enum import Enum

BinaryType = int | float | str | bool | bytes

class ByteOrder(Enum):
    LITTLE_ENDIAN = '<'
    BIG_ENDIAN = '>'
    NETWORK_ORDER = '!'
    NATIVE_ORDER = '='

    def __repr__(self):
        # return f'<{self.__class__.__name__}.{self.name}>'
        return f'<{self.name}>'


class Format:
    def __init__(self, fmt: str, size: int = 1, byte_order:ByteOrder=ByteOrder.BIG_ENDIAN):
        self.fmt = fmt
        self.size = size
        self.byte_order = byte_order
        self.full_format = self.byte_order.value + self.fmt

    def pack(self, value: BinaryType) -> bytes:
        return struct.pack(self.byte_order + self.full_format, value)

    def unpack(self, packed_data: bytes) -> BinaryType:
        return struct.unpack(self.byte_order + self.full_format, packed_data)[0]


# String format
class String(Format):
    """A class to handle fixed-size string format."""

    def __init__(self, size: int,fill=b'\x00'):
        """
        Args:
            size (int): Size of the string (in bytes).
        """
        self.fill = fill
        super().__init__(f'{size}s', size)

    def pack(self, value: str) -> bytes:
        """
        Packs a string into binary format with padding to the specified size.

        Args:
            value (str): The string to pack.

        Returns:
            bytes: The packed binary data.
        """
        # Pad the string to the fixed size
        return super().pack(value.encode('utf-8').ljust(self.size, self.fill))

    def unpack(self, packed_data: bytes) -> str:
        """
        Unpacks binary data into a string, stripping padding.

        Args:
            packed_data (bytes): The packed binary data.

        Returns:
            str: The unpacked string.
        """
        return super().unpack(packed_data).decode('utf-8').rstrip('\x00')

class PascalString(Format):
    def __init__(self):
        import warnings
        warnings.warn('Pascal String Not Supported',DeprecationWarning,stacklevel=2)
        super().__init__('p', 2)

    def pack(self, value: str,truncate=False):
        # Ensure the string length is less than 255
        if truncate:
            value=value[:254]

        elif len(value) >= 255:
            raise ValueError(f"String too long ({len(value)}) to pack as Pascal String. Limit=255")

        # Prepend the length before packing
        length_byte = len(value).to_bytes(1, 'little')
        value_byte = value.encode()

        return length_byte + value_byte

    def unpack(self, value: bytes):
        # First byte is the length of the string
        str_len = value[0]

        # The rest is the string data
        str_data = value[1:1 + str_len].decode()

        return str_data


class Char(Format):
    """A class to handle unsigned 8-bit integer format."""

    def __init__(self):
        super().__init__('c', 1)

class _Bool(Format):
    """A class to handle unsigned boolean values."""

    def __init__(self):
        super().__init__('?', 1)

class Half(Format):
    """A class to handle half precision floats."""

    def __init__(self):
        super().__init__('e', 2)

class Float(Format):
    """A class to handle float format."""

    def __init__(self):
        super().__init__('f', 4)

class Double(Format):
    """A class to handle double precision floats format."""

    def __init__(self):
        super().__init__('d', 8)

class UInt8(Format):
    """A class to handle unsigned 8-bit integer format."""

    def __init__(self):
        super().__init__('B', 1)


class Int8(Format):
    """A class to handle signed 8-bit integer format."""

    def __init__(self):
        super().__init__('b', 1)


class Int16(Format):
    """A class to handle unsigned 16-bit integer format."""

    def __init__(self):
        super().__init__('h', 2)


class UInt16(Format):
    """A class to handle unsigned 16-bit integer format."""

    def __init__(self):
        super().__init__('H', 2)


class Int32(Format):
    """A class to handle signed 32-bit integer format."""

    def __init__(self):
        super().__init__('i', 4)


class UInt32(Format):
    """A class to handle unsigned 32-bit integer format."""

    def __init__(self):
        super().__init__('I', 4)


class Int64(Format):
    """A class to handle signed 64-bit integer format."""

    def __init__(self):
        super().__init__('q', 8)


class UInt64(Format):
    """A class to handle unsigned 64-bit integer format."""

    def __init__(self):
        super().__init__('Q', 8)


class BinaryStruct:

    def __init__(self, byte_order: ByteOrder, fields: list[Format]):
        self.byte_order: ByteOrder = byte_order
        self.fields = fields

        # Create struct format string in constructor
        self.struct_format = self.byte_order.value + ''.join([field.fmt for field in fields])

    def pack(self, *values: BinaryType) -> bytes:
        # Check the amount of values
        if len(values) != len(self.fields):
            raise ValueError(f"Expected {len(self.fields)} values, got {len(values)}")

        # Convert string values to bytes
        values = [v.encode('utf-8') if isinstance(v, str) else v for v in values]

        # Pack the values
        return struct.pack(self.struct_format, *values)

    def unpack(self, packed_data: bytes) -> list[BinaryType]:
        raw_result = struct.unpack(self.struct_format, packed_data)
        # Convert bytes back to string and strip null characters
        result = [r.decode('utf-8').rstrip('\0') if isinstance(r, bytes) else r for r in raw_result]

        return result


def as_ascii(bytes_obj, fill_char:str= '.'):
    hex_dump = " ".join(f"{b:02x}" for b in bytes_obj)
    ascii_chars = []
    for b in bytes_obj:
        if 32 <= b <= 126:  # printable ASCII range
            ascii_chars.append(chr(b))
        else:
            ascii_chars.append(fill_char)
    ascii_representation = ''.join(ascii_chars)
    return hex_dump, ascii_representation


def join_mixed_list(mixed_list):
    formatted_list = []
    for i in mixed_list:
        if type(i) is int:
            formatted_list.append('0x{:X}'.format(i))
        elif type(i) is str:
            formatted_list.append(i)
        elif type(i) is bytes:
            formatted_list.append(i.decode('utf-8'))
    result = ' '.join(formatted_list)
    return result


# Example Usage
if __name__ == "__main__":
    data = ['Hello', 'World', 255,-2, 0xdead, 0x12345678, 0x1234567887654321,0.2,1.2,2.2]
    print(join_mixed_list(data))
    for order in [ByteOrder.LITTLE_ENDIAN, ByteOrder.BIG_ENDIAN, ByteOrder.NATIVE_ORDER, ByteOrder.NETWORK_ORDER]:
        # Create a BinaryStruct with a 10-character string, 1-byte unsigned integer, and 16-bit unsigned integer
        bs = BinaryStruct(byte_order=order, fields=[String(10), String(10),
                                                    UInt8(),Int8(), UInt16(), UInt32(), UInt64(),
                                                    Half(),Float(),Double()])

        # Pack values
        packed = bs.pack(*data)
        # Unpack values
        unpacked = bs.unpack(packed)

        hex_dump, ascii_repr = as_ascii(packed)
        print(f'Order:{order:<24} HEX {hex_dump} ASCII "{ascii_repr} UNPACKED={unpacked}')

