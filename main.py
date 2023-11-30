from pprint import pprint
from dotenv import load_dotenv
import os

from gspread import Worksheet

from Client import Client

import gspread
from gspread import Cell

import discord
from discord import app_commands

load_dotenv()

CLIENT_TOKEN = os.getenv("OSU_TOKEN")
DISCORD_BOT_TOKEN = os.getenv("BOT_TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT")

DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

client = Client(CLIENT_TOKEN)

sa = gspread.service_account(filename='service_account.json')
sheet = sa.open("UTT scores")
worksheet = sheet.worksheet("Data")


@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=DISCORD_GUILD_ID))
    print("Ready!")


@tree.command(
    name="sync",
    description="Sync the commands if there's a bug",
    guild=discord.Object(id=DISCORD_GUILD_ID)
)
async def sync(interaction: discord.Interaction):
    await tree.sync(guild=discord.Object(id=DISCORD_GUILD_ID))
    await interaction.response.send_message("Les commandes ont été synchronisées.", ephemeral=True)


@tree.command(
    name="add_match",
    description="Adds scores of the osu! match with mp link provided into the sheet",
    guild=discord.Object(id=DISCORD_GUILD_ID)
)
@app_commands.describe(mp_link="The multiplayer link of the match")
async def add_match(interaction: discord.Interaction, mp_link: str):
    match_id = get_mp_id(mp_link)
    await interaction.response.send_message("Le match est en train d'être ajouté...", ephemeral=True)
    update_sheet_with_game_id(int(match_id))
    await interaction.edit_original_response(content="Le match a bien été pris en compte !")


@tree.command(
    name="show_stats",
    description="Shows stats about a specified osu! match",
    guild=discord.Object(id=DISCORD_GUILD_ID)
)
@app_commands.describe(mp_link="The multiplayer link of the match")
async def show_stats(interaction: discord.Interaction, mp_link: str):
    match_id = get_mp_id(mp_link)
    await interaction.response.send_message("Récupération des statistiques...", ephemeral=True)
    embed = show_stats_in_ebeed(match_id)
    await interaction.edit_original_response(embed=embed)


def update_sheet_with_game_id(game_id: int):
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

    cells_to_update = []

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
            row, col = update_score_in_sheet(user, beatmap_id, score_done, rows)
            if row == -1 or col == -1:
                continue
            cells_to_update.append(Cell(row=row, col=col, value=score_done))

    print(cells_to_update)
    worksheet.update_cells(cells_to_update)


def update_score_in_sheet(player: str, map_id: str, score: int, rows: list):
    index_col = 0
    index_row = 1

    for row in rows:
        index_row += 1
        if str(row["id"]).casefold() == map_id.casefold():
            for key in row.keys():
                index_col += 1
                if str(key).casefold() == player.casefold():
                    if row[key] == '':
                        row[key] = 0
                    if int(row[key]) < int(score):
                        print("Le score réalisé est supérieur à celui de la sheet !")
                        row[key] = score
                        return index_row, index_col

    return -1, -1


def show_stats_in_ebeed(match_id: str):
    mp = client.get_multiplayer_info(match_id)
    mp_name = mp["match"]["name"]
    games = mp["games"]

    # {
    #   000111002: {
    #       player_1 : 1000,
    #       player_2 : 0000$
    #   }
    # }
    scores_to_compare = {}

    pprint(games)

    for game in games:
        scores = game["scores"]

        beatmap_id = game["beatmap_id"]
        beatmap = client.get_beatmap(beatmap_id)[0]
        beatmap_name = beatmap["title"]
        beatmap_difficulty_name = beatmap["version"]

        print(f"La map {beatmap_name} en {beatmap_difficulty_name} a été jouée. ({beatmap_id})")

        scores_to_compare[beatmap_id] = {}

        for score in scores:
            user_id = score["user_id"]
            score_done = score["score"]

            scores_to_compare[beatmap_id][user_id] = score_done

    pprint(scores_to_compare)

    string_to_add = ""
    description = ""

    player1_wins = 0
    player2_wins = 0
    usernames = []

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

    for beatmap in scores_to_compare.keys():
        print(f"beatmap")
        scores = list(scores_to_compare[beatmap].values())
        users = list(scores_to_compare[beatmap].keys())

        stage = ""

        for row in rows:
            if int(row["id"]) == int(beatmap):
                stage = row["Stage"]

        for user_id in users:
            usernames.append(client.get_user(user_id, 3)[0]["username"])

        wining_score = max(scores[0], scores[1])
        index_wining_score = scores.index(wining_score)

        if index_wining_score == 0:
            player1_wins += 1
        else:
            player2_wins += 1

        wining_user = usernames[index_wining_score]
        score_difference = int(scores[index_wining_score]) - int(scores[0 if index_wining_score == 1 else 1])

        string_to_add += f"**{stage}** - {wining_user} : {wining_score}. (+{score_difference}) \n"

    win = True if player1_wins > player2_wins else False
    description += (
        f'{"**" if win else ""}{usernames[0]}  {player1_wins}{"**" if win else ""}'
        f' - '
        f'{"**" if not win else ""}{player2_wins}  {usernames[1]}{"**" if not win else ""} \n\n'
    )
    description += string_to_add

    embed = discord.Embed(
        colour=discord.Colour.dark_teal(),
        title=f"*{mp_name}*",
        description=description
    )

    return embed


def get_mp_id(mp_link: str):
    STR_NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    match_id = mp_link[22:]  # Sous le format https://osu.ppy.sh/mp/111463775

    if match_id[0] not in STR_NUMBERS:
        match_id = mp_link[37:]

    return match_id


bot.run(DISCORD_BOT_TOKEN)
