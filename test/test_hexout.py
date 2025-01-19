import pytest
import math
from hexout import HexOut

@pytest.fixture
def byte_data():
    return b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16'

@pytest.fixture
def short_byte_data():
    return b'\x00\x01\x02\x03\x04\x05\x06\x07'



@pytest.mark.parametrize("byte_data,expected", [
    (b'\x00\x01\x02\x03', "00 01 02 03"),
    (b'\x0F\xAF\xB0\x1F\x2F', "0F AF B0 1F 2F"),
    (b'\xFF', "FF"),
    (b'\x00\x00\x00\x00\x00\x01', "00 00 00 00 00 01"),
    (b'\x00\x10\x20\x30\x40\x50\x60\x70\x80\x90\xA0\xB0\xC0\xD0\xE0\xF0',
     "00 10 20 30 40 50 60 70 80 90 A0 B0 C0 D0 E0 F0")
])
def test_hexout_single_line(byte_data, expected):
    # Initialize HexOut with columns=0
    ho = HexOut()

    # Call and test
    assert ho.as_hex(byte_data) == expected

@pytest.mark.parametrize("byte_data, columns, expected", [
    (b'\x00\x01\x02\x03\x04', 4, "00 01 02 03\n04"),
    (b'\x00\x01\x02\x03\x04\x05', 4, "00 01 02 03\n04 05"),
    (b'\x00\x01\x02\x03\x04\x05\x06', 4, "00 01 02 03\n04 05 06"),
    (b'\x00\x01\x02\x03\x04\x05\x06\x07', 4, "00 01 02 03\n04 05 06 07")
])
def test_hexout_multi_line(byte_data, columns, expected):
    ho = HexOut(columns=columns)
    assert ho.as_hex(byte_data) == expected


@pytest.mark.parametrize("byte_data, hex_format, expected", [
    (b'\x01\x02\x03\x04', "{}", "1 2 3 4"),  # Without leading zeros
    (b'\xA1\xB2\xC3\xD4', "{:04X}", "00A1 00B2 00C3 00D4"),  # With leading zeros and fixed width
    (b'\xA1\xB2\xC3\xD4', "{:04x}", "00a1 00b2 00c3 00d4"),  # With leading zeros and fixed width
    (b'\x01\xFF', "{:#04x}", "0x01 0xff"),  # With '0x' prefix and lowercase
    (b'\x0A\x0B\x0C\x0D', "{:#06X}", "0X000A 0X000B 0X000C 0X000D"),  # With '0X' prefix, leading zeros and fixed width
])
def test_hexout_different_formats(byte_data, hex_format, expected):
    # Initialize HexOut with hex_format
    ho = HexOut(hex_format=hex_format)

    # Call and test
    value = ho.as_hex(byte_data)
    assert value == expected

@pytest.mark.parametrize("byte_data, columns, addr_fmt, expected", [
    (b'\x00\x01\x02\x03\x04', 1, "{:02X}: ", "00: 00\n01: 01\n02: 02\n03: 03\n04: 04"),
    (b'\x00\x01\x02\x03\x04', 2,  "{:04X}: ","0000: 00 01\n0002: 02 03\n0004: 04"),
    (b'\x00\x01\x02\x03\x04', 4,  "{:06X}: ", "000000: 00 01 02 03\n000004: 04"),
    (b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F', 8, "{:08X}: ",
     "00000000: 00 01 02 03 04 05 06 07\n00000008: 08 09 0A 0B 0C 0D 0E 0F")
])
def test_hexout_multi_line_address_width(byte_data, columns, addr_fmt, expected):
    ho = HexOut(columns=columns, addr_format= addr_fmt,show_address=True)
    value = ho.as_hex(byte_data)
    assert value == expected

@pytest.mark.parametrize("byte_data, base_address, columns, addr_fmt, expected", [
    (b'\x00\x01\x02\x03\x04', 0x10, 1, "{:02X}: ", "10: 00\n11: 01\n12: 02\n13: 03\n14: 04"),
    (b'\x00\x01\x02\x03\x04', 0x20, 2, "{:04X}: ", "0020: 00 01\n0022: 02 03\n0024: 04"),
    (b'\x00\x01\x02\x03\x04', 0x30, 4, "{:06X}: ", "000030: 00 01 02 03\n000034: 04"),
    (b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F', 0x40, 8, "{:08X}: ",
     "00000040: 00 01 02 03 04 05 06 07\n00000048: 08 09 0A 0B 0C 0D 0E 0F")
])
def test_hexout_multi_line_base_address(byte_data, base_address, columns, addr_fmt, expected):
    ho = HexOut(columns=columns, show_address=True, addr_format=addr_fmt, base_address=base_address)
    value = ho.as_hex(byte_data)
    assert value == expected

