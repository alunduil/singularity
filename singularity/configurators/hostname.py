# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import subprocess

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class HostnameConfigurator(SingularityConfigurator):
    """Common configurator actions for hostname functionality."""

    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * Running as root
        * Can find the hostname command

        """

        if "hostname" not in configuration:
            logger.info("Must be passed a hostname in the message")
            return False

        if os.getuid() != 0:
            logger.info("This command must be run as uid 0!")
            return False

        self._hostname_path = None # pylint: disable=W0201

        try:
            self._hostname_path = subprocess.check_output("which hostname", shell = True).strip() # pylint: disable=C0301,W0201,E1103
        except subprocess.CalledProcessError:
            pass

        logger.debug("hostname path: %s", self._hostname_path)

        if self._hostname_path is None:
            logger.info("Must have access to hostname")
            return False

        logger.info("HostnameConfigurator is runnable!")
        return True

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.
        
        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration settings to be applied by this configurator (dict)

        ### Description

        Runs the password commond on the password provided.

        """

        command = [ self._hostname_path, configuration["hostname"] ]
        subprocess.check_call(command) # pylint: disable=C0301

        return { "": "" }

