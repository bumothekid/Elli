import nextcord

async def developerLogging(interaction, text) -> nextcord.Embed: 
        embed = nextcord.Embed(
            color=0x1494DE
        )

        embed.add_field(name="Sever", value=f"```ini\n{interaction.guild}```", inline=False)
        embed.add_field(name="Command", value=f"```ini\n{interaction.message.content}```", inline=False)
        embed.add_field(name="Aktion", value=f"```css\n{text}```", inline=False)

        return embed

async def errorLogging(text) -> nextcord.Embed:
        return nextcord.Embed(
            description=text,
            color=nextcord.Color.dark_red()
        )

async def criticalErrorLogging(interaction, text) -> nextcord.Embed:
    embed = nextcord.Embed(
        color=nextcord.Color.dark_red()
    )

    embed.add_field(name="Sever", value=f"```ini\n{interaction.guild}```", inline=False)
    embed.add_field(name="Command", value=f"```ini\n{interaction.message.content}```", inline=False)
    embed.add_field(name="Aktion", value=f"```python\n{text}```", inline=False)

    return embed