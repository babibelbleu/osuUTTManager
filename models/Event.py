class Event:
    def __init__(self, event_json):
        import globals

        print(event_json[0])

        _event = event_json[0]

        self.beatmap = globals.client.get_beatmap(_event["beatmap_id"]) if _event["beatmap_id"] is not None else None
        self.beatmapset_id = _event["beatmapset_id"]
        self.date = _event["date"]
        self.event_text = _event["display_html"]
        self.epic_factor = _event["epicfactor"]
