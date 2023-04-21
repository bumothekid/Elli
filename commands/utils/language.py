import os
import json
from .embeds import localizationError
from .database import readOne, insert, update
from nextcord.ext.commands import Bot

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

    for file in os.listdir(f"./language/{cog}"):
        if file.endswith(".json"):
            with open(f"./language/{cog}/{file}", "r", encoding="utf-8") as f:
                languageStrings[file.replace(".json", "")] = json.load(f)
            
    return languageStrings

def getLocale(bot: Bot, languageStrings: dict, language: str, string: str, *args):
    if language not in languageStrings:
        return f"Missing language {language}"

    if string not in languageStrings[language]:
        localizationError(bot, f"Missing string {string} in language {language}")
        
        return f"Missing string {string} in language {language}"
    
    try:
        return languageStrings[language][string].format(*args)
    except IndexError as e:
        missingArgs = e.args[0].split("index ")[1].split(" out of range")[0]
        
        localizationError(bot, f"Missing argument {missingArgs} in string {string} for language {language}.")
        return languageStrings[language][string]