# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import socket
import json

import singularity.communicators.helpers as helpers

from singularity.communicators import Communicator
from singularity.parameters import SingularityParameters

logger = logging.getLogger(__name__) # pylint: disable=C0103

class SocketCommunicator(Communicator):
    def __init__(self, path = None, *args, **kwargs):
        super(SocketCommunicator, self).__init__(*args, **kwargs)

        path = path or SingularityParameters()["socket_communicator.path"] or os.path.join(SingularityParameters()["main.cache"], "singularity.sock") # pylint: disable=C0301

        logger.info("Setting up socket at %s", path)

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

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

        identifier = hash(self) # Purely for API consistency.

        self.connection, address = self.socket.accept() # pylint: disable=W0612

        message = ""
        messages = self.connection.makefile("r")
        while True:
            piece = messages.readline().strip()

            if not len(piece): # Blank line separates messages ...
                break

            message += piece
        messages.close()

        logger.info("Got message, %s, from the user.", message)

        return identifier, helpers.translate(message)

    def send(self, identifier, message, status = 0):
        """Send the passed message to the user.

        ### Description

        Send the message to the user and wait for confirmation that
        evertyhing was successful.

        """

        logger.info("Sending message, %s", message)

        message = json.dumps({
            "returncode": status,
            "message": message,
            })

        try:
            self.connection.send(message) # This method does exist! I swear! pylint: disable=E1101,C0301
        except socket.error as error:
            if error.errno != 32: # No listener present!
                raise

