from __future__ import annotations

from typing import Union, Any, Sequence
from collections import Hashable


class Schema(tuple):
    def build_row(self, values: Sequence[str]) -> Row:
        if len(values) != len(self):
            raise ValueError(f"Expected {len(self)} rows, got {len(values)}")
        return Row(**{item: values[i] for i, item in enumerate(self)})

    def new_table(self):
        return Table(self)


class Row(tuple):
    _default_separator = " : "

    def __new__(cls, **kwargs) -> Row:
        items = kwargs.items()
        row = super(Row, cls).__new__(cls, (value for (_, value) in items))
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

    def __str__(self) -> str:
        return str(self._separator).join(self) + "\n"


class Table(list):
    _schema: Schema

    def __new__(cls, headings: Sequence[str]) -> Table:
        table = super(Table, cls).__new__(cls)
        return table

    def __init__(self, headings: Sequence[str]):
        super(Table, self).__init__()
        self._schema = Schema(headings)
        self.append(Row(**{heading: heading for heading in headings}))

    def append(self, row: Union[Row, Sequence[str]]) -> Table:
        if not isinstance(row, Row):
            row = self.schema.build_row(row)
        if row.schema != self.schema:
            raise ValueError(f"The row provided had an incorrect schema, expected {self._schema}, got {row.schema}")
        super(Table, self).append(row)
        return self

    def add_row_values(self, *args) -> Table:
        self.append(self._schema.build_row(*args))
        return self

    @property
    def schema(self) -> Schema:
        return self._schema

    def __str__(self) -> str:
        return "".join(self)

    @property
    def body(self) -> Sequence[Row]:
        return tuple(self[1:])
