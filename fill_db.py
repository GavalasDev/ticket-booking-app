import random
import csv

import generators.happenings
import generators.seats
import generators.reservations
import generators.tickets
from connection import Connection
from app import App


random.seed(2001)

def _read_csv_to_dict(filename, key_type):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            key = key_type(row.pop(next(iter(row))))
            data[key] = row

    return data


categories = {"Theater":{}, "Concert":{}}

users = _read_csv_to_dict("data/User.csv", str)
print("Read {} users.".format(len(users)))

events = _read_csv_to_dict("data/Event.csv", int)
print("Read {} events.".format(len(events)))

locations = _read_csv_to_dict("data/Location.csv", int)
print("Read {} locations.".format(len(locations)))

happenings = generators.happenings.generate(events, locations)
print("Generated {} happenings.".format(len(happenings)))

seats = generators.seats.generate(locations)
print("Generated {} seats.".format(len(seats)))


print("Initial data generation successful!")
print("-"*40)

dbname = input("Database name: ")

connection = Connection(dbname, log=False)
print("Connected to database.")

connection.clear_tables()
print("Cleared all database data.")

connection.insert_to_table("Category", [], categories)
connection.insert_to_table("User", ["password", "name"], users)
connection.insert_to_table("Event", ["description", "name", "category"], events)
connection.insert_to_table("Location", ["name", "description", "latitude", "longitude", "capacity"], locations)
connection.insert_to_table("Happening", ["event_id", "datetime", "location_id", "available_seats"], happenings)
connection.insert_to_table("Seat", ["number", "location_id", "type"], seats)

connection.commit_all()
print("Successfully wrote initial data to database!")
print("-"*40)

del connection

print("Connecting to the app interface...")
app = App(dbname, log=False)
print("Successfully connected to app!")
reservations = generators.reservations.generate(app)
print("Generated {} reservations.".format(len(reservations)))

tickets = generators.tickets.generate(app)
print("Generated {} tickets.".format(len(tickets)))

app.connection.commit_all()
print("Successfully wrote all data to database!")
