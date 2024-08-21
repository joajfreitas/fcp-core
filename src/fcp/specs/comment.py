from serde import Model, fields


class Comment(Model):
    value: fields.Str()
