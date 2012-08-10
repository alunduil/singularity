# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import json
import os

logger = logging.getLogger(__name__) # pylint: disable=C0103

def translate(message): # pylint: disable=R0912
    """Translate the expected message to the new format.

    ### Arguments

    Argument | Description
    -------- | -----------
    message  | The string received from Xen or another communicator.

    ### Description

    If other communicators use a different message format this will have to be
    factored back into the individual communicators.

    ### Message Format Expected

    {
      "name": "resetnetwork",
    }

    {
      "name": "",
      "value": "",
    }

    {
      "label": "public",
      "ips": [
        { 
          "netmask": "255.255.255.0",
          "enabled": "1",
          "ip": "198.101.227.76"
        }
      ],
      "mac": "40:40:97:83:78:2e",
      "ip6s": [
        {
          "netmask": "96",
          "enabled": "0",
          "ip": "2001:4800:780F:0511:1E87:052F:FF83:782E",
          "gateway": "fe80::def"
        }
      ],
      "gateway": "198.101.227.1",
      "slice": "21006919",
      "dns": [
        "72.3.128.240",
        "72.3.128.241"
      ]
    }
    
    {
      "label": "private",
      "ips": [
        {
          "netmask": "255.255.128.0",
          "enabled": "1",
          "ip": "10.180.144.116"
        }
      ],
      "routes": [
        {
          "route": "10.176.0.0",
          "netmask": "255.240.0.0",
          "gateway": "10.180.128.1"
        },
        {
          "route": "10.191.192.0",
          "netmask": "255.255.192.0",
          "gateway": "10.180.128.1"
        }
      ],
      "mac": "40:40:a1:47:e2:af"
    }

    """

    parsed = json.loads(message)

    logger.info("Received message, %s", parsed)
    logger.debug("Type of message, %s", type(parsed))

    message = {}

    # TOOD Refactor this "parsing" to be more elegant.

    try:
        message["function"] = parsed["name"]
    except KeyError:
        logger.warning("Did not recieve 'name' from message, %s", parsed)
    
    try:
        message["arguments"] = parsed["value"]
    except KeyError:
        logger.warning("Did not recieve 'value' from message, %s", parsed)

    message["ips"] = {}

    try:
        logger.debug("Interface name for %s: %s", parsed["mac"], interface(parsed["mac"]))
        message["ips"][interface(parsed["mac"])] = []
    except KeyError:
        logger.warning("Did not receive 'mac' from message, %s", parsed)

    try:
        for ip in parsed["ips"]: # pylint: disable=C0103
            message["ips"][interface(parsed["mac"])].append((cidr(ip["ip"], ip["netmask"]), "ipv4")) # pylint: disable=C0301
    except KeyError:
        logger.warning("Did not receive 'ips' or 'ips.ip' or 'ips.netmask' from message, %s", parsed) # pylint: disable=C0301

    try:
        for ip in parsed["ip6s"]: # pylint: disable=C0103
            message["ips"][interface(parsed["mac"])].append((cidr(ip["ip"], ip["netmask"]), "ipv6")) # pylint: disable=C0301
    except KeyError:
        logger.warning("Did not receive 'ip6s' or ip6s.ip' or 'ip6s.netmask' from message, %s", parsed) # pylint: disable=C0301

    try:
        message["routes"][interface(parsed["mac"])] = []
    except KeyError:
        logger.warning("Did not receive 'mac' from message, %s", parsed)

    try:
        for ip in parsed["ips"]: # pylint: disable=C0103
            message["routes"][interface(parsed["mac"])].append(("default", ip["gateway"], "ipv4")) # pylint: disable=C0301
    except KeyError:
        logger.warning("Did not receive 'ips' or 'ips.gateway' from message, %s", parsed) # pylint: disable=C0301

    try:
        for ip in parsed["ip6s"]: # pylint: disable=C0103
            message["routes"][interface(parsed["mac"])].append(("default", ip["gateway"], "ipv6")) # pylint: disable=C0301
    except KeyError:
        logger.warning("Did not receive 'ip6s' or 'ip6s.gateway' from message, %s", parsed) # pylint: disable=C0301

    try:
        message["routes"][interface(parsed["mac"])].append(("default", parsed["gateway"], "ipv4")) # Should be ipv4 but need to verify ... # pylint: disable=C0301 
    except KeyError:
        logger.warning("Did not receive 'gateway' from message, %s", parsed)

    try:
        for route in parsed["routes"]:
            message["routes"][interface(parsed["mac"])].append((cidr(route["route"], route["netmask"]), route["gateway"], "ipv4")) # Should be ipv4 but need to verify ... # pylint: disable=C0301
    except KeyError:
        logger.warning("Did not receive 'routes' or 'routes.route' or 'routes.netmask' or 'routes.gateway' from message, %s", parsed) # pylint: disable=C0301

    try:
        logger.debug("Received DNS list: %s", parsed["dns"])
        message["resolvers"] = []
        for resolver in parsed["dns"]:
            logger.debug("Resolver to create an entry for: %s", resolver)
            message["resolvers"].append((resolver, "ipv4", interface(parsed["mac"]))) # Should be ipv4 but need to verify ... # pylint: disable=C0301
    except KeyError:
        logger.warning("Did not receive 'dns' or 'mac' from message, %s", parsed)
        if "resolvers" in message and not len(message["resolvers"]):
            del message["resolvers"]

    if len(message["ips"]):
        if not any([ len(message["ips"][nic]) for nic in message["ips"].iterkeys() ]):
            del message["ips"]
    else:
        del message["ips"]

    logger.info("Compiled message: %s", message)

    return message

def interface(mac_address):
    """The interface name for the given MAC address."""

    sys_net = os.path.join(os.path.sep, "sys", "class", "net")

    nics = {}
    for nic in os.listdir(sys_net):
        with open(os.path.join(sys_net, nic, "address")) as mac:
            nics[mac.read().strip()] = nic

    return nics[mac_address]

def cidr(ip, netmask): # pylint: disable=C0103
    """Converts an IP and Netmask into CIDR notation."""

    bit_count = 0

    try:
        bits = reduce(lambda a, b: a << 8 | b, [ int(octet) for octet in netmask.split('.') ]) # pylint: disable=C0301

        while bits:
            bit_count += bits & 1
            bits >>= 1
    except AttributeError:
        bit_count = int(netmask)

    return "{0}/{1}".format(ip, bit_count)

