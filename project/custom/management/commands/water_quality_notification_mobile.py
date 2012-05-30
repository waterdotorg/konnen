import datetime
import logging
import multiprocessing
import signal
import sys
import time

from decimal import Decimal

from django import db
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import smart_str

from sms import send_message
from custom.models import LocationPost, LocationSubscription, LocationPostNotificationLog

# Get an instance of a logger
logger = logging.getLogger(__name__)
# TODO need logging, both normal and concurrent

class Command(BaseCommand):
    help = 'Push new water quality updates to location followers'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.num_processes = multiprocessing.cpu_count()
        self.work_queue = multiprocessing.Queue()

    def worker(self, *args, **kwargs):
        while True:
            try:
                location_post_id = self.work_queue.get_nowait()
                location_post = LocationPost.objects.get(id=location_post_id)
                logger.info("Starting water_quality_notification_mobile processing for LocationPost id: %d" % location_post.id)
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
                    phone_subscription=True,
                    user__is_active=True,
                    user__profile__id__isnull=False,
                ).exclude(user__profile__mobile='')

                logger.info("Found %d mobile subscriptions for %s location" % (location_subscriptions.count(), location_post.location))

                for location_subscription in location_subscriptions:
                    # Have we already sent a notification???
                    try:
                        existing_log = LocationPostNotificationLog.objects.get(
                            user=location_subscription.user,
                            location_post=location_post,
                            notification_type=LocationPostNotificationLog.MOBILE,
                        )
                        logger.info("Already sent mobile notification to %s for LocationPost id %d" % (location_subscription.user, location_post.id))
                        continue
                    except:
                        pass

                    profile = location_subscription.user.get_profile()
                    language = profile.language
                    translation.activate(language)

                    reply_message = render_to_string('water_quality_notification/sms/mobile.txt', {
                        'location': location_post.location, 'location_post': location_post, 'safe_water': safe_water,
                        'language': language})
                    sms_result = send_message(smart_str(reply_message), [profile.mobile])

                    if sms_result:
                        location_post_notification_log = LocationPostNotificationLog(
                            user=location_subscription.user,
                            location_post=location_post,
                            notification_type=LocationPostNotificationLog.MOBILE,
                        )
                        location_post_notification_log.save()
                        logger.info("Successfully sent mobile notification for LocationPost id %d to %s" % (location_post.id, location_subscription.user))
                    translation.deactivate()

                location_post.water_quality_notification_mobile_status = LocationPost.COMPLETE_STATUS
                location_post.save()

            except Exception, e:
                logger.error("Error processing water_quality_notification_mobile for LocationPost id %d: %s" % (location_post.id, e))
            finally:
                translation.deactivate()
                location_post.water_quality_notification_mobile_semaphore = False
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
                water_quality_notification_mobile_status=LocationPost.PENDING_STATUS,
                water_quality_notification_mobile_semaphore=False,
            )
            for location_post in location_posts:
                try:
                    location_post.water_quality_notification_mobile_semaphore = True
                    location_post.save()
                    self.work_queue.put(location_post.id)
                    logger.info("Added LocationPost id %d to water_quality_notification_mobile processing queue" % location_post.id)
                except:
                    logger.error("Error adding LocationPost id %d to water_quality_notification_mobile processing queue" % location_post.id)
                    location_post.water_quality_notification_mobile_semaphore = True
                    location_post.save()
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(90)