"""Common types used by several dataclasses."""
__all__ = [
    "Email",
    "PasswordHash",
    "RawPassword",
    "Username",
    "NotSet",
]

import typing as t
from enum import Enum, auto

Email = t.NewType("Email", str)
PasswordHash = t.NewType("PasswordHash", str)
RawPassword = t.NewType("RawPassword", str)
Username = t.NewType("Username", str)


class NotSet(Enum):
    NOT_SET = auto()
