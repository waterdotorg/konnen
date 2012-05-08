import logging
import time

import sms

from django import db
from django.core.management.base import BaseCommand, CommandError

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sms Message Polling'
    args = ''

    def handle(self, *args, **options):
        while True:
            try:
                s = sms.get_messages()
            except Exception, e:
                logger.error("Error importing sms messages: %s" % e)
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(5)