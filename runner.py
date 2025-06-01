import asyncio
from scheduler import reminder_loop, poll_messages

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # создаём два фоновых таска
    loop.create_task(reminder_loop())
    loop.create_task(poll_messages())
    # зациклваем event loop
    print("Запускаем бота (две фоновые корутины: reminder_loop и poll_messages)...")
    loop.run_forever()
