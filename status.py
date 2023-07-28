# --------------------------------------------------------------------
# status.py
#
# Author: Lain Musgrove (lain.musgrove@gmail.com)
# Date: Thursday July 27, 2023
# --------------------------------------------------------------------

from datetime import datetime
from dataclasses import dataclass
from typing import Callable

from maths import secs


# --------------------------------------------------------------------
MessageCallback = Callable[["Message"], str]


# --------------------------------------------------------------------
@dataclass
class Message:
    subject: str
    callback: MessageCallback
    display_sec: float
    update_sec: float
    content: str = "(empty)"
    display_ttl: datetime = datetime.min
    update_ttl: datetime = datetime.min

    def update(self, now: datetime) -> bool:
        if self.display_ttl == datetime.min:
            if self.display_sec > 0:
                self.display_ttl = now + secs(self.display_sec)
            else:
                self.display_ttl = datetime.max

        if self.display_ttl < now:
            return False

        if self.update_ttl < now:
            self.content = self.callback(self)
            if self.update_sec > 0:
                self.update_ttl = now + secs(self.update_sec)
            else:
                self.update_ttl = datetime.max

        return True


# --------------------------------------------------------------------
class IdleMessage(Message):
    def __init__(self):
        super().__init__("idle", self._print, 0, 0.01)
        self.animation = "/-\\|"
        self.offset = 0

    def _print(self, msg: Message):
        return self.animation[self.offset]

    def update(self, now: datetime):
        super().update(now)
        self.offset = (self.offset + 1) % len(self.animation)
        return True


# --------------------------------------------------------------------
class Status:
    idle = IdleMessage()
    update_sec = 0.05

    subjects: list[str] = []
    messages: dict[str, Message] = {}
    offset = -1
    rotate_sec: float = 1.0
    offset_ttl: datetime = datetime.min

    @classmethod
    def update_messages(cls, now: datetime):
        dead_keys = [k for k, m in cls.messages.items() if not m.update(now)]
        for key in dead_keys:
            del cls.messages[key]
        cls.subjects = [subj for subj in cls.subjects if subj in cls.messages]

        if cls.offset >= len(cls.subjects):
            cls.offset = len(cls.subjects) - 1

    @classmethod
    def show(
        cls,
        subject: str,
        message_f: str | MessageCallback,
        display_sec=1.0,
        update_sec=0,
    ):
        callback = message_f if callable(message_f) else (lambda m: str(message_f))
        new_subject = subject not in cls.messages
        cls.messages[subject] = Message(subject, callback, display_sec, update_sec)
        if new_subject:
            cls.subjects.append(subject)

    @classmethod
    def update(cls) -> str:
        now = datetime.now()
        cls.update_messages(now)

        if cls.subjects:
            if cls.offset_ttl < now or cls.offset < 0:
                cls.offset = (cls.offset + 1) % len(cls.subjects)
                cls.offset_ttl = now + secs(cls.rotate_sec)
            message = cls.messages[cls.subjects[cls.offset * -1]]

        else:
            message = Status.idle
            message.update(now)
            cls.offset = -1

        return message.content
