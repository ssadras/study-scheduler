from config import DEBUG, START_OF_DAY_HOUR, END_OF_DAY_HOUR, TIME_INTERVAL_TYPE
import matplotlib.pyplot as plt
import matplotlib.table
import pandas as pd
from db import Database

if TIME_INTERVAL_TYPE == 1:
    TIME_INTERVAL = 4
elif TIME_INTERVAL_TYPE == 2:
    TIME_INTERVAL = 2
else:
    TIME_INTERVAL = 1


class Scheduler:
    def __init__(self, path="database.sqlite3"):
        self.db = Database(path)
        self.df_weekly = pd.DataFrame(
            columns=['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

        if DEBUG:
            self.df_weekly = pd.DataFrame(
                columns=['index', 'Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

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

    def get_activities_by_a_type(self, act_type, start_date, end_date):
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

    def get_activities_by_set_of_types(self, types: tuple, start_date, end_date):
        """ get activities from the database e for a user """

        select_sql = f"""SELECT * FROM Activity WHERE type IN {types} AND date >= '{start_date}' 
                        AND date <= '{end_date}';"""

        cursor = self.db.select(select_sql)

        if cursor is None:
            print("No activities found for these types")
            return None

        cursor = cursor.fetchall()
        if cursor is None or len(cursor) == 0:
            print("No activities found for these types")
            return None

        return cursor

    def add_recurring_activities_to_dataframe(self, activities, start_date, end_date):
        """ Add all recurring activities to the dataframe """
        # todo: Finish this function
        pass

    def add_activity_to_dataframe(self, activity):
        """ Add an activity to the dataframe """

        # Find the day of the week
        column = pd.to_datetime(activity[5]).day_name()

        # Find the start and end time
        start_time = pd.to_datetime(activity[6]).strftime('%H:%M')
        end_time = pd.to_datetime(activity[7]).strftime('%H:%M')

        # Find the start and end time index
        start_time_index, end_time_index = self.get_start_and_end_time_index(start_time, end_time)

        # Find the title
        title = activity[2]

        if DEBUG:
            print("add_activity_to_dataframe:", start_time_index, end_time_index, column, title)

        # Add the title to the dataframe
        for i in range(start_time_index, end_time_index):
            if DEBUG:
                print("add_activity_to_dataframe 2:", i, (END_OF_DAY_HOUR - START_OF_DAY_HOUR) * TIME_INTERVAL,
                      len(self.df_weekly))

            if i < 0 or i >= (END_OF_DAY_HOUR - START_OF_DAY_HOUR) * TIME_INTERVAL:
                continue

            if (self.df_weekly.loc[i, column] == '' or self.df_weekly.loc[i, column] == 'nan'
                    or not isinstance(self.df_weekly.loc[i, column], str)):
                self.df_weekly.loc[i, column] = title
            else:
                self.df_weekly.loc[i, column] += f'\n{title}'

    def get_start_and_end_time_index(self, start_time, end_time):
        start_time_index = None
        end_time_index = None

        start_hour = int(start_time.split(':')[0])
        start_min = int(start_time.split(':')[1])

        end_hour = int(end_time.split(':')[0])
        end_min = int(end_time.split(':')[1])

        # Find the start and end time index
        if TIME_INTERVAL_TYPE == 1:
            start_time_index = (start_hour - START_OF_DAY_HOUR) * 4 + (start_min // 15)

            end_min_index = end_min // 15
            end_time_index = (end_hour - START_OF_DAY_HOUR) * 4 + end_min_index + (end_min % 15 > 0)

        elif TIME_INTERVAL_TYPE == 2:
            start_time_index = (start_hour - START_OF_DAY_HOUR) * 2 + (start_min // 30)
            end_time_index = (end_hour - START_OF_DAY_HOUR) * 2 + (end_min // 30) + (end_min % 30 > 0)

        elif TIME_INTERVAL_TYPE == 3:
            start_time_index = (start_hour - START_OF_DAY_HOUR)
            end_time_index = (end_hour - START_OF_DAY_HOUR) + (end_min > 0)

        if DEBUG:
            print("get_start_and_end_time_index:", start_time_index, end_time_index)

        return start_time_index, end_time_index

    def create_weekly_dataframe_hourly(self, start_date, end_date, types: tuple = (0, 1, 2, 3, 4, 5)):
        """ create a dataframe for the activities in the database for a period of time based on hourly intervals """

        # Get all activities in the interval
        activities = self.get_activities_by_set_of_types(types, start_date, end_date)

        # Add the time to the dataframe
        for i in range(START_OF_DAY_HOUR, END_OF_DAY_HOUR):
            self.df_weekly.loc[i - START_OF_DAY_HOUR, 'Time'] = f'{i}:00'

            if DEBUG:
                self.df_weekly.loc[i - START_OF_DAY_HOUR, 'index'] = f'{i - START_OF_DAY_HOUR}'

        # Add all activities to the dataframe
        if DEBUG:
            print("create_weekly_dataframe_hourly:", activities)

        for activity in activities:
            self.add_activity_to_dataframe(activity)

        # Fill all empty cells with empty string
        self.df_weekly.fillna('', inplace=True)

        return self.df_weekly

    def create_weekly_dataframe_30_mins(self, start_date, end_date, types: tuple = (0, 1, 2, 3, 4, 5)):
        """ create a dataframe for the activities in the database for a period of time based on 30 minutes intervals """
        # Get all activities in the interval
        activities = self.get_activities_by_set_of_types(types, start_date, end_date)

        # Add the time to the dataframe
        for i in range(START_OF_DAY_HOUR, END_OF_DAY_HOUR):
            self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 2, 'Time'] = f'{i}:00'
            self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 2 + 1, 'Time'] = f'{i}:30'

            if DEBUG:
                self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 2, 'index'] = f'{(i - START_OF_DAY_HOUR) * 2}'
                self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 2 + 1, 'index'] = f'{(i - START_OF_DAY_HOUR) * 2 + 1}'

        # Add all activities to the dataframe
        if DEBUG:
            print("create_weekly_dataframe_30_mins:", activities)

        for activity in activities:
            self.add_activity_to_dataframe(activity)

        # Fill all empty cells with empty string
        self.df_weekly.fillna('', inplace=True)

        return self.df_weekly

    def create_weekly_dataframe_15_mins(self, start_date, end_date, types: tuple = (0, 1, 2, 3, 4, 5)):
        """ create a dataframe for the activities in the database for a period of time based on 15 minutes intervals """
        # Get all activities in the interval
        activities = self.get_activities_by_set_of_types(types, start_date, end_date)

        # Add the time to the dataframe
        for i in range(START_OF_DAY_HOUR, END_OF_DAY_HOUR):
            self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4, 'Time'] = f'{i}:00'
            self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4 + 1, 'Time'] = f'{i}:15'
            self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4 + 2, 'Time'] = f'{i}:30'
            self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4 + 3, 'Time'] = f'{i}:45'

            if DEBUG:
                self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4, 'index'] = f'{(i - START_OF_DAY_HOUR) * 4}'
                self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4 + 1, 'index'] = f'{(i - START_OF_DAY_HOUR) * 4 + 1}'
                self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4 + 2, 'index'] = f'{(i - START_OF_DAY_HOUR) * 4 + 2}'
                self.df_weekly.loc[(i - START_OF_DAY_HOUR) * 4 + 3, 'index'] = f'{(i - START_OF_DAY_HOUR) * 4 + 3}'

        # Add all activities to the dataframe
        if DEBUG:
            print("create_weekly_dataframe_15_mins:", activities)

        for activity in activities:
            self.add_activity_to_dataframe(activity)

        # Fill all empty cells with empty string
        self.df_weekly.fillna('', inplace=True)

        return self.df_weekly

    def visualize_calendar(self, start_date, end_date):
        """ Visualize the calendar for the interval of start_date to end_date and save it as an image.
        It needs to be in a timetable format. (Columns should be days of the week and rows should be hours of
        the day)
        The rows need title of each hour and the columns need the day of the week.
        """

        # Create the dataframe
        if TIME_INTERVAL_TYPE == 1:
            self.create_weekly_dataframe_15_mins(start_date, end_date)
        elif TIME_INTERVAL_TYPE == 2:
            self.create_weekly_dataframe_30_mins(start_date, end_date)
        else:
            self.create_weekly_dataframe_hourly(start_date, end_date)

        # Create the figure and axes objects
        fig, ax = plt.subplots()

        # Remove the axes
        ax.axis('off')

        # Create the table
        table: matplotlib.table.Table = ax.table(cellText=self.df_weekly.values, colLabels=self.df_weekly.columns,
                                                 loc='center')

        # Set the cell width
        table.auto_set_column_width(col=list(range(len(self.df_weekly.columns))))

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

        fig.show()
