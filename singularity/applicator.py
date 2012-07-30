# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

from singularity.parameters import SingularityParameters

logger = logging.getLogger("console") # pylint: disable=C0103

class SingularityApplicator(object):
    def __init__(self, arguments):
        self.arguments = arguments

    def __call__(self, functions = None):
        """Apply an existing configuration to the system.

        ### Description

        Checks for an existing set of configuration items in the cache
        directory (defaults to /var/cache/singularity) and replaces the
        corresponding items in the filesystem.

        """

        if not os.access(SingularityParameters()["main.cache"], os.R_OK):
            return

        if functions == "all":
            functions = set([ 
                    "network", "hosts", "resolvers", "reboot", "password"
                    ])

        functions &= set([ func.strip() for func in SingularityParameters()["main.functions"].split(",") ]) # pylint: disable=C0301

        for function in functions:
            logger.info("Applying %s configuration to the system ...", function) # pylint: disable=C0301

        # Check for cached items in the cache directory
        # Backup files if requested
        # Overwrite system files with cached versions

