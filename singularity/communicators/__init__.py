# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from singularity import helpers

logger = logging.getLogger(__name__) # pylint: disable=C0103

def create(*args, **kwargs):
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

    if helpers.VIRTUAL == "xenU":
        from singularity.communicators.xencommunicator import XenCommunicator
        communicator = XenCommunicator(*args, **kwargs)
    # TODO Add KVM
    # TODO Add VirtualBox?
    # TODO Add VMWare?
    else: # Physical box or something we can't handle, set us up the socket.
        from singularity.communicators.socketcommunicator import SocketCommunicator # pylint: disable=C0301
        communicator = SocketCommunicator(*args, **kwargs)

    if not isinstance(communicator, Communicator):
        communicator = None

    return communicator

class Communicator(object):
    def receive(self):
        """Receive a message from the hypervisor and pass it to the requester.

        ### Description

        Blocking call that waits for a message from the hypervisor to process.
        Once we've received a message it is passed back to the caller of this
        method.

        Returns a tuple with an identifier for the message (to respond directly
        to that message) and the message received.

        The message should be a dictionary following the specification laid out
        in the singularity.configurators.SingularityConfigurator.runnable
        documentation.

        """

        raise NotImplementedError("class {0} does not implement 'receive(self)'".format(self.__class__.__name__)) # pylint: disable=C0301

    def send(self, identifier, message, status = 0):
        """Send a message (or response) to the hypervisor.

        ### Arguments

        Argument   | Description
        --------   | -----------
        identifier | The identifier of the message to respond to.
        message    | The message to send back to the hypervisor.
        status     | The status of the action that we are responding to.

        ### Description

        Blocking call that sends a message to the hypervisor.  

        """

        raise NotImplementedError("class {0} does not implement 'send(self, message)'".format(self.__class__.__name__)) # pylint: disable=C0301

