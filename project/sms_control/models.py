from django.core.validators import MaxLengthValidator
from django.db import models

class SmsControl(models.Model):
    phrase = models.CharField(max_length=160, unique=True)
    help_text = models.TextField(validators=[MaxLengthValidator(160)], blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.phrase

class SmsControlLocale(models.Model):
    name = models.CharField(max_length=100, unique=True)
    language_code = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % self.name

class SmsControlTrans(models.Model):
    sms_control = models.ForeignKey(SmsControl)
    sms_control_locale = models.ForeignKey(SmsControlLocale)
    phrase_trans = models.CharField(max_length=160, unique=True)
    help_text_trans = models.TextField(validators=[MaxLengthValidator(160)], blank=True)

    class Meta:
        unique_together = (('sms_control', 'sms_control_locale'),)

    def __unicode__(self):
        return u'%s %s' % (self.sms_control, self.phrase_trans)