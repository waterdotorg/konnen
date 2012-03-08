"""
Sms backend that writes messages to console instead of sending them.
"""
import sys
import threading

from sms.backends.base import BaseEmailBackend

class SmsBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()
        super(SmsBackend, self).__init__(*args, **kwargs)

    def send_messages(self, messages):
        """Write all messages to the stream in a thread-safe way."""
        if not messages:
            return
        self._lock.acquire()
        try:
            # The try-except is nested to allow for
            # Python 2.4 support (Refs #12147)
            try:
                stream_created = self.open()
                for message in messages:
                    self.stream.write('%s\n' % self.render_message(message))
                    self.stream.write('-'*79)
                    self.stream.write('\n')
                    self.stream.flush()  # flush after each message
                if stream_created:
                    self.close()
            except:
                if not self.fail_silently:
                    raise
        finally:
            self._lock.release()
        return len(messages)

    def render_message(message):
        return u"""from: %(from)s\nto: %(recipient_list)s\nflash: %(flash)s\n%(message)s""" % {
            'from': message.from_phone,
            'recipient_list': ", ".join(message.recipient_list),
            'flash': message.flash,
            'message': message.message,
        }
