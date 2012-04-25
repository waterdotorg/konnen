import logging
import time

from django import db
from django.core.management.base import BaseCommand, CommandError

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Digicel Inbox Polling'
    args = ''

    def handle(self, *args, **options):
        i = 0
        while True:
            if i > 10:
                logger.error('i is > 10 dude! sys.exit() confirmed!!!')
                raise Exception('My exception raised')
            i += 1
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(5)