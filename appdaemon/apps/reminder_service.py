from abc import ABC, abstractmethod
from datetime import timedelta, datetime, timezone, time, date
from typing import Dict, Any

import appdaemon.plugins.hass.hassapi as hass
from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_HOST = 'mongo'
MONGO_PORT = 27017

DEFAULT_TIME_FOR_REMINDER = time(hour=9, minute=0)
HOME_TELEGRAM = 'teledobbygroup'


class SendTarget(ABC):
    @abstractmethod
    def service(self) -> str:
        pass

    @abstractmethod
    def kwargs(self) -> Dict:
        pass

    @abstractmethod
    def dict(self) -> Dict:
        pass


class NotifyTarget(SendTarget):
    def __init__(self, service_name: str):
        self._service_name = service_name

    def service(self) -> str:
        return f'notify/{self._service_name}'

    def kwargs(self) -> Dict:
        return {}

    def dict(self):
        return {'notify': self._service_name}


class TelegramTarget(SendTarget):
    def __init__(self, chat_id: str):
        self._chat_id = chat_id

    def service(self) -> str:
        return 'telegram_bot/send_message'

    def kwargs(self) -> Dict:
        return {'target': self._chat_id}

    def dict(self):
        return {'chat_id': self._chat_id}


def get_send_target(send_to_dict: dict):
    if 'notify' in send_to_dict:
        return NotifyTarget(send_to_dict['notify'])
    if 'chat_id' in send_to_dict:
        return TelegramTarget(send_to_dict['chat_id'])
    return NotifyTarget(HOME_TELEGRAM)


class ReminderRecord:
    TypeName = "ReminderRecord"

    def __init__(self, message: str, send_at: datetime, send_to: SendTarget,
                 is_sent: bool, modified_on: datetime, _id=None):
        """
        send_at must be specified in local time. Translation to and from UTC for the database is handled by the
        encode and decode methods.
        """
        self.id_ = _id
        self.message = message
        self.send_at = send_at
        self.send_to = send_to
        self.is_sent = is_sent
        self.modified_on = modified_on

    @classmethod
    def new(cls, message: str, send_at: datetime,
            send_to: SendTarget = HOME_TELEGRAM):
        return cls(message=message,
                   send_at=send_at,
                   send_to=send_to,
                   is_sent=False,
                   modified_on=datetime.utcnow())

    @property
    def notify_service(self) -> str:
        return self.send_to.service()

    @property
    def notify_kwargs(self) -> dict:
        return self.send_to.kwargs()

    def encode(self) -> Dict[str, Any]:
        self: ReminderRecord
        return {
            "type": self.TypeName,
            "message": self.message,
            "send_at": self.send_at.astimezone().astimezone(timezone.utc),
            "send_to": self.send_to.dict(),
            "is_sent": self.is_sent,
            "modified_on": datetime.utcnow(),
        }

    @classmethod
    def decode(cls, doc: dict):
        assert doc["type"] == cls.TypeName
        return cls(
            _id=doc.get("_id", None),
            message=doc.get("message", ""),
            send_at=doc["send_at"].replace(tzinfo=timezone.utc).astimezone(),
            send_to=get_send_target(doc.get("send_to", {})),
            is_sent=doc["is_sent"],
            modified_on=doc["modified_on"])


