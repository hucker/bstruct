import struct

import hexout


class LibStruct:

    def __init__(self, human_readable_format: str):
        self.format = self.decode_human_readable_fmt(human_readable_format)
        self.human_format = human_readable_format
        self.bytes = b''

    def __repr__(self):
        return f"LibStruct(human_readable_format: '{self.human_format}' struct_format: '{self.format}')"

    def to_ascii(self, unprintable_char='.'):
        """Sometimes looking at strings makes sense."""
        return ''.join(chr(byte_) if 32 <= byte_ < 127 else unprintable_char for byte_ in self.bytes)

    def as_hex(self,
               columns: int = None,
               bytes_per_column=1,
               base_address: int = 0,
               addr_format: str = "{:02X} ",
               hex_format: str = "{:02X}",
               show_ascii: bool = False,
               show_address: bool = True):
        """
        Converts the byte array into a formatted string of hexadecimal byte values using the
        hexout package, using reasonable defaults for this application.

        Args:
          See hexout library for more information.

        Returns:
            str: A string representing the byte array in hexadecimal, optionally with memory addresses.
        """

        ho = hexout.HexOut(columns=columns,
                           bytes_per_column=bytes_per_column,
                           base_address=base_address,
                           addr_format=addr_format,
                           show_address=show_address,
                           hex_format=hex_format,
                           show_ascii=show_ascii)

        return ho.as_hex(self.bytes)

    def pack(self, *data) -> bytes:
        self.bytes = struct.pack(self.format, *data)
        return self.bytes

    def unpack(self, data: bytes) -> list:
        return struct.unpack(self.format, data)

    @staticmethod
    def decode_human_readable_fmt(format_string):
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

        endian_flag = {
            "little_endian": "<",
            "big_endian": ">",
            "network": "!",
            "native": "="
        }

        # Initialize result
        result = ""

        # Split string into parts
        parts = format_string.split()

        # Handle endian-ness
        if parts[0] in endian_flag:
            result += endian_flag[parts.pop(0)]

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
