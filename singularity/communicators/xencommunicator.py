# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import json
import Queue
import sys

import xen.xend.xenstore.xsutil as xs # pylint: disable=F0401

from xen.xend.xenstore.xswatch import xswatch # pylint: disable=F0401

import singularity.communicators.helpers as helpers

from singularity.communicators import Communicator
from singularity.helpers import crypto
from singularity.configurators.features import FeaturesConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class XenCommunicator(Communicator):
    """An attempt at introspecting the Openstack communication protocol.

    ### Description

    Reads from xenbus using the xen module and responding via the same
    mechanism.

    ### Notes

    Found the key!  /local/domain/<dom_id>
    To get the key: domid

    Although, once one knows this secret they can open up the following data
    structue with a xenstore ls /local/domain/<dom_id>:

    vm = "/vm/9a180993-ef93-6d0a-66bd-32557faa106e"
    vss = "/vss/9a180993-ef93-6d0a-66bd-32557faa106e"
    name = "slice21006919"
    cpu = ""
     0 = ""
      availability = "online"
     1 = ""
      availability = "online"
     2 = ""
      availability = "online"
     3 = ""
      availability = "online"
    memory = ""
     initial-reservation = "533504"
     static-max = "524288"
     target = "524288"
     dynamic-min = "524288"
     dynamic-max = "524288"
     memory-offset = "0"
    device = ""
     vbd = ""
      51744 = ""
       backend = "/local/domain/0/backend/vbd/89/51744"
       protocol = "x86_64-abi"
       state = "4"
       backend-id = "0"
       device-type = "disk"
       virtual-device = "51744"
       ring-ref = "8"
       event-channel = "27"
      51712 = ""
       backend = "/local/domain/0/backend/vbd/89/51712"
       protocol = "x86_64-abi"
       state = "4"
       backend-id = "0"
       device-type = "disk"
       virtual-device = "51712"
       ring-ref = "9"
       event-channel = "28"
     vif = ""
      0 = ""
       backend = "/local/domain/0/backend/vif/89/0"
       backend-id = "0"
       state = "4"
       handle = "0"
       mac = "40:40:97:83:78:2e"
       disconnect = "0"
       protocol = "x86_64-abi"
       tx-ring-ref = "10"
       rx-ring-ref = "1280"
       event-channel = "29"
       request-rx-copy = "1"
       feature-rx-notify = "1"
       feature-sg = "1"
       feature-gso-tcpv4 = "1"
      1 = ""
       backend = "/local/domain/0/backend/vif/89/1"
       backend-id = "0"
       state = "4"
       handle = "1"
       mac = "40:40:a1:47:e2:af"
       disconnect = "0"
       protocol = "x86_64-abi"
       tx-ring-ref = "1281"
       rx-ring-ref = "1282"
       event-channel = "30"
       request-rx-copy = "1"
       feature-rx-notify = "1"
       feature-sg = "1"
       feature-gso-tcpv4 = "1"
    error = ""
    drivers = ""
    control = ""
     platform-feature-multiprocessor-suspend = "1"
     feature-balloon = "1"
    attr = ""
     eth0 = ""
      ip = "xxx.xxx.xxx.xxx"
     eth1 = ""
      ip = "xxx.xxx.xxx.xxx"
     PVAddons = ""
      MajorVersion = "5"
      MinorVersion = "6"
      MicroVersion = "100"
      BuildVersion = "39153"
      Installed = "1"
    data = ""
     host = ""
     meminfo_total = "504076"
     meminfo_free = "159156"
     os_name = "gentoo"
     os_majorver = "2"
     os_minorver = "1"
     os_uname = "3.4.2-hardened-r1"
     os_distro = "gentoo"
     updated = "Tue Jul 31 20:09:21 CDT 2012"
    messages = ""
    vm-data = ""
     networking = ""
      40409783782e = "{"label":"public","ips":[{"netmask":"255.255.255.0","\..."
      4040a147e2af = "{"label":"private","ips":[{"netmask":"255.255.128.0",\..."
    platform = ""
     apic = "true"
     viridian = "true"
     acpi = "true"
     pae = "true"
     nx = "false"
     vcpu = ""
      number = "4"
      weight = "12"
    bios-strings = ""
     bios-vendor = "Xen"
     bios-version = ""
     system-manufacturer = "Xen"
     system-product-name = "HVM domU"
     system-version = ""
     system-serial-number = ""
     hp-rombios = ""
     oem-1 = "Xen"
     oem-2 = "MS_VM_CERT/SHA1/bdbeb6e0a816d43fa6d3fe8aaef04c2bad9d3e3d"
    unique-domain-id = "d5c91743-ae4b-cfe6-1976-04dde8c18fce"
    domid = "89"
    store = ""
     port = "1"
     ring-ref = "4912920"
    serial = ""
     0 = ""
      limit = "65536"
      tty = "/dev/pts/6"
      vncterm-pid = "18571"
      vnc-port = "5906"
    console = ""
     port = "2"
     ring-ref = "4912919"
     tty = "/dev/pts/6"

    Everything at the top level is directly accessible with xenstore (e.g.
    xenstore ls serial).  

    ### Communication

    The point of this method is to get information from the hypervisor, process
    that information, and then respond correctly.

    A special file (preferably universally unique) is used as the communication
    mechanism to talk with the host.  An example of one of these requests is
    shown here (JSON is the communication protocol):

    If the hypervisor runs the command version:
    >>> xenstore write data/host/d1e9770a-b30d-2320-6407-b27a2f7ed177 '{"name":"version", "value":"agent"}'

    The agent should respond with the following:
    >>> xenstore read data/guest/d1e9770a-b30d-2320-6407-b27a2f7ed177
    '{"message": "0.0.1.37", "returncode": "0"}'

    The commands the hypervisor may send (grabbed from openstack agent source:
    common/agent-client.py):

    * password
    * version
    * features
    * agentupdate
    * resetnetwork
    * injectfile
    * keyinit # Why can't we just have a diffie-hellman item?
    * kmsactivate # Apparently registers a RHEL box with RHN?
    * help # Registered as a command but only acts locally.

    Hostname is available in vm-data/hostname.
    IP information is available in vm-data/networking.

    """

    def __init__(self, receive_prefix = "data/host", send_prefix = "data/guest", data_prefix = "vm-data", *args, **kwargs): # pylint: disable=C0301
        """Initialize a communication "bus" with the Xen Hypervisor.

        ### Description

        Sets up watches on paths we'll be receiving data on in xenstore and 
        initializes pathing information used elsewhere.

        """

        super(XenCommunicator, self).__init__(*args, **kwargs)

        self._receive_prefix = receive_prefix
        self._send_prefix = send_prefix
        self._network_prefix = data_prefix + "/networking"
        self._hostname_prefix = data_prefix + "/hostname"

        self._queue = Queue.Queue()

        self.xs = xs.xshandle() # pylint: disable=C0103

        def xs_watch(path):
            logger.info("Received a watch even on %s", path)

            if path in [ self._receive_prefix, data_prefix ]:
                return True

            transaction = self.xs.transaction_start()
            message = self.xs.read(transaction, path)
            self.xs.transaction_end(transaction)

            logger.info("Received message, %s", message)

            self._queue.put((path, message))

            transaction = self.xs.transaction_start()
            message = self.xs.rm(transaction, path)
            self.xs.transaction_end(transaction)

            return True

        self.watches = []
        self.watches.append(xswatch(self._receive_prefix, xs_watch))

        transaction = self.xs.transaction_start()
        entries = self.xs.ls(transaction, self._receive_prefix)
        self.xs.transaction_end(transaction)

        logger.debug("Missed messages: %s", entries)

        if entries is not None:
            for path in [ self._receive_prefix + "/" + entry for entry in entries ]: # pylint: disable=C0301
                xs_watch(path)

    def __del__(self):
        logger.info("XenCommunicator watches are being removed.")
        for watch in self.watches:
            watch.unwatch()

    def receive(self): # pylint: disable=R0912
        """Recieve message from hypervisor and package for upstream consumption

        ### Description

        Wait for the watch to return some data and then pass that data to the
        caller.

        """

        message = None
        while message is None:
            path, message = self._queue.get(timeout = sys.maxint)
            logger.debug("Current message at path, %s: %s", path, message)

        identifier = path.replace(self._receive_prefix + "/", "")

        logger.info("Received identifier, %s", identifier)
        logger.info("Translating message: %s", message)
        logger.info("Type of message: %s", type(message))

        if type(message) is str:
            message = helpers.translate(message)

        if "function" in message:
            if message["function"] == "resetnetwork":
                msg = [] 

                # TODO Is this check necessary or should we just go for the 
                # TODO data?

                macs = set([ mac.replace(":", "") for mac in helpers.macs() if int(mac.replace(":", ""), 16) ]) # pylint: disable=C0301
                logger.debug("MAC Addresses: %s", macs)

                # TODO Is there a better way than a busy wait?
                # MAC Addresses are upper in next gen but lower in first gen
                # Why do things like this happen?

                entries = set()
                while set([ entry.lower() for entry in entries ]) < set([ mac.lower() for mac in macs ]): # Required since we can't assume anything about the entries coming back ... pylint: disable=C0301
                    transaction = self.xs.transaction_start()
                    entries = set(self.xs.ls(transaction, self._network_prefix))
                    self.xs.transaction_end(transaction)

                    logger.debug("Entries: %s", entries)

                for entry in entries:
                    transaction = self.xs.transaction_start()
                    msg.append(self.xs.read(transaction, self._network_prefix + "/" + entry)) # pylint: disable=C0301
                    self.xs.transaction_end(transaction)

                logger.debug("Message: %s", message)

                for item in msg:
                    tmp = helpers.translate(item)

                    logger.debug("Adding in items: %s", tmp)

                    if "ips" in tmp:
                        if "ips" not in message:
                            message["ips"] = {}
                        message["ips"].update(tmp.pop("ips"))

                    if "routes" in tmp:
                        if "routes" not in message:
                            message["routes"] = {}
                        message["routes"].update(tmp.pop("routes"))

                    message.update(tmp)

                    logger.debug("Message: %s", message)
                
                msg = None

                transaction = self.xs.transaction_start()
                if self.xs.ls(transaction, self._hostname_prefix) is not None:
                    msg = self.xs.read(transaction, self._hostname_prefix)
                self.xs.transaction_end(transaction)

                logger.debug("Found the hostname: %s", msg)

                if msg is not None:
                    message["hostname"] = msg

            elif message["function"] == "injectfile":
                message["function"] = "file"

            elif message["function"] == "agentupdate":
                message["function"] = "update"

            elif message["function"] == "keyinit":
                crypto.generate_keys(message["arguments"])

                logger.debug("Type of the key: %s", type(crypto.PUBLIC_KEY))

                self.send(identifier, str(crypto.PUBLIC_KEY), "D0")
                return self.receive() # Hoping it's not keyinit's all the way down ... # pylint: disable=C0301

            elif message["function"] == "version":
                logger.info("Faking the version passed back ...")

                self.send(identifier, "0.0.1.36") # Apparently it's a protocol version ...
                return self.receive()

            elif message["function"] == "password":
                if crypto.AES_KEYS is not None:
                    logger.info("Decrypting password")
                    message["password"] = crypto.decrypt(message["arguments"])
                    logger.debug("Password: encrypted => %s; decrypted => %s", message["arguments"], message["password"]) # pylint: disable=C0301
                    crypto.AES_KEYS = None
                else:
                    self._queue.put((path, message))
                    return self.receive() # Potential for busy loop with itself if no keyinit ever comes ... # pylint: disable=C0301

        logger.debug("Passing back identifier, %s, message, %s", identifier, message) # pylint: disable=C0301

        return identifier, message

    def send(self, identifier, message, status = 0):
        """Send the passed message to the hypervisor.

        ### Description

        Send the message to the hypervisor.

        """

        # I'm getting used to lying to the hypervisor but this is ridiculous.
        features = FeaturesConfigurator().content({})["message"]

        if message == features:
            message = []

            feature_mapping = {
                    "resetnetwork": set(["hosts", "network", "resolvers"]),
                    "injectfile": set(["file"]),
                    "agentupdate": set(["update"]),
                    }

            features = set(features.split(','))

            for result, items in feature_mapping.iteritems():
                if items & features:
                    message.append(result)
                    features -= items

            message.extend(features)
            message.append("keyinit") # Built-in to the communicator ...

            # The following are required for instances to start on build ...
            # Potentially restating items here in the event that other code
            # specifying these actions is removed.
            message.append("version")
            message.append("features")
            message.append("resetnetwork")
            message.append("keyinit")
            message.append("password")

            message = ",".join(list(set(message)))

            logger.debug("Replaced features for xen: %s", message)

        # TODO Add error handling that is appropriate here ...

        message = json.dumps({
            "returncode": str(status), # Upstream can't take an int ...
            "message": message,
            })

        transaction = self.xs.transaction_start()
        self.xs.write(transaction, self._send_prefix + "/" + identifier, message) # pylint: disable=C0301
        self.xs.transaction_end(transaction)

