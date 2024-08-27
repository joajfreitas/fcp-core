from serde import Model, fields


class Comment(Model):
    value: str = fields.Str()
