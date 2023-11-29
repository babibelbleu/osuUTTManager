from pprint import pprint
from dotenv import load_dotenv
import os
from Client import Client

import gspread

load_dotenv()

CLIENT_TOKEN = os.getenv("TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT")

client = Client(CLIENT_TOKEN)


def main():
    sa = gspread.service_account(filename='service_account.json')
    sheet = sa.open("UTT scores")
    worksheet = sheet.worksheet("Data")

    games = client.get_multiplayer_info(111463775)["games"]

    for game in games:
        scores = game["scores"]

        beatmap_id = game["beatmap_id"]
        beatmap = client.get_beatmap(beatmap_id)[0]
        beatmap_name = beatmap["title"]
        beatmap_difficulty_name = beatmap["version"]

        print(f"La map {beatmap_name} en {beatmap_difficulty_name} a été jouée. ({beatmap_id})")
        print("------------------SCORES------------------")

        for score in scores:
            user = client.get_user(score["user_id"], 3)[0]["username"]
            score_done = score["score"]
            print(f"{user} : {score_done}")


def test():
    pprint(client.get_beatmap(4384215))


# test()
main()
