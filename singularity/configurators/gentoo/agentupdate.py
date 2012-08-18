# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import subprocess

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class AgentUpdateConfigurator(SingularityConfigurator):
    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * Running as root
        * Can find the emerge command

        """

        if "function" not in configuration:
            logger.info("Must be passed a function in the message")
            return False

        if configuration["function"] != "agentupdate":
            logger.info("Must be passed \"agentupdate\" as the function")
            return False

        if os.getuid() != 0:
            logger.info("This command must be run as uid 0!")
            return False

        self._emerge_path = None # pylint: disable=W0201

        for prefix in ["/bin/", "/usr/bin/"]:
            try:
                self._emerge_path = subprocess.check_output(prefix + "which emerge") # pylint: disable=W0201,C0301
            except subprocess.CalledProcessError:
                pass

            if self._emerge_path is not None:
                break

        logger.debug("emerge path: %s", self._chpasswd_path)

        if self._emerge_path is None:
            logger.info("Must have access to emerge")
            return False

        logger.info("AgentUpdateConfigurator is runnable!")
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

        subprocess.check_call("{0} -1 app-emulation/singularity".format(self._emerge_path)) # pylint: disable=C0301

        return { "": "" }

