"""
Wrapper around the struct module to provide a better developer experience.

The speed of this code should be ever so slightly slower because

"""

import struct
from typing import Tuple
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
    def __init__(self, fmt: str, size: int = 1, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
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

    def __init__(self, size: int, fill=b'\x00'):
        """
        Args:
            size (int): Size of the string (in bytes).
        """
        if size <= 1:
            raise ValueError(f'Size for string ({size}) must be greater than 1.')
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
    """TODO: This hasn't been implemented and tested yet."""

    def __init__(self):
        import warnings
        warnings.warn('Pascal String Not Supported', DeprecationWarning, stacklevel=2)
        super().__init__('p', 2)

    def pack(self, value: str, truncate=False):
        # Ensure the string length is less than 255
        if truncate:
            value = value[:254]

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


class Bool_(Format):
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
        """
        Initialize class with the byte ordering and a list of Format field classes.

        The list of fields is used to make a format string usable by the underlying
        struct class fields that are created using a string with types encoded into
        single character type ID's.  While this worked back in the day, you would need
        to have the type characters memorized in order to be sure you were correct.

        With the binary struct, you  build the string from python Format objects.

        This is a more verbose, but has the benefit of enabling the IDE to verify types.
        """

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
        result = (r.decode('utf-8').rstrip('\0') if isinstance(r, bytes) else r for r in raw_result)

        return tuple(result)


def as_ascii(bytes_obj: bytes, fill_char: str = '.', hex_fmt: str = '{:02X}') -> Tuple[str, str]:
    """
    Convert a bytes object into a human-readable hex dump and ASCII
    representation.

    This function takes a bytes object as input and provides two different
    representations of the data. It returns a pair of strings. The first
    string is a hex dump, where each byte is represented as a two-character
    hexadecimal value in uppercase. The second string is an ASCII
    representation, where each byte corresponding to a printable ASCII
    character is converted to that character. Bytes outside the printable
    ASCII range are replaced with a specified fill character.

    Args:
        bytes_obj (bytes): The bytes object to be processed.
        fill_char (str):   The character to use for bytes outside the
                            printable ASCII range. Defaults to '.'.
        hex_fmt (str):     The format string for hex representation. Defaults
                            to '{:02X}' which is 2-digit uppercase hex
                            representation.

    Returns:
        Tuple[str, str]: A pair of strings representing the hex dump and
                         ASCII representation of the input bytes respectively.

    Example:
        >>> as_ascii(b'Hello World!', fill_char='.')
        ('48 65 6C 6C 6F 20 57 6F 72 6C 64 21', 'Hello World!')
    """
    hex_dump = " ".join(hex_fmt.format(b) for b in bytes_obj)
    ascii_chars = [chr(b) if 32 <= b <= 126 else fill_char for b in bytes_obj]
    ascii_representation = ''.join(ascii_chars)

    return hex_dump, ascii_representation


def join_mixed_list(mixed_list,
                    int_fmt: str = '0x{:X}',
                    float_fmt: str = '{:.2f}',
                    str_fmt: str = '{}',
                    bytes_fmt: str = '{}',
                    separator: str = ' ',
                    formats: dict = None):
    """
    Take the list of unpacked values and create a string representation of the data.

    Reasonable defaults are provided for each type.  At
    """

    # User can optionally provide the types format dictionary.
    formats = formats or {
        int: int_fmt,
        float: float_fmt,
        str: str_fmt,
        bytes: lambda b: bytes_fmt.format(b.decode('utf-8')),
    }

    formatted_list = [
        formats.get(type(i), str_fmt).format(i) if type(i) != bytes else formats[type(i)](i)
        for i in mixed_list
    ]

    return separator.join(formatted_list)


def debug_function():
    data = ['Hello', 'World', 255, -2, 0xdead, 0x12345678, 0x1234567887654321, 0.2, 1.2, 2.2]
    print(join_mixed_list(data))
    for order in [ByteOrder.LITTLE_ENDIAN, ByteOrder.BIG_ENDIAN, ByteOrder.NATIVE_ORDER, ByteOrder.NETWORK_ORDER]:
        # Create a BinaryStruct with a 10-character string, 1-byte unsigned integer, and 16-bit unsigned integer
        bs = BinaryStruct(byte_order=order, fields=[String(10), String(10),
                                                    UInt8(), Int8(), UInt16(), UInt32(), UInt64(),
                                                    Half(), Float(), Double()])

        # Pack values
        packed = bs.pack(*data)
        # Unpack values
        unpacked = bs.unpack(packed)

        hex_dump, ascii_repr = as_ascii(packed)
        print(f'Order:{order:<24} HEX {hex_dump} ASCII "{ascii_repr} UNPACKED={unpacked}')


debug_function()
