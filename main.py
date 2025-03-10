from pprint import pprint
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service

from ossapi import Ossapi
from webdriver_manager.chrome import ChromeDriverManager

import gspread
from gspread import Cell

import discord
from discord import app_commands

from bs4 import BeautifulSoup

from utils import remove_duplicate_elements_in_list, check_if_score_is_choke

from globals import DISCORD_GUILD_ID, DISCORD_BOT_TOKEN, client

ENVIRONMENT = os.getenv("ENVIRONMENT")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

sa = gspread.service_account(filename='service_account.json')
sheet = sa.open("UTT scores")
worksheet = sheet.worksheet("UTT2024")


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
    name="sync_stats",
    description="Synchronize the bot with recent stats added on the sheet",
    guild=discord.Object(id=DISCORD_GUILD_ID)
)
async def sync_stats(interaction: discord.Interaction):
    global rows
    rows = worksheet.get_all_records()
    await interaction.response.send_message("Synchronisation terminée !", ephemeral=True)


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
@app_commands.describe(how_many_warmups="Number of maps that have to be ignored")
async def show_stats(interaction: discord.Interaction, mp_link: str, how_many_warmups: int):
    match_id = get_mp_id(mp_link)
    await interaction.response.send_message("Récupération des statistiques...", ephemeral=True)
    embed = await show_stats_in_embeed(match_id, how_many_warmups)
    await interaction.edit_original_response(embed=embed)


@tree.command(
    name="get_seedings",
    description="retrieves gamers assembly seedings.",
    guild=discord.Object(id=DISCORD_GUILD_ID)
)
async def get_seedings(interaction: discord.Interaction):
    await interaction.response.send_message("Récupération des participants à la GA...", ephemeral=True)
    players = await get_players_from_ga()
    await interaction.edit_original_response(content="Récupération des statistiques des joueurs...")
    players_pp = await get_data_from_players(players)
    await interaction.edit_original_response(content="Attribution des seedings...")
    embed = await get_seedings_from_players(players_pp)
    await interaction.edit_original_response(content="", embed=embed)



@tree.command(
    name="check_player_scores",
    description="Checks a plyers's scores with their potential chokes on them",
    guild=discord.Object(id=DISCORD_GUILD_ID)
)
@app_commands.describe(player="The name of the player. Default is Babibelbleu")
@app_commands.describe(pool="If you want to retrieve scores from a specific pool.")
async def check_player_scores(interaction: discord.Interaction, player: str = "Babibelbleu", pool: str = None):
    await interaction.response.send_message("Récupération des scores...", ephemeral=True)
    embed = await show_individual_stats_from_player(player, pool)
    await interaction.edit_original_response(content="", embed=embed)


@tree.command(
    name="compare",
    description="Compare scores between two players",
    guild=discord.Object(id=DISCORD_GUILD_ID)
)
@app_commands.describe(player1="The name of the first player to compare scores")
@app_commands.describe(player2="The name of the second player to compare scores. Default is Babibelbleu")
async def compare(interaction: discord.Interaction, player1: str, player2: str = "Babibelbleu"):
    await interaction.response.send_message("Récupération des statistiques...", ephemeral=True)
    embed = await compare_stats_from_players(player1, player2)
    await interaction.edit_original_response(content="", embed=embed)


async def get_players_from_ga():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    browser = webdriver.Chrome(service=service, options=options)

    string_to_add = ""

    players = []
    try:
        browser.get("https://ga2024.gamers-assembly.net/tournois/osumania-4k-gamers-assembly-festival-edition-2024")
        timeout_in_seconds = 30
        WebDriverWait(browser, timeout_in_seconds).until(ec.presence_of_element_located((By.CLASS_NAME, 'table')))
        html = browser.page_source
        soup = BeautifulSoup(html, features="lxml")
        elements = soup.select(".table > tbody > tr > td")

        for el in elements:
            players.append(str(el).replace("<td>", "").replace("</td>", ""))

        players = remove_duplicate_elements_in_list(players)

        NAMES_TO_REPLACE = [("Callypig", "Big pro Gorilla"), ("Simca", "Simca_"), ("Stay", "- Stay -"), ("Kaneko", "Whirst")]

        for old_name, new_name in NAMES_TO_REPLACE:
            i = players.index(old_name)
            players[i] = new_name

        string_to_add += "__The following players are in the tournament :__\n"

        for player in players:
            string_to_add += "- " + player + "\n"
    except TimeoutException:
        print("I give up...")
        string_to_add += "There was a TimeoutException."
    finally:
        browser.quit()

    return players


