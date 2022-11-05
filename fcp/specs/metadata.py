from serde import Model, fields


class MetaData(Model):
    line: fields.Int()
    end_line: fields.Int()
    column: fields.Int()
    end_column: fields.Int()
    start_pos: fields.Int()
    end_pos: fields.Int()
    filename: fields.Str()