@pytest.mark.parametrize('col_separator,base_address,addr_format,expected_output', [
    (' ', 0, '', '0000: 00 01\n0002: 02 03'),  # default to 4 digit address
    (' ', 0x100, '0x{:04x}: ', '0x0100: 00 01\n0x0102: 02 03'),
    ('\t', 0, '{:04x}: ', '0000: 00\t01\n0002: 02\t03'),
    (' ', 0x100, '{:04x}: ', '0100: 00 01\n0102: 02 03'),
    (' | ', 0x200, '{:04x}: ', '0200: 00 | 01\n0202: 02 | 03'),

])
def test_base_address_and_separator(col_separator, base_address, addr_format, expected_output):
    data = b'\x00\x01\x02\x03'
    ho = HexOut(columns=2, show_address=True,addr_format = addr_format, base_address=base_address,col_separator=col_separator)

    value = ho.as_hex(data)
    assert value == expected_output

def test_hexout_smoke():
    byte_data = bytes([i % 256 for i in range(127)])  # reduce data size
    columns = 8
    bytes_per_column = 2
    addr_format = "{:06X}: "
    ho = HexOut(columns=columns,
                    addr_format=addr_format,
                    hex_format = "{:04X}",
                    show_address=True,
                    col_separator=' - ',
                    line_separator='\n\n',
                    bytes_per_column=bytes_per_column)
    result = ho.as_hex(byte_data)

    hex_representation = lambda b: f"{int.from_bytes(b, 'big'):04X}"
    represent_bytes_as_hex = lambda s: ' - '.join(
        hex_representation(byte_data[i:i + bytes_per_column]) for i in
        range(s, min(s + bytes_per_column * columns, len(byte_data)), bytes_per_column)
    )

    expected_output = '\n\n'.join(
        addr_format.format(i * bytes_per_column * columns) + represent_bytes_as_hex(i * bytes_per_column * columns)
        for i in range(0, math.ceil(len(byte_data) / (bytes_per_column * columns)))
    )
    assert result == expected_output.strip()

@pytest.mark.parametrize("byte_data, bytes_per_column, hex_format, expected", [
    (b"\x00\x01\x02\x04", 2, "0b{:016b}", "0b0000000000000001 0b0000001000000100"),
    (b"\x0F\xAF\x3C\x2F", 2, "0b{:016b}", "0b0000111110101111 0b0011110000101111"),
    (b"\xFE\xFF\x00\x01", 2, "0b{:016b}", "0b1111111011111111 0b0000000000000001"),
    (b"\xAA\xBB\xCC\xDD", 1, "0b{:08b}", "0b10101010 0b10111011 0b11001100 0b11011101"),
])
def test_binary_output(byte_data, bytes_per_column, hex_format, expected):
    ho = HexOut(bytes_per_column=bytes_per_column, hex_format=hex_format)
    value = ho.as_hex(byte_data)
    assert value == expected


@pytest.mark.parametrize("byte_data, bytes_per_column, hex_format, expected", [
    (b"\x00\x01\x02\x04", 2, "0b{:016b}", "0000: 0b0000000000000001 0b0000001000000100"),
    (b"\x0F\xAF\x3C\x2F", 2, "0b{:016b}", "0000: 0b0000111110101111 0b0011110000101111"),
    (b"\xFF\xFF\x00\x00", 2, "0b{:016b}", "0000: 0b1111111111111111 0b0000000000000000"),
    (b"\xAA\xBB\xCC\xDD", 1, "0b{:08b}", "0000: 0b10101010 0b10111011 0b11001100 0b11011101"),
])
def test_binary_output_with_address(byte_data, bytes_per_column, hex_format, expected):
    ho = HexOut(bytes_per_column=bytes_per_column, hex_format=hex_format, show_address=True, addr_format="{:04X}: ")
    value = ho.as_hex(byte_data)
    assert value == expected