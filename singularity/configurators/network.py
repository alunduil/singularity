# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import subprocess

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class NetworkConfigurator(SingularityConfigurator):
    """Common configurator actions for network functionality."""

    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * Running as root
        * Can find the ip command

        """

        if "ips" not in configuration:
            logger.info("Must be passed ips in the message")
            return False

        if "routes" not in configuration:
            logger.info("Must be passed routes in the message")
            return False

        if os.getuid() != 0:
            logger.info("This command must be run as uid 0!")
            return False

        self._ip_path = None # pylint: disable=W0201

        for prefix in ["/bin/", "/usr/bin/"]:
            try:
                self._ip_path = subprocess.check_output(prefix + "which ip") # pylint: disable=C0301,W0201
            except subprocess.CalledProcessError:
                pass

            if self._ip_path is not None:
                break

        logger.debug("ip path: %s", self._ip_path)

        if self._ip_path is None:
            logger.info("Must have access to ip")
            return False

        logger.info("NetworkConfigurator is runnable!")
        return True

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.
        
        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration settings to be applied by this configurator (dict)

        ### Description

        Runs the ip commond on the information provided.

        """

        for interface, ips in configuration["ips"].iteritems():
            for ip in ips: # pylint: disable=C0103
                logger.info("Calling: %s addr add %s dev %s", self._ip_path, ip[0], interface) # pylint: disable=C0301
                subprocess.check_call("{0} addr add {1} dev {2}".format(self._ip_path, ip[0], interface)) # pylint: disable=C0301

        for interface, routes in configuration["routes"].iteritems():
            for route in routes:
                logger.info("Calling: %s route add to %s via %s dev %s", self._ip_path, route[0], route[1], interface) # pylint: disable=C0301
                subprocess.check_call("{0} route add to {1} via {2} dev {3}".format(self._ip_path, route[0], route[1], interface)) # pylint: disable=C0301

        return { "": "" }

class GentooNetworkConfigurator(SingularityConfigurator):
    def functions(self):
        return ["network"]

    @property
    def confd_net_path(self): # pylint: disable=R0201
        return os.path.join(os.path.sep, "etc", "conf.d", "net")

    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * On a Gentoo system
        * Has a writable /etc/conf.d/net file

        """

        if "ips" not in configuration:
            logger.info("Must be passed ips in the message")
            return False

        if os.access(self.confd_net_path, os.W_OK):
            logger.info("Can't write to %s", self.confd_net_path)
            return False

        logger.info("GentooNetworkConfigurator is runnable!")
        return True

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.

        ### Arguments

        Argumnet      | Description
        --------      | -----------
        configuration | Configuration settings to be applied by this configurator (dict)

        ### Description

        Provides the contents of /etc/conf.d/net.

        """

        lines = []

        for interface, ips in configuration["ips"]:
            lines.append("config_{0}=\"".format(interface))
            for ip in ips: # pylint: disable=C0103
                lines.append(ip[0])
            lines.append("\"")

        for interface, routes in configuration["ips"]:
            lines.append("routes_{0}=\"".format(interface))
            for route in routes:
                lines.append("{0} via {1}".format(route[0], route[1]))
            lines.append("\"")

        return { self.confd_net_path, lines }

