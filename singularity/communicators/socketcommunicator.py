# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from singularity.communicators import Communicator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class SocketCommunicator(Communicator):
    def __init__(self, path = None, *args, **kwargs):
        super(SocketCommunicator, self).__init__(*args, **kwargs)

        if not path:
            path = SingularityParameters()["socket_communicator.path"]
            if not path:
                path = os.path.join(SingularityParameters()["main.cache"], "singularity.sock")

        logger.info("Setting up socket at %s", path)

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        if os.access(path, os.W_OK):
            os.remove(path)

        self.socket.bind(path)
        self.socket.listen(0) # To best emulate a hypervisor we only allow one connection. # pylint: disable=C0301
        self.connection = None

    def __del__(self):
        self.connection.close()

    def receive(self):
        """Recieve message from the user and package for upstream consumption

        ### Description

        Wait for a connection and read a message.

        """

        self.connection, address = self.socket.accept()

        message = ""
        while True:
            piece = self.connection.recv(4096)
            logger.debug("Received piece: %s", piece)
            if not piece:
                break
            message += piece

        logger.info("Got message, %s, from the user.")
        return hash(self), message

    def send(self, identifier, message):
        """Send the passed message to the user.

        ### Description

        Send the message to the user and wait for confirmation that
        evertyhing was successful.

        """

        logger.info("Sending message, %s")
        self.connection.send(message)