async def get_data_from_players(players: list):
    api = Ossapi(15715, "NJ7Q98JQuNlo5jmNBAq0JlBnmqSN0CjkkcsA64Jn")
    players_pp = {}

    for player in players:
        user = api.user(player, mode="mania")
        players_pp[player] = float(user.statistics.variants[0].pp)

    return players_pp


async def get_seedings_from_players(players_pp: dict):
    sorted_players_by_pp = sorted(players_pp.items(), key=lambda x: x[1], reverse=True)
    sorted_players_by_pp_copy = sorted(players_pp.items(), key=lambda x: x[1], reverse=True)

    if len(sorted_players_by_pp) % 2 == 1:
        print(len(sorted_players_by_pp) // 2)
        sorted_players_by_pp.insert(len(sorted_players_by_pp) // 2, ("Exilfaker", 6545.2))
        sorted_players_by_pp_copy.insert(len(sorted_players_by_pp) // 2, ("Exilfaker", 6545.2))
        print(sorted_players_by_pp)

    embed_string = ""

    matches = []

    index = 0

    for player, pp in sorted_players_by_pp_copy:
        index += 1
        embed_string += "Seed #" + str(index) + ": " + player + "\n"

        if len(sorted_players_by_pp) != 0:
            matches.append((sorted_players_by_pp[0], sorted_players_by_pp[-1]))
            sorted_players_by_pp.remove(sorted_players_by_pp[0])
            sorted_players_by_pp.remove(sorted_players_by_pp[-1])

    match_str = ""

    for p1, p2 in matches:
        match_str += f"- {p1[0]} vs {p2[0]} \n"

    return discord.Embed(title="**Matches**", description=match_str)


async def show_individual_stats_from_player(player: str, pool: str):
    embed_desc_str: str = ""
    choke_str: str = f"{player} has a choke on "

    for map_scores in rows:
        if pool is not None and not map_scores['Stage'].startswith(pool):
            continue

        if map_scores[player] == "":
            string_to_add: str = f"{map_scores['Stage']}: N/C"
        else:
            string_to_add: str = f"{map_scores['Stage']}: {map_scores[player]}"

        if type(map_scores[player]) == str:
            choke_str += f"{map_scores['Stage']}, "

        embed_desc_str += string_to_add + "\n"

    embed = discord.Embed(title=f"**List of {player}'s scores**", description=embed_desc_str)
    embed.set_footer(text=choke_str)

    return embed


async def compare_stats_from_players(player1: str, player2: str):

    embed_desc_str: str = ""
    p1_wins_str: str = f"{player1} wins on "
    p2_wins_str: str = f"{player2} wins on "

    p1_wins, p2_wins = get_number_of_winning_scores(player1, player2)

    p1_current_wins: int = 0
    p2_current_wins: int = 0

    for map_scores in rows:
        if map_scores[player1] == "" or map_scores[player2] == "":
            string_to_add = f"{map_scores['Stage']} : NC"
        else:
            player1_score = int(str(map_scores[player1]).replace("*", ""))
            player2_score = int(str(map_scores[player2]).replace("*", ""))
            if player1_score > player2_score:
                p1_current_wins += 1

                difference: int = player1_score - player2_score
                string_to_add = f"{map_scores['Stage']} : **{player1}** with {map_scores[player1]} (+{difference})"

                p1_wins_str += map_scores['Stage']
                p1_wins_str = p1_wins_str + ", " if p1_wins != p1_current_wins else p1_wins_str + f"."
            else:
                p2_current_wins += 1

                difference: int = player2_score - player1_score
                string_to_add = f"{map_scores['Stage']} : **{player2}** with {map_scores[player2]} (+{difference})"

                p2_wins_str += map_scores['Stage']
                p2_wins_str = p2_wins_str + ", " if p2_wins != p2_current_wins else p2_wins_str + f"."

        embed_desc_str += string_to_add + "\n"

    embed = discord.Embed(title=f"**Comparison of {player1} vs {player2}**", description=embed_desc_str)
    embed.set_footer(text=p1_wins_str + "\n" + p2_wins_str)

    return embed


def get_number_of_winning_scores(player1: str, player2: str):
    p1_wins: int = 0
    p2_wins: int = 0

    for map_scores in rows:
        if map_scores[player1] == "" or map_scores[player2] == "":
            continue
        else:
            player1_score = int(str(map_scores[player1]).replace("*", ""))
            player2_score = int(str(map_scores[player2]).replace("*", ""))
            if player1_score > player2_score:
                p1_wins += 1
            else:
                p2_wins += 1

    return p1_wins, p2_wins


def update_sheet_with_game_id(game_id: int):
    games = client.get_multiplayer_info(game_id).games

    cells_to_update = []

    for game in games:
        scores = game.scores

        beatmap_id = game.beatmap.id
        beatmap_name = game.beatmap.title
        beatmap_difficulty_name = game.beatmap.difficulty_name

        print(f"La map {beatmap_name} en {beatmap_difficulty_name} a été jouée. ({beatmap_id})")
        print("------------------SCORES------------------")

        for score in scores:
            user = score.user.username
            score_done = score.score
            is_sore_choke = check_if_score_is_choke(score, game.beatmap)
            print(f"{user} : {score_done}")
            print(f"The score is potentially {'not' if not is_sore_choke else ''} a choke !")
            row, col = update_score_in_sheet(user, beatmap_id, int(score_done), is_sore_choke)
            if row == -1 or col == -1:
                continue
            value_to_update = int(score_done) if not is_sore_choke else score_done + "*"
            cells_to_update.append(Cell(row=row, col=col, value=value_to_update))

    if len(cells_to_update) > 0:
        print("updating cells")
        worksheet.update_cells(cells_to_update)
    else :
        print("Aucune cellule à mettre à jour")


def update_score_in_sheet(player: str, map_id: str, score: int, is_score_choke: bool):
    index_col = 0
    index_row = 1

    for row in rows:
        index_row += 1
        if str(row["id"]).casefold() == map_id.casefold():
            for key in row.keys():
                index_col += 1
                if str(key).casefold() == player.casefold():
                    is_score_choke_in_sheet = type(row[key]) is str and row[key][-1].casefold() == "*".casefold()
                    score_in_sheet = row[key]
                    if row[key] == '':
                        row[key] = 0
                    if type(row[key]) is str and is_score_choke_in_sheet:
                        score_in_sheet = row[key][:-1]  # Remove the '*' to cast to integer
                    if int(score) < int(score_in_sheet):
                        print("Le score réalisé est supérieur à celui de la sheet !")
                        row[key] = score
                        return index_row, index_col
                    if is_score_choke != is_score_choke_in_sheet:
                        # Update the sheet because we have to remove or add the choke mark ('*')
                        return index_row, index_col

    return -1, -1


async def show_stats_in_embeed(match_id: str, how_many_warmups: int):
    mp = client.get_multiplayer_info(match_id)
    mp_name = mp.name
    games = mp.games

    # {
    #   000111002: {
    #       player_1 : 1000,
    #       player_2 : 0000$
    #   }
    # }
    scores_to_compare = {}

    pprint(games)

    for game in games:
        if how_many_warmups > 0:
            how_many_warmups -= 1
            continue
        scores = game.scores

        beatmap_id = game.beatmap.id
        beatmap_name = game.beatmap.title
        beatmap_difficulty_name = game.beatmap.difficulty_name

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

    for beatmap in scores_to_compare.keys():
        print(f"beatmap")
        scores = list(scores_to_compare[beatmap].values())
        users = list(scores_to_compare[beatmap].keys())

        stage = ""

        for row in rows:
            if int(row["id"]) == int(beatmap):
                stage = row["Stage"]

        for user_id in users:
            usernames.append(client.get_user(user_id, 3).username)

        wining_score = max(int(scores[0]), int(scores[1]))
        index_wining_score = scores.index(str(wining_score))

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
