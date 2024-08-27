from serde import Model, fields


class MetaData(Model):
    line: fields.Int()
    end_line: fields.Int()
    column: fields.Int()
    end_column: fields.Int()
    start_pos: fields.Int()
    end_pos: fields.Int()
    filename: fields.Str()


test = MetaData(
    line=1, end_line=2, column=3, end_column=4, start_pos=5, end_pos=6, filename="test"
)
print(test.to_json())
