from __future__ import annotations

from typing import Union, Any, Sequence, Dict, Tuple, List
from collections import Hashable


class Schema(tuple):
    """
    Represents the table headings. Can be used to instantiate a new table
    or row with these headings.
    """
    def build_row(self, values: Sequence[str]) -> Row:
        """
        Instantiates a new row with these headings. Cell values should
        be passed as a list
        """
        if len(values) != len(self):
            raise ValueError(f"Expected {len(self)} rows, got {len(values)}")
        return Row(**{item: values[i] for i, item in enumerate(self)})

    def new_table(self):
        """
        Instantiates a new table with these headings
        """
        return Table(self)


class Row(tuple):
    """
    Represents a table row, is immutable and implements the mapping
    interface to allow access to the cell values using the heading names
    as keys.
    """
    _default_separator = " : "
    _default_line_end = "\n"

    def __new__(cls, **kwargs) -> Row:
        _items = kwargs.items()
        row = super(Row, cls).__new__(cls, (value for (_, value) in _items))
        return row

    def __init__(self, **kwargs):
        items = kwargs.items()
        index_map, values = (
            {key: index for index, (key, _) in enumerate(items)},
            tuple(value for (_, value) in items),
        )
        self._index_map = index_map
        self._separator = self._default_separator

    def __getitem__(self, item: Union[str, int, slice]) -> Any:
        try:
            index = (int, slice, str).index(type(item))
        except ValueError:
            raise TypeError(f"A row cannot be indexed by values of type {type(item)}")

        try:
            return (
                lambda i: super(Row, self).__getitem__(i),
                lambda i: super(Row, self).__getitem__(i),
                lambda i: super(Row, self).__getitem__(self._index_map[i]),
            )[
                index
            ](item)
        except KeyError:
            raise KeyError(f"No column named {item} exists")
        except IndexError:
            raise IndexError(f"Row index {item} out of bounds, rows are indexed from {0} to {len(self)}")

    def get(self, column_key: Hashable, default=None) -> Any:
        """
        This method is implemented identically to
        >>> dict().get(key="...", _default=None)
        """
        if not isinstance(column_key, Hashable):
            raise TypeError(f"The key type supplied ({type(column_key)}) does not implement a __hash__ method")

        index = self._index_map.get(column_key)
        if index is not None:
            return self[index]
        else:
            return default

    @property
    def separator(self) -> str:
        return self._separator

    @separator.setter
    def separator(self, value: str) -> None:
        self._separator = value

    @property
    def schema(self) -> Schema:
        return Schema(self._index_map.keys())

    def items(self) -> Sequence[Tuple[str, str]]:
        """
        This method is implemented identically to
        >>> dict().items()
        """
        return [
            (heading, self[heading]) for heading in self._index_map.keys()
        ]

    def __str__(self) -> str:
        return str(self._separator).join([str(cell) for cell in self]) + "\n"


class Table(list):
    """
    Represents tabular data formatted as text
    """
    _schema: Schema
    _hlines: set

    def __new__(cls, headings: Sequence[str]) -> Table:
        table = super(Table, cls).__new__(cls)
        return table

    def __init__(self, headings: Sequence[str]):
        super(Table, self).__init__()
        self._schema = Schema(headings)
        self._hlines = set()
        self.append(Row(**{heading: heading for heading in headings}))

    def append(self, row: Union[Row, Sequence[str]]) -> Table:
        """
        Pass a row instance or Sequence[str] to append the row to
        the table body.
        """
        if not isinstance(row, Row):
            row = self.schema.build_row(row)
        if row.schema != self.schema:
            raise ValueError(f"The row provided had an incorrect schema, expected {self._schema}, got {row.schema}")
        super(Table, self).append(row)
        return self

    def add_row(self, *args) -> Table:
        """
        acts like append but expects a row of values as arguments i.e.
        >>> table.add_row('cell1', 'cell2', 'cell3')

        """
        self.append(self._schema.build_row(args))
        return self

    @property
    def schema(self) -> Schema:
        return self._schema

    def __str__(self) -> str:
        return self.format(headings=True)

    @property
    def columns(self) -> Dict[list]:
        return {
            heading: [row[heading] for row in self.body] for heading in self.schema
        }

    def format(self, headings: bool = True) -> str:
        """
        Returns a formatted string representation of the table.
        Set headings=True to include the headings in a row at the top.
        """
        col_widths = self._get_column_widths(headings)
        rows: Sequence[Row] = self.body
        lines = self._get_formatted_rows(col_widths, rows)
        lines = self._insert_hlines(lines)

        if headings:
            lines = self._prepend_headings(col_widths, lines)

        return "\n".join(lines) + "\n"

    def _get_column_widths(self, headings) -> Dict[str, int]:
        return {
            heading: max([len(str(cell)) for cell in column] + [len(heading)] * int(headings))
            for heading, column in self.columns.items()
        }

    def _prepend_headings(self, col_widths, lines: List[str]) -> List[str]:
        justified_cells = [str(cell).ljust(col_widths[heading]) for heading, cell in self[0].items()]
        lines = [self[0].separator.join(justified_cells)] + [*lines]
        return lines

    def _get_formatted_rows(self, col_widths: Dict[str, int], rows: Sequence[Row]) -> List[str]:
        lines = [
            row.separator.join(
                [
                    str(cell).ljust(col_widths[heading])
                    for heading, cell in row.items()
                ]
            )
            for row in rows
        ]
        return lines

    def _insert_hlines(self, lines: List[str]) -> List[str]:
        for row_index in self._hlines:
            if row_index == -1:
                lines[0] = "-" * len(lines[0]) + "\n" + lines[0]
            else:
                lines[row_index] += "\n" + "-" * len(lines[row_index])
        return lines

    @property
    def body(self) -> Sequence[Row]:
        return tuple(self[1:])

    def hline(self) -> None:
        """
        Inserts a horizontal divider after the last appended row.
        If called before any rows are appended, it will appear under
        the headings.
        """
        self._hlines.add(len(self.body) - 1)

