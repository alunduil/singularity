# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

import singularity.information as info

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class VersionConfigurator(SingularityConfigurator):
    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * Recieve a function of version

        """

        if "function" not in configuration:
            logger.info("Must be passed a function in the message")
            return False

        if configuration["function"] != "version":
            logger.info("Must be passed \"version\" as the function")
            return False

        logger.info("VersionConfigurator is runnable!")
        return True

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.
        
        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration settings to be applied by this configurator (dict)

        ### Description

        Returns the requested version information.  As a return message.

        """

        versions = {
                "agent": info.VERSION,
                "singularity": info.VERSION,
                }

        if "arguments" in configuration:
            try:
                return { "message": versions[configuration["arguments"]] }
            except KeyError: # Default to the agent version.
                return { "message": versions["agent"] }
        return { "message": "versions: {0}".format(versions) }

