from scheduler import Scheduler

scheduler = Scheduler()

scheduler.create_tables()

scheduler.insert_user("sadra_s", "sadra", "s.setarehdan@mail.utoronto.ca")
scheduler.insert_activity('sadra_s', 'test', 'test', 1, '1-22-2024', '13:00', '16:00')
scheduler.insert_activity("sadra_s", "test2", "test2", 1, "1-22-2024", "13:00", "16:00", True, 0, "1-25-2024")
# Jeremy part 😅
