import random
import time

def _random_time_in_2023():
    # Generate a random year, month, and day in 2023
    year = 2023
    month = random.randint(1, 12)
    day = random.randint(1, 28)

    # Generate a random hour and minute between 16:00 and 23:59
    hour = random.randint(16, 23)
    minute = random.randint(0, 59)

    # Create a tuple with the year, month, day, hour, and minute
    timestamp = (year, month, day, hour, minute, 0, 0, 0, 0)

    # Convert the tuple to a Unix timestamp
    unix_timestamp = time.mktime(timestamp)

    iso8601_string = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(unix_timestamp))

    return(iso8601_string)


def _random_location_based_on_category(category):
    if category == "Theater":
        return random.randint(1, 102)
    elif category == "Concert":
        return random.randint(103, 122)
    return 0


def generate(events, locations):

    locations = dict(locations)

    happenings = {}

    current_id = 1
    for event_id, event in events.items():
        for i in range(1, random.randint(2, 11)):
            location_id = _random_location_based_on_category(event["category"])
            happening = {"event_id": event_id,
                         "datetime": _random_time_in_2023(),
                         "location_id": location_id,
                         "available_seats": locations[location_id]["capacity"]}
            happenings[current_id] = happening
            current_id += 1
    return happenings
