from unittest import TestCase

from table.table import Row


class RowTest(TestCase):
    row_dict = {
        "column_1": "value_1",
        "column_2": "value_2",
        "column_3": "value_3",
    }

    def test_row_constructor(self):
        row = Row(**self.row_dict)

        assert all(row[key] == self.row_dict[key] for key in self.row_dict.keys())
        assert all(row[index] == self.row_dict[key] for index, key in enumerate(self.row_dict.keys()))
        assert row == tuple(self.row_dict.values())

    def test_get(self):
        row = Row(**self.row_dict)

        assert all(row.get(key) for key in self.row_dict.keys())
        assert row.get("non_existant_key") is None
        assert row.get("non_existant_key", "some_default") == "some_default"

    def test_slice_access(self):
        row = Row(**self.row_dict)

        assert row[1:3] == tuple(self.row_dict.values())[1:3]

    def test_str_cast(self):
        row = Row(**self.row_dict)

        assert str(row) == row.separator.join(self.row_dict.values()) + "\n"

