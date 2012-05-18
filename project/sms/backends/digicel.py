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

    def send_message(self, message, recipient_list, from_phone=None, id=None):
        """
        Send message to recipient list.
        :returns: True on success, False otherwise
        :rtype: Boolean
        """
        params = {
            'method': 'send',
            'username': self.get_username(),
            'password': self.get_password(),
            'message': message,
            'dest': ','.join(map(str, recipient_list)),
        }
        if id:
            params.update({'id': int(id)})

        params = urlencode(params)
        response = requests.get(self.get_api_url(), params=params, verify=False)

        if not response.ok:
            if not self.fail_silently:
                raise Exception("Digicel Send sms response header returned status code of %d" % response.status_code)
            else:
                return False

        response_dom = minidom.parseString(response.content)
        response_status_code = int(response_dom.getElementsByTagName('status')[0].firstChild.data)
        if response_status_code != 0:
            if not self.fail_silently:
                raise Exception("Digicel Send response status code error %d: %s" % (response_status_code,
                    DIGICEL_RESPONSE_STATUS_CODES[response_status_code]))
            else:
                return False
        else:
            return True

    def get_failed_messages(self, id):
        params = {
            'method': 'fail',
            'username': self.get_username(),
            'password': self.get_password(),
            'id': id,
        }
        params = urlencode(params)
        response = requests.get(self.get_api_url(), params=params, verify=False)

        if not response.ok:
            if not self.fail_silently:
                raise Exception("Digicel Failed Messages sms response header returned status code of %d" % response.status_code)
            else:
                return False

        response_dom = minidom.parseString(response.content)
        response_status_code = int(response_dom.getElementsByTagName('status')[0].firstChild.data)
        if response_status_code != 0:
            if not self.fail_silently:
                raise Exception("Digicel Failed Messages response status code error %d: %s" % (response_status_code,
                    DIGICEL_RESPONSE_STATUS_CODES[response_status_code]))
            else:
                return False
        else:
            return response_dom #TODO need to parse response_dom to failed phone number list

    def get_messages(self, start=None, max=None):
        params = {'method':'inbox','username':self.get_username(),'password':self.get_password()}

        if start:
            params.update({'first': int(start)})

        if max:
            params.update({'max': int(max)})

        params = urlencode(params)
        response = requests.get(self.get_api_url(), params=params, verify=False)

        if not response.ok:
            if not self.fail_silently:
                raise Exception("Digicel get inbox sms response header returned status code of %d" % response.status_code)
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
            records = response_dom.getElementsByTagName('record')
            records.reverse()
            for record in records:
                try:
                    Sms.objects.get(
                        from_number=record.getElementsByTagName('tel')[0].firstChild.data,
                        to_number=settings.SMS_USERNAME,
                        message=record.getElementsByTagName('message')[0].firstChild.data,
                        sent_date=datetime.datetime.strptime(
                            record.getElementsByTagName('datetime')[0].firstChild.data,
                            '%d-%m-%Y %H:%M'),
                    )
                    break
                except Sms.DoesNotExist:
                    sms = Sms(
                        from_number=record.getElementsByTagName('tel')[0].firstChild.data,
                        to_number=settings.SMS_USERNAME,
                        message=record.getElementsByTagName('message')[0].firstChild.data,
                        sent_date=datetime.datetime.strptime(
                            record.getElementsByTagName('datetime')[0].firstChild.data,
                            '%d-%m-%Y %H:%M'),
                    )
                    sms.save()
            return True