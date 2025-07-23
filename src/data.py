class Event:
    def __init__(self, name, pinned_date, start_time, end_time, is_periodic=False):
        self.name = name
        self.date = pinned_date
        self.start_time = start_time
        self.end_time = end_time
        self.is_periodic = is_periodic
        self.description = ""
        self.repeat_interval = ""

    def load_from_json(self, json_event):
        self.name = json_event["name"]
        self.date = json_event["date"]
        self.start_time = json_event["start_time"]
        self.end_time = json_event["end_time"]
        self.is_periodic = json_event["is_periodic"]
        self.description = json_event["description"]
        self.repeat_interval = json_event["repeat_interval"]

    def to_json(self):
        return {
            "name": self.name,
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_periodic": self.is_periodic,
            "description": self.description,
            "repeat_interval": self.repeat_interval,
        }

class Calendar:
    pass