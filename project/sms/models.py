from django.db import models
from django.utils.translation import ugettext_lazy as _

class Sms(models.Model):
    from_number = models.CharField(max_length=30)
    to_number = models.CharField(max_length=30)
    message = models.CharField(max_length=160, blank=True)
    sent_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Sms messages")

    def __unicode__(self):
        return u'%s:%s %s' % (self.from_number, self.to_number, self.message)
