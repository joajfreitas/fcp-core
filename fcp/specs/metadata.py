from serde import Model, fields


class MetaData(Model):
    line: fields.Int()
    column: fields.Int()
    filename: fields.Str()
