from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

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
