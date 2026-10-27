from datetime import datetime, timedelta

from decimal import Decimal, ROUND_HALF_UP

from surety import Array, Bool, DateTime, Dictionary, Int, String, Uuid, Float
from surety.sdk import dates
from surety.sdk.fakeable import fake


class Keys:
    ApiKey = 'devboard_api_key'
    TaskDraft = 'devboard_task_draft'


class TaskDraft(Dictionary):
    Title = String(name='title')
    Description = String(name='description')
    Labels = String(name='labels')
