import random
import nextcord
import asyncio
import re
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time as time_, mktime
from datetime import datetime, timedelta
from .utils.embeds import infoEmbed, errorEmbed, successEmbed
from .utils.database import delete, readAll, insert, readOne, update

class Giveaways(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="giveaway", aliases=["gv"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _giveaway(self, ctx):
        await infoEmbed(self, ctx, "**<a:Giveaway:1087437215648456794> Giveaway Commands**\n\n> `-giveaway create`\n> `-giveaway quick <#channel> <zeit in minuten> <winner> <preis>`\n> `-giveaway drop <#channel> <preis>`\n> `-giveaway end <#channel> <messageid>`\n> `-giveaway reroll <#channel> <messageid> <winner>`\n> `-giveaway list`")

    @_giveaway.command(name="create", aliases=["start"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def _create(self, ctx):
        if len(readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])) >= 9:
            return await errorEmbed(self, ctx, "Du kannst nur `9` Giveaways gleichzeitig starten.")

        questions = [
            f"Bevor wir das Giveaway starten können musst du ein paar fragen beantworten\n\n> In welchem Channel soll das Giveaway stattfinden?\n> **Beispiel:** {ctx.channel.mention}",
            "Bevor wir das Giveaway starten können musst du ein paar fragen beantworten\n\n> Wie lange soll das Giveaway gehen? `<m | h | d>`\n> **Beispiel:** `1d 5h 30m`",
            "Bevor wir das Giveaway starten können musst du ein paar fragen beantworten\n\n> Was soll der Preis sein?",
            "Bevor wir das Giveaway starten können musst du ein paar fragen beantworten\n\n> Wie viele Gewinner soll es geben?"
        ]

        anwsers = {}
        message = None

        for i, question in enumerate(questions):
            embed = nextcord.Embed(
                    description=question,
                    color=nextcord.Color.blurple()
            )

            if message != None:
                await message.edit(embed=embed)
            else:
                message = await ctx.reply(embed=embed)

            while True:
                try:
                    userAnwser = await self.bot.wait_for("message", timeout=120, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                except asyncio.TimeoutError:
                    if message is not None:
                        await message.delete()
                    
                    return await errorEmbed(self, ctx, "Du hast mehr als `2` Minuten gebraucht um zu antworten.\n\n> Der Giveaway startvorgang wurde abgebrochen.")

                match i:
                    case 0:
                        await userAnwser.delete()
                        try:
                            channelid = re.findall(r"[0-9]+", userAnwser.content)[0]
                            anwser = self.bot.get_channel(int(channelid))

                            if anwser == None:
                                embed = nextcord.Embed(
                                    description=question + "\n\n> `Ich konnte diesen Channel nicht finden bitte versuche erneut`",
                                    color=nextcord.Color.blurple()
                                )

                                await message.edit(embed=embed)
                                continue
                        except:
                            embed = nextcord.Embed(
                                description=question + "\n\n> `Ich konnte diesen Channel nicht finden bitte versuche erneut`",
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            continue
                    case 1:
                        await userAnwser.delete() 
                        timeRegex = re.compile(r'(?:(\d{1,5})(h|s|m|d))+?')
                        timeDict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

                        time = (userAnwser.content).lower()

                        matches = re.findall(timeRegex, time)
                        anwser = 0

                        if not matches:
                            embed = nextcord.Embed(
                                description=question + f"\n\n> `Ungültige Zeitangabe`",
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            continue
                        for key, value in matches:
                            try:
                                anwser += timeDict[value] * float(key)
                            except KeyError:
                                embed = nextcord.Embed(
                                    description=question + f"\n\n> `{value} ist ein ungültiger Zeitschlüssel`\n> `< s | m | h | d> sind gültige Zeitschlüssel`",
                                    color=nextcord.Color.blurple()
                                )

                                await message.edit(embed=embed)
                                continue
                            except ValueError:
                                embed = nextcord.Embed(
                                    description=question + f"\n\n> `{key} ist keine ganze Zahl`",
                                    color=nextcord.Color.blurple()
                                )

                                await message.edit(embed=embed)
                                continue
                        
                        if round(anwser) < 120:
                            embed = nextcord.Embed(
                                description=question + f"\n\n> `Die Zeit muss mindestens 120 Sekunden betragen`",
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            continue

                        anwser = round(anwser)
                    case 2:
                        await userAnwser.delete()

                        if userAnwser.content == '':
                            anwser = "Nichts!"
                        elif len(userAnwser.content) > 150:
                            embed = nextcord.Embed(
                                description=question + f"\n\n> `Der Preis darf aus maximal 150 Zeichen bestehen`",
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            continue
                        else:
                            anwser = userAnwser.content
                    case 3:
                        await userAnwser.delete()

                        if not userAnwser.content.isdigit():
                            embed = nextcord.Embed(
                                description=question + f"\n\n> `Die anzahl an gewinnern muss eine ganze Zahl sein`",
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            continue

                        elif int(userAnwser.content) >= 100 or int(userAnwser.content) <= 0:
                            embed = nextcord.Embed(
                                description=question + f"\n\n> `Die anzahl an Gewinnern darf nicht größer als 100 sein`",
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            continue
                        anwser = int(userAnwser.content)
                        await message.delete()


                            
                anwsers[i] = anwser
                break
            
        now = datetime.now()
        unix = int(mktime((now + timedelta(seconds=anwsers[1])).timetuple()))

        embed = nextcord.Embed(
            title=anwsers[2],
            description=f"Reagiere mit <a:Giveaway:1087437215648456794> um Teilzunehmen\n\n> Endet: <t:{unix}:R> (<t:{unix}:f>)\n> Host: {ctx.author.mention}",
            color=ctx.author.color,
            timestamp=now + timedelta(seconds=anwsers[1])
        )
        embed.set_footer(text=f"{anwsers[3]} Gewinner | Endet")

        message = await anwsers[0].send(embed=embed)

        insert(table="giveaways", columns="guild_id, channel_id, message_id, start, duration, prize, winner, hoster_id", values=[ctx.guild.id, anwsers[0].id, message.id, time_(), anwsers[1], anwsers[2], anwsers[3], ctx.author.id])

        emote = self.bot.get_emoji(958492679749140510)

        await message.add_reaction(emote)

        await successEmbed(self, ctx, f"**<a:Giveaway:1087437215648456794> Giveaway gestartet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{anwsers[0].id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{anwsers[0].id}/{message.id}/)\n> **Gewinner:** {anwsers[3]}\n> **Bis:** <t:{unix}:f>")

    @_giveaway.command(name="quick", aliases=["q", "quickstart"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _quick(self, ctx, channel: nextcord.TextChannel, minutes, winner, *, prize):
        if len(readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])) >= 9:
            return await errorEmbed(self, ctx, "Du kannst nur `9` Giveaways gleichzeitig starten.")

        if len(prize) > 150:
            return await errorEmbed(self, ctx, "Der Preis darf aus maximal `150` Zeichen bestehen.")

        if not minutes.isdigit():
            return await errorEmbed(self, ctx, "Die Zeitangabe muss in minuten angegeben sein.")
        
        if not winner.isdigit():
            return await errorEmbed(self, ctx, "Die Anzahl an Gewinnern muss eine ganze Zahl sein.")

        elif int(winner) >= 100:
            return await errorEmbed(self, ctx, "Die anzahl an Gewinnern darf nicht größer als `100` sein.")

        if prize == "":
            return await errorEmbed(self, ctx, "Du musst einen Gewinn angeben.")

        seconds = int(minutes) * 60
        now = datetime.now()
        unix = int(mktime((now + timedelta(seconds=seconds)).timetuple()))

        embed = nextcord.Embed(
            title=prize,
            description=f"Reagiere mit <a:Giveaway:1087437215648456794> um Teilzunehmen\n\n> Endet: <t:{unix}:R> (<t:{unix}:f>)\n> Host: {ctx.author.mention}",
            color=ctx.author.color,
            timestamp=now + timedelta(seconds=seconds)
        )
        embed.set_footer(text=f"{winner} Gewinner | Endet")

        message = await channel.send(embed=embed)

        insert(table="giveaways", columns="guild_id, channel_id, message_id, start, duration, prize, winner, hoster_id", values=[ctx.guild.id, channel.id, message.id, time_(), seconds, prize, winner, ctx.author.id])

        emote = self.bot.get_emoji(958492679749140510)

        await message.add_reaction(emote)

        await successEmbed(self, ctx, f"**<a:Giveaway:1087437215648456794> Giveaway gestartet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}/)\n> **Gewinner:** {winner}\n> **Bis:** <t:{unix}:f>")

    @_giveaway.command(name="drop")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _drop(self, ctx, channel: nextcord.TextChannel, *, prize):
        if len(readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])) >= 9:
            embed = nextcord.Embed(
                description="Du kannst nur **9** Giveaways gleichzeitig starten",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        if len(prize) > 150:
            return await errorEmbed(self, ctx, "Der Preis darf aus maximal `150` Zeichen bestehen.")

        embed = nextcord.Embed(
            title=prize,
            description=f"Reagiere mit <a:Giveaway:1087437215648456794>, um den Drop einzusammeln \n\n> Host: {ctx.author.mention}",
            color=ctx.author.color,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Drop von {ctx.author.name}")

        message = await channel.send(embed=embed)

        emote = self.bot.get_emoji(958492679749140510)

        await message.add_reaction(emote)

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: u.bot == False and r.message.id == message.id and r.emoji == emote, timeout=300)
        except asyncio.TimeoutError:
            return await errorEmbed(self, channel, "<a:Giveaway:1087437215648456794> Drop wurde abgebrochen.**\n\n**> Drop nach 5 Minuten abgelaufen.")

        embed = nextcord.Embed(
            title=prize,
            description=f"**<a:Giveaway:1087437215648456794> Drop erhalten**\n\n> **Gewinner:** {user.mention}\n> **Preis:** {prize}",
            color=ctx.author.color
        )

        await message.edit(embed=embed)

        await successEmbed(self,
                            channel,
                            f"Herzlichen Glückwunsch, {user.mention} hat den Drop eingesammelt und {prize} gewonnen\n> Es waren `{sum(member.status!=nextcord.Status.offline and not member.bot for member in ctx.guild.members)}` andere User online",
                            color=ctx.author.color
        )
        

    @_giveaway.command(name="end", aliases=["stop"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _end(self, ctx, channel: nextcord.TextChannel, message):
        try:
            message = await channel.fetch_message(message)
        except:
            raise commands.MessageNotFound(argument=message)

        giveaway = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[ctx.guild.id, message.id])

        if giveaway is None:
            return await errorEmbed(self, ctx, "Es wurde kein aktives Gewinnspiel mit dieser Nachrichten ID gefunden.")

        await successEmbed(self, ctx, f"**<a:Giveaway:1087437215648456794> Das Giveaway wird in kürze beendet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}/)\n> **Gewinner:** {giveaway[6]}")
        
        update(table="giveaways", columns="duration", where="guild_id message_id", values=["0", ctx.guild.id, message.id])

    @_giveaway.command(name="reroll")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _rerroll(self, ctx, channel: nextcord.TextChannel, message, winners):
        try:
            message = await channel.fetch_message(message)
        except:
            raise commands.MessageNotFound(argument=message)

        if not winners.isdigit():
            return await errorEmbed(self, ctx, "Die anzahl an gewinnern muss eine ganze Zahl sein.")

        giveaway = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[ctx.guild.id, message.id])

        if giveaway is not None:
            return await errorEmbed(self, ctx, "Das Giveaway ist noch am laufen.**\n> **Du kannst mit `-giveaway end <#channel> <messageid>` das Gewinnspiel beenden.")

        emote = self.bot.get_emoji(958492679749140510)
        is_giveaway = any(reaction.emoji == emote for reaction in message.reactions)

        if not is_giveaway:
            return await errorEmbed(self, ctx, "Diese Nachricht ist kein Giveaway.")

        guild = self.bot.get_guild(ctx.guild.id)
        winner_list = []

        entries = list(await message.reactions[0].users().flatten())
        entries.pop(entries.index(guild.me))

        hosterid = re.findall(r"[0-9]+", message.embeds[0].description)[-1]
        hoster = guild.get_member(int(hosterid))
        
        if hoster in entries:
            entries.pop(entries.index(hoster))

        backupEntries = entries.copy()

        for _ in range(int(winners)):
            if not entries:
                break
            winner = random.choice(entries)
            winner_list.append(winner.mention)

            entries.pop(entries.index(winner))

        if not winner_list:
            return await errorEmbed(self, ctx, "Es konnte kein Gewinner entschieden werden.")

        winners = ', '.join(winner_list)

        if len(winner_list) > 1:
            string = f"Herzlichen Glückwunsch, {winners} haben {message.embeds[0].title} gewonnen\n> `{len(backupEntries)}` gültige Teilnehmer"
        else:
            string = f"Herzlichen Glückwunsch, {winners} hat {message.embeds[0].title} gewonnen\n> `{len(backupEntries)}` gültige Teilnehmer"

        embed = nextcord.Embed(
            description=string,
            color=ctx.author.color
        )
        await ctx.reply(embed=embed)

    
    @_giveaway.command(name="list", aliases=["show"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _list(self, ctx):
        giveaways = readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])

        if not giveaways:
            return await errorEmbed(self, ctx, "Es wurden keine aktiven Giveaways gefunden.")

        fields = []

        for giveaway in giveaways:
            giveaway_channel_link = f"[`📎`Link](https://discord.com/channels/{ctx.guild.id}/{giveaway[1]}/)"
            giveaway_message_link = f"[`📎`Link](https://discord.com/channels/{ctx.guild.id}/{giveaway[1]}/{giveaway[2]}/)"
            giveaway_price = giveaway[5]
            giveaway_winner = giveaway[6]
            giveaway_hoster = ctx.guild.get_member(int(giveaway[7]))

            start = datetime.fromtimestamp(giveaway[3])
            unix = int(mktime((start + timedelta(seconds=giveaway[4])).timetuple()))

            fields.append({"name": f"**{giveaway_price}**", "value": f"> **Channel:** {giveaway_channel_link}\n> **Nachricht:** {giveaway_message_link}\n> **Hoster:** {giveaway_hoster.mention}\n> **Gewinner:** {giveaway_winner}\n> **Bis:** <t:{unix}:f>", "inline": True})
        
        await infoEmbed(self, ctx, "**<a:Giveaway:1087437215648456794> Aktive Giveaways**", fields=fields)

    @Cog.listener()
    async def on_ready(self):
        for i in self.bot.guilds:
            running = readAll(columns="message_id, channel_id", table="giveaways", where="guild_id", values=[i.id])

            if running:
                for giveaway in running:
                    await self.giveawayTimer(guild_id=i.id, message_id=giveaway[0])

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emote = self.bot.get_emoji(958492679749140510)
        if payload.emoji == emote:
            guild = self.bot.get_guild(payload.guild_id)
            if payload.member == guild.me:
                await asyncio.sleep(5)
                exists = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[payload.guild_id, payload.message_id])
                if exists is not None:
                    await self.giveawayTimer(guild_id=payload.guild_id, message_id=payload.message_id)

    @Cog.listener()
    async def on_message_delete(self, message):
        exists = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[message.guild.id, message.id])

        if exists is not None:
            delete(table="giveaways", where="guild_id message_id", values=[message.guild.id, message.id])

    @Cog.listener()
    async def on_guild_remove(self, guild):
        giveaways = readAll(columns="message_id", table="giveaways", where="guild_id")
        
        if giveaways:
            for giveaway in giveaways:
                delete(table="giveaways", where="guild_id message_id", values=[guild.id, giveaway[0]])

    async def giveawayTimer(self, guild_id, message_id):
        while True:
            now = time_()
            time = readOne(columns="start, duration", table="giveaways", where="guild_id message_id", values=[guild_id, message_id])
            if time is None:
                return
            if round(now - time[0]) >= time[1]:
                break
            await asyncio.sleep(30)

        giveaway = readOne(columns="channel_id, winner, hoster_id, prize, start, duration", table="giveaways", where="guild_id message_id", values=[guild_id, message_id])

        if giveaway is not None:
            guild = self.bot.get_guild(guild_id)
            channel = self.bot.get_channel(giveaway[0])
            message = await channel.fetch_message(message_id)
            host = guild.get_member(giveaway[2])

            winner_amount = giveaway[1]
            winner_list = []

            unix = int(mktime((datetime.fromtimestamp(giveaway[4]) + timedelta(seconds=giveaway[5])).timetuple()))


            entries = list(await message.reactions[0].users().flatten())
            entries.pop(entries.index(guild.me))
            if host in entries:
                entries.pop(entries.index(host))

            backupEntries = entries.copy()

            for _ in range(winner_amount):
                if not entries:
                    break
                winner = random.choice(entries)
                winner_list.append(winner.mention)

                entries.pop(entries.index(winner))

            if not winner_list:
                embed = nextcord.Embed(
                    title=giveaway[3],
                    description=f"Es konnten keine Gewinner entschieden werden\n\n> Endete: <t:{unix}:R> (<t:{unix}:f>)\n> Host: {host.mention}",
                    color=host.color,
                    timestamp=datetime.fromtimestamp(giveaway[4]) + timedelta(seconds=giveaway[5])
                )
                embed.set_footer(text=f"{giveaway[1]} Gewinner | Endete")

                await message.edit(embed=embed)

                await errorEmbed(self, channel, "Es konnte kein Gewinner entschieden werden.")

                return delete(table="giveaways", where="guild_id message_id", values=[guild_id, message_id])

            winners = ', '.join(winner_list)

            embed = nextcord.Embed(
                title=giveaway[3],
                description=f"Gewinner: {winners}\n\n> Endete: <t:{unix}:R> (<t:{unix}:f>)\n> Host: {host.mention}",
                color=host.color,
                timestamp=datetime.fromtimestamp(giveaway[4]) + timedelta(seconds=giveaway[5])
            )
            embed.set_footer(text=f"{giveaway[1]} Gewinner | Endete")

            await message.edit(embed=embed)

            if len(winner_list) > 1:
                string = f"Herzlichen Glückwunsch, {winners} haben {giveaway[3]} gewonnen\n> `{len(backupEntries)}` gültige Teilnehmer"
            else:
                string = f"Herzlichen Glückwunsch, {winners} hat {giveaway[3]} gewonnen\n> `{len(backupEntries)}` gültige Teilnehmer"

            await successEmbed(self, channel, string, color=host.color)

            delete(table="giveaways", where="guild_id message_id", values=[guild_id, message_id])            

def setup(bot):
    bot.add_cog(Giveaways(bot))