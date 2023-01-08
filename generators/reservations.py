import random
import time
from tqdm import tqdm

import sys
sys.path.insert(0, '')

import filters as f

def _random_time_in_2022():
    # Generate a random year, month, and day in 2022
    year = 2022
    month = random.randint(1, 12)
    day = random.randint(1, 28)

    hour = random.randint(0, 23)
    minute = random.randint(0, 59)

    timestamp = (year, month, day, hour, minute, 0, 0, 0, 0)

    # Convert the tuple to a Unix timestamp
    unix_timestamp = time.mktime(timestamp)

    iso8601_string = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(unix_timestamp))

    return(iso8601_string)


def _random_reservation(email, app):

    receipt_num = random.randint(100000000, 999999999)

    datetime = _random_time_in_2022()

    tickets_no = random.randint(1, 6)

    available_happening_ids = app.get_table_fields("Happening", ["id"],
                                                  [f.HappeningSeats(tickets_no)])

    # prioritize happening #2001 so that it fills up first
    happening_id = 2001 if 2001 in available_happening_ids else random.choice(available_happening_ids)

    return {"user_email": email, 
            "receipt_num": receipt_num,
            "datetime": datetime,
            "tickets_no": tickets_no,
            "happening_id": happening_id}


def generate(app):
    reservations = []

    users = app.get_users()

    user_emails = list(users.keys())
    for user_email in tqdm(user_emails, desc="Generating Reservations...", unit='users'):
        number_of_reservations = random.randint(0, 10)
        for _ in range(number_of_reservations):
            reservation = _random_reservation(user_email, app)
            app.create_reservation(reservation, commit=False)
            reservations.append(reservation)

    return reservations
