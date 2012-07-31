# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import logging.handlers

# Setup basic console logging until the full logger is configured ...
handler = logging.StreamHandler() # pylint: disable=C0103
handler.setFormatter(logging.Formatter("%(levelname)s => %(name)s: %(pathname)s:%(lineno)d in %(funcName)s: %(message)s")) # pylint: disable=C0301

logger = logging.getLogger("console") # pylint: disable=C0103
logger.addHandler(handler)

import os

if "LOGLEVEL" in os.environ:
    logger.setLevel(getattr(logging, os.environ["LOGLEVEL"].upper()))

import sys

import singularity.information

from singularity.parameters import SingularityParameters
from singularity.applicator import SingularityApplicator
from singularity.daemon import SingularityDaemon

class SingularityApplication(object): # pylint: disable=R0903
    def __init__(self):
        global logger # pylint: disable=W0603

        SingularityParameters(
                description = singularity.information.DESCRIPTION,
                epilog = "".join([
                    "Copyright (C) {i.COPY_YEAR} by {i.AUTHOR} Licensed under ",
                    "a {i.LICENSE} License",
                    ]).format(i = singularity.information)
                )

        # Someone set us up the logger mechanisms ...
        root = logging.getLogger("singularity")
        root.setLevel(getattr(logging, SingularityParameters()["main.loglevel"].upper()))
        sladdr = { "linux2": "/dev/log", "darwin": "/var/run/syslog", }

        dhl = logging.handlers.SysLogHandler(facility = "daemon", address = sladdr[sys.platform]) # pylint: disable=C0301
        nhl = logging.handlers.SysLogHandler(facility = "daemon", address = sladdr[sys.platform]) # pylint: disable=C0301

        if SingularityParameters()["main.loghandler"] == "-":
            dhl = logging.StreamHandler(stream = sys.stderr)
            nhl = logging.StreamHandler(stream = sys.stderr)
        elif SingularityParameters()["main.loghandler"] != "syslog":
            dhl = logging.FileHandler(SingularityParameters["main.loghandler"], delay = True) # pylint: disable=C0301
            nhl = logging.FileHandler(SingularityParameters["main.loghandler"], delay = True) # pylint: disable=C0301

        dhl.setLevel(logging.DEBUG)
        nhl.setLevel(logging.INFO)

        dhl.setFormatter(logging.Formatter("%(levelname)s => %(name)s: %(pathname)s:%(lineno)d in %(funcName)s: %(message)s")) # pylint: disable=C0301
        nhl.setFormatter(logging.Formatter("%(levelname)s => %(name)s: %(message)s")) # pylint: disable=C0301

        class LevelFilter(logging.Filter):
            def __init__(self, level, *args, **kwargs):
                super(LevelFilter, self).__init__(*args, **kwargs)
                self._level = level

            def filter(self, record):
                return record.levelno <= self._level

        # TODO Switch to custom formatter instead to handle various formats ...
        dhl.addFilter(LevelFilter(logging.DEBUG))

        root.addHandler(dhl)
        root.addHandler(nhl)

        logger = logging.getLogger(__name__)

        for module in [ module for name, module in sys.modules.iteritems() if name.startswith("singularity") and module and "logger" in module.__dict__ ]: # pylint: disable=C0301
            logger.debug("Module logger being changed on: %s", str(module))
            module.logger = logging.getLogger(module.__name__)

    def run(self):
        logger.info("Running %s ... ", SingularityParameters()["subcommand"])
        subcommands = {
                "apply": SingularityApplicator,
                "daemon": SingularityDaemon,
                }
        subcommands[SingularityParameters()["subcommand"]]()()

