from config import DEBUG, START_OF_DAY_HOUR, END_OF_DAY_HOUR
import matplotlib.pyplot as plt
import matplotlib.table
import pandas as pd
from db import Database


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
                            pattern INTEGER NOT NULL,
                            endDate DATE NOT NULL
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

        insert_sql = f"""INSERT INTO User (username, name, email)
                        VALUES ('{username}', '{name}', '{email}');"""

        try:
            self.db.insert(insert_sql)
        except Exception as e:
            print(f"The error '{e}' occurred")
            return False

        return True

    def get_user(self, username):
        """ get a user from the database """

        select_sql = f"""SELECT * FROM User WHERE username = '{username}';"""

        cursor = self.db.select(select_sql)

        if cursor is None:
            print("User does not exist")
            return None

        cursor = cursor.fetchone()
        if cursor is None:
            print("User does not exist")
            return None

        return cursor

    def insert_activity(self, username, title, description, act_type, date, start_time, end_time, is_recurring=False,
                        recurring_pattern=None, recurring_end_date=None):
        """ insert an activity into the database

        act_type: 0-Busy 1-Group Meeting 2-Personal Optional 3-Group Optional 4-Fun 5-Other
        """

        recurring_activity_id = None

        if is_recurring:
            recurring_activity_id = self.insert_recurring_activity(recurring_pattern, recurring_end_date)

        user_id = self.get_user(username)
        if user_id is None:
            print("User does not exist")
            return False

        user_id = user_id[0]

        insert_sql = f"""INSERT INTO Activity (userID, title, description, type, date, startTime, endTime, isRecurring, 
                    recurringActivityID) VALUES ({user_id}, '{title}', '{description}', {act_type}, '{date}', '{start_time}'
                    , '{end_time}', '{is_recurring}', '{recurring_activity_id}');"""

        try:
            self.db.insert(insert_sql)
        except Exception as e:
            print(f"The error '{e}' occurred")
            return False

        return True

    def insert_recurring_activity(self, recurring_pattern, recurring_end_date):
        """ insert a recurring activity into the database

        recurring_pattern: 0-Daily 1-Weekly 2-Monthly 3-Yearly
        """

        insert_sql = f"""INSERT INTO RecurringActivity (pattern, endDate)
                        VALUES ('{recurring_pattern}', '{recurring_end_date}');"""

        recurring_activity_id = self.db.insert_with_output_id(insert_sql)

        return recurring_activity_id

    def get_activities_by_user(self, username, start_date, end_date):
        """ get activities from the database for a user """

        user_id = self.get_user(username)
        if user_id is None:
            print("User does not exist")
            return None

        user_id = user_id[0]

        select_sql = f"""SELECT * FROM Activity WHERE userID = {user_id} AND date >= '{start_date}' 
                        AND date <= '{end_date}';"""

        cursor = self.db.select(select_sql)

        if cursor is None:
            print("No activities found for this user")
            return None

        cursor = cursor.fetchall()
        if cursor is None or len(cursor) == 0:
            print("No activities found for this user")
            return None

        return cursor

    def get_activities_by_date(self, start_date, end_date):
        """ get activities from the database for a user """

        select_sql = f"""SELECT * FROM Activity WHERE date >= '{start_date}' 
                        AND date <= '{end_date}';"""

        cursor = self.db.select(select_sql)

        if cursor is None:
            print("No activities found for this period of time")
            return None

        cursor = cursor.fetchall()
        if cursor is None or len(cursor) == 0:
            print("No activities found for this period of time")
            return None

        return cursor

    def get_activities_by_type(self, act_type, start_date, end_date):
        """ get activities from the database e for a user """

        select_sql = f"""SELECT * FROM Activity WHERE type = {act_type} AND date >= '{start_date}' 
                        AND date <= '{end_date}';"""

        cursor = self.db.select(select_sql)

        if cursor is None:
            print("No activities found for this type")
            return None

        cursor = cursor.fetchall()
        if cursor is None or len(cursor) == 0:
            print("No activities found for this type")
            return None

        return cursor

    def visualize_calendar(self, start_date, end_date):
        """ Visualize the calendar for the interval of start_date to end_date and save it as an image.
        It needs to be in a timetable format. (Columns should be days of the week and rows should be hours of
        the day from 7 am to midnight)
        The rows need title of each hour and the columns need the day of the week.
        """

        # Get all activities in the interval
        activities = self.get_activities_by_date(start_date, end_date)

        # Create a dataframe
        df = pd.DataFrame(
            columns=['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

        # Add the time to the dataframe
        for i in range(START_OF_DAY_HOUR, END_OF_DAY_HOUR):
            df.loc[i - START_OF_DAY_HOUR, 'Time'] = f'{i}:00'

        # Add all activities to the dataframe
        print(activities)
        for activity in activities:
            # Find the day of the week
            day_of_week = pd.to_datetime(activity[5]).day_name()

            # Find the start and end time
            start_time = pd.to_datetime(activity[6]).strftime('%H:%M')
            end_time = pd.to_datetime(activity[7]).strftime('%H:%M')

            # Find the start and end time index
            start_time_index = int(start_time.split(':')[0]) - START_OF_DAY_HOUR
            end_time_index = int(end_time.split(':')[0]) - START_OF_DAY_HOUR

            # Find the title
            title = activity[2]

            print(start_time_index, end_time_index, day_of_week, title)

            # Add the title to the dataframe
            for i in range(start_time_index, end_time_index):
                if (df.loc[i, day_of_week] == '' or df.loc[i, day_of_week] == 'nan'
                        or not isinstance(df.loc[i, day_of_week], str)):
                    df.loc[i, day_of_week] = title
                else:
                    df.loc[i, day_of_week] += f'\n{title}'

        # Fill all empty cells with empty string
        df.fillna('', inplace=True)

        # Create the figure and axes objects
        fig, ax = plt.subplots()

        # Remove the axes
        ax.axis('off')

        # Create the table
        table: matplotlib.table.Table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')

        # Set the cell width
        table.auto_set_column_width(col=list(range(len(df.columns))))

        # Set the cell height
        for i in range(START_OF_DAY_HOUR, END_OF_DAY_HOUR):
            height = 0.05

            # check the number of lines in the cell
            for j in range(1, 8):
                num_lines = len(table[(i - (START_OF_DAY_HOUR - 1), j)].get_text().get_text().split('\n'))
                height = max(height, num_lines * 0.05)

            # set the cell heights
            for j in range(0, 8):
                table[(i - (START_OF_DAY_HOUR - 1), j)].set_height(height)

        # Set the font size
        table.set_fontsize(14)

        # Set the figure size
        fig.set_size_inches(18.5, 10.5)

        # Save the figure
        fig.savefig('calendar.png', dpi=100)
