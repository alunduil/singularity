# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

from singularity.parameters import SingularityParameters

logger = logging.getLogger("console") # pylint: disable=C0103

class SingularityApplicator(object):
    def __call__(self, actions = None):
        """Apply an existing configuration to the system.

        ### Description

        Checks for an existing set of configuration items in the cache
        directory (defaults to /var/cache/singularity) and replaces the
        corresponding items in the filesystem.

        """

        cache_dir = SingularityParameters()["main.cache"]

        if not os.access(cache_dir, os.R_OK):
            logger.warning("Cache directory is not accessible.  Application aborted!") # pylint: disable=C0301
            return

        if not actions:
            actions = SingularityParameters()["action"]

        if actions == "all":
            actions = set([ "network", "hosts", "resolvers", "reboot", "password" ]) # pylint: disable=C0301

        actions &= set([ func.strip() for func in SingularityParameters()["main.functions"].split(",") ]) # pylint: disable=C0301

        for action in actions:
            logger.info("Applying %s configuration to the system ...", action)

            action_dir = os.path.join(cache_dir, action)

            if not os.access(action_dir, os.R_OK):
                logger.warning("Cache for %s not accessible.  Application of %s skipped!", action, action) # pylint: disable=C0301
                continue

            if os.access(os.path.join(action_dir, "conflict")):
                logger.error("Conflict found for %s!  Please check the logs for more information.") # pylint: disable=C0301
                continue

            # Find all files in action_dir
            # Backup all matching files in system if requested
            # Move all files from action_dir to the system locations

