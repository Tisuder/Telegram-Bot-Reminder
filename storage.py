import json
import aiofiles
from datetime import datetime
from models import Reminder, reminders

DB_FILE = 'reminders.json'

async def get_db():
    """
    при старте загружает все напоминания из файла в список reminders
    """
    try:
        async with aiofiles.open(DB_FILE, 'r', encoding='utf-8') as f:
            text = await f.read()
            data = json.loads(text)
            # data = json.load(f)
            for item in data:
                # ISO-строка -> datetime
                t = datetime.fromisoformat(item['time'])
                reminders.append(Reminder(
                    time=t,
                    text=item['text'],
                    chat_id=item['chat_id'],
                    sent=item.get('sent', False)
                ))
    except (FileNotFoundError, json.JSONDecodeError):
        # файла нет или пустой — просто игнорируем
        pass

async def update_db(rem_list: list[Reminder]):
    """
    записывает в файл все текущие напоминания (включая sent=True)
    """
    data = []
    for r in rem_list:
        data.append({
            'time': r.time.isoformat(),
            'text': r.text,
            'chat_id': r.chat_id,
            'sent': r.sent
        })
    text = json.dumps(data, ensure_ascii=False, indent=4)
    async with aiofiles.open(DB_FILE, 'w', encoding='utf-8') as f:
        await f.write(text)
 