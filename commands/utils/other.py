import nextcord
from re import I, findall
from .database import readOne, insert
from string import capwords

class safeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def getPrefixFromDatabase(bot, message):
    prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[message.guild.id])

    if prefix is None:
        insert(table="guilds", columns="guild_id, prefix", values=[message.guild.id, "-"])
        return "-"

    return prefix

def devCheck(authorid: int) -> bool:
    devs = readOne(columns="developer", table="cursy")
    devlist = findall(r"[0-9]+", devs[0])

    if str(authorid) not in devlist:
        return False
    
    return True

def messagePinned(message: nextcord.Message) -> bool:
    return not message.pinned

def capString(string: str) -> str:
    return capwords(string.lower())

def checkLink(text: str) -> bool:
    if "https://" in text or "http://" in text:
        return True
    
    if "discord." in text or "discordapp." in text:
        return True
    
    return False