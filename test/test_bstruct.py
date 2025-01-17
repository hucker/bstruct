
import bstruct
import struct
import pytest

@pytest.mark.parametrize(
    "human_readable_format,expected_bstruct_format",
    [
        ("native 2*s p", "=2sp"),
        ("big_endian 3*int32 3*float", ">3i3f"),
        ("little_endian 2*bool 3*padding 30*s 2*uint32", "<2?3x30s2I"),
        ("native 2*int16 padding", "=2hx"),
        ("big_endian 2*byte", ">2b"),
        ("little_endian 2*ubyte", "<2B"),
        ("native int32", "=i"),
        ("big_endian 2*uint32", ">2I"),
        ("big_endian float", ">f"),
        ("little_endian double", "<d"),
        ("native int64", "=q"),
        ("big_endian uint64", ">Q"),
        ("little_endian char", "<c"),
        ("native 10*s", "=10s"),
        ("big_endian 3*padding", ">3x"),
        ("little_endian p", "<p"),
        ("native P", "=P"),
        ("big_endian bool byte", ">?b"),
        ("little_endian int16 int32", "<hi"),
        ("native int32 float", "=if"),
        ("big_endian double int64", ">dq"),
        ("little_endian s p", "<sp"),
        ("native P 3*padding", "=P3x"),
        ("big_endian uint64 4*s", ">Q4s"),
        ("little_endian 5*uint16 ubyte", "<5HB"),
        ("native double int16 padding", "=dhx"),
        ("big_endian 4*bool byte", ">4?b"),
        ("little_endian int32 int16", "<ih"),
        ("native uint32 uint16", "=IH"),
        ("big_endian 2*int64 2*uint64", ">2q2Q"),
        ("little_endian uint32 int32","<Ii"),
        ("native 3*float double", "=3fd"),
        ("big_endian 20*p 21*P", ">20p21P"),
        ("little_endian padding ubyte", "<xB"),
        ("native bool padding", "=?x"),
        ("big_endian byte int16", ">bh"),
        ("little_endian int16 padding", "<hx"),

        ("big_endian P 3*padding", ">P3x"),
    ])
def test_compile_format_string(human_readable_format, expected_bstruct_format):
    bs = bstruct.StructLib(human_readable_format)
    result = bs.format
    assert result == expected_bstruct_format


def test_round_trip():
    format_fields = "little_endian bool float double ubyte byte uint16 int16 uint32 int32 uint64 int64"
    expected_format = "<?fdBbHhIiQq"

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
    "format_fields, expected_format, data",
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
def test_round_trip(format_fields, expected_format, data):
    bs = bstruct.StructLib(format_fields)

    assert bs.format == expected_format

    # Use the bstruct class to pack and unpack the data fields
    packed_data = bs.pack(*data)
    unpacked_data = bs.unpack(packed_data)

    # Now use the baseline
    expected_packed = struct.pack(expected_format, *data)
    expected_unpacked_data = struct.unpack(expected_format, expected_packed)

    assert unpacked_data == expected_unpacked_data