# noinspection PyAttributeOutsideInit
class ReminderService(hass.Hass):

    def initialize(self):
        self.setup_storage()
        self.load_state({})
        self.listen_event(self.set_reminder, event='ad_reminder_set')
        self.listen_event(self.read_all_reminders, event='ad_reminder_read')
        self.run_minutely(self.load_state,
                          start=self.now().replace(second=1, microsecond=0).time())

    def setup_storage(self):
        storage_client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.collection: Collection = storage_client.ad_db.reminders
        self.close_storage_conn = lambda: storage_client.close()

    def load_state(self, kwargs):
        unsent_reminders = self.collection.find({
            'is_sent': False,
            'send_at': {
                '$lte': (self.now() + timedelta(minutes=1)).replace(second=0, microsecond=0)
            }
        })
        [self._send_reminder(doc)
         for doc in unsent_reminders]

    def _send_reminder(self, doc):
        record = ReminderRecord.decode(doc)
        send_at = record.send_at.replace(second=0, microsecond=0)
        now = self.now().replace(second=0, microsecond=0)
        if send_at > now:
            return
        if send_at == now:
            self.send_reminder({"storage_id": record.id_})
            return
        self._send_reminder_if_it_is_late(record, send_at)

    def _send_reminder_if_it_is_late(self, record, send_at):
        self.log(f'Found unsent reminder that was scheduled for {send_at}')
        record.message += f' (Originally scheduled to be sent at {send_at})'
        self.collection.update_one(
            filter={"_id": record.id_},
            update={'$set': {
                'message': record.message,
                'modified_on': self.now().astimezone(timezone.utc)  # The DB needs UTC
            }})
        self.send_reminder({"storage_id": record.id_})

    def set_reminder(self, event_name: str, data, kwargs: dict):
        """
        :param data: requires 'at' or 'in' key, with as value a dictionary of 
        the keyword arguments to:
        date, time or datetime if the key is 'at'
        timedelta if the key is 'in'
        if both are given, 'in' takes precedence
        optional keys are:
        message: str    message to send at the indicated time
        send_to: dict   if given, should contain either a 'notify' or 'chat_id' 
        key, with a str value for either
            - the notify service name or the telegram chat_id to send the
              message to
            - if not given, it will be sent to the default target
        """
        self.log(f'Received event of type {event_name}\n with data: {data}')
        record = self._create_reminder_record(data)
        if record.send_at < self.now():
            record.send_at += timedelta(days=1)
        storage_id = self.collection.insert_one(record.encode())
        self.log(f'Scheduled reminder at {record.send_at}')
        self._notify_of_set_reminder(record)

    def _notify_of_set_reminder(self, record: ReminderRecord):
        time_to_reminder: timedelta = record.send_at - self.now()
        self.call_service(
            record.notify_service,
            message=f'Over ' +
                    self._format_as_hours_minutes(time_to_reminder) +
                    ' stuur ik: '
                    f'"{record.message}"')

    def _create_reminder_record(self, data: dict) -> ReminderRecord:
        send_at = self._get_reminder_time(data)
        return ReminderRecord.new(
            message=data.get("message",
                             f"This is a reminder, scheduled at {self.now()}"),
            send_at=send_at,
            send_to=get_send_target(data.get("send_to", {})))

    def _get_reminder_time(self, data) -> datetime:
        in_when = data.get("in", None)
        if in_when is not None:
            period = timedelta(**in_when)
            return self.now() + period
        at_when = data.get("at", None)
        if at_when is not None:
            send_at_local = datetime.combine(
                self._try_get_date(at_when),
                self._try_get_time(at_when)
            )
            return send_at_local.astimezone()
        raise ValueError("Data of ad_reminder_set event must contain 'in' or 'at' info")

    def _try_get_date(self, data: Dict[str, int]) -> date:
        try:
            return date(**data)
        except TypeError:
            return self.today()

    @staticmethod
    def _try_get_time(data: Dict[str, float]) -> time:
        try:
            return time(**data)
        except TypeError:
            return DEFAULT_TIME_FOR_REMINDER

    def send_reminder(self, kwargs: dict):
        this_reminder_by_id = {"_id": kwargs["storage_id"]}
        record = ReminderRecord.decode(
            self.collection.find_one(this_reminder_by_id))
        self.call_service(
            record.notify_service,
            message=record.message,
            **record.notify_kwargs)
        self.collection.update_one(
            this_reminder_by_id,
            {'$set': {
                'is_sent': True,
                'modified_on': self.now().astimezone(timezone.utc)  # The DB needs UTC
            }})

    def read_all_reminders(self, event_name: str, data, kwargs: dict):
        self.log(f'Received event of type {event_name}')
        docs = self.collection.find()
        self.log(str(list(docs)))

    @staticmethod
    def _format_as_hours_minutes(td: timedelta) -> str:
        """ Formats timedelta like 12u30, 1u00 (NL localized)"""
        return "u".join(
            str(td + timedelta(seconds=1)
                ).split(":")[:-1])

    def now(self) -> datetime:
        """ Returns the local datetime, aware with the current timezone """
        return self.datetime(aware=True)  # noqa

    def today(self) -> date:
        return self.date()  # noqa

    def __del__(self):
        self.close_storage_conn()
