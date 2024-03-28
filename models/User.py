import pycountry
from .Event import Event


class User:
    def __init__(self, req_result):
        from utils import convertSecondsToDateTime
        _user = req_result[0]

        self.average_accuracy = _user["accuracy"]
        self.count_100 = _user["count100"]
        self.count_300 = _user["count300"]
        self.count_50 = _user["count50"]
        self.count_rank_a = _user["count_rank_a"]
        self.count_rank_s = _user["count_rank_s"]
        self.count_rank_sh = _user["count_rank_sh"]
        self.count_rank_ss = _user["count_rank_ss"]
        self.count_rank_ssh = _user["count_rank_ssh"]
        self.country_code = _user["country"]
        self.country_name = pycountry.countries.get(alpha_2=_user['country']).name
        self.last_event = Event(_user["events"]) if len(_user["events"]) > 0 else None
        self.join_date = _user["join_date"]
        self.level = _user["level"]
        self.play_count = _user["playcount"]
        self.pp_country_rank = _user["pp_country_rank"]
        self.pp_global_rank = _user["pp_rank"]
        self.pp = _user["pp_raw"]
        self.ranked_score = _user["ranked_score"]
        self.total_score = _user["total_score"]
        self.total_seconds_played = _user["total_seconds_played"]
        self.total_seconds_played_string = convertSecondsToDateTime(int(_user["total_seconds_played"]))
        self.user_id = _user["user_id"]
        self.username = _user["username"]
        self.avatar_link = f"http://s.ppy.sh/a/{_user['user_id']}"

    def __repr__(self) -> str:
        return str(self.__dict__)



