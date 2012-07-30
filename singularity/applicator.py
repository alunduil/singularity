# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

logger = logging.getLogger(__name__)

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

        # Check for cached items in the cache directory
        # Backup files if requested
        # Overwrite system files with cached versions

        pass

