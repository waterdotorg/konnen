import datetime
import logging
import multiprocessing
import os
import shlex
import signal
import sys
import time

from decimal import Decimal

from django import db
from django.contrib.auth.models import User, Group
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import smart_str

from custom.models import Location, LocationSubscription, LocationPost, WaterSourceType, Provider, \
    LocationPostReporterRemarks
from custom_user.models import Profile
from sms import send_message
from sms.models import Sms
from sms_control.models import SmsControl, SmsControlTrans

# Get an instance of a logger
logger = logging.getLogger(__name__)
# TODO need logging, both normal and concurrent

class Command(BaseCommand):
    help = 'Process Digicel Inbox Messages'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.num_processes = multiprocessing.cpu_count()
        self.work_queue = multiprocessing.Queue()

    def process_sms(self, sms, user_group='sys_public'):
        language = sms.get_language_from_sms()
        # Set user language preference
        sms.set_user_language_preference(language=language)
        control_word = sms.get_control_word_from_sms()
        action_word = sms.get_action_word_from_sms()
        try:
            translation.activate(language)

            if language == 'en':
                if user_group == 'sys_admin':
                    sms_control_translations = SmsControl.objects.all()
                elif user_group == 'sys_reporter':
                    sms_control_translations = SmsControl.objects.filter(Q(group__name='sys_public') | Q(group__name='sys_reporter'))
                else:
                    sms_control_translations = SmsControl.objects.filter(group__name='sys_public')
            else:
                if user_group == 'sys_admin':
                    sms_control_translations = SmsControlTrans.objects.select_related().filter(
                        sms_control_locale__language_code__iexact=language,
                    )
                elif user_group == 'sys_reporter':
                    sms_control_translations = SmsControlTrans.objects.select_related().filter(
                        Q(sms_control__group__name='sys_public') | Q(sms_control__group__name='sys_reporter'),
                        sms_control_locale__language_code__iexact=language,
                    )
                else:
                    sms_control_translations = SmsControlTrans.objects.select_related().filter(
                        sms_control_locale__language_code__iexact=language,
                        sms_control__group__name='sys_public',
                    )

            # No message text received
            if not sms.message:
                reply_message = render_to_string('sms_control/reply/null_message.txt',
                    {'sms_control_translations': sms_control_translations, 'language': language,})
                return send_message(smart_str(reply_message), [sms.from_number,])

            # No control word available
            if not control_word:
                reply_message = render_to_string('sms_control/reply/invalid_request.txt',
                    {'sms_control_translations': sms_control_translations, 'language': language,})
                return send_message(smart_str(reply_message), [sms.from_number,])

            # General help message
            if control_word == 'help':
                reply_message = render_to_string('sms_control/reply/help.txt',
                    {'sms_control_options': sms_control_translations, 'language': language,})
                return send_message(smart_str(reply_message), [sms.from_number,])

            # Control word + help. Ex. 'subscribe help'
            if action_word == 'help':
                reply_message = render_to_string('sms_control/reply/' + str(control_word) + '_help.txt',
                    {'language': language,})
                return send_message(smart_str(reply_message), [sms.from_number])

            # Subscribe
            if control_word == 'subscribe':
                ss = shlex.shlex(smart_str(sms.message))
                ss.whitespace += ','
                location_uid_args = list(ss)[1:]
                location_objects = []
                for location_uid in location_uid_args:
                    try:
                        location = Location.objects.get(uid=location_uid)
                        location_objects.append(location)
                    except:
                        pass

                if not location_objects:
                    # No valid locations received
                    reply_message = render_to_string('sms_control/reply/subscribe_location_error.txt',
                        {'language': language,})
                    return send_message(smart_str(reply_message), [sms.from_number])

                # Get profile and user objects
                try:
                    profile = Profile.objects.select_related().get(mobile=sms.from_number)
                    user = profile.user
                except Profile.DoesNotExist:
                    user = User(username=sms.from_number)
                    user.set_unusable_password()
                    user.save()
                    profile = Profile(user=user, mobile=sms.from_number)
                    profile.save()

                subscribed_locations = []
                for location_object in location_objects:
                    try:
                        location_subscription = LocationSubscription.objects.get(
                            user=user,
                            location=location_object,
                        )
                        location_subscription.phone_subscription = True
                        location_subscription.save()
                        subscribed_locations.append(location_object)
                    except LocationSubscription.DoesNotExist:
                        location_subscription = LocationSubscription(
                            user=user,
                            location=location_object,
                            email_subscription=LocationSubscription.EMAIL_NONE_FREQ,
                            phone_subscription=True,
                        )
                        location_subscription.save()
                        subscribed_locations.append(location_object)
                    except:
                        pass
                if not subscribed_locations:
                    return True
                reply_message = render_to_string('sms_control/reply/subscribe_success.txt',
                    {'subscribed_locations': subscribed_locations, 'language': language,})
                return send_message(smart_str(reply_message), [sms.from_number,])

            # UnSubscribe
            if control_word == 'unsubscribe':
                # Set anonymous variable
                try:
                    profile = Profile.objects.select_related().get(mobile=sms.from_number)
                    anonymous = False
                except:
                    profile = None
                    anonymous = True
                ss = shlex.shlex(smart_str(sms.message))
                ss.whitespace += ','
                location_uid_args = list(ss)[1:]
                location_objects = []

                if not anonymous and 'all' in location_uid_args:
                    try:
                        location_subscriptions = LocationSubscription.objects.select_related().filter(
                            user=profile.user,
                            phone_subscription=True,
                        )
                        for ls in location_subscriptions:
                            location_objects.append(ls.location)
                        if not location_objects:
                            # User not subscribed to any locations
                            reply_message = render_to_string('sms_control/reply/unsubscribe_no_subscriptions_error.txt',
                                {'language': language,})
                            return send_message(smart_str(reply_message), [sms.from_number])
                    except:
                        pass
                else:
                    for location_uid in location_uid_args:
                        try:
                            location = Location.objects.get(uid=location_uid)
                            location_objects.append(location)
                        except:
                            pass

                if not location_objects:
                    # No valid locations received
                    reply_message = render_to_string('sms_control/reply/unsubscribe_location_error.txt',
                        {'language': language,})
                    return send_message(smart_str(reply_message), [sms.from_number])

                # Get profile and user objects
                try:
                    profile = Profile.objects.select_related().get(mobile=sms.from_number)
                    user = profile.user
                except:
                    reply_message = render_to_string('sms_control/reply/unsubscribe_no_account_error.txt',
                        {'language': language, 'sms': sms})
                    return send_message(smart_str(reply_message), [sms.from_number])

                unsubscribed_locations = []
                for location_object in location_objects:
                    try:
                        location_subscription = LocationSubscription.objects.get(
                            user=user,
                            location=location_object,
                        )
                        location_subscription.phone_subscription = False
                        location_subscription.save()
                        unsubscribed_locations.append(location_object)
                    except LocationSubscription.DoesNotExist:
                        unsubscribed_locations.append(location_object)

                    except:
                        pass
                if not unsubscribed_locations:
                    return True
                reply_message = render_to_string('sms_control/reply/unsubscribe_success.txt',
                    {'unsubscribed_locations': unsubscribed_locations, 'language': language,})
                return send_message(smart_str(reply_message), [sms.from_number,])

            # Report
            if control_word == 'report':
                # Set anonymous variable
                try:
                    profile = Profile.objects.select_related().get(mobile=sms.from_number)
                    anonymous = False
                except:
                    profile = None
                    anonymous = True
                ss = shlex.shlex(smart_str(sms.message))
                ss.whitespace += ','
                location_uid_args = list(ss)[1:]
                location_objects = []
                for location_uid in location_uid_args:
                    try:
                        location = Location.objects.get(uid=location_uid)
                        location_objects.append(location)
                    except:
                        pass

                if not location_objects:
                    if anonymous:
                        # No valid locations received
                        reply_message = render_to_string('sms_control/reply/report_location_error_anonymous.txt',
                            {'language': language,})
                        return send_message(smart_str(reply_message), [sms.from_number])
                    else:
                        try:
                            ls = LocationSubscription.objects.select_related().filter(
                                user=profile.user,
                                phone_subscription=True,
                            ).order_by('-location__published_date')[0]
                            try:
                                location_post = LocationPost.active_objects.filter(
                                    type=LocationPost.WATER_QUALITY_TYPE,
                                    location=ls.location,
                                ).order_by('-published_date')[0]
                                if location_post.chlorine_level >= Decimal('0.50') and location_post.chlorine_level < Decimal('2.00'):
                                    safe_water = True
                                else:
                                    safe_water = False
                            except:
                                location_post = None
                                safe_water = None
                            reply_message = render_to_string('sms_control/reply/report.txt',
                                {'location': ls.location, 'location_post': location_post, 'safe_water': safe_water,
                                 'language': language})
                            return send_message(smart_str(reply_message), [sms.from_number])
                        except:
                            reply_message = render_to_string('sms_control/reply/report_location_error.txt',
                                {'language': language,})
                            return send_message(smart_str(reply_message), [sms.from_number])
                else:
                    for location_object in location_objects:
                        try:
                            location_post = LocationPost.active_objects.filter(
                                type=LocationPost.WATER_QUALITY_TYPE,
                                location=location_object,
                            ).order_by('-published_date')[0]
                            if location_post.chlorine_level >= Decimal('0.50') and location_post.chlorine_level < Decimal('2.00'):
                                safe_water = True
                            else:
                                safe_water = False
                        except:
                            location_post = None
                            safe_water = None
                        reply_message = render_to_string('sms_control/reply/report.txt',
                            {'location': location_object, 'location_post': location_post, 'safe_water': safe_water,
                             'language': language})
                        result = send_message(smart_str(reply_message), [sms.from_number])
                        if not result:
                            return False
                    return True

            # Status
            if control_word == 'status':
                try:
                    profile = Profile.objects.select_related().get(mobile=sms.from_number)
                    ls = LocationSubscription.objects.select_related().filter(
                        user=profile.user,
                        phone_subscription=True,
                    )
                except:
                    ls = []
                reply_message = render_to_string('sms_control/reply/status.txt',
                    {'location_subscriptions': ls, 'language': language})
                return send_message(smart_str(reply_message), [sms.from_number])

            ### Reporter Class ###
            # Update
            if control_word == 'update':
                """
                Example of update sent from a reporter "131009 g 15 gd 0"
                    131009 - location uid
                    g - shorthand for source type
                    15 - 1.5 chlorine %
                    gd - organization code
                    0 - shorthand remarks
                """
                if user_group == 'sys_admin' or user_group == 'sys_reporter':
                    ss = shlex.shlex(smart_str(sms.message))
                    update_args = list(ss)[1:]
                    try:
                        profile = Profile.objects.select_related().get(mobile=sms.from_number)
                        user = profile.user
                    except:
                        reply_message = render_to_string('sms_control/reply/update_unknown_user_error.txt',
                            {'language': language,})
                        return send_message(smart_str(reply_message), [sms.from_number])

                    try:
                        location = Location.objects.get(uid=update_args[0])
                    except:
                        reply_message = render_to_string('sms_control/reply/update_location_error.txt',
                            {'language': language,})
                        return send_message(smart_str(reply_message), [sms.from_number])
                    try:
                        water_source_type = WaterSourceType.objects.get(mobile_shorthand_code__iexact=update_args[1])
                    except:
                        water_source_type = None
                    try:
                        chlorine_level_list = list(update_args[2])
                        chlorine_level = Decimal(str(chlorine_level_list[0]) + str('.') + str(''.join(chlorine_level_list[1:])))
                    except:
                        reply_message = render_to_string('sms_control/reply/update_chlorine_level_error.txt',
                            {'language': language,})
                        return send_message(smart_str(reply_message), [sms.from_number])
                    try:
                        provider = Provider.objects.get(mobile_shorthand_code__iexact=update_args[3])
                    except:
                        provider = None
                    try:
                        reporter_remark_code = int(update_args[4])
                        reporter_remark = LocationPostReporterRemarks.objects.get(code=reporter_remark_code)
                        remark = reporter_remark.text
                    except:
                        try:
                            remark = update_args[4]
                        except:
                            remark = ''
                    try:
                        location_post = LocationPost(
                            user=user,
                            location=location,
                            type=LocationPost.WATER_QUALITY_TYPE,
                            content=remark,
                            water_source_type=water_source_type,
                            provider=provider,
                            chlorine_level=chlorine_level,
                            status=LocationPost.PENDING_STATUS,
                            published_date=sms.sent_date,
                        )
                        location_post.save()
                        reply_message = render_to_string('sms_control/reply/update.txt', {'language': language,
                            'location_post': location_post,})
                        return send_message(smart_str(reply_message), [sms.from_number])
                    except:
                        reply_message = render_to_string('sms_control/reply/update_failed.txt', {'language': language,})
                        return send_message(smart_str(reply_message), [sms.from_number])
                else:
                    reply_message = render_to_string('sms_control/reply/invalid_request.txt',
                        {'sms_control_options': sms_control_translations, 'language': language,})
                    return send_message(smart_str(reply_message), [sms.from_number])

            ### Admin Class ###
            # Stats
            if control_word == 'stats':
                if user_group != 'sys_admin':
                    reply_message = render_to_string('sms_control/reply/invalid_request.txt',
                        {'sms_control_options': sms_control_translations, 'language': language,})
                    return send_message(smart_str(reply_message), [sms.from_number])
                location_posts = LocationPost.active_objects.filter(
                    type=LocationPost.WATER_QUALITY_TYPE,
                    published_date__gte=(datetime.datetime.now() - datetime.timedelta(days=1)),
                )
                users = User.objects.filter(is_active=True, groups__name='sys_public')
                locations = Location.active_objects.all()
                reply_message = render_to_string('sms_control/reply/stats.txt', {
                    'locations_posts_count': location_posts.count(),
                    'users_count': users.count(),
                    'locations_count': locations.count(),
                    'language': language,}
                )
                return send_message(smart_str(reply_message), [sms.from_number])

            return True
        except Exception, e:
            logger.error("Error processing sms id: %d. Error is %s", (sms.id, e))
            return False
        finally:
            translation.deactivate()


    def worker(self, *args, **kwargs):
        while True:
            try:
                sms_id = self.work_queue.get_nowait()
                sms = Sms.objects.get(id=sms_id)
                logger.info("Starting sms processing for id: %d" % sms.id)
            except Exception, e:
                time.sleep(5)
                continue

            try:
                user_group = 'sys_public'
                if sms.user_in_sys_reporter_group():
                   user_group = 'sys_reporter'
                if sms.user_in_sys_admin_group():
                    user_group = 'sys_admin'
                processing = self.process_sms(sms, user_group=user_group)
                if processing:
                    sms.status_processing=Sms.COMPLETED_STATUS
                    sms.save()
                    logger.info("Successfully processed sms id: %d" % sms.id)
            except Exception, e:
                logger.error("Error processing sms id %d: %s" % (sms.id, e))
            finally:
                sms.semaphore_processing = False
                sms.save()

    def handle(self, *args, **options):
        for i in range(self.num_processes):
            p = multiprocessing.Process(target=self.worker)
            p.daemon = True
            p.start()

        # catch TERM signal to allow finalizers to run and reap daemonic children
        signal.signal(signal.SIGTERM, lambda *args: sys.exit(-signal.SIGTERM))

        while True:
            sms_messages = Sms.objects.filter(
                semaphore_processing=False,
                status_processing=Sms.PENDING_STATUS,
            )
            for sms in sms_messages:
                try:
                    sms.semaphore_processing = True
                    sms.save()
                    self.work_queue.put(sms.id)
                    logger.info("Add sms id %d to processing queue" % sms.id)
                except:
                    logger.error("Error adding sms id %d to processing queue" % sms.id)
                    sms.semaphore_processing = False
                    sms.save()
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(5)