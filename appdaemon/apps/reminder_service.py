from datetime import timedelta, datetime
from enum import Enum
from typing import List, Set

import appdaemon.plugins.hass.hassapi as hass
from pymongo import MongoClient


class SendTarget(Enum):
    HOME_TELEGRAM = 'home_telegram'


class ReminderRecord:
    TypeName = "ReminderRecord"

    def __init__(self, message: str, send_at: datetime, send_to: SendTarget,
                 is_sent: bool, modified_on: datetime):
        self.message = message
        self.send_at = send_at
        self.send_to = send_to
        self.is_sent = is_sent
        self.modified_on = modified_on

    @classmethod
    def new(cls, message: str, send_at: datetime,
            send_to: SendTarget = SendTarget.HOME_TELEGRAM):
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
            "send_at": self.send_at,
            "send_to": self.send_to.value,
            "is_sent": self.is_sent,
            "modified_on": datetime.utcnow(),
        }

    @classmethod
    def decode(cls, doc: dict):
        assert doc["type"] == cls.TypeName
        return cls(
            message=doc.get("message", default=""),
            send_at=doc["send_at"],
            send_to=SendTarget[doc.get("send_to", default='home_telegram').upper()],
            is_sent=doc["is_sent"],
            modified_on=doc["modified_on"])


# noinspection PyAttributeOutsideInit
class ReminderService(hass.Hass):

    def initialize(self):
        self.connect_mongo()
        self.listen_event(self.set_reminder, event='ad_reminder_set')
        self.listen_event(self.read_reminder, event='ad_reminder_read')

    def connect_mongo(self):
        self.client = MongoClient(host='172.30.33.4', port=27017)
        db = self.client.admin
        serverStatusResult = db.command("serverStatus")
        # self.log(serverStatusResult)

    def set_reminder(self, event_name, data, kwargs):
        self.log(f'Received event of type {event_name}')
        dt = datetime.utcnow()
        record = ReminderRecord.new(data["message"], dt)
        self.client.ad_db.reminders.insert(
            record.encode()
        )

    def read_reminder(self, event_name, data, kwargs):
        self.log(f'Received event of type {event_name}')
        doc = self.client.ad_db.reminders.find_one()
        self.log(doc)


def get_instance_attributes(obj: object) -> Set[str]:  # TODO use this instead of manually enumerating attributes
    attrs_incl_class = (a for a in dir(obj)
                        if not a.startswith('__')
                        and not callable(getattr(obj, a)))
    class_attributes = dir(type(obj))
    return set(attrs_incl_class) - set(class_attributes)
