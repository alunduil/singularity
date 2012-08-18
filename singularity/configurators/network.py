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

        try:
            self._ip_path = subprocess.check_output("which ip", shell = True) # pylint: disable=C0301,W0201
        except subprocess.CalledProcessError:
            pass

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
                command = [ self._ip_path, "address", "add", ip[0], "dev", interface ]
                subprocess.check_call(command)

        for interface, routes in configuration["routes"].iteritems():
            for route in routes:
                logger.info("Calling: %s route add to %s via %s dev %s", self._ip_path, route[0], route[1], interface) # pylint: disable=C0301
                command = [ self._ip_path, "route", "add", "to", route[0], "via", route[1], "dev", interface ]
                subprocess.check_call(command)

        return { "": "" }

