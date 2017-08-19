# Copyright 2017, Inderpreet Singh, All rights reserved.

import signal
import sys
import time

# my libs
from common import PylftpContext, Constants
from controller import ControllerJob
from web import WebAppJob


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


class Pylftpd:
    """
    Implements the service for pylftp
    It is run in the main thread (no daemonization)
    """
    def __init__(self):
        # Create context
        self.context = PylftpContext()

        # Register the signal handlers
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGINT, self.signal)

        # Print context to log
        self.context.print_to_log()

    def run(self):
        self.context.logger.info("Starting pylftpd")

        # Define child threads
        controller_job = ControllerJob(
            context=self.context.create_child_context(ControllerJob.__name__)
        )
        webapp_job = WebAppJob(
            context=self.context.create_child_context(WebAppJob.__name__)
        )

        try:
            # Start child threads here
            controller_job.start()
            webapp_job.start()
            while True:
                time.sleep(Constants.MAIN_THREAD_SLEEP_INTERVAL_IN_SECS)
        except ServiceExit:
            # Join all the threads here
            controller_job.terminate()
            webapp_job.terminate()

            # Wait for the threads to close
            controller_job.join()
            webapp_job.join()

        self.context.logger.info("Finished pylftpd")

    def signal(self, signum: int, _):
        # noinspection PyUnresolvedReferences
        # Signals is a generated enum
        self.context.logger.info("Caught signal {}".format(signal.Signals(signum).name))
        raise ServiceExit()


if __name__ == "__main__":
    if sys.hexversion < 0x03050000:
        sys.exit("Python 3.5 or newer is required to run this program.")

    pylftpd = Pylftpd()
    pylftpd.run()