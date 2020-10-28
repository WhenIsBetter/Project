
# I don't think it's worth rolling our own Date class
from datetime import datetime as Date


class TimeRange:

    # the properties are so they're read-only
    # we might decide against this, but for now it seems a convenient way to work with the logic

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def size(self):
        return self.end - self.start

    __start = None    # type: Date
    __end = None
    # todo: granularity?

    def __init__(self, start, end):
        # Sanity-check the input
        if start is None or not isinstance(start, Date):
            raise ValueError("AvailableTime: start must be a Date (datetime.datetime)")
        if end is None or not isinstance(end, Date):
            raise ValueError("AvailableTime: end must be a Date (datetime.datetime)")
        if (start - end) <= 0:  # note: date - date = datetime.timedelta
            raise ValueError("AvailableTime: end must be after start")

        self.__start = start
        self.__end = end

    # TODO TODO: defining a __less__ and similar functions for comparing these
