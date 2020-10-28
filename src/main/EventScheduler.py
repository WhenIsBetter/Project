from src.main.TimeRange import TimeRange


class EventScheduler:

    class _Node:
        def __init__(self, key):
            self.key = key
            self.prev = None
            self.prev_lvl = None
            self.next = None
            self.next_lvl = None
            self.accum = None

    _start = _Node(None) ; _start.accum = -1
    _end = _Node(None) ; _end.accum = -1

    class _List:
        def __init__(self):
            self.first = EventScheduler._start.deepcopy()
            self.first.next = EventScheduler._end.deepcopy()

        def empty(self):
            return (self.first.next == EventScheduler._end)

        def insertStart(self, new):
            self.insert_basic(self.find_prev(new.key), new)
            new.accum = new.prev + 1
            new.prevDrop = new.prev
            new.prev.nextDrop = new.prev.nextDrop.nextDrop

            new.nextDrop =

        def insertEnd(self, new):
            self.insert_basic(self.find_prev(new.key), new)
            new.accum = new.prev
            new.prevDrop =
            new.nextDrop =

        def find_prev(self, key):
            el = self.first.next
            while el != EventScheduler._end:
                if key > el.key:
                    return el.prev
                el = el.next
            return el.prev

        def insert_basic(self, curr, new):
            new.next = curr.next
            new.prev = curr
            curr.next.prev = new
            curr.next = new

        def delete(self, node):
            if node == EventScheduler._start or node == EventScheduler._end:
                raise Exception("Why are you deleting a start/end, stop that")

            node.next.prev = node.prev
            node.prev.next = node.next

    def __init__(self):
        self._event_lists = {}

    # returns a dict of lists of TimeRange objects, such that ret[i] is the list of ranges with i events during them
    def calc_times(self, event):
        llist = self._check_registered_event(event)

        # check if all the users have put in their calendars and whatnot
        # If they haven't, what to do? Throw an exception (not error, it's expected behavior)? TODO

        outlist = {}
        def temp_add(self, index, start, end):
            if index not in self: self[index] = []
            self[index].append(TimeRange(start, end))

        if llist.empty():
            return { [0]: TimeRange(event.start, event.end) }

        new_start = llist.find_prev(event.start)
        new_end = llist.find_prev(event.end)

        if not new_start.key == event.start:
            if new_start == EventScheduler._start:
                outlist.temp_add(0, event.start, new_start.next.key)
            elif new_start.key < event.start:   # fill in between event start and next time
                outlist.temp_add(new_start.accum, event.start, new_start.next.key)
            else: pass # ...this should never happen; add test or something to confirm
            new_start = new_start.next
        if not new_end.key == event.end:
            outlist.temp_add(new_end.accum, new_end.key, event.end)

        el = new_start
        while el != new_end:
            outlist.temp_add(el.accum, el.key, el.next.key)
            el = el.next

        return outlist

    def overlay_availability(self, event, avail):
        llist = self._check_registered_event(event)

        new_start = EventScheduler._Node(avail.start)
        new_start.source = avail
        new_end = EventScheduler._Node(avail.end)
        new_end.source = avail

        empty = llist.empty()
        llist.insert(new_start)
        llist.insert(new_end)

        if empty:
            new_start.accum = 1
            new_end.accum = 0
        else:
            new_start.accum = new_start.prev.accum
            new_end.accum = new_end.prev.end

            el = new_start
            while el != new_end:
                el.accum += 1
                el = el.next

    def get_events(self):
        return self._event_lists.keys()

    # I don't know what sorts of things should be passed in here
    # Also, should the DiscordBot class, in one of its command resolution functions,
    #  directly instantiate an Event? Or call a method here to create it,
    #   since Event is kind of under EventScheduler?
    def add_event(self, event):
        self._event_lists[event] = EventScheduler._List()

    def _check_registered_event(self, event):
        if event not in self._event_lists:
            raise Exception("Event wasn't added to current events")
        return self._event_lists[event]
