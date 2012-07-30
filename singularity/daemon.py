# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

logger = logging.getLogger("console")

class SingularityDaemon(object):
    def __init__(self, arguments):
        self.arguments = arguments

    def __call__(self, action = "start"):
        """Watch the communication module for system updates to apply.

        ### Description

        Watches the communication bus (i.e. xenbus for xenU) and updates the
        allowed configuration items or runs the appropriate commands on the
        system.

        """

        pass

