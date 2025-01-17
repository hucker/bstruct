
import bstruct
import struct
import pytest

@pytest.mark.parametrize(
    "format_field_structure, expected_bstruct_structure",
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
def test_compile_format_string(format_field_structure, expected_bstruct_structure):
    """Test that the various datatypes get the right format string for each byte ordering"""
    byte_orders = {"<":"little_endian", ">":"big_endian","=":"native","!":"network"}

    for symbol,order in byte_orders.items():
        human_readable_format = f"{order} {format_field_structure}"
        expected_bstruct_format = f"{symbol}{expected_bstruct_structure}"
        bs = bstruct.StructLib(human_readable_format)
        bs_format = bs.format
        assert bs_format == expected_bstruct_format

@pytest.mark.parametrize('symbol, order',
                         [("<", "little_endian"), (">", "big_endian"), ("=", "native"), ("!", "network")])
def test_round_trip2(symbol, order):

    format_fields = f"{order} bool float double ubyte byte uint16 int16 uint32 int32 uint64 int64"
    expected_format = f"{symbol}?fdBbHhIiQq"

    # Initialize some useful data
    b = 1
    f = 2.25
    d = 3.125
    u8 = 255
    i8 = -128
    u16 = 65535
    i16 = -32768
    u32 = 4294967295
    i32 = -2147483648
    u64 = 18446744073709551615
    i64 = -9223372036854775808
    bs = bstruct.StructLib(format_fields)

    assert bs.format == expected_format

    data = [b, f, d, u8, i8, u16,i16,u32,i32, u64, i64]

    # Use the bstruct class to pack and unpack the data fields
    packed_data = bs.pack(*data)
    unpacked_data = bs.unpack(packed_data)

    # Now use the baseline
    expected_packed = struct.pack(expected_format, *data)
    expected_unpacked_data = struct.unpack(expected_format, expected_packed)

    assert unpacked_data == expected_unpacked_data





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
    bs = bstruct.StructLib(bstruct_format)

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

    bs = bstruct.StructLib(bstruct_format_with_order)

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
    bs = bstruct.StructLib(bstruct_byte_order + " " + bstruct_format)

    assert bs.format == struct_byte_order + struct_format

    # Use the bstruct class to pack and unpack the data fields
    packed_data = bs.pack(*data)
    unpacked_data = bs.unpack(packed_data)

    # Now use the baseline
    expected_packed = struct.pack(struct_byte_order + struct_format, *data)
    expected_unpacked_data = struct.unpack(struct_byte_order + struct_format, expected_packed)

    assert unpacked_data == expected_unpacked_data