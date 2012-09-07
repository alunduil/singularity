# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from __future__ import print_function

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
from singularity.cache import SingularityCache

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

        if not os.path.exists(SingularityParameters()["daemon.run"]):
            os.makedirs(SingularityParameters()["daemon.run"])

        context.pidfile = PidFile(SingularityParameters()["daemon.pidfile"])
        context.umask = 0o002
        context.uid = pwd.getpwnam(SingularityParameters()["daemon.uid"]).pw_uid
        context.gid = grp.getgrnam(SingularityParameters()["daemon.gid"]).gr_gid
        context.prevent_core = not SingularityParameters()["daemon.coredumps"]
        context.detach_process = not SingularityParameters()["daemon.nodaemonize"] # pylint: disable=C0301

        context.files_preserve = []
        context.files_preserve.extend([ handler.stream for handler in logging.getLogger().handlers if hasattr(handler, "stream") ]) # pylint: disable=C0301
        context.files_preserve.extend([ handler.socket for handler in logging.getLogger().handlers if hasattr(handler, "socket") ]) # pylint: disable=C0301

        logger.debug("Preserved files: %s", context.files_preserve)
        logger.debug("Open files: %s", [ os.path.realpath(os.path.join(os.path.sep, "proc", "self", "fd", fd)) for fd in os.listdir(os.path.join(os.path.sep, "proc", "self", "fd")) ]) # pylint: disable=C0301

        def term_handler(signum, frame): # pylint: disable=W0613
            """TERM and INT shut down the daemon."""
            logger.info("Shutting down.")
            context.close()
            logging.shutdown()
            sys.exit(0)

        def hup_handler(signum, frame): # pylint: disable=W0613
            """HUP signal reloads the configuration and configurators."""
            SingularityParameters().reinit()
            self._configurators = SingularityConfigurators()

        context.signal_map = {
                signal.SIGTERM: term_handler,
                signal.SIGINT: term_handler,
                signal.SIGHUP: hup_handler,
                }

        logger.info("Starting up.")
        with context:

            self._configurators = SingularityConfigurators() # pylint: disable=W0201,C0301
            self._communicator = communicators.create() # pylint: disable=W0201

            while True:
                logger.debug("Open files: %s", [ os.path.realpath(os.path.join(os.path.sep, "proc", "self", "fd", fd)) for fd in os.listdir(os.path.join(os.path.sep, "proc", "self", "fd")) ]) # pylint: disable=C0301

                identifier, message = self._communicator.receive()
                logger.info("Got message, %s, with identifier, %s", message, identifier) # pylint: disable=C0301

                functions = set()
                response = ""

                # TODO Add proper error handling here ...

                logger.debug("Length of configurators: %s", len(self._configurators)) # pylint: disable=C0301

                for configurator in self._configurators:
                    if configurator.function not in [ func.strip() for func in SingularityParameters()["main.functions"].split(",") ]: # pylint: disable=C0301
                        logger.info("Configurator, %s, is not allowed.", configurator) # pylint: disable=C0301
                        continue

                    if not configurator.runnable(message):
                        logger.info("Configurator, %s, is not runnable.", configurator) # pylint: disable=C0301
                        continue

                    logger.info("Found configurator, %s, with function, %s", configurator, configurator.function) # pylint: disable=C0301
                    functions.add(configurator.function)

                    for filename, content in configurator.content(message).iteritems(): # pylint: disable=C0301
                        if "message" == filename:
                            response += content + "\n"
                        elif filename.startswith("/"):
                            SingularityCache()[configurator.function + "." + filename] = content # pylint: disable=C0301

                logger.info("Applying the functions found ...")
                logger.debug("Functions found: %s", functions)
                SingularityApplicator()(actions = functions)

                response = "" + "\n" + response

                self._communicator.send(identifier, response.strip())
           
    def stop(self):
        """Stop any running daemons.
        
        ### Description

        Sends a SIGTERM to any daemon that is currently running.
        
        """
        if self.running:
            logger.info("Sending daemon, %s, SIGTERM.", self.daemon_pid)
            os.kill(self.daemon_pid, signal.SIGTERM)
        else:
            logger.warning("Daemon not running.")
            print("Singularity is not running ...", file = sys.stderr)

    def reinit(self):
        """Reinitializes the daemon.

        ### Description

        Sends a SIGHUP to any daemon that is currently running.  If no daemon
        is running it starts the daemon.

        """

        if self.running:
            logger.info("Sending daemon, %s, SIGHUP.", self.daemon_pid)
            os.kill(self.daemon_pid, signal.SIGHUP)
        else:
            logger.warning("Daemon not running.")
            self.start()

    def restart(self):
        """Stop and start the daemon.

        ### Description

        Stops the daemon and then waits for it to actually stop running before
        starting the daemon again.

        """

        self.stop()

        while self.running:
            time.sleep(1)

        self.start()

    def status(self):
        """Reports the pid of a running daemon."""
        logger.info("Singularity is running at %s", self.daemon_pid)

    @property
    def daemon_pid(self): # pylint: disable=R0201
        """Returns the pid of a running daemon."""
        try: # There is a race condition if we do a check first ... skipping.
            with open(SingularityParameters()["daemon.pidfile"], "r") as pidfile: # pylint: disable=C0301
                return int(pidfile.readline())
        except IOError as error:
            if error.errno != 2:
                raise
            return None

    @property
    def running(self):
        """True if the daemon is currently running."""
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

