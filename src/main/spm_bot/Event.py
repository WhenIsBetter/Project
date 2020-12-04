class Event:

    # public variables. If need be, we can make them properties for verification.

    start = None
    end = None
    eventOrganizer = None
    attendees = []

    # Note: how the event is reported probably makes more sense
    #  in the DiscordBot class -- eg a "display times" command or something
    #  I don't think it belongs here, but we can talk about it more

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def size(self):
        return self.end - self.start