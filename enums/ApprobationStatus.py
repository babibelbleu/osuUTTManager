from enum import Enum


class ApprobationStatus(Enum):
    LOVED = 4
    QUALIFIED = 3
    APPROVED = 2
    RANKED = 1
    PENDING = 0
    WORK_IN_PROGRESS = -1
    GRAVEYARD = -2
