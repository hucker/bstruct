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

