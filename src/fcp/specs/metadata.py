from serde import serde, strict


@serde(type_check=strict)
class MetaData:
    line: int
    end_line: int
    column: int
    end_column: int
    start_pos: int
    end_pos: int
    filename: str

    @staticmethod
    def default_metadata() -> "MetaData":
        return MetaData(
            line=1,
            end_line=1,
            column=1,
            end_column=1,
            start_pos=1,
            end_pos=1,
            filename="default.fcp",
        )  # type: ignore
