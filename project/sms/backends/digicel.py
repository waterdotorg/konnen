"""
Digicel sms gateway backend.

Configuration example.
~~~~~~~~~~~~~~~~~~~~~~

Modify your settings.py::

    SMS_BACKEND = 'sms.backends.digicel.SmsBackend'
    SMS_USERNAME = 'foo'
    SMS_PASSWORD = 'bar'
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

import datetime
import requests

from urllib import urlencode
from xml.dom import minidom

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from sms.backends.base import BaseSmsBackend
from sms.models import Sms

DIGICEL_API_URL = 'https://smsenlot.digicelhaiti.com:8443/bulksms/BulkSMSHTTP'
DIGICEL_RESPONSE_STATUS_CODES = {
    0: _('Message submitted successfully'),
    -1: _('System Error'),
    50: _('Authentication Error'),
    51: _('Message is too long (must be <= 160 characters)'),
    52: _('Phone number validation error'),
    53: _('Message is null or empty'),
    54: _('Exceeded the maximum amount of destination numbers'),
    55: _('Schedule is set before current time'),
    56: _('Schedule is set for out-of-services hours')
}

class SmsBackend(BaseSmsBackend):
    """
    SMS Backend for Digicel provider.
    """

    def get_username(self):
        return getattr(settings, 'SMS_USERNAME', '')

    def get_password(self):
        return getattr(settings, 'SMS_PASSWORD', '')

    def get_api_url(self):
        return DIGICEL_API_URL

    def _send(self, message):
        """
        Private method to send one message.

        :param SmsMessage message: SmsMessage class instance.
        :returns: True if message is sent else False
        :rtype: bool
        """

        payload = {
            'username': self.get_username(),
            'password': self.get_password(),
            'from_phone': message.from_phone,
            'destination': ",".join(message.recipient_list),
            'message': message.message,
        }
        response = requests.post(self.get_api_url(), payload, verify=False)

        if response.status_code != 200:
            if not self.fail_silently:
                raise Exception("Digicel Send sms response header returned status code of %d" % response.status_code)
            else:
                return False

        response_dict = self._parse_response(response.content)
        if int(response_dict['status']) != 0:
            if not self.fail_silently:
                raise Exception("Digicel Send response status code error %d: %s" % (int(response_dict['status']),
                    DIGICEL_RESPONSE_STATUS_CODES[int(response_dict['status'])]))
            else:
                return False

        else:
            return True
        return False

    def send_messages(self, messages):
        """
        Send messages.

        :param list messages: List of SmsMessage instances.
        :returns: number of messages sent successful.
        :rtype: int
        """
        counter = 0
        for message in messages:
            res = self._send(message)
            if res:
                counter += 1

        return counter

    def get_failed_messages(self):
        #TODO method=fail, id, username, password required
        return

    def get_inbox(self, first=None, max=None):
        params = {'method':'inbox','username':self.get_username(),'password':self.get_password()}

        #TODO if we aren't given a first keyword arg, let's get this from the db
        if first:
            params.update({'first': int(first)})

        if max:
            params.update({'max': int(max)})

        params = urlencode(params)
        response = requests.get(self.get_api_url(), params=params, verify=False)

        if response.status_code != 200:
            if not self.fail_silently:
                raise Exception("Digicel send sms response header returned status code of %d" % response.status_code)
            else:
                return False

        response_dom = minidom.parseString(response.content)
        response_status_code = int(response_dom.getElementsByTagName('status')[0].firstChild.data)
        if response_status_code != 0:
            if not self.fail_silently:
                raise Exception("Digicel Inbox response status code error %d: %s" % (response_status_code,
                    DIGICEL_RESPONSE_STATUS_CODES[response_status_code]))
            else:
                return False
        else:
            records = t_dom.getElementsByTagName('record')
            for record in records:
                sms = Sms(
                    from_number=record.getElementsByTagName('tel')[0].firstChild.data,
                    to_number=settings.SMS_USERNAME,
                    message=record.getElementsByTagName('message')[0].firstChild.data,
                    sent_date=datetime.datetime.strptime(
                        record.getElementsByTagName('datetime')[0].firstChild.data,
                        '%d-%m-%Y %H:%M'),
                )
                sms.save()
