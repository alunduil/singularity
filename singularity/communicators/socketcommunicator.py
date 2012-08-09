# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import socket
import json

from singularity.communicators import Communicator
from singularity.parameters import SingularityParameters

logger = logging.getLogger(__name__) # pylint: disable=C0103

class SocketCommunicator(Communicator):
    def __init__(self, path = None, *args, **kwargs):
        super(SocketCommunicator, self).__init__(*args, **kwargs)

        # TODO Clean this up ...
        if not path:
            path = SingularityParameters()["socket_communicator.path"]
            if not path:
                path = os.path.join(SingularityParameters()["main.cache"], "singularity.sock") # pylint: disable=C0301

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

        # TODO Factor this out for the xen module as well.
        parsed = json.loads(message)

        message = {}

        try:
            message["function"] = parsed["name"]
        except KeyError:
            logger.warning("Did not recieve 'name' from message, %s", message)
        
        try:
            message["arguments"] = parsed["value"]
        except KeyError:
            logger.warning("Did not recieve 'value' from message, %s", message)

        # The other messages we can handle:
        # {
        #   "label": "public",
        #   "ips": [
        #     { 
        #       "netmask": "255.255.255.0",
        #       "enabled": "1",
        #       "ip": "198.101.227.76"
        #     }
        #   ],
        #   "mac": "40:40:97:83:78:2e",
        #   "ip6s": [
        #     {
        #       "netmask": "96",
        #       "enabled": "0",
        #       "ip": "2001:4800:780F:0511:1E87:052F:FF83:782E",
        #       "gateway": "fe80::def"
        #     }
        #   ],
        #   "gateway": "198.101.227.1",
        #   "slice": "21006919",
        #   "dns": [
        #     "72.3.128.240",
        #     "72.3.128.241"
        #   ]
        # }
        #
        # {
        #   "label": "private",
        #   "ips": [
        #     {
        #       "netmask": "255.255.128.0",
        #       "enabled": "1",
        #       "ip": "10.180.144.116"
        #     }
        #   ],
        #   "routes": [
        #     {
        #       "route": "10.176.0.0",
        #       "netmask": "255.240.0.0",
        #       "gateway": "10.180.128.1"
        #     },
        #     {
        #       "route": "10.191.192.0",
        #       "netmask": "255.255.192.0",
        #       "gateway": "10.180.128.1"
        #     }
        #   ],
        #   "mac": "40:40:a1:47:e2:af"
        # }

        message["ips"] = {}

        try:
            message["ips"][interface(parsed["mac"])] = []
        except KeyError:
            logger.warning("Did not receive 'mac' from message, %s", message)

        try:
            for ip in parsed["ips"]:
                message["ips"][interface(parsed["mac"])].append((cidr(ip["ip"], ip["netmask"]), "ipv4"))
        except KeyError:
            logger.warning("Did not receive 'ips' or 'ips.ip' or 'ips.netmask' from message, %s", message)

        try:
            for ip in parsed["ip6s"]:
                message["ips"][interface(parsed["mac"])].append((cidr(ip["ip"], ip["netmask"]), "ipv6"))
        except KeyError:
            logger.warning("Did not receive 'ip6s' or ip6s.ip' or 'ip6s.netmask' from message, %s", message)

        try:
            message["routes"][interface(parsed["mac"])] = []
        except KeyError:
            logger.warning("Did not receive 'mac' from message, %s", message)

        try:
            for ip in parsed["ips"]:
                message["routes"][interface(parsed["mac"])].append(("default", ip["gateway"], "ipv4"))
        except KeyError:
            logger.warning("Did not receive 'ips' or 'ips.gateway' from message, %s", message)

        try:
            for ip in parsed["ip6s"]:
                message["routes"][interface(parsed["mac"])].append(("default", ip["gateway"], "ipv6"))
        except KeyError:
            logger.warning("Did not receive 'ip6s' or 'ip6s.gateway' from message, %s", message)

        try:
            message["routes"][interface(parsed["mac"])].append(("default", parsed["gateway"], "ipv4")) # Should be ipv4 but need to verify ...
        except KeyError:
            logger.warning("Did not receive 'gateway' from message, %s", message)

        try:
            for route in parsed["routes"]:
                message["routes"][interface(parsed["mac"])].append((cidr(route["route"], route["netmask"]), route["gateway"], "ipv4")) # Should be ipv4 but need to verify ...
        except KeyError:
            logger.warning("Did not receive 'routes' or 'routes.route' or 'routes.netmask' or 'routes.gateway' from message, %s", message)

        try:
            for resolver in parsed["dns"]:
                message["resolvers"].append((resolver, "ipv4", interface(parsed["mac"]))) # Should be ipv4 but need to verify ...
        except KeyError:
            logger.warning("Did not receive 'dns' from message, %s", message)

        return identifier, message

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

def interface(mac_address):
    """The interface name for the given MAC address."""
    return None

def cidr(ip, netmask):
    bit_count = 0

    try:
        bits = reduce(lambda a, b: a << 8 | b, map(int, netmask.split('.')))

        while bits:
            bit_count += bits & 1
            bits >>= 1
    except AttributeError:
        bit_count = int(netmask)

    return "{0}/{1}".format(ip, bit_count)

