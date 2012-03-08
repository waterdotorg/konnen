from django.conf import settings
from django.utils.encoding import smart_str

from sms.signals import sms_post_send

class SmsMessage(object):
    """
    A sms message
    """
    encoding = None     # None => use settings default

    def __init__(self, message='', from_phone=None, recipient_list=None, flash=False, connection=None):
        """
        Initialize a single SMS message (which can be sent to multiple recipients)
        """
        if recipient_list:
            assert not isinstance(recipient_list, basetring), '"recipient_list" argument must be a list or tuple'
            self.recipient_list = list(recipient_list)
        else:
            self.recipient_list = []

        self.from_phone = from_phone or getattr(settings, 'SMS_DEFAULT_FROM_PHONE', '')
        self.message = message
        self.flash = flash
        self.connection = connection

    def get_connection(self, fail_silently=False):
        from sms import get_connection
        if not self.connection:
            self.connection = get_connection(fail_silently=fail_silently)
        return self.connection

    def send(self, fail_silently=False):
        """
        Sends the sms message
        """
        if not self.recipient_list:
            # Don't bother creating the connection if there's nobody to send to
            return 0
        result = self.get_connection(fail_silently).send_messages([self])
        sms_post_send.send(sender=self, recipient_list=self.recipient_list, from_phone=self.from_phone,
            message=self.message, result=result)
        return result