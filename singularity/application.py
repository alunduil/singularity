# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import logging.handlers

# Setup basic console logging until the full logger is configured ...
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s-%(name)s: %(pathname)s:%(lineno)d in %(funcName)s: %(message)s"))

logger = logging.getLogger("console") 
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

import sys

import singularity.information

from singularity.parameters import SingularityParameters
from singularity.applicator import SingularityApplicator
from singularity.daemon import SingularityDaemon

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
        root = logging.getLogger("singularity")
        root.setLevel(getattr(logging, self.arguments["main.loglevel"].upper()))
        sladdr = { "linux2": "/dev/log", "darwin": "/var/run/syslog", }

        dhl = logging.handlers.SysLogHandler(facility = "daemon", address = sladdr[sys.platform])
        nhl = logging.handlers.SysLogHandler(facility = "daemon", address = sladdr[sys.platform])

        if self.arguments["main.loghandler"] == "-":
            dhl = logging.StreamHandler(stream = sys.stderr)
            nhl = logging.StreamHandler(stream = sys.stderr)
        elif self.arguments["main.loghandler"] != "syslog":
            dhl = logging.FileHandler(self.arguments["main.loghandler"], delay = True)
            nhl = logging.FileHandler(self.arguments["main.loghandler"], delay = True)

        dhl.setLevel(logging.DEBUG)
        nhl.setLevel(logging.INFO)

        # TODO Setup a custom formatter to handle levels appropriately ...
        dhl.setFormatter(logging.Formatter("%(levelname)s-%(name)s: %(pathname)s:%(lineno)d in %(funcName)s: %(message)s"))
        nhl.setFormatter(logging.Formatter("%(levelname)s-%(name)s: %(message)s"))

        root.addHandler(dhl)
        root.addHandler(nhl)

        for module in [ module for name, module in sys.modules.iteritems() if name.startswith("singularity") and module and "logger" in module.__dict__ ]:
            logger.debug("Module logger being changed on: %s", str(module))
            module.logger = logging.getLogger(module.__name__)

    def run(self):
        subcommands = {
                "apply": SingularityApplicator,
                "daemon": SingularityDaemon,
                }
        subcommands[self.arguments["subcommand"]](self.arguments)()

