class Event:

    # Note: how the event is reported probably makes more sense
    #  in the DiscordBot class -- eg a "display times" command or something
    #  I don't think it belongs here, but we can talk about it more

    def __init__(self, start, end, organizer, guild):

        # public variables. If need be, we can make them properties for verification.
        self.start = start
        self.end = end
        self.eventOrganizer = organizer
        self.guild = guild  # The server ID that this event belongs to

        # Oh boy, kinda jampacked but basically this is a dict that stores discord user ID to a list of time ranges that
        # a person ISN'T available
        self.attendees = {}

    # Pass in discord member ID, and a list of TimeRange objects where the user CAN'T make the event
    def update_attendee_conflicting_times(self, member_id, timeranges: list):

        if not isinstance(timeranges, list):
            raise Exception("timeranges parameter MUST be a list of TimeRange objects!")

        self.attendees[member_id] = timeranges

    # Returns a dictionary that maps discord member IDs to their respective list of conflicting times (TimeRange objects)
    def get_attendees_conflicting_times(self) -> dict:
        return self.attendees

    @property
    def size(self):
        return self.end - self.start