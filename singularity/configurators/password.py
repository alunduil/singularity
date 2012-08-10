# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import pwd
import os
import subprocess

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class PasswordConfigurator(SingularityConfigurator):
    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * Running as root
        * Can find the passwd command

        """

        if pwd.getpwuid(os.getuid())[0] != "root":
            logger.info("This command must be run as root!")
            return False

        if subprocess.call("which passwd", shell = True) != 0:
            logger.info("Must have access to passwd")
            return False

        if "password" not in configuration:
            logger.info("Must be passed a password in the message")
            return False

        logger.info("PasswordConfigurator is runnable!")
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

        subprocess.call("passwd {0}".format(configuration["password"]), shell = True) # pylint: disable=C0301

        return { "": "" }

