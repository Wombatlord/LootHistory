from __future__ import annotations

from typing import Union, Any, Iterable
from collections import Hashable


class Stringy(str):
    def __str__(self) -> str:
        pass


def _quacks_like_a(obj: Any, duck: type) -> bool:
    """

    """
    impl_dunder = {*obj.__class__.__dict__.keys()} & {*duck.__dict__.keys()} == {*duck.__dict__.keys()}
    return impl_dunder or isinstance(obj, duck)


class Schema(tuple):
    def __new__(cls, *args):
        if not all(_quacks_like_a(item, Stringy) for item in args):
            raise ValueError("Headings must be string like!")
        return super(Schema, cls).__new__(cls, *args)

    def build_row(self, *values) -> Row:
        if len(values) != len(self):
            raise ValueError(f"Expected {len(self)} rows, got {len(values)}")
        return Row.__new__(**{item: values[i] for i, item in enumerate(self)})


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
        if not _quacks_like_a(column_key, Hashable):
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
        if not _quacks_like_a(value, Stringy):
            raise TypeError(f"The separator must be str or implement __str__, {type(value)} does not satisfy this.")
        self._separator = value

    @property
    def schema(self) -> Schema:
        return Schema(self._index_map.keys())

    def __str__(self) -> str:
        return str(self._separator).join(self) + "\n"


class Table(list):
    _schema: Schema

    def __new__(cls, headings: Iterable[str]) -> Table:
        table = super(Table, cls).__new__(cls)
        cls.__init__(table, headings)
        return table

    def __init__(self, schema: Iterable[str]):
        super(Table, self).__init__()
        self._schema = Schema(schema)
        self.append(Row(**{heading: heading for heading in schema}))

    def append(self, row: Row) -> Table:
        if row.schema != self._schema:
            raise ValueError(f"The row provided had an incorrect schema, expected {self._schema}, got {row.schema}")
        super(Table, self).append(row)
        return self

    def add_row_values(self, *args) -> Table:
        self.append(self._schema.build_row(*args))
        return self

    def __str__(self) -> str:
        return "".join(self)
