import datetime

from django.db import models

from countries.models import Country

class Location(models.Model):
    PENDING_STATUS = 0
    ACTIVE_STATUS = 1
    COMPLETE_STATUS = 2
    CANCELLED_STATUS = 3
    HIDDEN_STATUS = 4

    STATUS_CHOICES = (
        (PENDING_STATUS, 'Pending'),
        (ACTIVE_STATUS, 'Active'),
        (COMPLETE_STATUS, 'Complete'),
        (CANCELLED_STATUS, 'Cancelled'),
        (HIDDEN_STATUS, 'Hidden'),
    )

    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=100, unique=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='location-images', max_length=256, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=26, decimal_places=20, blank=True, null=True)
    longitude = models.DecimalField(max_digits=26, decimal_places=20, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=ACTIVE_STATUS)
    published_date = models.DateTimeField(default=datetime.datetime.now())
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
            return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('location', (), {'slug': self.slug,})
