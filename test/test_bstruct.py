"""
Test the thin wrapper around the struct module.  The intent of these tests is to make sure that
the thin wrapper around struct works as expected.  I'm not trying to test struct, I'm trying to make
sure that my code converts the single character binary data packet into a string that can be passed
the struct module.


For the most part these tests very that I can do all sorts of things with all the support types
and my mappings for those types.  Once that works I very that my code gets the same answer as struct
pack and unpack.  I am not trying to validate struct and assume that it just works.


"""

import libstruct
import struct
import pytest

@pytest.mark.parametrize('struct_byte_order, bstruct_byte_order',
                         [("<", "little_endian"), (">", "big_endian"), ("=", "native"), ("!", "network")])
@pytest.mark.parametrize(
    "bstruct_format_field, expected_bstruct_structure",
    [
        ("2*s p", "2sp"),
        ("3*int32 3*float", "3i3f"),
        ("2*bool 3*padding 30*s 2*uint32", "2?3x30s2I"),
        ("ubyte byte uint16 int16 uint32 int32 uint64 int64", "BbHhIiQq"),
        ("bool ubyte byte uint16 int16", "?BbHh"),
        ("2*byte", "2b"),
        ("2*ubyte", "2B"),
        ("int32", "i"),
        ("2*uint32", "2I"),
        ("float", "f"),
        ("double", "d"),
        ("int64", "q"),
        ("uint64", "Q"),
        ("char", "c"),
        ("10*s", "10s"),
        ("3*padding", "3x"),
        ("p", "p"),
        ("P", "P"),
        ("bool byte", "?b"),
        ("int16 int32", "hi"),
        ("int32 float", "if"),
        ("double int64", "dq"),
        ("s p", "sp"),
        ("P 3*padding", "P3x"),
        ("uint64 4*s", "Q4s"),
        ("5*uint16 ubyte", "5HB"),
        ("double int16 padding", "dhx"),
        ("4*bool byte", "4?b"),
        ("int32 int16", "ih"),
        ("uint32 uint16", "IH"),
        ("2*int64 2*uint64", "2q2Q"),
        ("uint32 int32", "Ii"),
        ("3*float double", "3fd"),
        ("20*p 21*P", "20p21P"),
        ("padding ubyte", "xB"),
        ("bool padding", "?x"),
        ("byte int16", "bh"),
        ("int16 padding", "hx"),
    ])
def test_compile_format_string(struct_byte_order, bstruct_byte_order,
                               bstruct_format_field, expected_bstruct_structure):
    """Test that the various datatypes get the correct format string for each byte ordering

    Args:
        struct_byte_order: The byte order symbol used in struct.
        bstruct_byte_order: The byte order name used in bstruct.
        bstruct_format_field: The format field used in bstruct.
        expected_bstruct_structure: The expected structure format in bstruct including byte order.
    """

    bstruct_format_with_order = f"{bstruct_byte_order} {bstruct_format_field}"
    expected_struct_format_full = f"{struct_byte_order}{expected_bstruct_structure}"
    bs = libstruct.LibStruct(bstruct_format_with_order)
    actual_struct_format_full = bs.format
    assert actual_struct_format_full == expected_struct_format_full

@pytest.mark.parametrize('struct_byte_order, bstruct_byte_order',
                         [("<", "little_endian"), (">", "big_endian"), ("=", "native"), ("!", "network")])
def test_round_trip2(struct_byte_order, bstruct_byte_order):
    """Test if data can make a round trip - packaged and unpackaged back and forth.

    Args:
        struct_byte_order: The byte order as used by struct.
        bstruct_byte_order: The byte order as used by bstruct.
    """

    bstruct_format = f"{bstruct_byte_order} bool float double ubyte byte uint16 int16 uint32 int32 uint64 int64"
    expected_struct_format = f"{struct_byte_order}?fdBbHhIiQq"

    # Initialize some useful data
    test_bool = 1
    test_float = 2.25
    test_double = 3.125
    test_ubyte = 255
    test_byte = -128
    test_uint16 = 65535
    test_int16 = -32768
    test_uint32 = 4294967295
    test_int32 = -2147483648
    test_uint64 = 18446744073709551615
    test_int64 = -9223372036854775808

    bs = libstruct.LibStruct(bstruct_format)

    assert bs.format == expected_struct_format

    data = [test_bool, test_float, test_double, test_ubyte, test_byte, test_uint16, test_int16, test_uint32,
            test_int32, test_uint64, test_int64]

    # Use the bstruct class to pack and unpack the data fields
    packed_data_by_bs = bs.pack(*data)
    unpacked_data_by_bs = bs.unpack(packed_data_by_bs)

    # Now use the baseline struct for packing and unpacking
    packed_data_by_struct = struct.pack(expected_struct_format, *data)
    unpacked_data_by_struct = struct.unpack(expected_struct_format, packed_data_by_struct)

    # The unpacked data by bstruct and struct should be the same
    assert unpacked_data_by_bs == unpacked_data_by_struct





