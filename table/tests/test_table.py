from unittest import TestCase

from table.table import Row, Schema, Table


class RowTest(TestCase):
    row_dict = {
        "column_1": "value_1",
        "column_2": "value_2",
        "column_3": "value_3",
    }

    def test_row_constructor(self):
        row = Row(**self.row_dict)

        assert isinstance(row, Row)
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

    def test_schema_getter(self):
        row = Row(**self.row_dict)

        assert row.schema == Schema(self.row_dict.keys())


class SchemaTest(TestCase):
    row_headings = [f"column_{i}" for i in range(1, 4)]
    row_values = [f"value_{i}" for i in range(1, 4)]

    def test_schema_constructor(self):
        schema = Schema(self.row_headings)

        assert isinstance(schema, Schema)
        assert schema == tuple(self.row_headings)

    def test_build_row(self):
        schema = Schema(self.row_headings)

        expected_row = Row(**{self.row_headings[i]: value for i, value in enumerate(self.row_values)})
        assert schema.build_row(self.row_values) == expected_row

    def test_new_table(self):
        schema = Schema(self.row_headings)
        table = schema.new_table()

        assert len(table) == 1
        assert table[0] == schema


class TableTest(TestCase):
    row_headings = [f"column_{i}" for i in range(4)]
    rows = [
        tuple(f"value_{i}_{j}" for i in range(4)) for j in range(10)
    ]

    def test_table_constructor(self):
        table = Table(self.row_headings)

        assert len(table) == 1
        assert table[0] == Schema(self.row_headings)

    def test_append(self):
        table = Table(self.row_headings).append(self.rows[0])

        assert len(table) == 2
        assert table[1] == self.rows[0]
        assert table.body[0] == self.rows[0]

    def test_indexing(self):
        table = Table(self.row_headings)
        for row in self.rows:
            table.append(row)

        assert len(table) == len(self.rows) + 1
        for j, row in enumerate(table.body):
            for i, cell in enumerate(row):
                assert cell == f"value_{i}_{j}", f"{cell}, i={i}, j={j}"

        for j in range(len(table.body)):
            for i in range(len(table.body[j])):
                cell = table.body[j][table.schema[i]]
                assert cell == f"value_{i}_{j}", f"{cell}, i={i}, j={j}"
