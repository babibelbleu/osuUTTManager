from models import Game


class Multiplayer:
    def __init__(self, req_result):
        _mp = req_result
        _mp_info = _mp["match"]

        self.games = [Game(game) for game in _mp["games"]]
        self.start_time = _mp_info["start_time"]
        self.end_time = _mp_info["end_time"]
        self.name = _mp_info["name"]
        self.id = _mp_info["match_id"]
