import asyncio
import random
import nextcord
import requests

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import capString, checkLink, connectionTimeout

languageStrings = {}
class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ssp", aliases=["rsp", "rps"])
    @commands.cooldown(5, 20, commands.BucketType.user)
    async def _ssp(self, ctx, choice: str = None):
        guildLocale = getGuildLanguage(ctx.guild.id)

        stone = getLocale(self.bot, languageStrings, guildLocale, "stone")
        scissors = getLocale(self.bot, languageStrings, guildLocale, "scissors")
        paper = getLocale(self.bot, languageStrings, guildLocale, "paper")

        if choice is not None and choice.lower() not in [stone, scissors, paper]:
            await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspWrongChoice"))
            return

        botchoice = random.choice([stone, scissors, paper])

        if choice is None:
            i = 0

            await infoEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspWrongChoice"))

            while i < 3:
                try:
                    anwser = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                except asyncio.TimeoutError:
                    await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspTimeout"))
                    break
                
                if anwser.content.lower() not in [stone.lower(), scissors.lower(), paper.lower()]:
                    if i == 3:
                        await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspThreeTries"))
                        break

                    await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspWrongChoice"))
                    continue
            
                choice = anwser.content
                break
        
        choice = capString(choice)
        
        if choice == botchoice:
            await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspDraw", choice, botchoice), color=nextcord.Color.light_gray())
        
        elif choice == stone and botchoice == scissors:
            await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspWin", choice, botchoice))
        
        elif choice == stone and botchoice == paper:
            await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspLose", choice, botchoice), color=nextcord.Color.red())
        
        elif choice == scissors and botchoice == stone:
            await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspLose", choice, botchoice), color=nextcord.Color.red())
        
        elif choice == scissors and botchoice == paper:
            await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspWin", choice, botchoice))
        
        elif choice == paper and botchoice == stone:
            await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspWin", choice, botchoice))

        elif choice == paper and botchoice == scissors:
            await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspLose", choice, botchoice), color=nextcord.Color.red())
        
        else:
            await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "sspUnexpectedOutcome"))
    
    @commands.command(name="8ball", aliases=["8b", "ask"])
    @commands.cooldown(5, 20, commands.BucketType.user)
    async def _8ball(self, ctx, *, question: str):
        guildLocale = getGuildLanguage(ctx.guild.id)

        anwsers = [getLocale(self.bot, languageStrings, guildLocale, "yes"), getLocale(self.bot, languageStrings, guildLocale, "safe"), "100%", getLocale(self.bot, languageStrings, guildLocale, "maybe"), getLocale(self.bot, languageStrings, guildLocale, "notReally"), getLocale(self.bot, languageStrings, guildLocale, "yeah"), getLocale(self.bot, languageStrings, guildLocale, "betterNot"), getLocale(self.bot, languageStrings, guildLocale, "no"), getLocale(self.bot, languageStrings, guildLocale, "nope"), getLocale(self.bot, languageStrings, guildLocale, "never"), getLocale(self.bot, languageStrings, guildLocale, "notAtAll"), getLocale(self.bot, languageStrings, guildLocale, "notSure"), getLocale(self.bot, languageStrings, guildLocale, "noWay")]

        if checkLink(ctx.message.content):
            await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "noLinksQuestion"))
            return
        
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "8ballSuccess", random.choice(anwsers), question))
                
    @commands.command(name="cat", aliases=["kitty", "kitten"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _cat(self, ctx):
        async with ctx.channel.typing():
            try:
                r = requests.get("https://aws.random.cat/meow", timeout=10)
                r.raise_for_status()
            except requests.exceptions.ConnectTimeout as e:
                return await connectionTimeout(self.bot, ctx)
            except requests.exceptions.RequestException as e:
                raise commands.CommandError(e)
            
            data = r.json()

            await successEmbed(self.bot, ctx, f"**Kitty**\n\n> **URL:** [`📎` Link]({data['file']})", image=data['file'])

    @commands.command(name="dog", aliases=["puppy"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _dog(self, ctx):
        async with ctx.channel.typing():
            try:
                r = requests.get("https://random.dog/woof.json", timeout=10)
                r.raise_for_status()
            except requests.exceptions.ConnectTimeout as e:
                return await connectionTimeout(self.bot, ctx)
            except requests.exceptions.RequestException as e:
                raise commands.CommandError(e)
            
            data = r.json()

            if data['url'].endswith(".mp4"):
                return await self._dog(ctx)
                
            await successEmbed(self.bot, ctx, f"**Dog**\n\n> **URL:** [`📎` Link]({data['url']})", image=data['url'])

    # TODO: Fix meme command

    @commands.command(name="meme", aliases=["memes"], enabled=False)
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

    @commands.command(name="reverse")
    @commands.cooldown(5, 20, commands.BucketType.user)
    async def _reverse(self, ctx, *, text: str):
        guildLocale = getGuildLanguage(ctx.guild.id)

        reverse = text[::-1]

        if checkLink(text) or checkLink(reverse):
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "noLinksText"))
        
        await infoEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "reverseSuccess", ctx.author, reverse))

    

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("fun")
    bot.add_cog(Fun(bot))