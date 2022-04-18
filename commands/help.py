import nextcord
from nextcord.ext import commands

cache = []

class ClassHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def help(self, ctx):
        embed = nextcord.Embed(
            color=0x6850be)

        embed.add_field(name="──────────────────", value="_ _", inline=False)
        embed.add_field(name=":dart: General", value="```help general```")
        embed.add_field(name=":bulb: Useful", value="```help useful```")
        embed.add_field(name=":tada: Comedy", value="```help comedy```")
        embed.add_field(name=":alembic: Image", value="```help image```")
        embed.add_field(name=":satellite: Reddit", value="```help reddit```")
        embed.add_field(name=":envelope_with_arrow: Invite", value="```help invite```")
        embed.add_field(name=":performing_arts: Roles", value="```help roles```")
        embed.add_field(name=":gift: Giveaway", value="```help giveaway```")
        embed.add_field(name=":loud_sound: Temp", value="```help temp```")
        embed.add_field(name=":crossed_swords: Moderation", value="```help moderation```")
        embed.add_field(name=":shield: Captcha", value="```help captcha```")
        embed.add_field(name=":gear: Config", value="```help config```")
        embed.add_field(name="──────────────────",
                        value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                              f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                              f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                        inline=False)

        embed.set_author(name="Riku's Commands | 🏠 Home",
                         icon_url=self.bot.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        msg = await ctx.reply(embed=embed, mention_author=False, view=HelpButtonView())
        cache.append(f"{msg.id}|{ctx.author.id}")

class HelpButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.add_item(HelpButton())

class HelpButton(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Home", emoji="🏠"),
            nextcord.SelectOption(label="General", emoji="🎯"),
            nextcord.SelectOption(label="Useful", emoji="💡"),
            nextcord.SelectOption(label="Comedy", emoji="🎉"),
            nextcord.SelectOption(label="Image", emoji="⚗️"),
            nextcord.SelectOption(label="Reddit", emoji="📡"),
            nextcord.SelectOption(label="Invite", emoji="📨"),
            nextcord.SelectOption(label="Roles", emoji="🎭"),
            nextcord.SelectOption(label="Giveaway", emoji="🎁"),
            nextcord.SelectOption(label="Temp", emoji="🔊"),
            nextcord.SelectOption(label="Moderation", emoji="⚔️"),
            nextcord.SelectOption(label="Captcha", emoji="🛡"),
            nextcord.SelectOption(label="Config", emoji="⚙️")
        ]
        super().__init__(placeholder="Select Help-Category", options=options)

    async def callback(self, interaction):
        if f"{interaction.message.id}|{interaction.user.id}" in cache:
            if self.values[0] == "Home":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":dart: General", value="```help general```")
                embed.add_field(name=":bulb: Useful", value="```help useful```")
                embed.add_field(name=":tada: Comedy", value="```help comedy```")
                embed.add_field(name=":alembic: Image", value="```help image```")
                embed.add_field(name=":satellite: Reddit", value="```help reddit```")
                embed.add_field(name=":envelope_with_arrow: Invite", value="```help invite```")
                embed.add_field(name=":performing_arts: Roles", value="```help roles```")
                embed.add_field(name=":gift: Giveaway", value="```help giveaway```")
                embed.add_field(name=":loud_sound: Temp", value="```help temp```")
                embed.add_field(name=":crossed_swords: Moderation", value="```help moderation```")
                embed.add_field(name=":shield: Captcha", value="```help captcha```")
                embed.add_field(name=":gear: Config", value="```help config```")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🏠 Home",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "General":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":dart: General",
                                value="> `ping` - Shows the bot's latency\n"
                                      "> `invite` - Shows the bot's invite link\n"
                                      "> `stats` - Shows the bot's statistics")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🎯 General",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Useful":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 1",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Comedy":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 2",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Image":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 3",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Reddit":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 4",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Invite":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 5",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Roles":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 6",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Giveaway":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 7",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Temp":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 8",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Moderation":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 9",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Captcha":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 10",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

            if self.values[0] == "Config":
                embed = nextcord.Embed(
                    color=0x6850be)

                embed.add_field(name="──────────────────", value="_ _", inline=False)
                embed.add_field(name=":sheep: Platzhalter Nr. 11",
                                value="> `platzhalter` - Platzhalter")
                embed.add_field(name="──────────────────",
                                value=f"[`👾` Invite](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📠` Support](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - "
                                      f"[`📤` Vote](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                                inline=False)

                embed.set_author(name="Riku's Commands | 🐑 Platzhalter",
                                 icon_url=interaction.message.author.avatar.url)
                embed.set_thumbnail(url=interaction.message.author.avatar.url)

                await interaction.message.edit(embed=embed)

def setup(bot):
    bot.add_cog(ClassHelp(bot))
