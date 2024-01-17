import sqlite3
from sqlite3 import Error


# Sadra part 😎

class Database:
    def __init__(self, path):
        self.path = path
        self.conn = None

    def create_connection(self):
        """ create a database connection to a SQLite database """

        if self.conn is not None:
            return self.conn

        try:
            self.conn = sqlite3.connect(self.path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.conn

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement """
        # todo: create the table and database structure: (functionalities needed: plans, optional plans, due dates,
        #  unexpected events, meetings, next event, show overall schedule
        pass
