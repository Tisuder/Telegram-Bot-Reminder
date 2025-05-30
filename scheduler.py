import asyncio
from datetime import datetime
from models import reminders, Reminder
from utils import send_telegram_message
from storage import get_db, update_db
from utils import get_updates, parse_reminder

async def reminder_loop():
    """
    Бесконечный цикл, который раз в 10 секунд
    проверяет напоминалки и отправляет сообщения.
    """
    # один раз при старте подтягиваем из файла
    await get_db()
    while True:
        now = datetime.now()
        changed = False
        for r in reminders:
            # отправка напоминания
            if not r.sent and r.time <= now:
                send_telegram_message(f'Напоминаю, что:\n{r.text}', r.chat_id)
                r.sent = True
                changed = True
        if changed:
            await update_db(reminders)
        await asyncio.sleep(10)


async def poll_messages():
    """
    Бесконечный цикл, который раз в секунду
    вызывает getUpdates и обрабатывает новые сообщения.
    """
    last_update_id: int | None = None

    while True:
        data = get_updates(offset=(last_update_id + 1) if last_update_id is not None else None)
        for upd in data.get("result", []):
            uid = upd["update_id"]
            # пропускаем уже прочитанные апдейты
            if last_update_id is None or uid > last_update_id:
                last_update_id = uid

                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg["text"]

                # парсим команду
                try:
                    dt, body = parse_reminder(text)
                except ValueError as e:
                    send_telegram_message(f"Ошибка парсинга: {e}", chat_id)
                    continue

                # сохраняем напоминание
                rem = Reminder(time=dt, text=body, chat_id=chat_id)
                reminders.append(rem)
                await update_db(reminders)

                # подтверждаем пользователю
                send_telegram_message(
                    f"Напоминание установлено на {dt.strftime('%Y-%m-%d %H:%M')}",
                    chat_id
                )
        await asyncio.sleep(1)