from datetime import timedelta, datetime, timezone, time, date

import appdaemon.plugins.hass.hassapi as hass
from pymongo import MongoClient

MONGO_HOST = '172.30.33.4'
MONGO_PORT = 27017

DEFAULT_TIME_FOR_REMINDER = time(hour=9, minute=0)
HOME_TELEGRAM = 'teledobbygroup'


class ReminderRecord:
    TypeName = "ReminderRecord"

    def __init__(self, message: str, send_at: datetime, send_to: str,
                 is_sent: bool, modified_on: datetime, _id=None):
        self.id_ = _id
        self.message = message
        self.send_at = send_at
        self.send_to = send_to
        self.is_sent = is_sent
        self.modified_on = modified_on

    @classmethod
    def new(cls, message: str, send_at: datetime,
            send_to: str = HOME_TELEGRAM):
        return cls(message=message,
                   send_at=send_at,
                   send_to=send_to,
                   is_sent=False,
                   modified_on=datetime.utcnow())

    def encode(self):
        self: ReminderRecord
        return {
            "type": self.TypeName,
            "message": self.message,
            "send_at": self.send_at.astimezone(timezone.utc),
            "send_to": self.send_to,
            "is_sent": self.is_sent,
            "modified_on": datetime.utcnow(),
        }

    @classmethod
    def decode(cls, doc: dict):
        assert doc["type"] == cls.TypeName
        return cls(
            _id=doc.get("_id", None),
            message=doc.get("message", ""),
            send_at=doc["send_at"].astimezone(timezone.utc).astimezone(),
            send_to=doc.get("send_to", HOME_TELEGRAM),
            is_sent=doc["is_sent"],
            modified_on=doc["modified_on"])


# noinspection PyAttributeOutsideInit
class ReminderService(hass.Hass):

    def initialize(self):
        self.setup_storage()
        self.load_state()
        self.listen_event(self.set_reminder, event='ad_reminder_set')
        self.listen_event(self.read_all_reminders, event='ad_reminder_read')

    def setup_storage(self):
        storage_client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.collection = storage_client.ad_db.reminders
        self.close_storage_conn = lambda: storage_client.close()

    def load_state(self):
        unsent_reminders = self.collection.find({'is_sent': False})
        for doc in unsent_reminders:
            record = ReminderRecord.decode(doc)
            self.log(f'Found unsent reminder that was scheduled for {record.send_at}')
            if record.send_at < self.now():
                record.send_at = self.now() + timedelta(seconds=1)
                record.message += f' (Originally scheduled to be sent at {record.send_at})'
            self.schedule_reminder(record.send_at, record.id_)

    def set_reminder(self, event_name, data, kwargs):
        self.log(f'Received event of type {event_name}')
        record = self.get_reminder_record(data)
        if record.send_at < self.now():
            record.send_at += timedelta(days=1)
        storage_id = self.collection.insert(record.encode())
        self.schedule_reminder(record.send_at, storage_id)

    def schedule_reminder(self, send_at, storage_id):
        self.run_at(self.send_reminder,
                    start=send_at.astimezone(),
                    storage_id=storage_id)

    def get_reminder_record(self, data: dict) -> ReminderRecord:
        send_at = self.get_reminder_time(data)
        return ReminderRecord.new(
            message=data.get("message",
                             f"This is a reminder, scheduled at {self.now()}"),
            send_at=send_at,
            send_to=data.get("send_to", HOME_TELEGRAM))

    def get_reminder_time(self, data) -> datetime:
        in_when = data.get("in", None)
        if in_when is not None:
            period = timedelta(**in_when)
            return self.now() + period
        at_when = data.get("at", None)
        if at_when is not None:
            send_at_local = datetime.combine(
                self.try_get_date(data),
                self.try_get_time(data)
            ).astimezone()
            return send_at_local.astimezone(timezone.utc)
        raise ValueError("Data of ad_reminder_set event must contain 'in' or 'at' info")

    def try_get_date(self, data: dict) -> date:
        try:
            return date(**data)
        except TypeError:
            return self.today()

    def try_get_time(self, data: dict) -> time:
        try:
            return time(**data)
        except TypeError:
            return DEFAULT_TIME_FOR_REMINDER

    def send_reminder(self, kwargs):
        this_reminder_by_id = {"_id": kwargs["storage_id"]}
        record = ReminderRecord.decode(
            self.collection.find_one(this_reminder_by_id))
        self.call_service(f'notify/{record.send_to}', message=record.message)
        self.collection.update_one(
            this_reminder_by_id,
            {'$set': {
                'is_sent': True,
                'modified_on': self.now().astimezone(timezone.utc)
            }})

    def read_all_reminders(self, event_name, data, kwargs):
        self.log(f'Received event of type {event_name}')
        docs = self.collection.find()
        self.log(str(list(docs)))

    def now(self) -> datetime:
        return self.datetime(aware=True)

    def today(self) -> date:
        return self.date()

    def __del__(self):
        self.close_storage_conn()
