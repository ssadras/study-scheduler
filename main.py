from scheduler import Scheduler
from disctoken import token
import discord


scheduler = Scheduler()

scheduler.create_tables()

scheduler.insert_user("sadra_s", "sadra", "test@test.com")
# scheduler.insert_activity('sadra_s', 'test', 'test', 1, '1-22-2024', '15:00', '16:00')
# scheduler.insert_activity("sadra_s", "test2", "test2", 2, "1-22-2024", "13:00", "16:00", True, 0, "1-25-2024")
# scheduler.insert_activity("sadra_s", "test3", "test3", 2, "1-25-2024", "9:00", "12:00", True, 0, "1-25-2024")
# scheduler.insert_activity("sadra_s", "test4", "test4", 1, "1-27-2024", "19:00", "21:00", True, 0, "1-25-2024")
# scheduler.insert_activity("sadra_s", "test5", "test4", 1, "1-23-2024", "12:15", "14:35", True, 0, "1-25-2024")
scheduler.visualize_calendar("1-22-2024", '1-29-2024')
# Jeremy part 😅


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token)
