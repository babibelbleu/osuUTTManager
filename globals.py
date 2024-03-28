import os

from dotenv import load_dotenv

from Client import Client

load_dotenv()

CLIENT_TOKEN = os.getenv("OSU_TOKEN")
DISCORD_BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

client = Client(CLIENT_TOKEN)
