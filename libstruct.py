import binascii
import struct
import hexout

class LibStruct:

    def __init__(self, human_readable_format: str):
        self.format = self.decode_human_readable_fmt(human_readable_format)
        self.human_format = human_readable_format
        self.bytes = b''

    def __repr__(self):
        return f"LibStruct(human_readable_format: '{self.human_format} struct_format: {self.format}')"

    def to_ascii(self, unprintable_char='.'):
        """Sometimes looking at strings makes sense."""
        return ''.join(chr(byte_) if 32 <= byte_ < 127 else unprintable_char for byte_ in self.bytes)

    def to_hex(self, bytes_per_row: int = None, base_address: int = None, address_width: int = 8):
        """
        Converts the byte array into a formatted string of hexadecimal byte values.

        Args:
          bytes_per_row (int, optional): The number of bytes to include on each line.
            Defaults to the length of the byte array (i.e., the entire array on one line).
          base_address (int, optional): The base memory address for the byte array. If provided,
            each line will be preceded by the memory address of the first byte of that line,
            formatted as a hexadecimal number of width address_width. Defaults to None (no addresses displayed).
          address_width (int, optional): The number of hexadecimal digits to display for the memory address.
            Defaults to 8.

        Returns:
            str: A string representing the byte array in hexadecimal, optionally with memory addresses.
        """
        ho = hexout.HexOut(bytes_per_row=bytes_per_row,
                           base_address=base_address,
                           address_width=address_width)

        return ho.to_hex(self.bytes)

    def pack(self, *data) -> bytes:
        self.bytes = struct.pack(self.format, *data)
        return self.bytes

    def unpack(self, data: bytes) -> list:
        return struct.unpack(self.format, data)

    def decode_human_readable_fmt(self, format_string):
        struct_format_dict = {
            "bool": "?",
            "byte": "b",
            "int8": "b",
            "ubyte": "B",
            "uint8": "B",
            "int16": "h",
            "uint16": "H",
            "int32": "i",
            "uint32": "I",
            "int64": "q",
            "uint64": "Q",
            "float": "f",
            "double": "d",
            "char": "c",
            "s": "s",
            "string": "s",
            "str": "s",
            "p": "p",
            "pascal": "p",
            "P": "P",
            "pointer": "P",
            "padding": "x",
            "pad": 'x',
        }

        endianess_flag = {
            "little_endian": "<",
            "big_endian": ">",
            "network": "!",
            "native": "="
        }

        # Initialize result
        result = ""

        # Split string into parts
        parts = format_string.split()

        # Handle endianess
        if parts[0] in endianess_flag:
            result += endianess_flag[parts.pop(0)]

        # Handle types and repetition
        for part in parts:
            # If '*' exists, there is repetition
            if '*' in part:
                repeat, type_ = part.split('*')

                # Ignore if padding value is not a digit or padding itself
                if repeat.isdigit() or type_ == "padding":
                    struct_format = struct_format_dict[type_]

                    # If repetition is number
                    if repeat.isdigit():
                        repeat = int(repeat)
                        result += str(repeat) + struct_format
                    else:  # If padding itself
                        result += struct_format
            else:  # If no '*', type only
                struct_format = struct_format_dict.get(part, "")

                # If type exists in dict
                if struct_format:
                    result += struct_format

        return result


if __name__ == "__main__":
    sl = LibStruct(human_readable_format="big_endian 10*str int32 20*str")
    b = sl.pack(*[b"hello", 32, b"world"])
    print(sl.to_ascii())
    print(sl.to_hex(bytes_per_row=8, base_address=0x1000, address_width=4))
    print(sl.to_hex(bytes_per_row=4))
    print(sl)