@pytest.mark.parametrize(
    "bstruct_format, struct_format, test_data",
    [
        ("little_endian bool float double ubyte byte uint16 int16 uint32 int32 uint64 int64", "<?fdBbHhIiQq",
         [1, 2.25, 3.125, 255, -128, 65535, -32768, 4294967295, -2147483648, 18446744073709551615,
          -9223372036854775808]),
        ("ubyte byte uint16 int16 uint32 int32 uint64 int64", "BbHhIiQq",
         [255, -128, 65535, -32768, 4294967295, -2147483648, 18446744073709551615, -9223372036854775808]),
        ("float double", "fd", [2.25, 3.125]),
        ("bool ubyte byte uint16 int16", "?BbHh", [1, 255, -128, 65535, -32768]),
    ],
)
def test_round_trip(bstruct_format, struct_format, test_data):
    bs = libstruct.LibStruct(bstruct_format)

    assert bs.format == struct_format

    # Use the bstruct class to pack and unpack the data fields
    packed_data_by_bstruct = bs.pack(*test_data)
    unpacked_data_by_bstruct = bs.unpack(packed_data_by_bstruct)

    # Now use the baseline
    packed_data_by_struct = struct.pack(struct_format, *test_data)
    unpacked_data_by_struct = struct.unpack(struct_format, packed_data_by_struct)

    assert unpacked_data_by_bstruct == unpacked_data_by_struct


def test_strings():
    bstruct_format_with_order = "little_endian char 10*s"
    struct_format_with_order = "<c10s"
    test_data = [b'a', b'hello']

    bs = libstruct.LibStruct(bstruct_format_with_order)

    assert bs.format == struct_format_with_order

    # Use the bstruct class to pack and unpack the data fields
    packed_by_bstruct = bs.pack(*test_data)
    unpacked_by_bstruct = bs.unpack(packed_by_bstruct)

    # Now use the baseline struct for packing and unpacking
    packed_by_struct = struct.pack(struct_format_with_order, *test_data)
    unpacked_by_struct = struct.unpack(struct_format_with_order, packed_by_struct)

    # The unpacked data by bstruct and struct should be the same
    assert unpacked_by_bstruct == unpacked_by_struct



# This layer of parametrization is for byte orderings
@pytest.mark.parametrize('bstruct_byte_order, struct_byte_order', [
    ("little_endian", "<"),
    ("big_endian", ">"),
    ("native", "="),
    ("network", "!"),
])
@pytest.mark.parametrize('bstruct_format, struct_format, data', [
    ("char 5*s", "c5s", [b'a', b'hello']),
    ("char 7*s", "c7s", [b'a', b'abcd123']),
])
def test_strings2(bstruct_byte_order, struct_byte_order, bstruct_format, struct_format, data):
    bs = libstruct.LibStruct(bstruct_byte_order + " " + bstruct_format)

    assert bs.format == struct_byte_order + struct_format

    # Use the bstruct class to pack and unpack the data fields
    packed_data = bs.pack(*data)
    unpacked_data = bs.unpack(packed_data)

    # Now use the baseline
    expected_packed = struct.pack(struct_byte_order + struct_format, *data)
    expected_unpacked_data = struct.unpack(struct_byte_order + struct_format, expected_packed)

    assert unpacked_data == expected_unpacked_data

@pytest.mark.parametrize('bstruct_byte_order, struct_byte_order',
                         [("little_endian", "<"),
                          ("big_endian", ">"),
                          ("native", "="),
                          ("network", "!"),
                          ])
@pytest.mark.parametrize('bstruct_format, struct_format, data',
                         [("10*p", "10p", [b'hello']),
                          ("20*p 20*p", "20p20p", [b'abcd123', b'hello']),
                          ])
def test_pascal_strings(bstruct_byte_order, struct_byte_order, bstruct_format, struct_format, data):
    """Test for Pascal strings with various byte orders and formats.

    It seems that you've embarked on quite the unique journey! Testing Pascal strings
    in Python, are we? I'm convinced that even the creator of Python wouldn't have seen this
    one coming. It's as if you've opened a coding time capsule from the era of frizzy hair,
    disco music, and the Pascal peak! Keep going; you might be the sole torchbearer keeping
    the Pascal string legacy alive in the 21st century.

    Args:
        bstruct_byte_order: The byte order used in bstruct.
        struct_byte_order: The byte order used in struct.
        bstruct_format: The format used in bstruct.
        struct_format: The format expected to be used in struct.
        data: The data to be packed and unpacked.
    """

    bs = libstruct.LibStruct(bstruct_byte_order + " " + bstruct_format)

    assert bs.format == struct_byte_order + struct_format

    # Use the bstruct class to pack and unpack the data fields
    packed_data_by_bs = bs.pack(*data)
    unpacked_data_by_bs = bs.unpack(packed_data_by_bs)

    # Now use the struct library for comparison
    packed_data_by_struct = struct.pack(struct_byte_order + struct_format, *data)
    unpacked_data_by_struct = struct.unpack(struct_byte_order + struct_format, packed_data_by_struct)

    assert unpacked_data_by_bs == unpacked_data_by_struct

