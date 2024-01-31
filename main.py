import re

import requests
import json
from scheduler import Scheduler
from keys import TOKEN, CHANNEL_ID

scheduler = Scheduler()

scheduler.create_tables()

# scheduler.insert_user("sadra_s", "sadra", "test@test.com")
# # scheduler.insert_activity('sadra_s', 'test', 'test', 1, '01-22-2024', '15:00', '16:00')
# # scheduler.insert_activity("sadra_s", "test2", "test2", 2, "01-22-2024", "13:00", "16:00", True, 0, "01-25-2024")
# # scheduler.insert_activity("sadra_s", "test3", "test3", 2, "01-25-2024", "9:00", "12:00", True, 0, "01-25-2024")
# # scheduler.insert_activity("sadra_s", "test4", "test4", 1, "01-27-2024", "19:00", "21:00", True, 0, "01-25-2024")
# # scheduler.insert_activity("sadra_s", "test5", "test4", 1, "01-23-2024", "12:15", "14:35", True, 0, "01-25-2024")
# scheduler.visualize_calendar("1-22-2024", '1-29-2024')
# Jeremy part 😅

BASE_URL = 'https://discord.com/api/v10'


def get_messages(channel_id):
    """ get messages from a channel from discord API """
    url = f'{BASE_URL}/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    return response.json()


def send_message(channel_id, content):
    url = f'{BASE_URL}/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'content': content,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


def handle_command(channel_id, command, arguments):
    """ handle a command sent by a user"""

    response_content = ''

    if command == '!add_user':
        # Add a user to the database

        # Extract username, name and email from arguments
        parts = arguments.split(";")
        if len(parts) != 3:
            send_message(channel_id, "Invalid arguments. (Need username;name;email)")
            return

        username = parts[0]
        name = parts[1]
        email = parts[2]

        # Add the user to the database
        scheduler.insert_user(username, name, email)

        response_content = f"User {username} added successfully"

    elif command == '!add_activity':
        # Add an activity to the database

        # Extract username, title, description, act_type, date, start_time, end_time, is_recurring=False,
        #                         recurring_pattern=None, recurring_end_date=None
        parts = arguments.split(";")
        if len(parts) != 7 and len(parts) != 10:
            send_message(channel_id,
                         "Invalid arguments. (Need username;title;description;act_type;date;start_time;end_time or "
                         "username;title;description;act_type;date;start_time;end_time;is_recurring;recurring_pattern"
                         ";recurring_end_date)")
            return

        username = parts[0]
        title = parts[1]
        description = parts[2]
        act_type = int(parts[3])
        date = parts[4]
        start_time = parts[5]
        end_time = parts[6]

        # check validity of input
        if (act_type < 0 or act_type > 5 or len(date) != 10
                or not re.search(r"[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]", date)
                or len(start_time) != 5 or not re.search("[0-9][0-9]-[0-9][0-9]", start_time)
                or len(end_time) != 5 or not re.search("[0-9][0-9]-[0-9][0-9]", end_time)):
            send_message(channel_id, "Invalid arguments. (act_type must be 0-5, date must be mm-dd-yyyy, start_time "
                                     "and end_time must be hh:mm)")
            return

        is_recurring = False
        recurring_pattern = None
        recurring_end_date = None

        if len(parts) > 7 and parts[7] == 'True':
            is_recurring = parts[7]
            recurring_pattern = parts[8]
            recurring_end_date = parts[9]

        # Add the activity to the database
        scheduler.insert_activity(username, title, description, act_type, date, start_time, end_time, is_recurring,
                                  recurring_pattern, recurring_end_date)

        response_content = f"Activity {title} added successfully"

    elif command == '!help':
        if arguments == '':
            # Show the list of commands
            response_content = """List of commands:
!add_user username;name;email 
!add_activity username;title;description;act_type;date;start_time;end_time (not recurring)
!add_activity username;title;description;act_type;date;start_time;end_time;is_recurring;recurring_pattern;recurring_end_date
!help command - Show this message"""

        elif arguments == '!add_user':
            response_content = """Help: !add_user username;name;email
    - Add a user to the database
    - Example: !add_user tes_t;test;test@test.com
    - username: The username of the user
    - name: The name of the user
    - email: The email of the user"""

        elif arguments == '!add_activity':
            response_content = """Help: !add_activity username;title;description;act_type;date;start_time;end_time (not recurring)
    - Add an activity to the database (not recurring)
    - Example: !add_activity tes_t;test;test;1;1-22-2024;15:00;16:00
    - username: The username of the user
    - title: The title of the activity
    - description: The description of the activity
    - act_type: The type of the activity (0-Busy 1-Group Meeting 2-Personal Optional 3-Group Optional 4-Fun 5-Other)
    - date: The date of the activity (format: m-d-yyyy)
    - start_time: The start time of the activity (format: hh:mm)
    - end_time: The end time of the activity (format: hh:mm)
    
- Add an activity to the database (recurring)
    - Example: !add_activity tes_t;test;test;1;1-22-2024;15:00;16:00;True;2;1-25-2024
    - username: The username of the user
    - title: The title of the activity
    - description: The description of the activity
    - act_type: The type of the activity (0-Busy 1-Group Meeting 2-Personal Optional 3-Group Optional 4-Fun 5-Other)
    - date: The date of the activity (format: mm-dd-yyyy)
    - start_time: The start time of the activity (format: hh:mm)
    - end_time: The end time of the activity (format: hh:mm)
    - is_recurring: True if the activity is recurring, False otherwise
    - recurring_pattern: The pattern of the recurring activity (0-Daily 1-Weekly 2-Monthly 3-Yearly)
    - recurring_end_date: The end date of the recurring activity (format: mm-dd-yyyy)"""

    else:
        response_content = 'Unknown command. Use !help to see the list of commands'

    send_message(channel_id, response_content)


def main():
    # Replace 'YOUR_CHANNEL_ID' with the actual channel ID where you want the bot to operate
    channel_id = CHANNEL_ID

    # set of checked messages ids
    checked_messages_files = open("message_ids.txt", "r")
    list_of_messages = checked_messages_files.readlines()
    for i in range(len(list_of_messages)):
        list_of_messages[i] = list_of_messages[i].strip()

    checked_messages = set(list_of_messages)
    checked_messages_files.close()

    while True:
        messages = get_messages(channel_id)
        checked_messages_files = open("message_ids.txt", "a")

        for message in messages:
            if message['id'] in checked_messages:
                continue

            checked_messages.add(message['id'])
            checked_messages_files.write(message['id'] + "\n")

            # Check if the message is a command
            if message['content'].startswith('!'):
                # Extract command and arguments
                parts = message['content'].split(maxsplit=1)
                command = parts[0]
                arguments = parts[1] if len(parts) > 1 else ''

                # Handle the command
                handle_command(channel_id, command, arguments)

        checked_messages_files.close()


if __name__ == "__main__":
    main()
