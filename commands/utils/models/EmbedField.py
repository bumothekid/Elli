from dataclasses import dataclass

@dataclass
class EmbedField:
    name: str
    value: str
    inline: bool = False