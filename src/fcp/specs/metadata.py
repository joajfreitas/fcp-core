from serde import serde, strict


@serde(type_check=strict)
class MetaData:
    """MetaData information for AST nodes."""

    line: int
    end_line: int
    column: int
    end_column: int
    start_pos: int
    end_pos: int
    filename: str
