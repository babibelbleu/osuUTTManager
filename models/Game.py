class Game:
    def __init__(self, game):
        from enums import Gamemode, ScoringType, TeamType
        from utils import getModsString
        from models import MultiplayerScore
        from globals import client

        self.id = game["game_id"]
        self.start_time = game["start_time"]
        self.end_time = game["end_time"]
        self.beatmap = client.get_beatmap(int(game["beatmap_id"]))
        self.play_mode = Gamemode(int(game["play_mode"]))
        self.match_type = game["match_type"]
        self.scoring_type = ScoringType(int(game["scoring_type"]))
        self.team_type = TeamType(int(game["team_type"]))
        self.global_mods = getModsString(int(game["mods"]))
        self.scores = [MultiplayerScore(score, self.play_mode) for score in game["scores"]]
