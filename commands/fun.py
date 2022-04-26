import asyncio
import random

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import capString

class fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("ssp")
    @commands.cooldown(5, 20, commands.BucketType.user)
    async def _ssp(self, ctx, choice: str = None):
        botchoice = random.choice(["stein", "schere", "papier"])

        if choice is None:
            i = 0

            await infoEmbed(self.bot, ctx, "Wähle `Stein`, `Schere` oder `Papier`")

            while i < 3:
                try:
                    anwser = self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                except asyncio.TimeoutError:
                    await errorEmbed(self.bot, ctx, "Der Befehl wurde abgebrochen, da du zu lange zum antwortet gebraucht hast.")
                    break
                
                if anwser.lower() not in ["stein", "schere", "papier"]:
                    if i == 3:
                        await errorEmbed(self.bot, ctx, "Du hast `3` Versuche verbraucht der befehl wird abgebrochen.")
                        break
                    await errorEmbed(self.bot, ctx, "Bitte wähle `Stein`, `Schere` oder `Papier`")
                    continue
            
                choice = anwser.lower()
                break
        
        if choice == botchoice:
            await successEmbed(self.bot, ctx, f"**Unentschieden!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        elif choice == "stein" and botchoice == "schere":
            await successEmbed(self.bot, ctx, f"**Du hast gewonnen!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        elif choice == "stein" and botchoice == "papier":
            await successEmbed(self.bot, ctx, f"**Du hast verloren!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        elif choice == "schere" and botchoice == "stein":
            await successEmbed(self.bot, ctx, f"**Du hast verloren!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        elif choice == "schere" and botchoice == "papier":
            await successEmbed(self.bot, ctx, f"**Du hast gewonnen!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        elif choice == "papier" and botchoice == "stein":
            await successEmbed(self.bot, ctx, f"**Du hast gewonnen!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")

        elif choice == "papier" and botchoice == "schere":
            await successEmbed(self.bot, ctx, f"**Du hast verloren!**\n\n> **Deine Wahl:** `{capString(choice)}`\n> **Bot Wahl:** `{capString(botchoice)}`")
        
        else:
            await errorEmbed(self.bot, ctx, "Es ist ein Fehler aufgetreten.")

        
                
                
                

def setup(bot):
    bot.add_cog(fun(bot))