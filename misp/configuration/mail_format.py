from enum import Enum, auto


class MailFormat(Enum):
    default = auto()
    none = auto()
    org = auto()
    instance = auto()
    full = auto()
