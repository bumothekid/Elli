from dataclasses import dataclass

@dataclass
class LevelingGuild:
    guild_id: int
    enabled: bool
    cooldown: float
    mention: bool
    message: str