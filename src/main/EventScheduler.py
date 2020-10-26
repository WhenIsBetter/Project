

class EventScheduler:

    class _Node:
        def __init__(self, content):
            self.content = content
            self.prev = None
            self.next = None

    _start = _Node(None)
    _end = _Node(None)

    def __init__(self):
        self._linked_list = {}

    # returns a list of AvailableTime objects
    def calc_times(self, event):
        pass

        # check if event is in current_events, maybe?

        # check if all the users have put in their calendars and whatnot
        # If they haven't, what to do? Throw an exception (not error, it's expected behavior)? TODO

        # Algorithm to find times goes below:

    def overlay_availability(self, event, avail):
        if self.overlay_availability.link_add_helper is None:
            def temp(curr_range, new_node):
                new_node.next = curr_range.next
                new_node.prev = curr_range
                curr_range.next.prev = new_node
                curr_range.next = new_node
            self.overlay_availability.link_add_helper = temp

        if event not in self._linked_list:
            raise Exception("Event wasn't added to current events")
        new_node = EventScheduler._Node(avail)

        curr_range = self._linked_list[event]
        while curr_range.next != self._end and curr_range.content < new_node.content:
            curr_range = curr_range.next
        self.overlay_availability.link_add_helper(curr_range, new_node)
    # TODO : This doesn't actually work, needs splitting 
    overlay_availability.link_add_helper = None


    def get_events(self):
        return self._linked_list.keys()

    # I don't know what sorts of things should be passed in here
    # Also, should the DiscordBot class, in one of its command resolution functions,
    #  directly instantiate an Event? Or call a method here to create it,
    #   since Event is kind of under EventScheduler?
    def add_event(self, event):
        new_start = EventScheduler._start.deepcopy()
        new_start.next = EventScheduler._end.deepcopy()

        self._linked_list[event] = new_start

    # ... we need to figure out this API in more detail
