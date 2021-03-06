# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import sys

logger = logging.getLogger("console") # pylint: disable=C0103

CONFIG_DIR = os.path.join(os.path.sep, "etc", "singularity")

COMMON_PARAMETERS = [
        { # --loglevel=LEVEL, -l=LEVEL; LEVEL => warning
            "options": [ "--loglevel", "-l" ],
            "default": "warning",
            "metavar": "LEVEL",
            "choices": ["debug", "info", "warning", "error", "critical"],
            "help": \
                    "The logging level (corresponds to the levels in the " \
                    "python logging module).  LEVEL defaults to warning.",
            },
        { # --backup, -b
            "options": [ "--backup", "-b" ],
            "default": False,
            "action": "store_true",
            "help": \
                    "Create backup files of all items modified by " \
                    "singularity.  The backup file will be prefixed with '.' " \
                    "and suffixed with '.bak'.",
            },
        # TODO Change short option?
        { # --configuration=DIR, -f=DIR; DIR => /etc/singularity
            "options": [ "--configuration", "-f" ],
            "default": CONFIG_DIR,
            "metavar": "DIR",
            "help": \
                    "The configuration directory to use for various " \
                    "settings.  DIR defaults to /etc/singularity",
            },
        { # --cache=DIR, -c=DIR; DIR => /var/cache/singularity
            "options": [ "--cache", "-c" ],
            "default": os.path.join(os.path.sep, "var", "cache", "singularity"),
            "metavar": "DIR",
            "help": \
                    "The directory in which to cache items.  DIR defaults " \
                    "to /var/cache/singularity",
            },
        { # --loghandler=HANDLER, -l=HANDLER; HANDLER => syslog
            "options": [ "--loghandler", "-H" ],
            "default": "syslog",
            "metavar": "HANDLER",
            "help": \
                    "The log handler to utilize.  HANDLER defaults to " \
                    "syslog.  If a filepath is passed log messages will be " \
                    "sent to that file.",
            },
        { # --functions=FUNCTIONS, -F=FUNCTIONS; FUNCTIONS => network,hosts,resolvers,reboot,password # pylint: disable=C0301
            "options": [ "--functions", "-F" ],
            "default": "network,hosts,hostname,resolvers,password,file,update,version,features", # TODO Generate this somehow? # pylint: disable=C0301
            "metavar": "FUNCTIONS",
            "help": \
                    "The functions that should be handled by singularity.  " \
                    "FUNCTIONS defaults to \"network,hosts,resolvers,reboot," \
                    "password\".  By specifying a subset of these functions; " \
                    "only the specified functions will be handled by " \
                    "singularity.  WARNING!  IF NETWORK IS NOT ENABLED; NEW " \
                    "SERVERS BUILT FROM IMAGES WILL NOT HAVE ANY NETWORKING " \
                    "CONFIGURATION AND WILL NOT BE ACCESSIBLE OVER THE " \
                    "INTERNET",
            },
        ]

APPLY_PARAMETERS = [
        { # --noop
            "options": [ "--noop" ],
            "action": "store_true",
            "default": False,
            "help": \
                    "Show what actions would occur but don't apply any " \
                    "changes.  Works like a dry run mode and forces info " \
                    "level logging.  Overrides --force if it is specified.",
            },
        ]

DEFAULT_RUN = os.path.join(os.path.sep, "var", "run", "singularity")

