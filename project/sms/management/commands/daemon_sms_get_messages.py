import logging
import time

import sms

from django import db
from django.core.management.base import BaseCommand, CommandError

# Get an instance of a logger
logger = logging.getLogger(__name__)
# TODO need logging, both normal and concurrent

class Command(BaseCommand):
    help = 'Sms Message Polling'
    args = ''

    def handle(self, *args, **options):
        while True:
            try:
                logger.info("Starting sms get messages")
                s = sms.get_messages()
                logger.info("Ending sms get messages: %s" % s)
            except Exception, e:
                logger.error("Error importing sms messages: %s" % e)
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(5)