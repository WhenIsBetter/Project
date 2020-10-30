from enum import Enum


# Represents server-wide privileges
#  individualized privileges should be handled in a more granular way
#  (eg what if an event is only open to users with certain roles? etc)
class UserPrivilege(Enum):
    ADMIN = 1       # edit/delete anybody's events
    SUBMIT = 2      # edit/delete only their own events
    ATTEND = 3      # can't submit events
    # ... this is a rough draft, of course. We need to discuss this more.


class DiscordUser:

    googleAccount = None  # some sort of id or containing class
    _free_times = []  # list of AvailableTimes. Public.
    _privileges = {}

    def __init__(self):

        # default privileges: only able to attend events
        for priv in UserPrivilege:
            self._privileges[priv] = False
        self._privileges[UserPrivilege.ATTEND] = True

    def get_privilege(self, event):
        return self._privileges
        # just return privs, but maybe edit if
        #   eg a given event has specific requirements for its attendees (eg only managers)

    def get_free_times(self):
        # does this need access to the event in question? maybe not, let the user filter the data
        return self._free_times  # needs to check if we've pulled _free_times from Google recently
        # in fact, todo: how to get data from Google

    # TODO the API for adding times
    # it might need to be more than just the list, because what if eg the user has
    #  overlapping timeslots in the list? Or we need to change availability? etc
    # Needs discussion:
    def add_timerange(self, date):
        pass

    def remove_timerange(self, date):
        pass
