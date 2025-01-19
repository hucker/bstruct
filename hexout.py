from typing import Generator

class HexOut:
    def __init__(self, bytes_per_column: int = 1, columns: int = 0, base_address:int=0, col_separator: str = " ",
                 line_separator: str = "\n",
                 hex_format: str = "{:02X}",
                 addr_format:str = "{:04X}: ",
                 show_address:bool = False):
        self.bytes_per_column = bytes_per_column
        self.columns = columns
        self.base_address = base_address
        self.addr_format = addr_format or '{:04X}: '  # This fixes a test case
        self.show_address = show_address
        self.column_separator = col_separator
        self.line_separator = line_separator
        self.hex_format = hex_format or "{:02X}"

    def _yield_bytes_as_ints(self, byte_data: bytes) -> Generator[int, None, None]:
        """Collect up the bytes into integers and stream those."""
        for i in range(0, len(byte_data), self.bytes_per_column):
            bytes_in_chunk = byte_data[i:i + self.bytes_per_column]
            yield int.from_bytes(bytes_in_chunk, 'big')

    def _yield_ints_as_list(self, integer_data: Generator[int, None, None]) -> Generator[list[int], None, None]:
        """ Collect the ints up in to a list of integers used on a single line. """
        line = []
        for i, data in enumerate(integer_data, 1):
            line.append(data)
            if self.columns > 0 and i % self.columns == 0:
                yield line
                line = []
        if line:  # handle the last column
            yield line

    def _yield_lines_as_string(self, lines: Generator[list[int], None, None]) -> Generator[str, None, None]:
        """Make the string given the list of integers."""
        for i, line in enumerate(lines, 1):
            formatted_hex_line = self.column_separator.join(self.hex_format.format(num) for num in line)
            if self.show_address:
                address = self.addr_format.format(((i - 1) * self.bytes_per_column * self.columns) + self.base_address)
            else:
                address = ''
            yield address + formatted_hex_line

    def generate_hex(self, byte_data: bytes) -> Generator[str, None, None]:
        """Generator that yields line-by-line hexadecimal representing the byte data."""
        stage1 = self._yield_bytes_as_ints(byte_data)
        stage2 = self._yield_ints_as_list(stage1)
        return self._yield_lines_as_string(stage2)

    def as_hex(self, byte_data: bytes,line_separator=None) -> str:
        """Return the full hex string, which is just making a list out of the hex generator."""
        line_separator = line_separator or self.line_separator
        return line_separator.join(self.generate_hex(byte_data))

