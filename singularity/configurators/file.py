# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import base64

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class FileConfigurator(SingularityConfigurator):
    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * Recieve a function of file
        * Receive an argument

        """

        if "function" not in configuration:
            logger.info("Must be passed a function in the message")
            return False

        if configuration["function"] != "file":
            logger.info("Must be passed \"file\" as the function")
            return False

        if "arguments" not in configuration:
            logger.info("Must be passed an argument in the message")
            return False

        logger.info("FeaturesConfigurator is runnable!")
        return True

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.
        
        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration settings to be applied by this configurator (dict)

        ### Description

        Writes the file passed out to the disk.
        
        """
        
        # TODO Add capability to inject files with commas in them.
        filename, content = base64.b64decode(configuration["arguments"]).split(',', 1) # pylint: disable=C0301

        return { filename: content.split('\n') }

