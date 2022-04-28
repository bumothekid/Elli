import asyncio
from pprint import pprint
import random
import aiohttp
import nextcord
import requests

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import capString, checkLink

class fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ssp", aliases=["rsp", "rps"])
    @commands.cooldown(5, 20, commands.BucketType.user)
    async def _ssp(self, ctx, choice: str = None):
        botchoice = random.choice(["stein", "schere", "papier"])

        if choice is None:
            i = 0

            await infoEmbed(self.bot, ctx, "Wähle `Stein`, `Schere` oder `Papier`")

            while i < 3:
                try:
                    anwser = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                except asyncio.TimeoutError:
                    await errorEmbed(self.bot, ctx, "Der Befehl wurde abgebrochen, da du zu lange zum antwortet gebraucht hast.")
                    break
                
                if anwser.content.lower() not in ["stein", "schere", "papier"]:
                    if i == 3:
                        await errorEmbed(self.bot, ctx, "Du hast `3` Versuche verbraucht der befehl wird abgebrochen.")
                        break
                    await errorEmbed(self.bot, ctx, "Bitte wähle `Stein`, `Schere` oder `Papier`")
                    continue
            
                choice = anwser.content
                break
        
        choice = choice.lower()
        
        if choice == botchoice:
            await successEmbed(self.bot, ctx, f"**Unentschieden!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`", color=nextcord.Color.white())
        
        elif choice == "stein" and botchoice == "schere":
            await successEmbed(self.bot, ctx, f"**Du hast gewonnen!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        elif choice == "stein" and botchoice == "papier":
            await successEmbed(self.bot, ctx, f"**Du hast verloren!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`", color=nextcord.Color.red())
        
        elif choice == "schere" and botchoice == "stein":
            await successEmbed(self.bot, ctx, f"**Du hast verloren!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`", color=nextcord.Color.red())
        
        elif choice == "schere" and botchoice == "papier":
            await successEmbed(self.bot, ctx, f"**Du hast gewonnen!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        elif choice == "papier" and botchoice == "stein":
            await successEmbed(self.bot, ctx, f"**Du hast gewonnen!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")

        elif choice == "papier" and botchoice == "schere":
            await successEmbed(self.bot, ctx, f"**Du hast verloren!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`", color=nextcord.Color.red())
        
        else:
            await errorEmbed(self.bot, ctx, "Es ist ein Fehler aufgetreten.")
    
    @commands.command(name="8ball", aliases=["8b", "ask"])
    @commands.cooldown(5, 20, commands.BucketType.user)
    async def _8ball(self, ctx, *, question: str):
        anwsers = ["Ja", "Sicher", "100%", "Vielleicht", "Eher weniger", "Joa", "Lieber nicht", "Nein"]

        if checkLink(ctx.message):
            await errorEmbed(self.bot, ctx, "Du kannst keine Links in deine Frage schreiben.")
            return

        await successEmbed(self.bot, ctx, f"**8ball**\n\n> **Antwort:** *{random.choice(anwsers)}*\n\n> **Frage:** *{question}`")
                
    @commands.command(name="cat", aliases=["kitty", "kitten"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _cat(self, ctx):
        async with ctx.channel.typing():
            try:
                r = requests.get("https://aws.random.cat/meow")
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                await errorEmbed(self.bot, ctx, "Es ist ein Fehler aufgetreten.")
                return
            data = r.json()

            await successEmbed(self.bot, ctx, f"**Kitty**\n\n> **URL:** [`📎` Link]({data['file']})", image=data['file'])

    @commands.command(name="dog", aliases=["puppy"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _dog(self, ctx):
        async with ctx.channel.typing():
            try:
                r = requests.get("https://random.dog/woof.json")
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                await errorEmbed(self.bot, ctx, "Es ist ein Fehler aufgetreten.")
                return
            data = r.json()

            if data['url'].endswith(".mp4"):
                return await self._dog(ctx)
                
            await successEmbed(self.bot, ctx, f"**Dog**\n\n> **URL:** [`📎` Link]({data['url']})", image=data['url'])

    # TODO: Fix meme command

    @commands.command(name="meme", aliases=["memes"])
    @commands.cooldown(5, 20, commands.BucketType.user)
    async def _meme(self, ctx):
        await errorEmbed(self.bot, ctx, "Der Meme befehl ist momentan deaktiviert.")
        # print("aaa")
        # r = requests.get("https://www.reddit.com/r/memes/new.json?")
        # print("bbb")
        # r.raise_for_status()
        # except requests.exceptions.RequestException as e:
        # return await errorEmbed(self.bot, ctx, "Es ist ein Fehler aufgetreten.")
        
        # data = r.json()
        # pprint(data)
        # num = random.randint(0, 20)
        # meme = data["data"]["children"][num]["data"]

        # title = meme["title"]
        # memeURL = meme["url"]
        # upvotes = meme["ups"]
        # comments = meme["num_comments"]
        # await infoEmbed(self.bot, ctx, f"**[{title}]({memeURL})**", image=memeURL, footer={"text": f"👍 {upvotes} | 💬 {comments}", "icon_url": ""})

    

def setup(bot):
    bot.add_cog(fun(bot))