import datetime
import logging
import multiprocessing
import os
import time

from django import db
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process Digicel Inbox Messages'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.num_processes = 4
        self.work_queue = multiprocessing.Queue()

    def worker(self, *args, **kwargs):
        while True:
            try:
                job = self.work_queue.get_nowait()
                logger.info("Starting " + str(job) + " ...") # TODO need logging handler to write to file
                mail_admins(str(job) + 'pid: ' + str(os.getpid()), 'ppid: ' + str(os.getppid()))
                logger.info("Sent email " + str(job))
            except:
                pass
            time.sleep(5)

    def handle(self, *args, **options):
        for i in range(self.num_processes):
            multiprocessing.Process(target=self.worker).start()

        i = 0
        while True:
            # TODO: Select messages with .STATUS_NEW
            # TODO: Update message to .STATUS_PROCESSING and .save() model
            # TODO: self.work_queue.put(message.id)
            self.work_queue.put(i)
            logger.info("Adding " + str(i) + " queue")
            if i > 30:
                logger.error('i > 30 ' + 'pid: ' + str(os.getpid()))
                raise Exception('My exception raised')
                break
            i += 1
            # TODO: test memory leakage with DEBUG=False. Uncomment reset_queries() if memory leakage present.
            #db.reset_queries()
            time.sleep(5)