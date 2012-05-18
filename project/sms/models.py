from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sms_control.models import SmsControl, SmsControlTrans

class Sms(models.Model):
    PENDING_STATUS = 0
    COMPLETED_STATUS = 1
    CANCELLED_STATUS = 2

    PROCESSING_CHOICES = (
        (PENDING_STATUS, _('Pending')),
        (COMPLETED_STATUS, _('Completed')),
        (CANCELLED_STATUS, _('Cancelled')),
    )

    from_number = models.CharField(max_length=30)
    to_number = models.CharField(max_length=30)
    message = models.TextField(validators=[MaxLengthValidator(160)], blank=True)
    sent_date = models.DateTimeField()
    semaphore_processing = models.BooleanField(default=False)
    status_processing = models.SmallIntegerField(choices=PROCESSING_CHOICES, default=PENDING_STATUS)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Sms messages")

    def __unicode__(self):
        return u'%s:%s %s' % (self.from_number, self.to_number, self.message)

    def get_language_from_sms(self):
        if not self.message:
            return getattr(settings, 'LANGUAGE_CODE', 'en')

        try:
            control_word = self.message.split()[0].lower()
        except:
            return getattr(settings, 'LANGUAGE_CODE', 'en')

        # Check english control word first
        try:
            sms_control = SmsControl.objects.filter(phrase__iexact=control_word).get()
            return 'en'
        except:
            pass

        try:
            sms_control_trans = SmsControlTrans.objects.select_related().filter(
                phrase_trans__iexact=control_word,
            ).get()
            return sms_control_trans.sms_control_locale.language_code

        except:
            return getattr(settings, 'LANGUAGE_CODE', 'en')

    def get_control_word_from_sms(self):
        if not self.message:
            return None

        try:
            control_word = self.message.split()[0].lower()
        except:
            return None

        # Check english control word first
        try:
            sms_control = SmsControl.objects.filter(phrase__iexact=control_word).get()
            return sms_control.phrase.lower()
        except:
            pass

        # Check translation control word and return english default if available...
        try:
            sms_control_trans = SmsControlTrans.objects.select_related().filter(
                phrase_trans__iexact=control_word,
            ).get()
            return sms_control_trans.sms_control.phrase.lower()
        except:
            return None

    def get_action_word_from_sms(self):
        if not self.message:
            return None

        try:
            action_word = self.message.split()[1].lower()
            return action_word
        except:
            return None