@pytest.mark.parametrize("fmt, data, columns, base_address, addr_fmt, expected", [
    ("5*s", [b'hello'], 5, 0, "0x{:02X} ", '0x00 68 65 6C 6C 6F'),
    # Add more scenarios here
    ("4*s", [b'some'], 4, 0x1234, "0x{:04X} ", '0x1234 73 6F 6D 65')
])
def test_bstruct_hexout(fmt, data, columns, base_address, addr_fmt, expected):
    bs = libstruct.LibStruct(fmt)
    bs.pack(*data)
    hex_str = bs.as_hex(columns=columns, base_address=base_address, addr_format=addr_fmt)
    assert hex_str == expected


@pytest.mark.parametrize("fmt, expected_str", [
    ("5*int32", "LibStruct(human_readable_format: '5*int32' struct_format: '5i')"),
    ("5*uint8", "LibStruct(human_readable_format: '5*uint8' struct_format: '5B')"),
    ("2*float", "LibStruct(human_readable_format: '2*float' struct_format: '2f')"),
    ("6*double", "LibStruct(human_readable_format: '6*double' struct_format: '6d')"),
    ("3*int16", "LibStruct(human_readable_format: '3*int16' struct_format: '3h')"),
])
def test_bstruct_repr(fmt, expected_str):
    bs = libstruct.LibStruct(fmt)
    assert str(bs) == expected_str

@pytest.mark.parametrize("struct_format, data, expected, fill", [
    ("10*s", b"hello", "hello.....",'.'),
    ("5*s", b"hi", "hi...",'.'),
    ("15*s", b"help me", "help me........",'.'),
    ("10*s", b"", "----------",'-'),
    ("15*s", b"hello world", "hello worldXXXX",'X'),
])
def test_ascii(struct_format, data, expected,fill):
    bs = libstruct.LibStruct(struct_format)
    bs.pack(data)
    ascii = bs.to_ascii(unprintable_char=fill)
    assert ascii == expected


def test_large_data_hex():
    data = range(256)
    bs = libstruct.LibStruct("256*uint8")
    packed_data = bs.pack(*data)
    unpacked_data = bs.unpack(packed_data)
    assert list(unpacked_data) == list(data)
    hex = bs.as_hex(columns=16,addr_format='0x{:02X} ')

    expected = """0x00 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x10 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F
0x20 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F
0x30 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F
0x40 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F
0x50 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F
0x60 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F
0x70 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F
0x80 80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F
0x90 90 91 92 93 94 95 96 97 98 99 9A 9B 9C 9D 9E 9F
0xA0 A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AF
0xB0 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF
0xC0 C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB CC CD CE CF
0xD0 D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB DC DD DE DF
0xE0 E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF
0xF0 F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF"""

    assert hex == expected

    hex = bs.as_hex(columns=16, base_address=0,addr_format='0x{:04X} ',show_ascii=True)
    expected = """0x0000 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F ................
0x0010 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F ................
0x0020 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F  !"#$%&'()*+,-./
0x0030 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 0123456789:;<=>?
0x0040 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F @ABCDEFGHIJKLMNO
0x0050 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F PQRSTUVWXYZ[\]^_
0x0060 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F `abcdefghijklmno
0x0070 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F pqrstuvwxyz{|}~.
0x0080 80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F ................
0x0090 90 91 92 93 94 95 96 97 98 99 9A 9B 9C 9D 9E 9F ................
0x00A0 A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AF ................
0x00B0 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF ................
0x00C0 C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB CC CD CE CF ................
0x00D0 D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB DC DD DE DF ................
0x00E0 E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF ................
0x00F0 F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF ................"""

    assert hex == expected

@pytest.mark.parametrize("struct_format, data, cols, bytes_per_column,hex_fmt, expected", [

    ("16*uint8", list(range(0, 16)), 8, 2, '{: 4X}',
     "   1  203  405  607  809  A0B  C0D  E0F"),

    ("16*uint8", list(range(0, 16)), 8, 2, '{:04X}',
     "0001 0203 0405 0607 0809 0A0B 0C0D 0E0F"),

    ("32*uint8", list(range(0, 32)), 32,1,'{:02X}',
     "00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F"),

    ("16*uint8", list(range(0, 16)), 16,1,'{:02X}',
     "00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F"),

])
def test_examples(struct_format, data, cols, bytes_per_column,hex_fmt, expected):
    bs = libstruct.LibStruct(struct_format)
    bs.pack(*data)
    hex_value = bs.as_hex(columns=cols, show_address=False, bytes_per_column=bytes_per_column, show_ascii=False,hex_format=hex_fmt)
    assert hex_value == expected