import datetime

from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from countries.models import Country

class Community(models.Model):
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

class LocationActiveManager(models.Manager):
    def get_query_set(self):
        return super(LocationActiveManager, self).get_query_set().filter(
            status=Location.ACTIVE_STATUS,
            published_date__lte=datetime.datetime.now(),
        )

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
    uid = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='location-images', max_length=256, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=26, decimal_places=20, blank=True, null=True)
    longitude = models.DecimalField(max_digits=26, decimal_places=20, blank=True, null=True)
    community = models.ForeignKey(Community, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=ACTIVE_STATUS)
    published_date = models.DateTimeField(default=datetime.datetime.now())
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager() # Default manager.
    active_objects = LocationActiveManager()

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('location', (), {'slug': self.slug,})

    def get_chlorine_level(self):
        try:
            location_post = LocationPost.active_objects.filter(
                location=self,
                chlorine_level__isnull=False).order_by('-published_date')[:1][0]
        except:
            return None
        return location_post.chlorine_level

    def get_chlorine_level_status(self, chlorine_level=None):
        if not chlorine_level:
            chlorine_level = self.get_chlorine_level()
        if not chlorine_level:
            return None
        if chlorine_level >= Decimal('0.40') and chlorine_level <= Decimal('0.50'):
            return 'pass'
        else:
            return 'fail'

class LocationSubscription(models.Model):
    EMAIL_NONE_FREQ = 'none'
    EMAIL_IMMEDIATE_FREQ = 'immediate'
    EMAIL_DAILY_FREQ = 'daily'
    EMAIL_WEEKLY_FREQ = 'weekly'

    EMAIL_FREQ_CHOICES = (
        (EMAIL_NONE_FREQ, 'None'),
        (EMAIL_IMMEDIATE_FREQ, 'Immediate'),
        (EMAIL_DAILY_FREQ, 'Daily'),
        (EMAIL_WEEKLY_FREQ, 'Weekly'),
    )

    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)
    email_subscription = models.CharField(max_length=20, choices=EMAIL_FREQ_CHOICES, default=EMAIL_DAILY_FREQ)
    phone_subscription = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    unique_together = ("user", "location")

    def __unicode__(self):
        return u'%s : %s' % (self.user.get_full_name(), self.location)

class WaterSourceType(models.Model):
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title


class LocationPostActiveManager(models.Manager):
    def get_query_set(self):
        return super(LocationPostActiveManager, self).get_query_set().filter(
            status=LocationPost.ACTIVE_STATUS,
            published_date__lte=datetime.datetime.now(),
        )

class LocationPost(models.Model):
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

    WATER_QUALITY_TYPE = 'water_quality'

    TYPE_CHOICES = (
        (WATER_QUALITY_TYPE, 'Water Quality'),
    )

    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default=WATER_QUALITY_TYPE)
    title = models.CharField(max_length=256, blank=True)
    content = models.TextField(blank=True)
    water_source_type = models.ForeignKey(WaterSourceType, blank=True, null=True)
    chlorine_level = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=ACTIVE_STATUS)
    published_date = models.DateTimeField(default=datetime.datetime.now())
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager() # Default manager.
    active_objects = LocationPostActiveManager()

    def __unicode__(self):
        return u'%s' % self.title