from datetime import datetime, timedelta
from typing import Set, List
from pydantic import BaseModel #for validatoin

class Reminder(BaseModel):
    time : datetime
    text : str
    chat_id : int
    sent : bool = False

reminders: List[Reminder] = []