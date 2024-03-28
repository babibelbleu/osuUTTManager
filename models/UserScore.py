class UserScore():
    def __init__(self, req_result, mode):
        from globals import client
        from utils import getModsString

        _score = req_result[0]

        self.beatmap = client.get_beatmap(_score["beatmap_id"])
        self.count_100 = _score["count100"]
        self.count_300 = _score["count300"]
        self.count_50 = _score["count50"]
        self.count_320 = _score["countgeki"]
        self.count_200 = _score["countkatu"]
        self.count_miss = _score["countmiss"]
        self.date = _score["date"]
        self.mods = getModsString(int(_score["enabled_mods"]))
        self.mods_bitwise = _score["enabled_mods"]
        self.max_combo = _score["maxcombo"]
        self.is_perfect = _score["perfect"] == 1
        self.pp = _score["pp"]
        self.rank = _score["rank"]
        self.score = _score["score"]
        self.id = _score["score_id"]
        print("oui")
        self.user = client.get_user(_score["user_id"], mode)
