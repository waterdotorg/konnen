import django.dispatch

sms_post_send = django.dispatch.Signal(providing_args=['recipient_list', 'from_phone', 'message', 'result'])