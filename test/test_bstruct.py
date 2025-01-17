import pytest
import struct
import bstruct


@pytest.mark.parametrize("instance, type", [
    (bstruct.Int8(), bstruct.Int8),
    (bstruct.UInt8(), bstruct.UInt8),
    (bstruct.Int16(), bstruct.Int16),
    (bstruct.UInt16(), bstruct.UInt16),
    (bstruct.Int32(), bstruct.Int32),
    (bstruct.UInt32(), bstruct.UInt32),
    (bstruct.Int64(), bstruct.Int64),
    (bstruct.UInt64(), bstruct.UInt64),
])
def test_int_types(instance, type):
    assert isinstance(instance, type)


def test_float_types():
    assert isinstance(bstruct.Float(), bstruct.Float)
    assert isinstance(bstruct.Double(), bstruct.Double)
    assert isinstance(bstruct.Half(),bstruct.Half)


def test_string_type():
    s = bstruct.String(10)
    assert isinstance(s,bstruct.String)
    assert s.size == 10

@pytest.mark.parametrize("size", [ 0,-1,-100])
def test_bad_string(size):
    # The smallest string should have a single null character so 0 or less is invalid
    with pytest.raises(ValueError):
        _ = bstruct.String(size)


@pytest.mark.parametrize("byte_order, expected", [
    (bstruct.ByteOrder.NATIVE_ORDER, '='),
    (bstruct.ByteOrder.LITTLE_ENDIAN, '<'),
    (bstruct.ByteOrder.BIG_ENDIAN, '>'),
    (bstruct.ByteOrder.NETWORK_ORDER, '!'),
])
def test_byteorder(byte_order, expected):
    assert byte_order.value == expected

@pytest.mark.parametrize("format_cls, expected_fmt, expected_size", [
    (bstruct.Char, 'c', 1),
    (bstruct.Bool_, '?', 1),
    (bstruct.Half, 'e', 2),
    (bstruct.Float, 'f', 4),
    (bstruct.Double, 'd', 8),
    (bstruct.Int8, 'b', 1),
    (bstruct.UInt8, 'B', 1),
    (bstruct.Int16, 'h', 2),
    (bstruct.UInt16, 'H', 2),
    (bstruct.Int32, 'i', 4),
    (bstruct.UInt32, 'I', 4),
    (bstruct.Int64, 'q', 8),
    (bstruct.UInt64, 'Q', 8),
])
def test_format_attributes(format_cls, expected_fmt, expected_size):
    instance = format_cls()
    assert instance.fmt == expected_fmt
    assert instance.size == expected_size


@pytest.mark.parametrize("byte_order,fields,expected_format", [
    (bstruct.ByteOrder.LITTLE_ENDIAN, [bstruct.String(10), bstruct.Char()], "<10sc"),
    (bstruct.ByteOrder.BIG_ENDIAN, [bstruct.String(10), bstruct.Bool_()], ">10s?"),
    (bstruct.ByteOrder.LITTLE_ENDIAN, [bstruct.Char(), bstruct.Half(), bstruct.Float()], "<cef"),
    (bstruct.ByteOrder.BIG_ENDIAN, [bstruct.Float(), bstruct.Char(), bstruct.Double()], ">fcd"),
    (bstruct.ByteOrder.LITTLE_ENDIAN, [bstruct.UInt8(), bstruct.UInt16(), bstruct.UInt32()], "<BHI"),
    (bstruct.ByteOrder.BIG_ENDIAN, [bstruct.Int8(), bstruct.Char(), bstruct.UInt16()], ">bcH"),

    # Tests for different types of byte ordering
    (bstruct.ByteOrder.NATIVE_ORDER, [bstruct.String(10)], "=10s"),
    (bstruct.ByteOrder.LITTLE_ENDIAN, [bstruct.String(10)], "<10s"),
    (bstruct.ByteOrder.BIG_ENDIAN, [bstruct.String(10)], ">10s"),
    (bstruct.ByteOrder.NETWORK_ORDER, [bstruct.String(10)], "!10s"),

    # Same thing with some number types
    (bstruct.ByteOrder.NATIVE_ORDER, [bstruct.UInt32()], "=I"),
    (bstruct.ByteOrder.LITTLE_ENDIAN, [bstruct.String(10)], "<10s"),
    (bstruct.ByteOrder.BIG_ENDIAN, [bstruct.String(10)], ">10s"),
    (bstruct.ByteOrder.NETWORK_ORDER, [bstruct.String(10)], "!10s"),

    # testing BinaryStruct with all data types
    (bstruct.ByteOrder.LITTLE_ENDIAN, [
        bstruct.String(10),
        bstruct.Char(),
        bstruct.Bool_(),
        bstruct.Half(),
        bstruct.Float(),
        bstruct.Double(),
        bstruct.UInt8(),
        bstruct.Int8(),
        bstruct.UInt16(),
        bstruct.Int16(),
        bstruct.UInt32(),
        bstruct.Int32(),
        bstruct.UInt64(),
        bstruct.Int64()
    ], "<10sc?efdBbHhIiQq")
])
def test_binary_struct(byte_order, fields, expected_format):
    bs = bstruct.BinaryStruct(byte_order=byte_order, fields=fields)
    assert bs.struct_format == expected_format



#Everything above this point tests that we can make a nice type string for the struct module

# Now we need to do a full "system test" to show that we are calling the underlying
# Struct module.  The idea is if our code makes the right format string, then  we should be good
# to go since this is a passthrough....

def test_integration_test_numerics():
    byte_order = bstruct.ByteOrder.LITTLE_ENDIAN
    field_types = [
        bstruct.Bool_(),
        bstruct.Half(),
        bstruct.Float(),
        bstruct.Double(),
        bstruct.UInt8(),
        bstruct.Int8(),
        bstruct.UInt16(),
        bstruct.Int16(),
        bstruct.UInt32(),
        bstruct.Int32(),
        bstruct.UInt64(),
        bstruct.Int64()
    ]
    expected_type = "<?efdBbHhIiQq"

    # Here initialize some usefuldata
    b = 1
    half = 1.5 # Note that we use binary fraction floating point numbers .5,.25, .125, .0625 etc
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
    bs = bstruct.BinaryStruct(byte_order,field_types)

    values = [b, half, f, d, u8, i8, u16, i16, u32, i32, u64, i64]

    # Use the bstruct class to pack and unpack the data fields
    packed_data = bs.pack(*values)
    unpacked_data = bs.unpack(packed_data)

    # Now use the baseline
    ex_packed = struct.pack(expected_type, *values)
    ex_unpacked_data = struct.unpack(expected_type,ex_packed)

    assert unpacked_data == ex_unpacked_data