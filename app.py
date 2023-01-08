import random
import datetime

from connection import Connection
from filters import Filter

columns = {
        "Event": ["description", "name", "category"],
        "Happening": ["event_id", "datetime", "location_id", "available_seats"],
        "Location": ["name", "description", "latitude", "longitude", "capacity"],
        "Reservation": ["user_email", "receipt_num", "datetime", "tickets_no", "happening_id"],
        "Seat": ["number", "location_id", "type"],
        "Ticket": ["name", "reservation_num", "seat_id", "happening_id"],
        "User": ["password", "name"]
        }

class App:
    def __init__(self, dbname, log=True):
        self.connection = Connection(dbname, log)
        self.log = log

    def _get(self, table, select, filters = [], distinct=False, *args):
        dist_text = "DISTINCT" if distinct else "ALL"
        if not filters:
            command = f"SELECT {dist_text} {select} FROM {table}"
        else:
            f = Filter.combine(filters)
            command = f.query(select, distinct)
        result = self.connection.execute_and_fetch(command, *args)
        return result

    @staticmethod
    def _to_dict(sql_result, columns):
        result = {}
        for item in sql_result:
            key = item[0]
            value = dict(zip(columns, item[1:]))
            result[key] = value
        return result


    def _set(self, table, columns, key, values, commit=True):
        # Set key to None (NULL) to autoincrement (when possible)
        self.connection.insert_to_table(table, columns, {key: values}, commit)


    def get_table_fields(self, table, fields, filters = [], distinct=False, *args):
        result = self._get(table, ", ".join(fields), filters, distinct, *args)
        if len(fields) == 1:
            return [x[0] for x in result]
        else:
            return result

    def get_happening_descriptions(self, filters=[], *args):
        # combine tables Happening and Location to get location name
        if not any([f._contains_table("Location") for f in filters]):
            f = [Filter(["Happening", ("Location", "location_id=Location.id")], "")]
        else:
            f = []

        result = self._get("Happenings", "Happening.id, datetime, Location.name, available_seats", filters + f)
        return [(h[0], f"{h[1]} @ {h[2]} ({h[3]} available seat(s))") for h in result]


    def get_table_row(self, table, id_name, id_value, *args):
        f = Filter(table, "{id_name} = {id_value}")
        result = self._get(table, "*", [f], False, *args)
        return App._to_dict(result, table).values()[0]

    def get_categories(self):
        return self.get_table_fields("Categories", ["name"])

    def get_events(self, filters = [], *args):
        result = self._get("Event", "*", filters, *args)
        return App._to_dict(result, columns["Event"])

    def get_happenings(self, filters = [], *args):
        result = self._get("Happening", "*", filters, *args)
        return App._to_dict(result, columns["Happening"])

    def get_locations(self, filters = [], *args):
        result = self._get("Location", "*", filters, *args)
        return App._to_dict(result, columns["Location"])

    def get_reservations(self, filters = [], *args):
        result = self._get("Reservation", "*", filters, *args)
        return App._to_dict(result, columns["Reservation"])

    def get_seats(self, filters = [], *args):
        result = self._get("Seat", "*", filters, *args)
        return App._to_dict(result, columns["Seat"])

    def get_tickets(self, filters = [], *args):
        result = self._get("Ticket", "*", filters, *args)
        return App._to_dict(result, columns["Ticket"])

    def get_users(self, filters = [], *args):
        result = self._get("User", "*", filters, *args)
        return App._to_dict(result, columns["User"])

    def create_reservation(self, reservation, commit=True):
        self._set("Reservation", columns["Reservation"], None, reservation, commit)
        return self.connection.cursor.lastrowid

    def create_ticket(self, ticket, commit=True):
        self._set("Ticket", columns["Ticket"], None, ticket, commit)
        return self.connection.cursor.lastrowid

    def get_ticket_info(self, ticket_id):
        query = "SELECT T.barcode, T.name, T.reservation_num, S.number, L.name, H.datetime, E.name, E.description FROM Ticket T JOIN Seat S ON T.seat_id=S.id JOIN Happening H ON T.happening_id=H.id JOIN Location L ON H.location_id = L.id JOIN Event E ON H.event_id = E.id WHERE T.barcode=?"
        result = self.connection.execute_and_fetch(query, ticket_id)[0]
        columns = ["barcode", "name", "reservation_num", "seat", "location_name", "datetime", "event_name", "event_description"]
        return dict(zip(columns, result))


    def book(self, email, happening_id, names):
        seat_ids = self.get_available_seat_ids_for_happening(happening_id)
        if len(names) > len(seat_ids):
            return None

        reservation = {"user_email": email,
                       "receipt_num": random.randint(10000, 99999),
                       "datetime": datetime.datetime.now(),
                       "tickets_no": len(names),
                       "happening_id": happening_id}
        reservation_id = self.create_reservation(reservation)

        tickets = []
        
        for idx, name in enumerate(names):
            ticket = {"name": name,
                      "reservation_num": reservation_id,
                      "seat_id": seat_ids[idx],
                      "happening_id": happening_id}
            tickets.append(self.create_ticket(ticket))

        return tickets

    def get_available_seat_ids_for_happening(self, happening_id):
        # create custom filter
        tables = ["Seat s", ("Location l", "s.location_id=l.id"), ("Happening h", "h.location_id=l.id"), ("Ticket t", "s.id=t.seat_id AND t.happening_id = h.id", "LEFT")]
        where = "h.id = ? AND t.seat_id IS NULL"
        available_seats_in_happening = Filter(tables, where)
        command = available_seats_in_happening.query("s.id")
        result = self.connection.execute_and_fetch(command, happening_id)
        return [x[0] for x in result]