DAEMON_PARAMETERS = [
        { # --run=DIR, -r=DIR; DIR => /var/run
            "options": [ "--run", "-r" ],
            "default": DEFAULT_RUN,
            "metavar": "DIR",
            "help": \
                    "The directory to store runtime items (sockets, etc).  " \
                    "Defaults to /var/run.",
            },
        { # --pidfile=FILE, -p=FILE; FILE => /var/run/singularity.pid
            "options": [ "--pidfile", "-p" ],
            "default": os.path.join(DEFAULT_RUN, "singularity.pid"),
            "metavar": "FILE",
            "help": \
                    "The file that holds the PID of the running daemon.  " \
                    "FILE defaults to /var/run/singularity.pid",
            },
        { # --uid=USER, -u=USER; USER => root
            "options": [ "--uid", "-u" ],
            "default": "root",
            "metavar": "USER",
            "help": \
                    "Username for the daemon to run as.  USER defaults to " \
                    "root.  This can be changed but doesn't make sense with " \
                    "certain functions (i.e. password).",
            },
        { # --gid=GROUP, -g=GROUP; GROUP => root
            "options": [ "--gid", "-g" ],
            "default": "root",
            "metavar": "GROUP",
            "help": \
                    "Group for the daemon to run as.  GROUP defaults to " \
                    "root.  This can be changed but doesn't make sense with " \
                    "certain functions (i.e. password).",
            },
        { # --coredumps
            "options": [ "--coredumps" ],
            "action": "store_true",
            "default": False,
            "help": "Turns on coredumps from singularity.  Defaults to False",
            },
        { # --nodaemonize
            "options": [ "--nodaemonize" ],
            "action": "store_true",
            "default": False,
            "help": \
                    "Detach, fork, the process into the background.  " \
                    "Defaults to False.",
            },
        { # --configurators=DIR, -d=DIR
            "options": [ "--configurators", "-d" ],
            "metavar": "DIR",
            "action": "append",
            "nargs": "*",
            "help": \
                    "Directories that the daemon should check for other " \
                    "configurators that may be provided by another mechanism " \
                    "or by the administrator.  Defaults to []; which " \
                    "includes no extra directories.",
            },
        ]

DEFAULTS = {}
DEFAULTS.update(dict([ (item["options"][0][2:], item["default"]) for item in COMMON_PARAMETERS if "default" in item ])) # pylint: disable=C0301
DEFAULTS.update(dict([ (item["options"][0][2:], item["default"]) for item in APPLY_PARAMETERS if "default" in item ])) # pylint: disable=C0301
DEFAULTS.update(dict([ (item["options"][0][2:], item["default"]) for item in DAEMON_PARAMETERS if "default" in item ])) # pylint: disable=C0301

logger.debug("DEFAULTS dictionary: %s", DEFAULTS)

class SingularityParameters(object): # pylint: disable=R0903
    # The borg make life easier than singletons when you sillywalk ...

    __shared_state = {}

    def __init__(self, *args, **kwargs):
        """Initialize the collapsed parameters for Singularity.

        ### Arguments

        Argument | Description
        -------- | -----------
        args     | The arguments to pass to the internal ArgumentParser.
        kwargs   | The arguments to pass to the internal ArgumentParser.

        ### Description

        Reads the parameters from the command line and configuration file and
        presents them as attributes of this class.  Will resolve parameters in
        the following order:
        1. Arguments on the command line
        2. Arguments specified in a configuration file
        3. Argument defaults

        """

        self.__dict__ = self.__shared_state

        if "_arguments" not in self.__dict__:
            from singularity.parameters.arguments import SingularityArguments
            self._arguments = SingularityArguments(*args, **kwargs)

        if "_configuration" not in self.__dict__:
            self.reinit()

    def __getitem__(self, key):
        short = key

        logger.debug("Finding key, %s, in parameters", key)
        logger.debug("Dots found in key: %s", key.count("."))

        if key.count(".") > 0:
            logger.debug("Splitting key, %s", key)
            section, short = key.split(".", 1) # pylint: disable=W0612

        default = "" 
        if short in DEFAULTS:
            default = DEFAULTS[short]
        logger.debug("default: %s", default)

        argument = ""
        if key in self._arguments:
            argument = self._arguments[key]
        logger.debug("argument: %s", argument)

        configuration = ""
        if key in self._configuration:
            configuration = self._configuration[key]
        logger.debug("configuration: %s", configuration)

        # TODO Collapse dictionaries into one reference.
        # TODO Check for string length seems unnecessary.
        if len(str(default)) and str(default) in sys.argv[0] or argument != default:
            logger.debug("Selected value: %s", argument)
            return argument

        if configuration:
            logger.debug("Selected value: %s", configuration)
            return configuration

        logger.debug("Selected value: %s", default or None) 
        return default or None

    def reinit(self):
        """Reload the configuration file parameters."""

        from singularity.parameters.configuration import SingularityConfiguration # pylint: disable=C0301
        self._configuration = SingularityConfiguration(os.path.join(self._arguments["configuration"], "singularity.conf")) # pylint: disable=C0301,W0201
        
