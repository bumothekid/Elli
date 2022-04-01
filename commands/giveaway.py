import random
import sqlite3
import nextcord
import asyncio
import re
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time as time_, mktime
from datetime import datetime, timedelta

class giveaways(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="giveaway", aliases=["gv"], invoke_without_command=True)
    async def _giveaway(self, ctx):
        embed = nextcord.Embed(
            description="**<a:giveaway:958492679749140510> Giveaway Commands**\n\n> `!giveaway create`\n> `!giveaway quick <#channel> <winner> <time>`\n> `!giveaway drop <#channel> <zeit in minuten> <winner> <preis>`\n> `!giveaway end <#channel> <messageid>`\n> `!giveaway reroll <#channel> <messageid> <winner>`\n> `!giveaway list`",
            color=nextcord.Color.blurple()
        )
        await ctx.reply(embed=embed)

    @_giveaway.command(name="create", aliases=["start"])
    @commands.has_permissions(manage_guild=True)
    async def _create(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM giveaways WHERE guild_id = '{ctx.guild.id}'")
        giveaways = c.fetchall()

        if len(giveaways) >= 9:
            embed = nextcord.Embed(
                description="Du kannst nur **9** Giveaways gleichzeitig starten",
                color=nextcord.Color.dark_red()
            )

            await ctx.reply(embed=embed)
            return db.close()

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
                def check(m):
                    return lambda m: m.author == ctx.author and m.channel == ctx.channel

                try:
                    userAnwser = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    if message is not None:
                        await message.delete()
                    embed = nextcord.Embed(
                        description="Du hast mehr als 2 Minuten gebraucht um zu antworten\n\nDer Giveaway startvorgang wurde abgebrochen",
                        color=nextcord.Color.dark_red()
                    )

                    return await ctx.reply(embed=embed)

                match i:
                    case 0:
                        await userAnwser.delete()
                        try:
                            channelid = re.findall(r"[0-9]+", userAnwser.content)[0]
                            anwser = self.bot.get_channel(int(channelid))
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

                        elif int(userAnwser.content) >= 100:
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
            description=f"Reagiere mit <a:giveaway:958492679749140510> um Teilzunehmen\n\n> Endet: <t:{unix}:R> (<t:{unix}:f>)\n> Host: {ctx.author.mention}",
            color=ctx.author.color,
            timestamp=now + timedelta(seconds=anwsers[1])
        )
        embed.set_footer(text=f"{anwsers[3]} Gewinner | Endet")

        message = await anwsers[0].send(embed=embed)

        c.execute("INSERT INTO giveaways(guild_id, channel_id, message_id, start, duration, prize, winner, hoster_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", [ctx.guild.id, anwsers[0].id, message.id, time_(), anwsers[1], anwsers[2], anwsers[3], ctx.author.id])
        db.commit()
        c.close()
        db.close()

        emote = self.bot.get_emoji(958492679749140510)

        await message.add_reaction(emote)

        embed = nextcord.Embed(
            description=f"**<a:giveaway:958492679749140510> Giveaway gestartet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{anwsers[0].id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{anwsers[0].id}/{message.id}/)\n> **Gewinner:** {anwsers[3]}\n> **Bis:** <t:{unix}:f>",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_giveaway.command(name="quick", aliases=["q", "quickstart"])
    @commands.has_permissions(manage_guild=True)
    async def _quick(self, ctx, channel: nextcord.TextChannel, minutes, winner, *, prize):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM giveaways WHERE guild_id = '{ctx.guild.id}'")
        giveaways = c.fetchall()

        if len(giveaways) >= 9:
            embed = nextcord.Embed(
                description="Du kannst nur **9** Giveaways gleichzeitig starten",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        if len(prize) > 150:
            embed = nextcord.Embed(
                description="Der Preis darf aus maximal 150 Zeichen bestehen",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        if not minutes.isdigit():
            embed = nextcord.Embed(
                description="Die Zeitangabe muss in minuten angegeben sein",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)
        
        if not winner.isdigit():
            embed = nextcord.Embed(
                description="Die Anzahl an Gewinnern muss eine ganze Zahl sein",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)
        
        elif int(winner) >= 100:
            embed = nextcord.Embed(
                description="Die anzahl an Gewinnern darf nicht größer als **100** sein",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        if prize == "":
            embed = nextcord.Embed(
                description="Du musst einen Gewinn angeben",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        seconds = int(minutes) * 60
        now = datetime.now()
        unix = int(mktime((now + timedelta(seconds=seconds)).timetuple()))
        embed = nextcord.Embed(
            title=prize,
            description=f"Reagiere mit <a:giveaway:958492679749140510> um Teilzunehmen\n\n> Endet: <t:{unix}:R> (<t:{unix}:f>)\n> Host: {ctx.author.mention}",
            color=ctx.author.color,
            timestamp=now + timedelta(seconds=seconds)
        )
        embed.set_footer(text=f"{winner} Gewinner | Endet")

        message = await channel.send(embed=embed)

        c.execute("INSERT INTO giveaways(guild_id, channel_id, message_id, start, duration, prize, winner, hoster_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", [ctx.guild.id, channel.id, message.id, time_(), seconds, prize, winner, ctx.author.id])
        db.commit()
        c.close()
        db.close()

        emote = self.bot.get_emoji(958492679749140510)

        await message.add_reaction(emote)

        embed = nextcord.Embed(
            description=f"**<a:giveaway:958492679749140510> Giveaway gestartet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}/)\n> **Gewinner:** {winner}\n> **Bis:** <t:{unix}:f>",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)
        

    @_giveaway.command(name="end", aliases=["stop"])
    @commands.has_permissions(manage_guild=True)
    async def _end(self, ctx, channel: nextcord.TextChannel, message):
        try:
            message = await channel.fetch_message(message)
        except:
            raise commands.MessageNotFound(argument=message)

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM giveaways WHERE guild_id = '{ctx.guild.id}' AND message_id = '{message.id}'")
        giveaway = c.fetchone()

        if giveaway is None:
            embed = nextcord.Embed(
                description="Es wurde kein aktives Gewinnspiel mit dieser nachrichten ID gefunden",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        embed = nextcord.Embed(
            description="**<a:giveaway:958492679749140510> Das Giveaway wird in kürze beendet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{anwsers[0].id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{anwsers[0].id}/{message.id}/)\n> **Gewinner:** {anwsers[3]}\n> **Bis:** <t:{unix}:f>",
        )

        await ctx.reply(embed=embed)
        
        c.execute(f"UPDATE giveaways SET duration = '0' WHERE guild_id = '{ctx.guild.id}' AND message_id = '{message.id}'")
        db.commit()

    @_giveaway.command(name="reroll")
    @commands.has_permissions(manage_guild=True)
    async def _rerroll(self, ctx, channel: nextcord.TextChannel, message, winners):
        try:
            message = await channel.fetch_message(message)
        except:
            raise commands.MessageNotFound(argument=message)

        if not winners.isdigit():
            embed = nextcord.Embed(
                description="**Die anzahl an gewinnern muss eine ganze Zahl sein**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM giveaways WHERE guild_id = '{ctx.guild.id}' AND message_id = '{message.id}'")
        giveaway = c.fetchone()

        if giveaway is not None:
            embed = nextcord.Embed(
                description="**Das Giveaway ist noch am laufen**\n**Du kannst mit `!giveaway end <messageid>` das Gewinnspiel beenden**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        emote = self.bot.get_emoji(958492679749140510)
        is_giveaway = any(reaction.emoji == emote for reaction in message.reactions)

        if not is_giveaway:
            embed = nextcord.Embed(
                description="**Diese Nachricht ist kein Giveaway**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

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
            embed = nextcord.Embed(
                description="Es konnte kein Gewinner entschieden werden",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

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
    async def _list(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM giveaways WHERE guild_id = '{ctx.guild.id}'")
        giveaways = c.fetchall()

        if not giveaways:
            embed = nextcord.Embed(
                description="Es wurden keine aktiven Giveaways gefunden",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        embed = nextcord.Embed(
            description="**<a:giveaway:958492679749140510> Aktive Giveaways**",
            color=nextcord.Color.blurple()
        )

        for giveaway in giveaways:
            giveaway_channel_link = f"[`📎`Link](https://discord.com/channels/{ctx.guild.id}/{giveaway[1]}/)"
            giveaway_message_link = f"[`📎`Link](https://discord.com/channels/{ctx.guild.id}/{giveaway[1]}/{giveaway[2]}/)"
            giveaway_price = giveaway[5]
            giveaway_winner = giveaway[6]
            giveaway_hoster = ctx.guild.get_member(int(giveaway[7]))

            start = datetime.fromtimestamp(giveaway[3])
            unix = int(mktime((start + timedelta(seconds=giveaway[4])).timetuple()))

            embed.add_field(name=f"**{giveaway_price}**\n\n", value=f"> **Channel:** {giveaway_channel_link}\n> **Nachricht:** {giveaway_message_link}\n> **Hoster:** {giveaway_hoster.mention}\n> **Gewinner:** {giveaway_winner}\n> **Bis:** <t:{unix}:f>", inline=True)

        await ctx.reply(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        for i in self.bot.guilds:
            c.execute(f"SELECT message_id, channel_id FROM giveaways WHERE guild_id='{i.id}'")

            if running := c.fetchall():
                db.close()
                for giveaway in running:
                    await self.giveawayTimer(guild_id=i.id, message_id=giveaway[0])

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emote = self.bot.get_emoji(958492679749140510)
        if payload.emoji == emote:
            guild = self.bot.get_guild(payload.guild_id)
            if payload.member == guild.me:
                await asyncio.sleep(5)
                db = sqlite3.connect("database.db")
                c = db.cursor()
                c.execute(f"SELECT * FROM giveaways WHERE guild_id = '{payload.guild_id}' AND message_id = '{payload.message_id}'")
                exists = c.fetchone()
                if exists is not None:
                    await self.giveawayTimer(guild_id=payload.guild_id, message_id=payload.message_id)

    @Cog.listener()
    async def on_message_delete(self, message):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM giveaways WHERE guild_id='{message.guild.id}' AND message_id = '{message.id}'")
        exists = c.fetchone()

        if exists is not None:
            c.execute(f"DELETE FROM giveaways WHERE guild_id='{message.guild.id}' AND message_id='{message.id}'")
            db.commit()

    @Cog.listener()
    async def on_guild_remove(self, guild):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT message_id FROM giveaways WHERE guild_id='{guild.id}'")
        
        if giveaways := c.fetchall():
            for giveaway in giveaways:
                c.execute(f"DELETE FROM giveaways WHERE guild_id='{guild.id}' AND message_id = '{giveaway[0]}'")
            db.commit()

    async def giveawayTimer(self, guild_id, message_id):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        while True:
            now = time_()
            c.execute(f"SELECT start, duration FROM giveaways WHERE guild_id='{guild_id}' AND message_id='{message_id}'")
            time = c.fetchone()
            if time is None:
                return
            if round(now - time[0]) >= time[1]:
                break
            await asyncio.sleep(30)

        c.execute(f"SELECT channel_id, winner, hoster_id, prize, start, duration FROM giveaways WHERE guild_id='{guild_id}' AND message_id='{message_id}'")
        giveaway = c.fetchone()

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

                embed = nextcord.Embed(
                    description="Es konnte kein Gewinner entschieden werden",
                    color=nextcord.Color.dark_red()
                )

                await channel.send(embed=embed)

                c.execute(f"DELETE FROM giveaways WHERE guild_id='{guild_id}' AND message_id='{message_id}'")
                db.commit()
                return

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
            embed = nextcord.Embed(
                description=string,
                color=host.color
            )
            await channel.send(embed=embed)

            c.execute(f"DELETE FROM giveaways WHERE guild_id='{guild_id}' AND message_id='{message_id}'")
            db.commit()

            

def setup(bot):
    bot.add_cog(giveaways(bot))