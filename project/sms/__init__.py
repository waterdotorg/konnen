from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

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

def get_messages(start=None, max=None, fail_silently=False, auth_user=None, auth_password=None, connection=None):
    """
    Sms api to acquire messages from an inbox

    If auth_user is None, the SMS_USER setting is used.
    If auth_password is None, the SMS_PASSWORD setting is used.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    connection.get_messages(start=start, max=max)

def send_message(message, recipient_list, fail_silently=False, from_phone=None, id=None,
             auth_user=None, auth_password=None, connection=None):
    """
    Sms api for sending a single message to a recipient list.

    If auth_user is None, the SMS_USER setting is used.
    If auth_password is None, the SMS_PASSWORD setting is used.

    :returns: Boolean on sms gateway handshake.
    """
    connection = connection or get_connection(
        username = auth_user,
        password = auth_password,
        fail_silently = fail_silently
    )
    return connection.send_message(message, recipient_list, from_phone=from_phone, id=id)

def get_failed_messages(id, fail_silently=False, auth_user=None, auth_password=None, connection=None):
    """
    Sms api to acquire failed messages

    If auth_user is None, the SMS_USER setting is used.
    If auth_password is None, the SMS_PASSWORD setting is used.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    return connection.get_failed_messages(id)