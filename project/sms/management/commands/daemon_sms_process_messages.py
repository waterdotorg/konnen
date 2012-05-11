import datetime
import logging
import multiprocessing
import os
import signal
import sys
import time

from django import db
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError

from sms.models import Sms

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process Digicel Inbox Messages'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.num_processes = multiprocessing.cpu_count()
        self.work_queue = multiprocessing.Queue()

    def worker(self, *args, **kwargs):
        while True:
            try:
                sms_id = self.work_queue.get_nowait()
                sms = Sms.objects.get(id=sms_id)
                logger.info("Starting sms processing for id %d" % sms.id)
            except Exception, e:
                time.sleep(5)
                continue

            try:
                # TODO do sms processing code...

                sms.status_processing=Sms.COMPLETED_STATUS
                sms.save()
            except Exception, e:
                logger.error("Error processing sms id %d: %s" % (sms.id, e))
            finally:
                sms.semaphore_processing = False
                sms.save()
            time.sleep(5)

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
                    self.work_queue.put(sms.id)
                    logger.info("Add sms id %d to processing queue" % sms.id)
                    sms.semaphore_processing = True
                    sms.save()
                except Exception, e:
                    logger.error("Error adding sms id %d to processing queue" % sms.id)
                    sms.semaphore_processing = False
                    sms.save()
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(5)