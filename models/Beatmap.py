from enums import ApprobationStatus, Gamemode, MusicGenre


class Beatmap:
    def __init__(self, req_result):
        from globals import client

        _beatmap = req_result[0]

        self.approved = ApprobationStatus(int(_beatmap["approved"])).name
        self.approved_date = _beatmap["approved_date"]
        self.artist = _beatmap["artist"]
        self.artist_unicode = _beatmap["artist_unicode"]
        self.is_audio_available = _beatmap["audio_unavailable"] == 0
        self.id = _beatmap["beatmap_id"]
        self.beatmapset_id = _beatmap["beatmapset_id"]
        self.bpm = _beatmap["bpm"]
        self.mode = Gamemode(int(_beatmap["mode"]))
        self.count_normal_notes = _beatmap["count_normal"]
        self.count_slider = _beatmap["count_slider"]
        self.count_spinner = _beatmap["count_spinner"]
        self.creator = client.get_user(_beatmap["creator_id"], mode=self.mode.value)
        self.diff_aim = _beatmap["diff_aim"]
        self.ar = _beatmap["diff_approach"]
        self.od = _beatmap["diff_overall"]
        self.hp = _beatmap["diff_drain"]
        self.cs = _beatmap["diff_size"]
        self.speed = _beatmap["diff_speed"]
        self.sr = _beatmap["difficultyrating"]
        self.is_download_available = _beatmap["download_unavailable"] == 0
        self.favourite_count = _beatmap["favourite_count"]
        self.file_md5 = _beatmap["file_md5"]
        self.genre = MusicGenre(int(_beatmap["genre_id"]))
        self.map_length = _beatmap["hit_length"]
        self.language_id = _beatmap["language_id"]
        self.last_update = _beatmap["last_update"]
        self.max_combo = _beatmap["max_combo"]
        self.packs = _beatmap["packs"]
        self.pass_count = _beatmap["passcount"]
        self.play_count = _beatmap["playcount"]
        self.rating = _beatmap["rating"]
        self.source = _beatmap["source"]
        self.has_storyboard = _beatmap["storyboard"] == 1
        self.submit_date = _beatmap["submit_date"]
        self.tags = _beatmap["tags"]
        self.title = _beatmap["title"]
        self.title_unicode = _beatmap["title_unicode"]
        self.total_length = _beatmap["total_length"]
        self.difficulty_name = _beatmap["version"]
        self.has_video = _beatmap["video"] == 1
