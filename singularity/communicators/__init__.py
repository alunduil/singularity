# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

logger = logging.getLogger(__name__) # pylint: disable=C0103

class Communicator(object):
    @classmethod
    def communicator(cls, *args, **kwargs):
        """Factory returns communication mechanism for the current hypervisor.

        ### Description

        Uses a facter style determination of the hypervisor we are running under
        and returns the appropriate communication translator for that bus.

        We check that the communicator found is a subclass of Communicator only
        to ensure we correctly handle known errors from the API provided.  Also
        since this is not dynamically pluggable it acts as a check that nothing
        blatant is missing upon release.

        """

        communicator = None

        if os.access(os.path.join(os.path.sep, "proc", "xen", "capabilities"), os.R_OK): # pylint: disable=C0301
            from singularity.communicators.xen import XenCommunicator
            communicator = XenCommunicator(*args, **kwargs)

        if not isinstance(communicator, Communicator):
            communicator = None

        return communicator

