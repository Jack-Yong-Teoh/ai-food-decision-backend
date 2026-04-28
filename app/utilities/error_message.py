def field_required(field_name: str) -> str:
    return f"{field_name.upper()} IS REQUIRED."


def either_field_required(field_names: list[str]) -> str:
    or_fields = " OR ".join([field_name.upper() for field_name in field_names])
    return f"EITHER {or_fields} IS REQUIRED."


def invalid_format(
    field_name: str,
    expected_format: str,
) -> str:
    return f"{field_name.upper()} MUST BE IN {expected_format} FORMAT."


def invalid_object(field_name: str) -> str:
    return f"INVALID {field_name.upper()}."


def value_too_short(
    field_name: str,
    min_length: int,
) -> str:
    return f"{field_name.upper()} MUST BE AT LEAST {min_length} CHARACTERS LONG."


def value_too_long(
    field_name: str,
    max_length: int,
) -> str:
    return f"{field_name.upper()} MUST NOT EXCEED {max_length} CHARACTERS."


def value_out_of_range(
    field_name: str,
    min_value: int = None,
    max_value: int = None,
) -> str:
    if min_value is not None and max_value is not None:
        return f"{field_name.upper()} MUST BE BETWEEN {min_value} AND {max_value}."
    if min_value is not None:
        return f"{field_name.upper()} MUST BE AT LEAST {min_value}."
    if max_value is not None:
        return f"{field_name.upper()} MUST NOT EXCEED {max_value}."
    return f"{field_name.upper()} IS OUT OF RANGE."


def list_out_of_range(
    field_name: str,
    min_value: int = None,
    max_value: int = None,
) -> str:
    if min_value is not None and max_value is not None:
        return f"{field_name.upper()} MUST CONTAINS BETWEEN {min_value} AND {max_value} ITEMS."
    if min_value is not None:
        return f"{field_name.upper()} MUST CONTAINS AT LEAST {min_value} ITEMS."
    if max_value is not None:
        return f"{field_name.upper()} MUST NOT CONTAINS EXCEED {max_value} ITEMS."
    return f"{field_name.upper()} IS OUT OF RANGE."


def conflict_error(field_name: str) -> str:
    return f"{field_name.upper()} ALREADY EXISTS."


def incorrect_value(field_name: str) -> str:
    return f"INCORRECT {field_name.upper()}."


def object_expired(field_name: str) -> str:
    return f"{field_name.upper()} EXPIRED."


def object_not_found(object_name: str) -> str:
    return f"{object_name.upper()} NOT FOUND."


def general_error(message: str) -> str:
    return message.upper()


def missing_or_invalid_fields() -> str:
    return "SOME REQUIRED FIELDS ARE MISSING OR INVALID."


def account_deactivated() -> str:
    return "YOUR ACCOUNT IS DEACTIVATED."


def hit_rate_limit() -> str:
    return "RATE LIMIT EXCEEDED"
