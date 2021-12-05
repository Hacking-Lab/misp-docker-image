from enum import Enum, auto


class Role(Enum):
    admin = auto()
    org_admin = auto()
    investigator = auto()
    publisher = auto()
    sync_user = auto()
    automation_user = auto()
