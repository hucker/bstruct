# LibStruct

`LibStruct` is a Python class that offers a more human-friendly interface to the `struct` module,
allowing packing and unpacking of C-like struct data.  `LibStruct` is a thin wrapper on top of
the `struct` module.  This module provides for human readable packet definitions using intuitive
strings rather than single character types that allow:

`little_endian ubyte byte uint16 int16 uint32 int32 uint64 int64`

instead of

`<BbHhIiQq`

Some useful binary viewing tools are also provided.

## Features

Packs and unpacks bytes by mapping human-readable format strings to equivalent `struct` format symbols.
Provides format symbols for a variety of data types, including integer types, floating-point types,
characters, strings, Pascal strings and padding.
Supports specification of endianness in format strings using terms like `little_endian` and `big_endian`.

## Basic Usage

```python 
from libstruct import LibStruct

# Initialize with a format string
sl = LibStruct("bool int32 str")
# Pack data into bytes
packed_data = sl.pack(True, 123, b"Hello")
# Unpack bytes into data
unpacked_data = sl.unpack(packed_data) 
```

## Format Strings

The format strings used to initialize `LibStruct` are made up of space-separated parts.
Each part represents a type to be packed/unpacked.
Supported types include:

| Description            | Available Types                                   |
| ---------------------- | ------------------------------------------------- |
| Integer Types          | `int8`, `uint8`, `int16`, `uint16`, `int32`, `uint32`, `int64`, `uint64` |
| Floating Point Types   | `float`, `double`                                 |
| Byte and Character     | `byte`, `ubyte`, `char`                           |
| Strings                | `str`, `string`                                   |
| Pascal Strings         | `p`, `pascal`                                     |
| Padding                | `pad`, `padding`                                  |
| Endianness             | `little_endian`, `big_endian`, `network`, `native`|



To repeat a type, use `*` operator followed by number, e.g. `10*int32` to specify that you want to
handle 10 integers.

Endianness can be specified at the beginning of the format string. Supported options are `little_endian`, `
big_endian`, `network`, and `native`.

## Support for hex output.

Since we often need to look at binary data a way to print data in hex I've provided a simple
library that converts binary data "packets" into a formatted hex output.  When displaying data as
bytes you can optionally show the data as text in a 'standard' hex dump.


### Examples:

These examples show the viewing some of the data in various forms of hex dumps.  The parameters
of `.as_hex` are passed directly through to the `hexout` package.

```text
>>> data = range(256)
>>> bs = libstruct.LibStruct("256*uint8")
>>> packed_data = bs.pack(*data)
>>> hex = bs.as_hex(columns=16,addr_format='0x{:04X} ',show_ascii=True)

print(hex)
0x0000 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F ................
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
0x00F0 F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF ................
```
or a list of 8bit hex values
```text
>>> data = range(256)
>>> bs = libstruct.LibStruct("256*uint8")
>>> packed_data = bs.pack(*data)
>>> hex = bs.as_hex(bytes_per_column=1, columns=16)
00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F
20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F
30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F
40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F
50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F
60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F
70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F
80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F
90 91 92 93 94 95 96 97 98 99 9A 9B 9C 9D 9E 9F
A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AF
B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF
C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB CC CD CE CF
D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB DC DD DE DF
E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF
F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF
```
or

```text
>>>bdata = list(range(0,16))
>>> bs = libstruct.LibStruct("16*uint8")
>>> packed_data = bs.pack(*data)
>>> hex = bs.as_hex(bytes_per_column=4, columns=4)
>>> print(hex)
00010203 04050607 08090A0B 0C0D0E0F
10111213 14151617 18191A1B 1C1D1E1F
```


## Note

If data is provided that is out of range for bytes (0-255) a `ValueError` exception is thrown.

This class raises exceptions consistent with Python's `struct` module. So, when you are using `LibStruct`,
you might need to handle the same exceptions that you would when using `struct`.
Keep in mind that `str`/`string` type in `LibStruct` corresponds to the `struct` `s` format
(fixed-size string), and `p`/`pascal` corresponds to the `struct` `p` format (Pascal string). For the
difference between `s` and `p` in `struct`, you might need to refer to Python's `struct` module documentation.
Please note that this class provides a simple and limited interface to Python's `struct` module. For complex
struct packing/unpacking needs, it is recommended to directly use the `struct` module.



