from sqlalchemy import Enum


# pylint: disable-next=too-many-ancestors
class EnumValue(Enum):
    def __init__(self, *enums, **kw):
        kw["native_enum"] = False
        if not kw.get("values_callable"):
            kw["values_callable"] = lambda obj: [e.value for e in obj]
        super().__init__(*enums, **kw)
