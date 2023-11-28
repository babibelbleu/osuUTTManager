from pprint import pprint
from dotenv import load_dotenv
import os
from Client import Client


load_dotenv()

CLIENT_TOKEN = os.getenv("TOKEN")

client = Client(CLIENT_TOKEN)

print(help(client))
