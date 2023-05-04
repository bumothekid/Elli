import random
import nextcord
import asyncio
import re
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time as time_, mktime
from datetime import datetime, timedelta
from .utils.embeds import infoEmbed, errorEmbed, successEmbed
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.database import delete, readAll, insert, readOne, update

languageStrings = {}
class Giveaways(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="giveaway", aliases=["gv"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _giveaway(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])[0]

        await infoEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayDescription", prefix))

    @_giveaway.command(name="create", aliases=["start"])
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def _create(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if len(readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])) >= 9:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayLimit"))

        questions = [
            getLocale(self.bot, languageStrings, guildLocale, "giveawayQuestionChannel", ctx.channel.mention),
            getLocale(self.bot, languageStrings, guildLocale, "giveawayQuestionTime"),
            getLocale(self.bot, languageStrings, guildLocale, "giveawayQuestionPrize"),
            getLocale(self.bot, languageStrings, guildLocale, "giveawayQuestionWinner")
        ]

        anwsers = {}
        message = None
        trys = 0

        for i, question in enumerate(questions):
            embed = nextcord.Embed(
                    description=question,
                    color=nextcord.Color.blurple()
            )

            if message is None:
                message = await ctx.reply(embed=embed)
            else:
                await message.edit(embed=embed)

            while True:
                try:
                    userAnwser = await self.bot.wait_for("message", timeout=120, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                except asyncio.TimeoutError:
                    return await errorEmbed(self, ctx, "giveawayTimeout")
                
                if trys == 3:
                    return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayFails"))

                match i:
                    case 0:
                        await userAnwser.delete()
                        try:
                            channelid = re.findall(r"[0-9]+", userAnwser.content)[0]
                            anwser = self.bot.get_channel(int(channelid))

                            if anwser == None:
                                embed = nextcord.Embed(
                                    description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayChannelNotFound"),
                                    color=nextcord.Color.blurple()
                                )

                                await message.edit(embed=embed)
                                trys += 1
                                continue

                            trys = 0
                        except:
                            embed = nextcord.Embed(
                                description=question + "\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayChannelNotFound"),
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            trys += 1
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
                                description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayTimeInvalid"),
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            trys += 1
                            continue
                        for key, value in matches:
                            try:
                                anwser += timeDict[value] * float(key)
                            except KeyError:
                                embed = nextcord.Embed(
                                    description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayTimeValueInvalid", value),
                                    color=nextcord.Color.blurple()
                                )

                                await message.edit(embed=embed)
                                trys += 1
                                continue
                            except ValueError:
                                embed = nextcord.Embed(
                                    description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayTimeKeyInvalid", key),
                                    color=nextcord.Color.blurple()
                                )

                                await message.edit(embed=embed)
                                trys += 1
                                continue
                        
                        if round(anwser) < 120 or round(anwser) > 1555200:
                            embed = nextcord.Embed(
                                description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayTimeBetween"),
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            trys += 1
                            continue

                        trys = 0
                        anwser = round(anwser)
                    case 2:
                        await userAnwser.delete()

                        if userAnwser.content == '':
                            anwser = getLocale(self.bot, languageStrings, guildLocale, "giveawayNoPrize")
                        elif len(userAnwser.content) > 150:
                            embed = nextcord.Embed(
                                description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayCharLimit"),
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            trys += 1
                            continue
                        else:
                            trys = 0
                            anwser = userAnwser.content
                    case 3:
                        await userAnwser.delete()

                        if not userAnwser.content.isdigit():
                            embed = nextcord.Embed(
                                description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayWholeNumber"),
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            trys += 1
                            continue

                        elif int(userAnwser.content) >= 100 or int(userAnwser.content) <= 0:
                            embed = nextcord.Embed(
                                description=question + f"\n\n> " + getLocale(self.bot, languageStrings, guildLocale, "giveawayWinnerLimit"),
                                color=nextcord.Color.blurple()
                            )

                            await message.edit(embed=embed)
                            trys += 1
                            continue
                        
                        trys = 0
                        anwser = int(userAnwser.content)
                        await message.delete()


                            
                anwsers[i] = anwser
                break
            
        now = datetime.now()
        unix = int(mktime((now + timedelta(seconds=anwsers[1])).timetuple()))

        embed = nextcord.Embed(
            title=anwsers[2],
            description=getLocale(self.bot, languageStrings, guildLocale, "giveaway", unix, ctx.author.mention),
            color=ctx.author.color,
            timestamp=now + timedelta(seconds=anwsers[1])
        )
        embed.set_footer(text=getLocale(self.bot, languageStrings, guildLocale, "giveawayFooter", anwsers[3]))

        message = await anwsers[0].send(embed=embed)

        insert(table="giveaways", columns="guild_id, channel_id, message_id, start, duration, prize, winner, hoster_id", values=[ctx.guild.id, anwsers[0].id, message.id, time_(), anwsers[1], anwsers[2], anwsers[3], ctx.author.id])

        emote = self.bot.get_emoji(1087437215648456794)

        await message.add_reaction(emote)

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawaySuccess", ctx.guild.id, anwsers[0].id, message.id, anwsers[2], unix))

    @_giveaway.command(name="quick", aliases=["q", "quickstart"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _quick(self, ctx, channel: nextcord.TextChannel, minutes, winner, *, prize):
        guildLocale = getGuildLanguage(ctx.guild.id)
        if len(readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])) >= 9:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayLimit"))

        if len(prize) > 150:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayCharLimit"))

        if not minutes.isdigit():
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayTimeInMinutes"))
        
        elif int(minutes) < 2 or int(minutes) > 1555200:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayTimeBetween"))
        
        if not winner.isdigit():
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayWholeNumber"))

        elif int(winner) >= 100:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayWinnerLimit"))

        if prize == "":
            prize = getLocale(self.bot, languageStrings, guildLocale, "giveawayNoPrize")

        seconds = int(minutes) * 60
        now = datetime.now()
        unix = int(mktime((now + timedelta(seconds=seconds)).timetuple()))

        embed = nextcord.Embed(
            title=prize,
            description=getLocale(self.bot, languageStrings, guildLocale, "giveaway", unix, ctx.author.mention),
            color=ctx.author.color,
            timestamp=now + timedelta(seconds=seconds)
        )
        embed.set_footer(text=getLocale(self.bot, languageStrings, guildLocale, "giveawayFooter", winner))

        message = await channel.send(embed=embed)

        insert(table="giveaways", columns="guild_id, channel_id, message_id, start, duration, prize, winner, hoster_id", values=[ctx.guild.id, channel.id, message.id, time_(), seconds, prize, winner, ctx.author.id])

        emote = self.bot.get_emoji(1087437215648456794)

        await message.add_reaction(emote)

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawaySuccess", ctx.guild.id, channel.id, message.id, prize, winner, unix))

    @_giveaway.command(name="drop")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _drop(self, ctx, channel: nextcord.TextChannel, *, prize):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if len(readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])) >= 9:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayLimit"))

        if len(prize) > 150:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayCharLimit"))

        embed = nextcord.Embed(
            title=prize,
            description=getLocale(self.bot, languageStrings, guildLocale, "giveawayDrop"),
            color=ctx.author.color,
            timestamp=datetime.now()
        )
        embed.set_footer(text=getLocale(self.bot, languageStrings, guildLocale, "giveawayDrop", ctx.author.name))

        message = await channel.send(embed=embed)

        emote = self.bot.get_emoji(1087437215648456794)

        await message.add_reaction(emote)

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: u.bot == False and r.message.id == message.id and r.emoji == emote, timeout=300)
        except asyncio.TimeoutError:
            return await errorEmbed(self, channel, getLocale(self.bot, languageStrings, guildLocale, "giveawayDropTimeout"))
        
        embed = nextcord.Embed(
            title=prize,
            description=getLocale(self.bot, languageStrings, guildLocale, "giveawayDropEnd", user.mention, prize),
            color=ctx.author.color
        )

        await message.edit(embed=embed)

        await successEmbed(self,
                            channel,
                            getLocale(self.bot, languageStrings, guildLocale, "giveawayDropSuccess", user.mention, prize, sum(member.status!=nextcord.Status.offline and not member.bot for member in ctx.guild.members)),
                            color=ctx.author.color
        )
        

    @_giveaway.command(name="end", aliases=["stop"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _end(self, ctx, channel: nextcord.TextChannel, message):
        guildLocale = getGuildLanguage(ctx.guild.id)
        try:
            message = await channel.fetch_message(message)
        except:
            raise commands.MessageNotFound(argument=message)

        giveaway = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[ctx.guild.id, message.id])

        if giveaway is None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayNotFound"))

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayEnd", ctx.guild.id, channel.id, message.id, giveaway[6]))
        
        update(table="giveaways", columns="duration", where="guild_id message_id", values=["0", ctx.guild.id, message.id])

    @_giveaway.command(name="reroll")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _rerroll(self, ctx, channel: nextcord.TextChannel, message, winners):
        guildLocale = getGuildLanguage(ctx.guild.id)
        try:
            message = await channel.fetch_message(message)
        except:
            raise commands.MessageNotFound(argument=message)

        if not winners.isdigit():
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayWholeNumber"))

        giveaway = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[ctx.guild.id, message.id])

        if giveaway is not None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayStillRunning"))

        emote = self.bot.get_emoji(1087437215648456794)
        is_giveaway = any(reaction.emoji == emote for reaction in message.reactions)

        if not is_giveaway:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayNotFound"))

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
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayNoWinnerSmall"))

        winners = ', '.join(winner_list)

        if len(winner_list) > 1:
            string = getLocale(self.bot, languageStrings, guildLocale, "giveawayWinner", winners, message.embeds[0].title, len(backupEntries))
        else:
            string = getLocale(self.bot, languageStrings, guildLocale, "giveawayWinners", winners, message.embeds[0].title, len(backupEntries))

        embed = nextcord.Embed(
            description=string,
            color=ctx.author.color
        )
        await ctx.reply(embed=embed)

    
    @_giveaway.command(name="list", aliases=["show"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _list(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        giveaways = readAll(columns="*", table="giveaways", where="guild_id", values=[ctx.guild.id])

        if not giveaways:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayNoActive"))

        fields = []

        for giveaway in giveaways:
            giveaway_channel_link = f"[`📎`Link](https://discord.com/channels/{ctx.guild.id}/{giveaway[1]}/)"
            giveaway_message_link = f"[`📎`Link](https://discord.com/channels/{ctx.guild.id}/{giveaway[1]}/{giveaway[2]}/)"
            giveaway_price = giveaway[5]
            giveaway_winner = giveaway[6]
            giveaway_hoster = ctx.guild.get_member(int(giveaway[7]))

            start = datetime.fromtimestamp(giveaway[3])
            unix = int(mktime((start + timedelta(seconds=giveaway[4])).timetuple()))

            value = getLocale(self.bot, languageStrings, guildLocale, "giveawayField", giveaway_channel_link, giveaway_message_link, giveaway_hoster.mention, giveaway_winner, unix)
            fields.append({"name": f"**{giveaway_price}**", "value": value, "inline": True})
        
        
        await infoEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "giveawayList"), fields=fields)

    @Cog.listener()
    async def on_ready(self):
        if giveaways := readAll(columns="guild_id, message_id", table="giveaways"):
            for giveaway in giveaways:
                asyncio.ensure_future(self.giveawayTimer(guild_id=giveaway[0], message_id=giveaway[1]))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emote = self.bot.get_emoji(1087437215648456794)
        if payload.emoji == emote:
            guild = self.bot.get_guild(payload.guild_id)
            if payload.member == guild.me:
                await asyncio.sleep(5)
                exists = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[payload.guild_id, payload.message_id])
                if exists is not None:
                    asyncio.ensure_future(self.giveawayTimer(guild_id=payload.guild_id, message_id=payload.message_id))

    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild:
            return
        
        exists = readOne(columns="*", table="giveaways", where="guild_id message_id", values=[message.guild.id, message.id])

        if exists is not None:
            delete(table="giveaways", where="guild_id message_id", values=[message.guild.id, message.id])

    @Cog.listener()
    async def on_guild_remove(self, guild):
        if giveaways := readAll(columns="message_id", table="giveaways", where="guild_id", values=[guild.id]):
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
            guildLocale = getGuildLanguage(guild_id)
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
                    description=getLocale(self.bot, languageStrings, guildLocale, "giveawayNoWinnerBig", unix, host.mention),
                    color=host.color,
                    timestamp=datetime.fromtimestamp(giveaway[4]) + timedelta(seconds=giveaway[5])
                )

                embed.set_footer(text=getLocale(self.bot, languageStrings, guildLocale, "giveawayEndFooter", giveaway[1]))

                await message.edit(embed=embed)

                await errorEmbed(self, channel, getLocale(self.bot, languageStrings, guildLocale, "giveawayNoWinnerSmall"))

                return delete(table="giveaways", where="guild_id message_id", values=[guild_id, message_id])

            winners = ', '.join(winner_list)

            embed = nextcord.Embed(
                title=giveaway[3],
                description=getLocale(self.bot, languageStrings, guildLocale, "giveawayEnded", winners, unix, host.mention),
                color=host.color,
                timestamp=datetime.fromtimestamp(giveaway[4]) + timedelta(seconds=giveaway[5])
            )
            embed.set_footer(text=getLocale(self.bot, languageStrings, guildLocale, "giveawayEndFooter", giveaway[1]))

            await message.edit(embed=embed)

            if len(winner_list) > 1:
                string = getLocale(self.bot, languageStrings, guildLocale, "giveawayWinners", winners, giveaway[3], len(backupEntries))
            else:
                string = getLocale(self.bot, languageStrings, guildLocale, "giveawayWinner", winners, giveaway[3], len(backupEntries))

            await successEmbed(self, channel, string, color=host.color)

            delete(table="giveaways", where="guild_id message_id", values=[guild_id, message_id])            

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("giveaway")
    bot.add_cog(Giveaways(bot))