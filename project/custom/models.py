import datetime

from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from countries.models import Country

class Community(models.Model):
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("communities")

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
        (PENDING_STATUS, _('Pending')),
        (ACTIVE_STATUS, _('Active')),
        (COMPLETE_STATUS, _('Complete')),
        (CANCELLED_STATUS, _('Cancelled')),
        (HIDDEN_STATUS, _('Hidden')),
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

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            try:
                Location.objects.get(slug=slugify(self.title))
                self.slug = slugify(self.title + '-' + self.uid)
            except Location.DoesNotExist:
                self.slug = slugify(self.title)
        super(Location, self).save(*args, **kwargs)

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
        if chlorine_level == None:
            return 'none'
        if chlorine_level == Decimal('0.00'):
            return 'zero'
        if chlorine_level > Decimal('0.00') and chlorine_level < Decimal('0.50'):
            return 'low'
        if chlorine_level >= Decimal('0.50') and chlorine_level < Decimal('2.00'):
            return 'pass'
        return 'high'

class LocationSubscription(models.Model):
    EMAIL_NONE_FREQ = 'none'
    EMAIL_IMMEDIATE_FREQ = 'immediate'
    EMAIL_DAILY_FREQ = 'daily'
    EMAIL_WEEKLY_FREQ = 'weekly'

    EMAIL_FREQ_CHOICES = (
        (EMAIL_NONE_FREQ, _('None')),
        (EMAIL_IMMEDIATE_FREQ, _('Immediate')),
        (EMAIL_DAILY_FREQ, _('Daily')),
        (EMAIL_WEEKLY_FREQ, _('Weekly')),
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
    mobile_shorthand_code = models.CharField(max_length=3, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

class Provider(models.Model):
    title = models.CharField(max_length=100)
    mobile_shorthand_code = models.CharField(max_length=10, blank=True, null=True)
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
        (PENDING_STATUS, _('Pending')),
        (ACTIVE_STATUS, _('Active')),
        (COMPLETE_STATUS, _('Complete')),
        (CANCELLED_STATUS, _('Cancelled')),
        (HIDDEN_STATUS, _('Hidden')),
    )

    WATER_QUALITY_TYPE = 'water_quality'

    TYPE_CHOICES = (
        (WATER_QUALITY_TYPE, _('Water Quality')),
    )

    WATER_QUALITY_NOTIFICATION_STATUS_CHOICES = (
        (PENDING_STATUS, _('Pending')),
        (COMPLETE_STATUS, _('Complete')),
        (CANCELLED_STATUS, _('Cancelled')),
    )

    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default=WATER_QUALITY_TYPE)
    title = models.CharField(max_length=256, blank=True)
    content = models.TextField(blank=True)
    water_source_type = models.ForeignKey(WaterSourceType, blank=True, null=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)
    chlorine_level = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=ACTIVE_STATUS)
    published_date = models.DateTimeField(default=datetime.datetime.now())
    water_quality_notification_email_daily_status = models.SmallIntegerField(
        choices=WATER_QUALITY_NOTIFICATION_STATUS_CHOICES, default=PENDING_STATUS)
    water_quality_notification_email_daily_semaphore = models.BooleanField(default=False)
    water_quality_notification_email_immediate_status = models.SmallIntegerField(
        choices=WATER_QUALITY_NOTIFICATION_STATUS_CHOICES, default=PENDING_STATUS)
    water_quality_notification_email_immediate_semaphore = models.BooleanField(default=False)
    water_quality_notification_email_weekly_status = models.SmallIntegerField(
        choices=WATER_QUALITY_NOTIFICATION_STATUS_CHOICES, default=PENDING_STATUS)
    water_quality_notification_email_weekly_semaphore = models.BooleanField(default=False)
    water_quality_notification_mobile_status = models.SmallIntegerField(
        choices=WATER_QUALITY_NOTIFICATION_STATUS_CHOICES, default=PENDING_STATUS)
    water_quality_notification_mobile_semaphore = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager() # Default manager.
    active_objects = LocationPostActiveManager()

    def __unicode__(self):
        return u'%s' % self.title

class LocationPostReporterRemarks(models.Model):
    code = models.IntegerField(unique=True)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%d %s' % (self.code, self.text)