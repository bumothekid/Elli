from dataclasses import dataclass
from typing import Optional

@dataclass
class LevelingUser:
    user_id: int
    messages: int
    level: int
    xp: int
    cooldown: float
    xp_needed: int