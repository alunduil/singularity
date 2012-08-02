# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import daemon
import signal
import pwd
import grp
import os
import fcntl
import sys
import time

import singularity.communicators as communicators

from singularity.parameters import SingularityParameters
from singularity.configurators import SingularityConfigurators
from singularity.applicator import SingularityApplicator

logger = logging.getLogger("console") # pylint: disable=C0103

class SingularityDaemon(object):
    def __call__(self):
        actions = {
                "start": self.start,
                "stop": self.stop,
                "reload": self.reinit,
                "restart": self.restart,
                "status": self.status,
                }
        actions[SingularityParameters()["action"]]()

    def start(self): # pylint: disable=R0201
        """Watch the communication module for system updates to apply.

        ### Description

        Watches the communication bus (i.e. xenbus for xenU) and updates the
        allowed configuration items or runs the appropriate commands on the
        system.

        """

        # Summoning deamons is tricky business ... 
        #
        # "... for the demon shall bear a nine-bladed sword. NINE-bladed! Not
        # two or five or seven, but NINE, which he will wield on all wretched
        # sinners, sinners just like you, sir, there, and the horns shall be on
        # the head, with which he will..."

        context = daemon.DaemonContext()
        context.pidfile = PidFile(SingularityParameters()["daemon.pidfile"])
        context.umask = 0o002
        context.files_preserve = [ handler.stream for handler in logging.getLogger().handlers if hasattr(handler, "stream") ] # pylint: disable=C0301
        context.uid = pwd.getpwnam(SingularityParameters()["uid"]).pw_uid
        context.gid = grp.getgrnam(SingularityParameters()["gid"]).gr_gid
        context.prevent_core = not SingularityParameters()["coredumps"]

        def term_handler(signum, frame): # pylint: disable=W0613
            logger.info("Shutting down.")
            context.close()
            sys.exit(0)

        def hup_handler(signum, frame): # pylint: disable=W0613
            SingularityParameters().reinit()

        context.signal_map = {
                signal.SIGTERM: term_handler,
                signal.SIGINT: term_handler,
                signal.SIGHUP: hup_handler,
                }

        logger.info("Starting up.")
        with context:
            while True:
                communicator = communicators.create()
                identifier, message = communicator.receive()
                logger.info("Got message, %s, with identifier, %s", message, identifier) # pylint: disable=C0301

                functions = []

                # TODO Add proper error handling here ...

                for configurator in [ configurator for configurator in SingularityConfigurators() if configurator.runnable(message) ]: # pylint: disable=C0301
                    logger.info("Found configurator, %s, with functions, %s", configurator, configurator.functions) # pylint: disable=C0301
                    functions.extend(configurator.functions)
                    for filename, content in configurator.contents(message):
                        logger.info("Writing cache file, %s, from configurator, %s", os.path.join(SingularityParameters()["main.cache"], filename), configurator) # pylint: disable=C0301
                        with open(os.path.join(SingularityParameters()["main.cache"], filename), "w") as cachefile: # pylint: disable=C0301
                            cachefile.write(content)

                logger.info("Applying the functions found ...")
                SingularityApplicator()(actions = functions)

                # TODO Fill in response ...
                response = ""

                communicator.send(identifier, response)
           
    def stop(self):
        if self.running:
            logger.info("Sending daemon, %s, SIGTERM.", self.daemon_pid)
            os.kill(self.daemon_pid, signal.SIGTERM)
        else:
            logger.warning("Daemon not running.")

    def reinit(self):
        if self.running:
            logger.info("Sending daemon, %s, SIGHUP.", self.daemon_pid)
            os.kill(self.daemon_pid, signal.SIGHUP)
        else:
            logger.warning("Daemon not running.")

    def restart(self):
        self.stop()

        # TODO Change this to a non-busy wait somehow?
        while self.running:
            time.sleep(1)

        self.start()

    def status(self):
        logger.info("Singularity is running at %s", self.daemon_pid)

    @property
    def daemon_pid(self): # pylint: disable=R0201
        if os.access(SingularityParameters()["daemon.pidfile"], os.R_OK):
            with open(SingularityParameters()["daemon.pidfile"], "r") as pidfile: # pylint: disable=C0301
                return int(pidfile.readline())

    @property
    def running(self):
        return os.path.exists("/proc/{0}".format(self.daemon_pid))

class PidFile(object): # pylint: disable=R0903
    """Context manager for handling a locking pidfile.

    ### Description

    Implemented as class not generator because daemon is calling __exit__ with
    no parameters instead of the None, None, None specified by PEP-343.

    ### Notes

    http://code.activestate.com/recipes/577911-context-manager-for-a-daemon-pid-file/

    """

    def __init__(self, path):
        self.path = path
        self.pidfile = None

    def __enter__(self):
        self.pidfile = open(self.path, "a+")

        try:
            fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise SystemExit("Found an existing pidfile, %s, exiting.", self.path) # TODO Change this up a bit? # pylint: disable=C0301

        self.pidfile.seek(0)
        self.pidfile.truncate()
        self.pidfile.write(str(os.getpid()))
        self.pidfile.flush()
        self.pidfile.seek(0)

        return self.pidfile

    def __exit__(self, exc_type = None, exc_value = None, exc_tb = None):
        try:
            self.pidfile.close()
        except IOError as error:
            if error.errno != 9:
                raise
        os.remove(self.path)

