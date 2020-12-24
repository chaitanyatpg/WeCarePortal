from enum import IntEnum

class RateType(IntEnum):
    NORMAL = 1
    WEEKEND = 2
    HOLIDAY = 3
    LIVE_IN = 4
    WEEKEND_HOLIDAY = 5
    WEEKEND_LIVE_IN = 6
    HOLIDAY_LIVE_IN = 7
    WEEKEND_HOLIDAY_LIVE_IN = 8

    @classmethod
    def choices(cls):
        return tuple((i.name, RATE_TYPE_TO_DISPLAY_STRING[i]) for i in cls)

RATE_TYPE_TO_DISPLAY_STRING = {
    RateType.NORMAL: "Regular Rate",
    RateType.WEEKEND: "Weekend Rate",
    RateType.HOLIDAY: "Holiday Rate",
    RateType.LIVE_IN: "Live in Rate",
    RateType.WEEKEND_HOLIDAY: "Weekend and Holiday",
    RateType.WEEKEND_LIVE_IN: "Weekend and Live In",
    RateType.HOLIDAY_LIVE_IN: "Holiday and Live In",
    RateType.WEEKEND_HOLIDAY_LIVE_IN: "Weekend, Holiday and Live In"
}


