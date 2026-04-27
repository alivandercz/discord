import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CODES_MESSAGE = os.getenv(
    "CODES_MESSAGE",
    "Current secret codes:\n\n"
    "• `KOD123` — 500 mincí\n"
    "• `BONUS456` — prémiový předmět\n"
    "• `VITEJ789` — uvítací balíček\n\n"
    "Kódy jsou časově omezené, uplatni je co nejdříve!",
)


class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Slash příkazy synchronizovány.")

    async def on_ready(self):
        print(f"Přihlášen jako {self.user} (ID: {self.user.id})")


bot = Bot()


@bot.tree.command(name="codes", description="Získej aktuální kódy do soukromé zprávy")
async def codes(interaction: discord.Interaction):
    try:
        await interaction.user.send(CODES_MESSAGE)
        await interaction.response.send_message(
            "Codes have been just send to your DM!", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Nepodařilo se ti odeslat DM. Zkontroluj, zda máš povolené soukromé zprávy od členů serveru.",
            ephemeral=True,
        )


bot.run(TOKEN)
