from typing import TypedDict

class Credential(TypedDict):
    """Credential type for Sophos login"""
    username: str
    password: str

# Typo lol
Creditial = Credential