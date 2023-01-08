import random
import time
from tqdm import tqdm

import sys
sys.path.insert(0, '')

import filters as f

def generate(app):
    tickets = []
    reservations = app.get_reservations()
    for r_id, r_contents in tqdm(reservations.items(), desc="Generating Tickets...", unit='reservations'):
        available_seats = app.get_available_seat_ids_for_happening(r_contents["happening_id"])
        for i in range(r_contents["tickets_no"]):
            ticket = { "name": r_contents["user_email"].split("@")[0],
                       "reservation_num": r_id,
                       "seat_id": available_seats[i],
                       "happening_id": r_contents["happening_id"]}

            app.create_ticket(ticket, commit=False)
            tickets.append(ticket)

    return tickets
