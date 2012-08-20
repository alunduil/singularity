# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class GentooNetworkConfigurator(SingularityConfigurator):
    @property
    def function(self):
        return "network"

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

        if not os.access(self.confd_net_path, os.W_OK):
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

        logger.debug("ips: %s", configuration["ips"])

        for interface, ips in configuration["ips"].iteritems():
            lines.append("config_{0}=\"".format(interface))
            for ip in ips: # pylint: disable=C0103
                lines.append(ip[0])
            lines.append("\"")

        for interface, routes in configuration["ips"].iteritems():
            lines.append("routes_{0}=\"".format(interface))
            logger.debug("routes for %s: %s", interface, routes)
            for route in routes:
                lines.append("{0} via {1}".format(route[0], route[1]))
            lines.append("\"")

        return { self.confd_net_path: lines }

