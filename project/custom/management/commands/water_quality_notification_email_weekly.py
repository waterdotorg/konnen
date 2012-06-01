import datetime
import logging
import multiprocessing
import signal
import sys
import time

from decimal import Decimal

from django import db
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import smart_str

from custom.models import Location, LocationPost, LocationSubscription, LocationPostNotificationLog, \
    LocationSubscriptionNotificationLog

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Push new water quality updates to location followers via weekly email'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.num_processes = multiprocessing.cpu_count()
        self.work_queue = multiprocessing.Queue()
        self.current_site = Site.objects.get_current()

    def worker(self, *args, **kwargs):
        while True:
            try:
                location_subscription_id = self.work_queue.get_nowait()
                location_subscription = LocationSubscription.objects.get(id=location_subscription_id)
                logger.info("Starting water_quality_notification_email_weekly processing for LocationSubscription id: %d" % location_subscription.id)
            except Exception, e:
                time.sleep(20)
                continue

            try:
                # Have we already sent a subscription notification???
                existing_log = LocationSubscriptionNotificationLog.objects.filter(
                    user=location_subscription.user,
                    location_subscription=location_subscription,
                    notification_type=LocationSubscriptionNotificationLog.EMAIL_WEEKLY,
                    created_date__gte=(datetime.datetime.now() - datetime.timedelta(days=7)),
                )
                if existing_log.count():
                    raise Exception("Already sent weekly email notification to %s for LocationSubscription id %d" % (location_subscription.user, location_subscription.id))

                location_posts = LocationPost.active_objects.filter(
                    location=location_subscription.location,
                    type=LocationPost.WATER_QUALITY_TYPE,
                    published_date__gte=(datetime.datetime.now() - datetime.timedelta(days=7))
                )

                logger.info("Found %d LocationPosts for weekly email subscription" % location_posts.count())

                if location_posts.count():
                    profile = location_subscription.user.get_profile()
                    language = profile.language
                    translation.activate(language)

                    location_posts_processed = []
                    for location_post in location_posts:
                        if location_post.chlorine_level >= Decimal('0.50') and location_post.chlorine_level < Decimal('2.00'):
                            location_post.safe_water = True
                        else:
                            location_post.safe_water = False
                        location_posts_processed.append(location_post)

                    email_subject = render_to_string('water_quality_notification/email/weekly-subject.txt', {
                        'location': location_subscription.location, 'language': language
                    })

                    email_body = render_to_string('water_quality_notification/email/weekly.txt', {
                        'location': location_subscription.location, 'location_posts': location_posts_processed,
                        'language': language, 'current_site': self.current_site})

                    email_result = send_mail(
                        smart_str(email_subject),
                        smart_str(email_body),
                        settings.SERVER_EMAIL,
                        [location_subscription.user.email],
                    )

                    if email_result:
                        location_subscription_notification_log = LocationSubscriptionNotificationLog(
                            user=location_subscription.user,
                            location_subscription=location_subscription,
                            notification_type=LocationSubscriptionNotificationLog.EMAIL_WEEKLY,
                        )
                        location_subscription_notification_log.save()
                        logger.info("Successfully sent weekly email notification for LocationSubscription id %d to %s" % (location_subscription.id, location_subscription.user))
                    translation.deactivate()
            except Exception, e:
                logger.error("Error processing water_quality_notification_email_weekly for LocationSubscription id %d: %s" % (location_subscription.id, e))
            finally:
                translation.deactivate()
                location_subscription.water_quality_notification_email_weekly_semaphore = False
                location_subscription.save()

    def handle(self, *args, **options):
        for i in range(self.num_processes):
            p = multiprocessing.Process(target=self.worker)
            p.daemon = True
            p.start()

        # catch TERM signal to allow finalizers to run and reap daemonic children
        signal.signal(signal.SIGTERM, lambda *args: sys.exit(-signal.SIGTERM))

        while True:
            location_subscriptions = LocationSubscription.objects.filter(
                Q(last_email_weekly_date__lte=(datetime.datetime.now() - datetime.timedelta(days=7))) |
                Q(last_email_weekly_date__isnull=True),
                email_subscription=LocationSubscription.EMAIL_WEEKLY_FREQ,
                water_quality_notification_email_weekly_semaphore=False,
                user__is_active=True,
                location__status=Location.ACTIVE_STATUS,
                location__published_date__lte=datetime.datetime.now(),
            ).exclude(user__email='')

            for location_subscription in location_subscriptions:
                try:
                    location_subscription.water_quality_notification_email_weekly_semaphore = True
                    location_subscription.save()
                    self.work_queue.put(location_subscription.id)
                    logger.info("Added LocationSubscription id %d to water_quality_notification_email_weekly processing queue" % location_subscription.id)
                except:
                    logger.error("Error adding LocationSubscription id %d to water_quality_notification_email_weekly processing queue" % location_subscription.id)
                    location_subscription.water_quality_notification_email_weekly_semaphore = False
                    location_subscription.save()
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(600)