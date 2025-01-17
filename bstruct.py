
import struct

class StructLib:

    def __init__(self,human_readable_format:str):
        self.format = self.human_readable_fmt(human_readable_format)

    def pack(self,*data)->bytes:
        return struct.pack(self.format,*data)

    def unpack(self,data:bytes)->list:
        return struct.unpack(self.format,data)

    def human_readable_fmt(self, format_string):
        struct_format_dict = {
            "bool": "?",
            "byte": "b",
            "int8":"b",
            "ubyte": "B",
            "uint8":"B",
            "int16":"h",
            "uint16":"H",
            "int32":"i",
            "uint32":"I",
            "int64": "q",
            "uint64": "Q",
            "float": "f",
            "double": "d",
            "char": "c",
            "s": "s",
            "string":"s",
            "p": "p",
            "pascal":"p",
            "P": "P",
            "pointer":"P",
            "padding": "x",
            "pad":'x',
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
