# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import subprocess
import tempfile

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

        if "password" not in configuration:
            logger.info("Must be passed a password in the message")
            return False

        if os.getuid() != 0:
            logger.info("This command must be run as uid 0!")
            return False

        self._chpasswd_path = None # pylint: disable=W0201

        try:
            self._chpasswd_path = subprocess.check_output("which chpasswd", shell = True) # pylint: disable=C0301,W0201,E1103
        except subprocess.CalledProcessError:
            pass

        logger.debug("chpasswd path: %s", self._chpasswd_path)

        if self._chpasswd_path is None:
            logger.info("Must have access to chpasswd")
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

        logger.debug("Passed password: %s", configuration["password"]) # TODO MUST BE REMOVED! # pylint: disable=C0301

        # TODO Stop using a tempfile somehow ...
        password = tempfile.TemporaryFile()
        password.write("root:{0}\n".format(configuration["password"]))
        password.seek(0)

        command = [ self._chpasswd_path ] 

        subprocess.check_call(command, stdin = password)

        return { "": "" }

