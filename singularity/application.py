# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# muaor is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from singularity.parameters import SingularityParameters

logger = logging.getLogger("DEFAULT")

class SingularityApplication(object):
    def __init__(self):
        global logger

        self.arguments = SingularityParameters(
                description = "".join([
                    "singularity(8) -- An Agent for Openstack Guest and ",
                    "Hypervisor Intercommunication.",
                    ]),
                epilog = "".join([
                    "Copyright (C) 2012 by Alex Brandt Licensed under an MIT ",
                    "License",
                    ])
                )

        # Someone set us up the logger mechanisms ...
        root = logging.getLogger()
        root.setLevel(getattr(logging, self.arguments.loglevel.upper()))
        sladdr = { "linux2": "/dev/log", "darwin": "/var/run/syslog", }

        dfl = logging.Formatter("%(levelname)s-%(name): %(pathname)s:%{lineno)d in %(funcName)s: %(message)s")
        nfl = logging.Formatter("%(levelname)s-%(name): %(message)s")

        dhl = logging.SysLogHandler(facility = "daemon", address = sladdr[sys.platform])
        nhl = logging.SysLogHandler(facility = "daemon", address = sladdr[sys.platform])

        if self.arguments.logfile == "-":
            dhl = logging.StreamHandler(stream = sys.stderr)
            nhl = logging.StreamHandler(stream = sys.stderr)
        elif self.arguments.logfile != "syslog":
            dhl = logging.FileHandler(self.arguments.logfile, delay = True)
            nhl = logging.FileHandler(self.arguments.logfile, delay = True)

        dhl.setLevel(logging.DEBUG)
        nhl.setLevel(logging.INFO)

        dhl.setFormatter(dfl)
        nhl.setFormatter(nfl)

        root.addHandler(dhl)
        root.addHandler(nhl)

        logger = logging.getLogger(__name__)

    def run(self):
        subcommands = {
                "apply": SingularityApplicator,
                "daemon": SingularityDaemon,
                }
        subcommands[self.arguments.subcommand](self.arguments)

    def apply_(self):
        """Apply an existing configuration to the system.

        ### Description

        Checks for an existing set of configuration items in the cache
        directory (defaults to /var/cache/singularity) and replaces the
        corresponding items in the filesystem.

        ### Algorithm

        1. Check for cached items in cache directory
        2. Backup files if requested
        3. Overwrite system files with cached versions

        """

        pass

    def daemon(self):
        """Watch the communication module for system updates to apply.

        ### Description

        Watches the communication bus (i.e. xenbus for xenU) and updates the
        allowed configuration items or runs the appropriate commands on the
        system.

        """
        
        pass

