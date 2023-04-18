from dataclasses import dataclass

@dataclass
class LevelingGuild:
    guild_id: int
    enabled: bool
    xp: int
    cooldown: float
    mention: bool
    message: str
    channel_id: int
    custom_messages: dict
    roles: dict
    blacklist_channel: list
    blacklist_roles: list