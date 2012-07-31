# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

Communicator = None

if os.access(os.path.join(os.path.sep, "proc", "xen", "capabilities"), os.R_OK):
    from singularity.communicators.xen import XenCommunicator
    Communicator = XenCommunicator

