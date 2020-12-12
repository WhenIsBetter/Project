import copy
import datetime
from scheduler.TimeRange import TimeRange


class EventScheduler:

    # standard linked list node. key should be a datetime
    class _Node:
        def __init__(self, key):
            self.key = key
            self.prev = None
            self.next = None

        def __str__(self):
            return f"Node({self.key})"

    _start = _Node(None)
    _start.accum = 0
    _end = _Node(None)
    _end.accum = 0

    # standard linked list.
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
        self._event_lists = {}  # maps evens to the linked list representing their availability issues

    # returns a dict of lists of TimeRange objects, such that ret[i] is the list of ranges with i events during them
    def calc_times(self, event, max_missing = 0, min_time = datetime.timedelta(0) ):
        llist = self._check_registered_event(event)

        # check if all the users have put in their calendars and whatnot
        # If they haven't, what to do? Throw an exception (not error, it's expected behavior)? TODO

        outlist = []
        if llist.empty():
            return [TimeRange(event.start, event.end)]

        # The range we're actually looking between for the event
        new_start = llist.find_prev(event.start)
        new_end = llist.find_prev(event.end)

        if new_end.key < event.start:
            return [TimeRange(event.start, event.end)]

        # lots of careful work to handle when the event doesn't line up with availability lines
        start_append = False
        end_append = False
        if not new_start.key == event.start:
            if new_start == llist.first:    # the below is wrong, ie, start_append should only
                start_append = True         # trigger if that's actually valid given the next added piece
                outlist.append(TimeRange(event.start, new_start.next.key)) # 0
            elif new_start.key < event.start:   # fill in between event start and next time
                if new_start.accum <= max_missing:  # instead, I just check for valid combination at the end
                    start_append = True
                    outlist.append( TimeRange(event.start, new_start.next.key)) # new_start.accum,
            else: pass # ...this should never happen; add test or something to confirm
            # bundle-in if needed
            new_start = new_start.next
        if not new_end.key == event.end:
            end_append = True
            outlist.append( TimeRange( new_end.key, event.end) )   #new_end.accum

        # A truly awful loop. I'm sorry, I can't properly comment this.
        # roughly, it moves the 'start element' forward, then the 'end element' forward from there,
        #  until a range with an acceptable # missing is found
        added_something = False
        s_el = new_start
        while s_el != llist.last and s_el != new_end and s_el.accum > max_missing:
            s_el = s_el.next
        while s_el != llist.last and s_el.next != llist.last and s_el != new_end:

            e_el = s_el.next
            while e_el.next != llist.last and e_el.accum <= max_missing:
                e_el = e_el.next

            if e_el.key == s_el.key:
                if e_el.next == llist.last:
                    end_append = False
                    break
            else:
                ran = TimeRange(s_el.key, e_el.key)
                outlist.append(ran)
                added_something = True
            s_el = e_el.next

            if e_el == new_end:
                break

            while s_el != llist.last and s_el != new_end and s_el.accum > max_missing:
                s_el = s_el.next

        outlist.sort( key = lambda tr: tr.start )   #either start or end should work

        # combine the lil' bits off the start/end we chopped off earlier
        if added_something:
            if start_append and len(outlist) >= 2 and outlist[0].end == outlist[1].start:
                first = outlist.pop(0)
                second = outlist[0]
                outlist[0] = TimeRange(first.start, second.end)

            if end_append and len(outlist) >= 2 and outlist[-1].start == outlist[-2].end:
                last = outlist.pop(-1)
                second_to_last = outlist[-1]
                outlist[-1] = TimeRange(second_to_last.start, last.end)

        # take out the ones that're too short
        outlist = list(filter(lambda el: el.size >= min_time, outlist))
        return outlist

    def overlay_availability(self, event, avail):
        llist = self._check_registered_event(event)

        # construct the new start and end nodes
        new_start = EventScheduler._Node(avail.start)
        new_start.source = avail
        new_end = EventScheduler._Node(avail.end)
        new_end.source = avail

        empty = llist.empty()
        # ensure ends come before beginnings:
        new_start.key += datetime.timedelta(milliseconds=1)
        llist.insert(new_start)
        new_start.key -= datetime.timedelta(milliseconds=1)
        new_end.key -= datetime.timedelta(milliseconds=1)
        llist.insert(new_end)
        new_end.key += datetime.timedelta(milliseconds=1)

        # IMPORTANT: accum is always +1/-1 relative to the previous element
        #  it measures the number of people missing immediately after the relevant time
        #  hence, the first availability added will be
        #  1 at start (right after, 1 person's gone) and 0 at end (nobody else missing then)

        if empty:
            new_start.accum = 1
            new_end.accum = 0
        else:
            new_start.accum = new_start.prev.accum  # gets +1ed below
            new_end.accum = new_end.prev.accum

            el = new_start      # if 1 person's missing for a given amount of time...
            while el != new_end:
                el.accum += 1   # ...then 1 more will be missing at each discrete point on the span they're gone
                el = el.next

    def get_events(self):
        return self._event_lists.keys()

    # I don't know what sorts of things should be passed in here
    # Also, should the DiscordBot class, in one of its command resolution functions,
    #  directly instantiate an Event? Or call a method here to create it,
    #   since Event is kind of under EventScheduler?
    def add_event(self, event):
        self._event_lists[event.eid] = EventScheduler._List()

    def _check_registered_event(self, event):
        assert(event.eid != '')
        if event.eid not in self._event_lists:
            raise Exception("Event wasn't added to current events")
        return self._event_lists[event.eid]

    # useful function for testing:
    '''
                print("---------")
            urel = llist.first.next
            while urel != llist.last:
                print("|" + str(urel) + "|" + str(urel.key) + "|  |" + str(urel.prev) + "|" + str(urel.next) + "|")
                urel = urel.next
            print("---------")
            print("|" + str(new_start) + "|" + str(new_end) + "|  |" + str(new_start.prev) ) #+ "|" + str(new_start.prev.accum) + "|")


            print("|" + str(s_el) + "|" + str(e_el) + "|  |" + str(s_el.accum))
            
                    print([str(i) for i in outlist])

    '''
