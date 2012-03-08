from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from sms.message import SmsMessage

def get_connection(backend=None, fail_silently=False, **kwargs):
    """
    Load an e-mail backend and return an instance of it.

    If backend is None (default) settings.SMS_BACKEND is used.

    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    path = backend or getattr(settings, 'SMS_BACKEND', 'sms.backends.locmem.SmsBackend')
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing sms backend module %s: "%s"' % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass(fail_silently=fail_silently, **kwargs)


def send_sms(message, from_phone, recipient_list, flash=False, fail_silently=False,
             auth_user=None, auth_password=None, connection=None):
    """
    Easy wrapper for sending a single message to a recipient list.

    If auth_user is None, the SMS_USER setting is used.
    If auth_password is None, the SMS_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the SmsMessage class directly.

    :returns: the number of SMSs sent.
    """
    connection = connection or get_connection(
        username = auth_user,
        password = auth_password,
        fail_silently = fail_silently
    )
    return SmsMessage(message=message, from_phone=from_phone, recipient_list=recipient_list, flash=flash,
        connection=connection).send()

def send_mass_sms(datatuple, fail_silently=False, auth_user=None, auth_password=None, connection=None):
    """
    Given a datatuple of (message, from_phone, recipient_list, flash), sends each message to each
    recipient list.

    If from_phone is None, the SMS_DEFAULT_FROM_PHONE setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the SMS_USER setting is used.
    If auth_password is None, the SMS_PASSWORD setting is used.

    :returns: the number of SMSs sent.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the SmsMessage class directly.
    """

    connection = connection or get_connection(
        username = auth_user,
        password = auth_password,
        fail_silently = fail_silently
    )
    messages = []
    for message, from_phone, recipient_list, flash in datatuple:
        messages.append(SmsMessage(message=message, from_phone=from_phone, recipient_list=recipient_list, flash=flash))

    connection.send_messages(messages)