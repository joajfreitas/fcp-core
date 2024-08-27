from serde import fields
from typing import Any


class AnyField(fields.Field):  # type: ignore
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

    def __init__(self, type: Any = None, **kwargs: list[Any]) -> None:
        """
        Create a new `Optional`.
        """
        super(AnyField, self).__init__(**kwargs)
        self.type = type

    def serialize(self, value: Any) -> Any:
        """
        Serialize the given value using the inner `Field`.
        """
        return value

    def deserialize(self, value: Any) -> Any:
        """
        Deserialize the given value using the inner `Field`.
        """
        return value

    def normalize(self, value: Any) -> Any:
        """
        Normalize the given value using the inner `Field`.
        """
        return value

    def validate(self, value: Any) -> None:
        """
        Validate the given value using the inner `Field`.
        """
        pass
