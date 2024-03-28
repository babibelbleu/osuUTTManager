from __future__ import annotations

from models import User, Beatmap, Multiplayer

import requests


class Client:
    """
    Class Client for osu! API v1 requests.\n
    Use help(your_client_object) for more details about each method.
    """
    API_URL = "https://osu.ppy.sh/api"

    def __init__(self, token: str):
        self.token = token

    def _req(self, endpoint, params):
        params["k"] = self.token

        return requests.get(f"{self.API_URL}{endpoint}", params=params).json()

    def __repr__(self):
        return f"osu!Client v1.\n" \
               f"Use help(your_client_object) for more details about each method."

    def get_user(self, user: str | int, mode: int):
        """
        Fetches a user by their id or name.
        :param user:
        :param mode: The gamemode
        :return:
        """
        assert type(mode) is int, "mode has to be integer.\n 0:std \n 1:taiko \n 2:ctb \n 3:mania"

        params = {
            "u": user,
            "m": 3
        }

        return User(self._req("/get_user", params))

    def get_multiplayer_info(self, mp_id: int):
        params = {
            "mp": mp_id
        }

        return Multiplayer(self._req("/get_match", params))

    def get_beatmap(self, beatmap_id: int):
        params = {
            "b": beatmap_id
        }

        return Beatmap(self._req("/get_beatmaps", params))
