import sqlite3
from sqlite3 import Error

DEBUG = True


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


class Scheduler:
    def __init__(self, path="database.sqlite3"):
        self.db = Database(path)

    def create_tables(self):
        """ create tables in the database """

        user_table_sql = """CREATE TABLE IF NOT EXISTS User (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            username VARCHAR(255) NOT NULL,
                            name     VARCHAR(255),
                            email    VARCHAR(255)
                        );"""

        recurring_activity_table_sql = """CREATE TABLE IF NOT EXISTS RecurringActivity (
                            id      INTEGER PRIMARY KEY AUTOINCREMENT,
                            pattern VARCHAR(50) NOT NULL,
                            endDate DATE
                        );"""

        activities_table_sql = """CREATE TABLE IF NOT EXISTS Activity (
                            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                            userID              INTEGER NOT NULL,
                            title               VARCHAR(255),
                            description         TEXT,
                            type                INTEGER,
                            date                DATE,
                            startTime           TIME,
                            endTime             TIME,
                            isRecurring         BOOLEAN,
                            recurringActivityID INTEGER,
                            FOREIGN KEY (userID) REFERENCES User (id),
                            FOREIGN KEY (recurringActivityID) REFERENCES RecurringActivity (id)
                        );"""

        try:
            self.db.create_table(user_table_sql)
            self.db.create_table(recurring_activity_table_sql)
            self.db.create_table(activities_table_sql)
        except Exception as e:
            print(f"The error '{e}' occurred")
            return False

        return True

    def insert_user(self, username, name, email):
        """ insert a user into the database, if the user already exists, return False """

        user_id = self.get_user(username)
        if user_id is not None:
            print("User already exists")
            return False

        insert_sql = f"""INSERT INTO User (Username, Name, Email)
                        VALUES ('{username}', '{name}', '{email}');"""

        try:
            self.db.insert(insert_sql)
        except Exception as e:
            print(f"The error '{e}' occurred")
            return False

        return True

    def get_user(self, username):
        """ get a user from the database """

        select_sql = f"""SELECT * FROM User WHERE Username = '{username}';"""

        cursor = self.db.select(select_sql)

        if cursor is None:
            print("User does not exist")
            return None

        cursor = cursor.fetchone()
        if cursor is None:
            print("User does not exist")
            return None

        return cursor

    def insert_activity(self, username, title, description, type, date, start_time, end_time, is_recurring,
                        recurring_pattern, recurring_end_date):
        """ insert an activity into the database """

        recurring_activity_id = None

        if is_recurring:
            recurring_activity_id = self.insert_recurring_activity(recurring_pattern, recurring_end_date)

        user_id = self.get_user(username)
        if user_id is None:
            print("User does not exist")
            return False

        user_id = user_id[0]

        insert_sql = f"""INSERT INTO Activity (UserID, Title, Description, Type, Date, StartTime, EndTime, IsRecurring, 
                    RecurringActivityID) VALUES ({user_id}, '{title}', '{description}', {type}, '{date}', '{start_time}'
                    , '{end_time}', {is_recurring}, {recurring_activity_id});"""

        try:
            self.db.insert(insert_sql)
        except Exception as e:
            print(f"The error '{e}' occurred")
            return False

        return True

    def insert_recurring_activity(self, recurring_pattern, recurring_end_date):
        """ insert a recurring activity into the database """

        insert_sql = f"""INSERT INTO RecurringActivity (RecurrencePattern, RecurrenceEndDate)
                        VALUES ('{recurring_pattern}', '{recurring_end_date}');"""

        recurring_activity_id = self.db.insert_with_output_id(insert_sql)

        return recurring_activity_id
