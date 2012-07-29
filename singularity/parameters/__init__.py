# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# muaor is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

logger = logging.getLogger(__name__)

COMMON_PARAMETERS = [
        { # --loglevel=LEVEL, -l=LEVEL; LEVEL => warning
            "options": [ "--loglevel", "-l" ],
            "default": "warning",
            "metavar": "LEVEL",
            "choices": ["debug", "info", "warning", "error", "critical"],
            "help": "".join([
                "The logging level (corresponds to the levels in the python ",
                "logging module).  LEVEL defaults to warning.",
                ]),
            },
        { # --configuration=FILE, -f=FILE; FILE => /etc/singularity.conf
            "options": [ "--configuration", "-f" ],
            "default": os.path.join(os.path.sep, "etc", "singularity.conf"),
            "metavar": "FILE",
            "help": "".join([
                "The configuration file to use for various settings.  FILE ",
                "defaults to /etc/singularity.conf",
                ]),
            },
        { # --cache=DIR, -c=DIR; DIR => /var/cache/singularity
            "options": [ "--cache", "-c" ],
            "default": os.path.join(os.path.sep, "var", "cache", "singularity"),
            "metavar": "DIR",
            "help": "".join([
                "The directory in which to cache items.  DIR defaults to ",
                "/var/cache/singularity",
                ]),
            },
        { # --loghandler=HANDLER, -l=HANDLER; HANDLER => syslog
            "options": [ "--loghandler", "-l" ],
            "default": "syslog",
            "metavar": "HANDLER",
            "help": "".join([
                "The log handler to utilize.  HANDLER defaults to syslog.  If ",
                "a filepath is passed log messages will be sent to that file.",
                ]),
            },
        { # --functions=FUNCTIONS, -F=FUNCTIONS; FUNCTIONS => network,hosts,resolvers,reboot,password
            "options": [ "--functions", "-F" ],
            "default": "network,hosts,resolvers,reboot,password",
            "metavar": "FUNCTIONS",
            "help": "".join([
                "The functions that should be handled by singularity.  ",
                "FUNCTIONS defaults to \"network,hosts,resolvers,reboot,",
                "password\".  By specifying a subset of these functions; ",
                "only the specified functions will be handled by singularity.",
                ]),
            },
        ]

APPLY_PARAMETERS = [
        { # --force
            "options": [ "--force" ],
            "action": "store_true",
            "default": False,
            "type": bool,
            "help": "".join([
                "Force all functions to run even if a subset is specified ",
                "with --functions or -F.",
                ]),
            },
        { # --noop
            "options": [ "--noop" ],
            "action": "store_true",
            "default": False,
            "type": bool,
            "help": "".join([
                "Show what actions would occur but don't apply any changes. ",
                "Works like a dry run mode and forces info level logging.",
                "Overrides --force if it is specified.",
                ]),
            },
        ]

DAEMON_PARAMETERS = [
        { # --pidfile=FILE, -p=FILE; FILE => /var/run/singularity.pid
            "options": [ "--pidfile", "-p" ],
            "default": os.path.join(os.path.sep, "var", "run", "singularity.pid"),
            "metavar": "FILE",
            "help": "".join([
                "The file that holds the PID of the running daemon.  FILE ",
                "defaults to /var/run/singularity.pid",
                ]),
            },
        { # --uid=USER, -u=USER; USER => root
            "options": [ "--uid", "-u" ],
            "default": "root",
            "metavar": "USER",
            "help": "".join([
                "Username for the daemon to run as.  USER defaults to root. ",
                "This can be changed but doesn't make sense with certain ",
                "functions (i.e. password).",
                ]),
            },
        { # --gid=GROUP, -g=GROUP; GROUP => root
            "options": [ "--gid", "-g" ],
            "default": "root",
            "metavar": "GROUP",
            "help": "".join([
                "Group for the daemon to run as.  GROUP defaults to root. ",
                "This can be changed but doesn't make sense with certain ",
                "functions (i.e. password).",
                ]),
            },
        { # --coredumps
            "options": [ "--coredumps" ],
            "action": "store_true",
            "default": False,
            "type": bool,
            "help": "".join([
                "Turns on coredumps from singularity.",
                ]),
            },
        ]

