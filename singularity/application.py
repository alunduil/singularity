# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import logging.handlers
import sys

import singularity.information

from singularity.parameters import SingularityParameters

logger = logging.getLogger("console")

class SingularityApplication(object):
    def __init__(self):
        global logger

        self.arguments = SingularityParameters(
                description = singularity.information.DESCRIPTION,
                epilog = "".join([
                    "Copyright (C) {i.COPY_YEAR} by {i.AUTHOR} Licensed under ",
                    "a {i.LICENSE} License",
                    ]).format(i = singularity.information)
                )

        # Someone set us up the logger mechanisms ...
        root = logging.getLogger()
        root.setLevel(getattr(logging, self.arguments["main.loglevel"].upper()))
        sladdr = { "linux2": "/dev/log", "darwin": "/var/run/syslog", }

        dfl = logging.Formatter("%(levelname)s-%(name)s: %(pathname)s:%{lineno)d in %(funcName)s: %(message)s")
        nfl = logging.Formatter("%(levelname)s-%(name)s: %(message)s")

        dhl = logging.handlers.SysLogHandler(facility = "daemon", address = sladdr[sys.platform])
        nhl = logging.handlers.SysLogHandler(facility = "daemon", address = sladdr[sys.platform])

        if self.arguments["main.loghandler"] == "-":
            dhl = logging.StreamHandler(stream = sys.stderr)
            nhl = logging.StreamHandler(stream = sys.stderr)
        elif self.arguments["main.loghandler"] != "syslog":
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
        subcommands[self.arguments.subcommand](self.arguments)()

