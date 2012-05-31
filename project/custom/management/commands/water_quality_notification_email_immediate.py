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
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import smart_str

from custom.models import LocationPost, LocationSubscription, LocationPostNotificationLog

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Push new water quality updates to location followers via email'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.num_processes = multiprocessing.cpu_count()
        self.work_queue = multiprocessing.Queue()
        self.current_site = Site.objects.get_current()

    def worker(self, *args, **kwargs):
        while True:
            try:
                location_post_id = self.work_queue.get_nowait()
                location_post = LocationPost.objects.get(id=location_post_id)
                logger.info("Starting water_quality_notification_email_immediate processing for LocationPost id: %d" % location_post.id)
            except Exception, e:
                time.sleep(20)
                continue

            if location_post.chlorine_level >= Decimal('0.50') and location_post.chlorine_level < Decimal('2.00'):
                safe_water = True
            else:
                safe_water = False

            try:
                location_subscriptions = LocationSubscription.objects.select_related().filter(
                    location=location_post.location,
                    email_subscription=LocationSubscription.EMAIL_IMMEDIATE_FREQ,
                    user__is_active=True,
                ).exclude(user__email='')

                logger.info("Found %d immediate email subscriptions for %s location" % (location_subscriptions.count(), location_post.location))

                for location_subscription in location_subscriptions:
                    # Have we already sent a notification???
                    try:
                        existing_log = LocationPostNotificationLog.objects.get(
                            user=location_subscription.user,
                            location_post=location_post,
                            notification_type=LocationPostNotificationLog.EMAIL_IMMEDIATE,
                        )
                        logger.info("Already sent immediate email notification to %s for LocationPost id %d" % (location_subscription.user, location_post.id))
                        continue
                    except:
                        pass

                    profile = location_subscription.user.get_profile()
                    language = profile.language
                    translation.activate(language)

                    email_subject = render_to_string('water_quality_notification/email/immediate-subject.txt', {
                        'location': location_post.location, 'language': language
                    })

                    email_body = render_to_string('water_quality_notification/email/immediate.txt', {
                        'location': location_post.location, 'location_post': location_post, 'safe_water': safe_water,
                        'language': language, 'current_site': self.current_site})

                    email_result = send_mail(
                        smart_str(email_subject),
                        smart_str(email_body),
                        settings.SERVER_EMAIL,
                        [location_subscription.user.email],
                    )

                    if email_result:
                        location_post_notification_log = LocationPostNotificationLog(
                            user=location_subscription.user,
                            location_post=location_post,
                            notification_type=LocationPostNotificationLog.EMAIL_IMMEDIATE,
                        )
                        location_post_notification_log.save()
                        logger.info("Successfully sent immediate email notification for LocationPost id %d to %s" % (location_post.id, location_subscription.user))
                    translation.deactivate()

                location_post.water_quality_notification_email_immediate_status = LocationPost.COMPLETE_STATUS
                location_post.save()
            except Exception, e:
                logger.error("Error processing water_quality_notification_email_immediate for LocationPost id %d: %s" % (location_post.id, e))
            finally:
                translation.deactivate()
                location_post.water_quality_notification_email_immediate_semaphore = False
                location_post.save()

    def handle(self, *args, **options):
        for i in range(self.num_processes):
            p = multiprocessing.Process(target=self.worker)
            p.daemon = True
            p.start()

        # catch TERM signal to allow finalizers to run and reap daemonic children
        signal.signal(signal.SIGTERM, lambda *args: sys.exit(-signal.SIGTERM))

        while True:
            location_posts = LocationPost.active_objects.filter(
                water_quality_notification_email_immediate_status=LocationPost.PENDING_STATUS,
                water_quality_notification_email_immediate_semaphore=False,
            )
            for location_post in location_posts:
                try:
                    location_post.water_quality_notification_email_immediate_semaphore = True
                    location_post.save()
                    self.work_queue.put(location_post.id)
                    logger.info("Added LocationPost id %d to water_quality_notification_email_immediate processing queue" % location_post.id)
                except:
                    logger.error("Error adding LocationPost id %d to water_quality_notification_email_immediate processing queue" % location_post.id)
                    location_post.water_quality_notification_email_immediate_semaphore = False
                    location_post.save()
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(90)