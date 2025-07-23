from ..models.data import Event, CalendarData

class EventViewModel:
    def __init__(self, event = Event):
        self.event = event
