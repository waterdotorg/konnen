"""
Dummy sms backend that does nothing.
"""

from sms.backends.base import BaseEmailBackend

class SmsBackend(BaseEmailBackend):
    def send_messages(self, messages):
        return len(messages)
