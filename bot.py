import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CODES_FILE = "codes.txt"
DEFAULT_MESSAGE = "Thank you, here's the secret code 1111"

CODES_CHANNEL_ID = 1498405553838489763
TAG_MEMBER_ROLE_ID = 1498406704738599013
TAG_GUIDE_IMAGE = "tag_guide.png"


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
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash příkazy synchronizovány.")

    async def on_ready(self):
        print(f"Přihlášen jako {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        print(f"Zpráva: '{message.content}' v kanálu {message.channel.id} od {message.author}")

        if message.channel.id != CODES_CHANNEL_ID:
            return

        if message.content.strip().lower() != "done":
            return

        member = message.author
        guild = message.guild

        has_tag = (
            hasattr(member, "clan")
            and member.clan is not None
            and member.clan.guild_id == guild.id
        )

        tag_role = guild.get_role(TAG_MEMBER_ROLE_ID)

        if has_tag:
            if tag_role:
                await member.add_roles(tag_role)
            try:
                await member.send(load_codes())
            except discord.Forbidden:
                pass
            await message.channel.send(
                f"✅ {member.mention} Congratulations! Check your DMs for the secret code.",
                delete_after=15,
            )
        else:
            warning = (
                f"⚠️ Hey {member.mention}, you MUST have our tag applied to be able to get the secret codes. "
                f'Then type "Done" again.'
            )
            if os.path.exists(TAG_GUIDE_IMAGE):
                await message.channel.send(
                    warning, file=discord.File(TAG_GUIDE_IMAGE)
                )
            else:
                await message.channel.send(warning)

        try:
            await message.delete()
        except discord.Forbidden:
            pass


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
