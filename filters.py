class Filter():

    name = "Filter"

    def __init__(self, tables, where):
        self.tables = tables
        self.where = where

    def query(self, select="*", distinct=False):
        dist_text = "DISTINCT" if distinct else "ALL"
        return f"SELECT {dist_text} {select} FROM {Filter._join_table_string(self.tables)}" + (f" WHERE {self.where}" if self.where else "")
        

    def _contains_table(self, table):
        all_tables = [self.tables[0]]
        for t in self.tables[1:]:
            all_tables.append(t[0])
        if table in all_tables:
            return True
        return False

    # tables should be in the form of:
    # [table1, (table2, "key1=key2"), (table3, "key2=key3"), ...]
    @staticmethod
    def _join_table_string(tables):
        result = tables[0]
        for t in tables[1:]:
            table = t[0]
            on = t[1]
            join_type = "" if len(t) == 2 else t[2] + " "
            result += f" {join_type}JOIN {table} ON {on}"
        return result

    @staticmethod
    def combine(filters):
        tables = []
        for f in filters:
            for t in f.tables:
                if t not in tables:
                    tables.append(t)
        where = " AND ".join([f"({f.where})" for f in filters if f.where])
        return Filter(tables, where)


class FieldContains(Filter):
    def __init__(self, table, field, string):
        tables = [table]
        where = f"{field} LIKE '%{string}%'"
        super().__init__(tables, where)


class HappeningAvailable(Filter):
    def __init__(self, available=1):
        tables = ["Happening"]
        sign = ">" if available else "="
        where = f"available_seats {sign} 0"
        super().__init__(tables, where)


class HappeningSeats(Filter):
    def __init__(self, number, lessThan=False):
        tables = ["Happening"]
        sign = "<" if lessThan else ">="
        where = f"available_seats {sign} {number}"
        super().__init__(tables, where)

class EventCategory(Filter):
    def __init__(self, category):
        tables = ["Event"]
        where = f"category = '{category}'"
        super().__init__(tables, where)

class HappeningByEvent(Filter):
    def __init__(self, event_id):
        tables = ["Happening"]
        where = f"event_id = {event_id}"
        super().__init__(tables, where)

class HappeningTime(Filter):
    def __init__(self, timestamp, after=False):
        tables = ["Happening"]
        sign = ">" if after else "<"
        where = f"Happening.datetime {sign} datetime('{timestamp}')"
        super().__init__(tables, where)

class HappeningDistance(Filter):
    def __init__(self, lat, long, dist, greaterThan=False):
        tables = ["Happening", ("Location", "Happening.location_id=Location.id")]
        # Calculate the distance between the given coordinates and the location of the happening using the Haversine formula
        where = f"(6371 * acos(cos(radians({lat})) * cos(radians(latitude)) * cos(radians(longitude) - radians({long})) + sin(radians({lat})) * sin(radians(latitude)))) < {dist}"
        super().__init__(tables, where)
