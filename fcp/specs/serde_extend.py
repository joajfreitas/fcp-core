from serde import fields


class Any(fields.Field):
    """
    An any field.
    An `Any` is a field that is allowed to be of any type. Serialization,
    normalization, deserialization, and validation using the wrapped field will
    only be called if the value is not `None`.
    Args:
        inner: the `Field` class/instance that this `Optional` wraps.
        default: a value to use if there is no input field value or the input
            value is `None`. This can also be a callable that generates the
            default. The callable must take no positional arguments.
        **kwargs: keyword arguments for the `Field` constructor.
    """

    def __init__(self, type=None, **kwargs):
        """
        Create a new `Optional`.
        """
        super(Any, self).__init__(**kwargs)
        self.type = type

    # def _instantiate_with(self, model, kwargs):
    #    """
    #    Instantiate the corresponding model attribute from the keyword args.
    #    This method should .pop() from kwargs.
    #    """
    #    name = self._attr_name
    #    setattr(model, name, self._instantiate(kwargs.pop(name, None)))

    # def _serialize_with(self, model, d):
    #    """
    #    Serialize the corresponding model attribute to a dictionary.
    #    The value will only be added to the dictionary if it is not `None`.
    #    """
    #    value = self._serialize(getattr(model, self._attr_name))
    #    if value is not None:
    #        d[self._serde_name] = value
    #    return d

    # def _deserialize_with(self, model, d):
    #    """
    #    Deserialize the corresponding model attribute from a dictionary.
    #    If the field is not present in the dictionary then the model instance is
    #    left unchanged.
    #    """
    #    try:
    #        value = d[self._serde_name]
    #    except KeyError:
    #        return model, d
    #    setattr(model, self._attr_name, self._deserialize(value))
    #    return model, d

    # def _normalize_with(self, model):
    #    """
    #    Normalize the model attribute.
    #    """
    #    value = self._normalize(getattr(model, self._attr_name, None))
    #    setattr(model, self._attr_name, value)

    # def _instantiate(self, value):
    #    return value

    # def _serialize(self, value):
    #    if value is not None:
    #        value = self.serialize(value)
    #        for serializer in self.serializers:
    #            value = serializer(value)
    #    return value

    # def _deserialize(self, value):
    #    if value is not None:
    #        value = self.deserialize(value)
    #        for deserializer in self.deserializers:
    #            value = deserializer(value)
    #    return value

    # def _normalize(self, value):
    #    if value is not None:
    #        value = self.normalize(value)
    #        for normalizer in self.normalizers:
    #            value = normalizer(value)
    #    else:
    #        value = self._default()
    #    return value

    # def _validate(self, value):
    #    if value is not None:
    #        self.validate(value)
    #        for validator in self.validators:
    #            validator(value)

    def serialize(self, value):
        """
        Serialize the given value using the inner `Field`.
        """
        return value

    def deserialize(self, value):
        """
        Deserialize the given value using the inner `Field`.
        """
        return value

    def normalize(self, value):
        """
        Normalize the given value using the inner `Field`.
        """
        return value

    def validate(self, value):
        """
        Validate the given value using the inner `Field`.
        """
        pass
