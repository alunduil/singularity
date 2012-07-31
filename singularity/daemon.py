# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from singularity.parameters import SingularityParameters

logger = logging.getLogger("console") # pylint: disable=C0103

class SingularityDaemon(object):
    def __init__(self):
        """Initialize the daemon context."""


    def __call__(self):
        """Watch the communication module for system updates to apply.

        ### Description

        Watches the communication bus (i.e. xenbus for xenU) and updates the
        allowed configuration items or runs the appropriate commands on the
        system.

        """

        action = SingularityParameters()["action"]

        if action == "start":
            self.start()
        elif action == "stop":
            self.stop()
        elif action == "reload":
            self.reinit()
        elif action == "restart":
            self.stop()
            while self.running:
                time.sleep(1)
            self.start()

    def start(self):
        context = daemon.DaemonContext()

        context.umask = 0o002
        context.pidfile = PidFile(SingularityParameters()["daemon.pidfile"])
        context.files_preserve = [ handler.stream for handler in logger.handlers if hasattr(self, stream) ]

        def term(signum, frame):
            logger.info("Shutting down.")
            context.close()
            sys.exit(0)

        def hup(signum, frame):
            SingularityParameters().reinit()

        context.signal_map = {
                signal.SIGTERM: term,
                signal.SIGINT: term,
                signal.SIGHUP: hup,
                }

        logger.info("Starting up.")
        with context:
            pass
           
    def stop(self):
        if self.running:
            logger.info("Sending daemon, %s, SIGTERM.", self.pid)
            os.kill(self.pid, signal.SIGTERM)
        else:
            logger.warning("Daemon not running.")

    def reinit(self):
        if self.running:
            logger.info("Sending daemon, %s, SIGHUP.", self.pid)
            os.kill(self.pid, signal.SIGTERM)
        else:
            logger.warning("Daemon not running.")

    @property
    def pid(self):
        if os.access(SingularityParameters()["daemon.pidfile"], os.R_OK):
            with open(SingularityParameters()["daemon.pidfile"], "r") as pidfile:
                return pidfile.readline()

    @property
    def running(self):
        return os.path.exists("/proc/{0}".format(self.pid))

class PidFile(object):
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
            raise SystemExit("Found an existing pidfile, %s, exiting.", self.path)

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

