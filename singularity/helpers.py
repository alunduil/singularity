# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

logger = logging.getLogger(__name__) # pylint: disable=C0103

def virtual():
    """Emulate the ruby-facter virtual determination."""

    virtual = ""

    if os.access(os.path.join(os.path.sep, "proc", "xen", "capabilities"), os.R_OK): # pylint: disable=C0301
        virtual = "xenU"
    else:
        virtual = "physical"

    return virtual

VIRTUAL = virtual()

