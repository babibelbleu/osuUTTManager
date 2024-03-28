from enums import Gamemode


class MultiplayerScore:
    def __init__(self, score, play_mode: Gamemode):
        from globals import client
        from utils import getModsString

        self.slot = score["slot"]
        self.team = score["team"]
        self.user = client.get_user(int(score["user_id"]), play_mode.value)
        self.score = score["score"]
        self.max_combo = score["maxcombo"]
        self.rank = score["rank"]
        self.count_100 = score["count100"]
        self.count_300 = score["count300"]
        self.count_50 = score["count50"]
        self.count_320 = score["countgeki"]
        self.count_200 = score["countkatu"]
        self.count_miss = score["countmiss"]
        self.is_perfect = score["perfect"] == 1
        self.has_passed = score["pass"] == 1
        self.mods = getModsString(int(score["enabled_mods"]))
