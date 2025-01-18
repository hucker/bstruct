# StructLib

`StructLib` is a Python class that offers a more human-friendly interface to the `struct` module,
allowing packing and unpacking of C-like struct data.

## Features

Packs and unpacks bytes by mapping human-readable format strings to equivalent `struct` format symbols.
Provides format symbols for a variety of data types, including integer types, floating-point types,
characters, strings, Pascal strings and padding.
Supports specification of endianness in format strings using terms like `little_endian` and `big_endian`.

## Basic Usage

```python 
from structlib import StructLib

# Initialize with a format string
sl = StructLib("bool int32 str")
# Pack data into bytes
packed_data = sl.pack(True, 123, b"Hello")
# Unpack bytes into data
unpacked_data = sl.unpack(packed_data) 
```

## Format Strings

The format strings used to initialize `StructLib` are made up of space-separated parts.
Each part represents a type to be packed/unpacked.
Supported types include:
Integer types: `int8`, `uint8`, `int16`, `uint16`, `int32`, `uint32`, `int64`, `uint64`
Floating point types: `float`, `double`
Byte and character: `byte`, `ubyte`, `char`
Strings: `str`, `string`
Pascal strings: `p`, `pascal`
Padding: `pad`, `padding`
To repeat a type, use '' operator followed by number, e.g. `10int32`.
Endianness can be specified at the beginning of the format string. Supported options are `little_endian`, `
big_endian`, `network`, and `native`.

## Support for hex output.

Since we often need to look at binary data a way to print data in hex is provided with the to_hex method:

If you just call to_hex on the object you just get all of the bytes in 2 digit uper case, in a long string.  
Thankfull, to_hex allows for alot of functionality. You can specify bytes per row, a base address and the 
width of address data.  This is very useful for larger data objects.
```
bs.to_hex(bytes_per_row:int=8, base_address:int=0x1000, address_width:int=8)
```

```text
1000: 68 65 6C 6C 6F 00 00 00
1008: 00 00 00 00 00 20 77 6F
1010: 72 6C 64 00 00 00 00 00
1018: 00 00 00 00 00 00 00 00
```

## Note

This class raises exceptions consistent with Python's `struct` module. So, when you are using `StructLib`,
you might need to handle the same exceptions that you would when using `struct`.
Keep in mind that "str"/"string" type in `StructLib` corresponds to `struct`'s 's' format
(fixed-size string), and "p"/"pascal" corresponds to `struct`'s 'p' format (Pascal string). For the
difference between 's' and 'p' in `struct`, you might need to refer to Python's `struct` module documentation.
Please note that this class provides a simple and limited interface to Python's `struct` module. For complex
struct packing/unpacking needs, it is recommended to directly use the `struct` module.