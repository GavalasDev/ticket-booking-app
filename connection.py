import sqlite3

class Connection:
    def __init__(self, dbname, log=True):
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname)
        self.cursor = self.conn.cursor()
        self.log = log

    def __del__(self):
        self.conn.close()

    def commit_all(self):
        self.conn.commit()

    def get_table_names(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in self.cursor.fetchall() if t[0] != "sqlite_sequence"]
        return tables

    def clear_tables(self):
        tables = self.get_table_names()
        for table in tables:
            self.cursor.execute("DELETE FROM {}".format(table)) 

    def insert_to_table(self, tablename, columns, data, commit=False):
        for key, value in data.items():
            command = f"INSERT INTO {tablename} VALUES (" + "?," * len(columns) + "?)"
            values = [key] + [value[c] for c in columns]
            if self.log:
                print(command, values)
            self.cursor.execute(command, values)
            if commit:
                self.commit_all()

    def execute_and_fetch(self, command, *args):
        if self.log:
            print(command, args)
        self.cursor.execute(command, args)
        return self.cursor.fetchall()
