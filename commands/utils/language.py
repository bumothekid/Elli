import os
import json
from .database import readOne, insert, update

def getGuildLanguage(guild_id) -> str:
    result = readOne("language", "guilds", "guild_id", guild_id)

    if result is None:
        insert("guilds", "guild_id, prefix, language", [guild_id, "-", "en"])
        return "en"
    
    if result[0] is None:
        update("guilds", "language", "guild_id", ["en", guild_id])
        return "en"
    
    return result[0]

def updateGuildLanguage(guild_id, language: str):
    result = readOne("language", "guilds", "guild_id", guild_id)

    if result is None:
        insert("guilds", "guild_id, prefix, language", [guild_id, "-", language])
        return
    
    update("guilds", "language", "guild_id", [language, guild_id])

def getLanguageStrings(cog: str):
    languageStrings = {}

    for file in os.listdir(f"language/{cog}"):
        if file.endswith(".json"):
            with open(f"language/{cog}/{file}", "r", encoding="utf-8") as f:
                languageStrings[file.replace(".json", "")] = json.load(f)
            
    return languageStrings

def getLocale(languageStrings: dict, language: str, string: str, *args):
    if language not in languageStrings:
        return f"Missing language {language}"

    if string not in languageStrings[language]:
        return f"Missing string {string} in language {language}"

    return languageStrings[language][string].format(*args)