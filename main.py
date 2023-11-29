from pprint import pprint
from dotenv import load_dotenv
import os

from gspread import Worksheet

from Client import Client

import gspread

load_dotenv()

CLIENT_TOKEN = os.getenv("OSU_TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT")

client = Client(CLIENT_TOKEN)


def main():
    sa = gspread.service_account(filename='service_account.json')
    sheet = sa.open("UTT scores")
    worksheet = sheet.worksheet("Data")

    update_sheet_with_game_id(111463775, worksheet)


def update_sheet_with_game_id(game_id: int, worksheet: Worksheet):
    games = client.get_multiplayer_info(game_id)["games"]

    # [
    #   {
    #       id: xxxxx    // id de la beatmap jouée
    #       stage : LN1
    #       player1 : 0
    #       player2 : 0
    #       ...
    #   },
    #   ...
    # ]
    rows: list = worksheet.get_all_records()

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
            update_score_in_sheet(user, beatmap_id, worksheet, score_done, rows)


def update_score_in_sheet(player: str, map_id: str, worksheet: Worksheet, score: int, rows: list) -> bool:

    indexCol = 0
    indexRow = 1

    for row in rows:
        indexRow += 1
        if str(row["id"]).casefold() == map_id.casefold():
            for key in row.keys():
                indexCol += 1
                if str(key).casefold() == player.casefold():
                    if int(row[key]) < int(score):
                        print("Le score réalisé est supérieur à celui de la sheet !")
                        worksheet.update_cell(indexRow, indexCol, score)
                    return True


def test():
    pprint(client.get_beatmap(4384215))


# test()
main()
