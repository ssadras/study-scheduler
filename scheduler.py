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

        try:
            self.conn.execute(create_table_sql)
            print("Table created successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

        return self.conn


class Scheduler:
    def __init__(self, path):
        self.db = Database(path)

    def create_table(self):
        user_table_sql = """CREATE TABLE IF NOT EXISTS User (
                                        UserID INT PRIMARY KEY,
                                        Username VARCHAR(255) NOT NULL,
                                        Name VARCHAR(255),
                                        Email VARCHAR(255)
                                    );
                                    """

        recurring_activity_table_sql = """CREATE TABLE IF NOT EXISTS RecurringActivity (
                                        RecurringActivityID INT PRIMARY KEY,
                                        RecurrencePattern VARCHAR(50) NOT NULL,
                                        RecurrenceEndDate DATE
                                    );"""

        activities_table_sql = """CREATE TABLE IF NOT EXISTS Activity (
                                        ActivityID INT PRIMARY KEY,
                                        UserID INT,
                                        Title VARCHAR(255),
                                        Description TEXT,
                                        Type INT,
                                        Date DATE,
                                        StartTime TIME,
                                        EndTime TIME,
                                        IsRecurring BOOLEAN,
                                        RecurringActivityID INT,
                                        FOREIGN KEY (UserID) REFERENCES User(UserID),
                                        FOREIGN KEY (RecurringActivityID) REFERENCES RecurringActivity(RecurringActivityID)
                                    );"""

        try:
            self.db.create_table(user_table_sql)
            self.db.create_table(recurring_activity_table_sql)
            self.db.create_table(activities_table_sql)
        except Exception as e:
            print(f"The error '{e}' occurred")
            return False

        return True
