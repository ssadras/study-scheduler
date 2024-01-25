import sqlite3
from config import DEBUG
from sqlite3 import Error


class Database:
    def __init__(self, path):
        self.path = path
        self.conn = None

        self.create_connection()

    def create_connection(self):
        """ create a database connection to a SQLite database """

        if self.conn is not None:
            return self.conn

        try:
            self.conn = sqlite3.connect(self.path, isolation_level=None)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.conn

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement """

        if DEBUG:
            print("DB.create_table: ", create_table_sql)

        try:
            self.conn.execute(create_table_sql)
            print("Table created successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.conn

    def insert(self, insert_sql):
        """ insert a row into a table from the insert_sql statement """

        if DEBUG:
            print("DB.insert: ", insert_sql)

        try:
            self.conn.execute(insert_sql)
            print("Row inserted successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.conn

    def insert_with_output_id(self, insert_sql):
        """ insert a row into a table from the insert_sql statement and return the id of the inserted row """

        if DEBUG:
            print("DB.insert_with_output_id: ", insert_sql)

        cursor = None

        try:
            cursor = self.conn.execute(insert_sql)
            print("Row inserted successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

        return cursor.lastrowid

    def select(self, select_sql):
        """ select rows from a table from the select_sql statement """

        if DEBUG:
            print("DB.select: ", select_sql)

        cursor = None

        try:
            cursor = self.conn.execute(select_sql)
            print("Rows selected successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

        return cursor

    def update(self, update_sql):
        """ update rows from a table from the update_sql statement """

        if DEBUG:
            print("DB.update: ", update_sql)

        try:
            self.conn.execute(update_sql)
            print("Rows updated successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.conn

    def delete(self, delete_sql):
        """ delete rows from a table from the delete_sql statement """

        if DEBUG:
            print("DB.delete: ", delete_sql)

        try:
            self.conn.execute(delete_sql)
            print("Rows deleted successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.conn
