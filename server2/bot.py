import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CODES_FILE = "codes.txt"
DEFAULT_MESSAGE = os.getenv("CODES_MESSAGE", "Here's your secret code!")
CODES_CHANNEL_ID = int(os.getenv("CODES_CHANNEL_ID", "0"))
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

        if message.channel.id != CODES_CHANNEL_ID:
            return

        if message.content.strip().lower() != "done":
            return

        guild = message.guild
        member = await guild.fetch_member(message.author.id)
        print(f"fetch_member OK: {member}")

        try:
            raw = await self.http.request(
                discord.http.Route("GET", "/guilds/{guild_id}/members/{user_id}",
                                   guild_id=guild.id, user_id=member.id)
            )
            user_data = raw.get("user", {})
            clan_data = user_data.get("clan") or user_data.get("primary_guild")
            has_tag = (
                clan_data is not None
                and clan_data.get("identity_enabled", False)
                and str(clan_data.get("identity_guild_id")) == str(guild.id)
            )
            print(f"has_tag: {has_tag}, clan_data: {clan_data}")
        except Exception as e:
            print(f"RAW fetch error: {e}")
            has_tag = False

        try:
            if has_tag:
                try:
                    await member.send(load_codes())
                except discord.Forbidden:
                    print("DM zakázáno")
                await message.channel.send(
                    f"{member.mention} Check your DM for the secret code.",
                    delete_after=15,
                )
            else:
                warning = (
                    f"⚠️ Hey {member.mention}, you MUST have our tag applied to be able to get the secret codes. "
                    f'Then type "Done" again.'
                )
                print(f"image exists: {os.path.exists(TAG_GUIDE_IMAGE)}")
                if os.path.exists(TAG_GUIDE_IMAGE):
                    await message.channel.send(
                        warning, file=discord.File(TAG_GUIDE_IMAGE)
                    )
                else:
                    await message.channel.send(warning)
        except Exception as e:
            print(f"Chyba při odesílání: {e}")

        try:
            await message.delete()
        except discord.Forbidden:
            pass


bot = Bot()


@bot.tree.command(name="codes", description="Get the secret codes in your DM")
async def codes(interaction: discord.Interaction):
    message = load_codes()
    try:
        await interaction.user.send(message)
        await interaction.response.send_message(
            "Codes have been just sent to your DM!", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Could not send DM. Please enable direct messages from server members.",
            ephemeral=True,
        )


@bot.tree.command(name="setcodes", description="Set the secret codes message (admin only)")
@app_commands.describe(message="Message that will be sent to users via DM")
async def setcodes(interaction: discord.Interaction, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You don't have permission to use this command.", ephemeral=True
        )
        return

    save_codes(message)
    await interaction.response.send_message(
        f"Codes message updated:\n\n{message}", ephemeral=True
    )


bot.run(TOKEN)
