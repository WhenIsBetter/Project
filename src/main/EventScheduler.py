import copy
import datetime

from src.main.TimeRange import TimeRange


class EventScheduler:

    class _Node:
        def __init__(self, key):
            self.key = key
            self.prev = None
            self.next = None

        def __str__(self):
            return f"Node({self.key})"

    _start = _Node(None)
    _end = _Node(None)

    class _List:
        def __init__(self):
            self.first = copy.copy(EventScheduler._start)
            self.last = copy.copy(EventScheduler._end)
            self.first.next = self.last
            self.last.prev = self.first

        def empty(self):
            return (self.first.next == self.last)

        def insert(self, new):
            prel = self.find_prev(new.key)
            if prel == new:
                raise Exception("Why are you reinserting the same element")
            self.insert_after(prel, new)

        def find_prev(self, key):
            el = self.first.next
            while el != self.last:
                if key < el.key:
                    return el.prev
                el = el.next
            return el.prev

        def insert_after(self, curr, new):
            new.next = curr.next
            new.prev = curr
            curr.next.prev = new
            curr.next = new

        def delete(self, node):
            if node == self.first or node == self.last:
                raise Exception("Why are you deleting a start/end, stop that")

            node.next.prev = node.prev
            node.prev.next = node.next

    def __init__(self):
        self._event_lists = {}

    # returns a dict of lists of TimeRange objects, such that ret[i] is the list of ranges with i events during them
    def calc_times(self, event, max_missing = 0, min_time = datetime.timedelta(0) ):
        llist = self._check_registered_event(event)

        # check if all the users have put in their calendars and whatnot
        # If they haven't, what to do? Throw an exception (not error, it's expected behavior)? TODO

        outlist = []

        if llist.empty():
            return { [0]: TimeRange(event.start, event.end) }

        new_start = llist.find_prev(event.start)
        new_end = llist.find_prev(event.end)

        if not new_start.key == event.start:
            if new_start == llist.first:
                outlist.append(TimeRange(event.start, new_start.next.key)) # 0
            elif new_start.key < event.start:   # fill in between event start and next time
                outlist.append( TimeRange(event.start, new_start.next.key)) # new_start.accum,
            else: pass # ...this should never happen; add test or something to confirm
            # bundle-in if needed
            new_start = new_start.next
        if not new_end.key == event.end:
            # add walk-back TODO
            outlist.append( TimeRange( new_end.key, event.end) )   #new_end.accum

        s_el = new_start
        while s_el != llist.last and s_el != new_end and s_el.accum > max_missing:
            s_el = s_el.next

        while s_el != llist.last and s_el.next != llist.last and s_el != new_end:

            e_el = s_el.next
            while e_el.next != llist.last and e_el.accum <= max_missing:
                e_el = e_el.next

            ran = TimeRange(s_el.key, e_el.key)
            if ran.size > min_time:
                outlist.append(ran)
            s_el = e_el.next

            if e_el == new_end:
                break

            while s_el != llist.last and s_el != new_end and s_el.accum > max_missing:
                s_el = s_el.next
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
            new_end.accum = new_end.prev.accum

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
