import asyncio
from fastapi import FastAPI
from models import Reminder, reminders
from storage import update_db
from scheduler import reminder_loop, poll_messages

app = FastAPI()

@app.on_event("startup")
async def startup():
    #стартуем фоновые задачи: шедулер и поллинг
    asyncio.create_task(reminder_loop())
    asyncio.create_task(poll_messages())

#ручной API для добавления:
@app.post("/add")
async def add_api(rem: Reminder):
    reminders.append(rem)
    await update_db(reminders)
    return {"status": "added", "time": rem.time.isoformat()}
