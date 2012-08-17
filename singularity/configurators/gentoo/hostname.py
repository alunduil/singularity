# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class GentooHostnameConfigurator(SingularityConfigurator):
    def functions(self):
        return ["hostname"]

    @property
    def confd_hostname_path(self): # pylint: disable=R0201
        return os.path.join(os.path.sep, "etc", "conf.d", "hostname")

    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * On a Gentoo system
        * Has a writable /etc/conf.d/hostname file

        """

        if "hostname" not in configuration:
            logger.info("Must be passed a hostname in the message")
            return False

        if os.access(self.confd_hostname_path, os.W_OK):
            logger.info("Can't write to %s", self.confd_hostname_path)
            return False

        logger.info("GentooHostnameConfigurator is runnable!")
        return True

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.

        ### Arguments

        Argumnet      | Description
        --------      | -----------
        configuration | Configuration settings to be applied by this configurator (dict)

        ### Description

        Provides the contents of /etc/conf.d/hostname.

        """

        lines = [
                "# Set to the hostname of this machine",
                "hostname=\"{0}\"".format(configuration["hostname"].split('.', 1)[0]), # pylint: disable=C0301
                ]

        return { self.confd_hostname_path: lines }

