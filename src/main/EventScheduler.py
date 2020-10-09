

class EventScheduler:

    current_events = []

    # returns a list of AvailableTime objects
    def calc_times(self, event):
        pass

        # check if event is in current_events, maybe?

        # check if all the users have put in their calendars and whatnot
        # If they haven't, what to do? Throw an exception (not error, it's expected behavior)? TODO

        # Algorithm to find times goes below:

    # deepcopy so it doesn't affect the underlying list
    # we can undo if it's a performance problem,
    #  but if so then we probably shouldn't modify the list externally
    def get_events(self):
        return self.current_events.deepcopy()

    # I don't know what sorts of things should be passed in here
    # Also, should the DiscordBot class, in one of its command resolution functions,
    #  directly instantiate an Event? Or call a method here to create it,
    #   since Event is kind of under EventScheduler?
    def add_event(self):
        pass

    # ... we need to figure out this API in more detail
