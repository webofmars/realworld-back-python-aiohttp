"""Common types used by several dataclasses."""
__all__ = [
    "Email",
    "PasswordHash",
    "RawPassword",
    "Username",
]

import typing as t

Email = t.NewType("Email", str)
PasswordHash = t.NewType("PasswordHash", str)
RawPassword = t.NewType("RawPassword", str)
Username = t.NewType("Username", str)
