"""
Backend for test environment.
"""

import sms
from sms.backends.base import BaseSmsBackend

class SmsBackend(BaseSmsBackend):
    """
    Backend for use during test sessions.

    The test connection stores sms messages in a dummy outbox, rather than sending them out over the wire.

    The dummy outbox is accessible through the outbox instance attribute.
    """
    def __init__(self, *args, **kwargs):
        super(SmslBackend, self).__init__(*args, **kwargs)
        if not hasattr(sms, 'outbox'):
            sms.outbox = []

    def send_messages(self, messages):
        """Redirect messages to the dummy outbox"""
        sms.outbox.extend(messages)
        return len(messages)