"""
Twilio sms gateway backend.

Configuration example.
~~~~~~~~~~~~~~~~~~~~~~

Modify your settings.py::

    SMS_BACKEND = 'sms.backends.twilio.SmsBackend'
    SMS_ACCOUNT_SID = 'foo'
    SMS_ACCOUNT_TOKEN = 'bar'
    SMS_PHONE_NUMBER = '+13215439876'
    INSTALLED_APPS += ['sms']

Usage::

    from sms.message import SmsMessage
    message = SmsMessage(
        body = 'my 160 chars sms',
        from_phone = '111111111',
        recipient_list = ['222222222',]
    )
    message.send()
"""

from django.conf import settings
from dateutil import parser
from twilio.rest import TwilioRestClient
from sms.backends.base import BaseSmsBackend
from sms.models import Sms

class SmsBackend(BaseSmsBackend):
    """
    SMS Backend for Twilio provider.
    """

    def __init__(self, *args, **kwargs):
        super(SmsBackend, self).__init__(*args, **kwargs)
        self.account_sid = getattr(settings, 'SMS_ACCOUNT_SID')
        self.account_token = getattr(settings, 'SMS_ACCOUNT_TOKEN')
        self.phone_number = getattr(settings, 'SMS_PHONE_NUMBER', None)
        self.connection = TwilioRestClient(self.account_sid, self.account_token)

    def send_messages(self, message, recipient_list, from_phone=None):
        if not from_phone:
            from_phone = self.phone_number
        for recipient in recipient_list:
            self.connection.sms.messages.create(to=recipient, from_=from_phone, body=message)
        return True

    def get_messages(self, *args, **kwargs):
        if self.phone_number:
            kwargs.update({'to': self.phone_number})
        messages = self.connection.sms.messages.list(*args, **kwargs)
        for message in messages:
            try:
                Sms.objects.get(
                    from_number=message.from_,
                    to_number=message.to,
                    message=message.body,
                    sent_date=parser.parse(message.date_sent),
                )
                break
            except Sms.DoesNotExist:
                sms = Sms(
                    from_number=message.from_,
                    to_number=message.to,
                    message=message.body,
                    sent_date=parser.parse(message.date_sent),
                )
                sms.save()
        return True