import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CODES_FILE = "codes.txt"
DEFAULT_MESSAGE = "Žádné kódy zatím nebyly nastaveny."


def load_codes() -> str:
    if os.path.exists(CODES_FILE):
        with open(CODES_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return DEFAULT_MESSAGE


def save_codes(message: str):
    with open(CODES_FILE, "w", encoding="utf-8") as f:
        f.write(message)


class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash příkazy synchronizovány.")

    async def on_ready(self):
        print(f"Přihlášen jako {self.user} (ID: {self.user.id})")


bot = Bot()


@bot.tree.command(name="codes", description="Získej aktuální kódy do soukromé zprávy")
async def codes(interaction: discord.Interaction):
    message = load_codes()
    try:
        await interaction.user.send(message)
        await interaction.response.send_message(
            "Kódy ti byly zaslány do soukromé zprávy!", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Nepodařilo se odeslat DM. Zkontroluj, zda máš povolené soukromé zprávy od členů serveru.",
            ephemeral=True,
        )


@bot.tree.command(name="setcodes", description="Nastav zprávu s kódy (pouze admin)")
@app_commands.describe(zprava="Zpráva která bude odeslána hráčům přes DM")
async def setcodes(interaction: discord.Interaction, zprava: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Nemáš oprávnění používat tento příkaz.", ephemeral=True
        )
        return

    save_codes(zprava)
    await interaction.response.send_message(
        f"Zpráva s kódy byla aktualizována:\n\n{zprava}", ephemeral=True
    )


bot.run(TOKEN)
