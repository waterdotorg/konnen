"""
Digicel sms gateway backend.

Configuration example.
~~~~~~~~~~~~~~~~~~~~~~

Modify your settings.py::

    SMS_BACKEND = 'sms.backends.digicel.SmsBackend'
    SMS_USER = 'foo'
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

import requests

from xml.etree import ElementTree

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode

from sms.backends.base import BaseSmsBackend

DIGICEL_API_URL = 'https://smsenlot.digicelhaiti.com:8443/bulksms/BulkSMSHTTP'
DIGICEL_RESPONSE_STATUS_CODES = {
    0: 'Message submitted successfully',
    -1: 'System Error',
    50: 'Authentication Error',
    51: 'Message is too long (must be <= 160 characters)',
    52: 'Phone number validation error',
    53: 'Message is null or empty',
    54: 'Exceeded the maximum amount of destination numbers',
    55: 'Schedule is set before current time',
    56: 'Schedule is set for out-of-services hours'
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

    def _parse_response(self, response):
        """
        Parse response into python dictionary object.

        :param str response: http response
        :returns: response dict
        :rtype: dict
        """
        response_dict = {}
        elements = ElementTree.XML(response.content)
        for element in elements:
            response_dict[element.tag] = element.text
        return response_dict

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
                raise Exception("Digicel send sms response header returned status code of %d" % response.status_code)
            else:
                return False

        response_dict = self._parse_response(response.content)
        if int(response_dict['status']) != 0:
            if not self.fail_silently:
                raise Exception("Digicel response status code error %d: %s" % (int(response_dict['status']),
                    DIGICEL_RESPONSE_STATUS_CODES[int(response_dict['status'])]))
            else:
                return False

        else:
            return True
        return False

    def send_messages(self, messages):
        """
        Send messages.

        :param list messages: List of SmsMessage instences.
        :returns: number of messages seded succesful.
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

    def get_inbox(self):
        #TODO method=inbox, username, password, first, max
        return