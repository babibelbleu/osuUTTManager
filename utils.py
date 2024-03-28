from enums import Mod


def getModsString(number: int):
    string = ""
    for data in Mod:
        if data.value <= number:
            number -= data.value
            string += data.name

        if number == 0:
            return string

    return string


def convertSecondsToDateTime(seconds: int):
    seconds_to_minute = 60
    seconds_to_hour = 60 * seconds_to_minute
    seconds_to_day = 24 * seconds_to_hour

    days = seconds // seconds_to_day
    seconds %= seconds_to_day

    hours = seconds // seconds_to_hour
    seconds %= seconds_to_hour

    minutes = seconds // seconds_to_minute
    seconds %= seconds_to_minute

    secs = seconds

    return "%dd, %dh, %dm, %ds" % (days, hours, minutes, secs)


def remove_duplicate_elements_in_list(items: list):
    new_list = []
    for index, el in enumerate(items):
        if index % 2 == 1:
            new_list.append(el)
    return new_list
