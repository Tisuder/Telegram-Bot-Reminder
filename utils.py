import requests
import re
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")

def send_telegram_message(text: str, chat_id: int):
    """
    Отправляет текстовое сообщение в заданный чат
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, data=data)


def get_updates(offset: int | None = None, timeout: int = 30) -> dict:
    """
    Вызываем метод getUpdates с опциональным offset’ом, 
    чтобы получить только новые апдейты.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params: dict = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def parse_reminder(text: str) -> tuple[datetime, str]:
    """
    Парсит строку вида:
      - "через 2 часа 30 минут купить молоко"
      - "через 15 минут позвонить маме"
      - "Напомни купить молоко в 19:00"
      - "Напомни позвонить в дурку через 2 часа 30 минут"
      - "22.05.2025 18:30 встретиться с Иваном"
    Возвращает tuple(дата_выполнения, текст_напоминания).
    """
    now = datetime.now()
    # через N часов [M минут]
    # [А-Яа-яЁё]
    m = re.match(r'[\sА-Яа-яЁё]*через\s+(\d+)\s*час(?:а|ов)?(?:\s+(\d+)\s*минут(?:ы|а|у)?)?\s+(.+)', text, flags=re.IGNORECASE)
    if m:
        hours = int(m.group(1))
        minutes = int(m.group(2) or 0)
        return now + timedelta(hours=hours, minutes=minutes), m.group(3).strip()
    # через N минут
    m = re.match(r'[\sА-Яа-яЁё]*через\s+(\d+)\s*минут(?:ы|а|у|ку)?\s+(.+)', text, flags=re.IGNORECASE)
    if m:
        minutes = int(m.group(1))
        return now + timedelta(minutes=minutes), m.group(2).strip()
    # Напомни ... в HH:MM
    m = re.match(r'напомни\s+(.+?)\s+в\s+(\d{1,2}):(\d{2})', text, flags=re.IGNORECASE)
    if m:
        msg = m.group(1).strip()
        h, min_ = int(m.group(2)), int(m.group(3))
        dt = now.replace(hour=h, minute=min_, second=0, microsecond=0)
        if dt < now:
            dt += timedelta(days=1)
        return dt, msg
    # Напомни <text> через n часов N минут
    m = re.match(
        r"[\sА-Яа-яЁё]*напомни\s+(.+?)\s+через\s+(\d+)\s*час(?:а|ов)?(?:\s+(\d+)\s*минут(?:ы|а)?)?", text, flags=re.IGNORECASE)
    if m:
        msg = m.group(1).strip()
        hours = int(m.group(2))
        minutes = int(m.group(3) or 0)
        return now + timedelta(hours=hours, minutes=minutes), msg
    # dd.mm.yyyy HH:MM или d.m.yy H:M
    m = re.match(r'[\sА-Яа-яЁё]*(\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?)\s+(\d{1,2}):(\d{2})\s+(.+)', text)
    if m:
        from datetime import datetime as _dt
        date_str, h, min_, msg = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4).strip()
        for fmt in ("%d.%m.%Y", "%d.%m.%y", "%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
            try:
                d = _dt.strptime(date_str, fmt)
                return d.replace(hour=h, minute=min_, second=0, microsecond=0), msg
            except ValueError:
                continue
        raise ValueError("Не удалось распознать дату")
    raise ValueError("Не удалось распознать формат напоминания")


