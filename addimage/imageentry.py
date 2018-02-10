from typing import Tuple
from discord.ext import commands

import discord

class ImageEntry:
    def __init__(self, command_name:str, count:int, file_loc:str, author:int):
        super().__init__()
        self.command_name = command_name
        self.count = count
        self. file_loc = file_loc
        self.author = author

    def to_json(self) -> dict:
        return {
            "command_name": self.command_name,
            "count": self.count,
            "file_loc": self.file_loc,
            "author": self.author
        }

    @classmethod
    def from_json(cls, data: dict):
        return cls(data["command_name"], data["count"], data["file_loc"], data["author"])
