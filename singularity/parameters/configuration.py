# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import ConfigParser

logger = logging.getLogger("console")

class SingularityConfiguration(object):
    def __init__(self, configuration):
        """Initialize the Singularity configuration file parameters.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | The file to read configuration parameters from.

        ### Description

        Reads the parameters from the configuration file and presents them as
        attributes of this class.

        """

        defaults = {}

        import singularity.parameters

        defaults.update(_extract_defaults(singularity.parameters.COMMON_PARAMETERS))
        logger.debug("Default values after %s: %s", "COMMON_PARAMETERS", defaults)

        defaults.update(_extract_defaults(singularity.parameters.DAEMON_PARAMETERS))
        logger.debug("Default values after %s: %s", "DAEMON_PARAMETERS", defaults)

        self.__dict__["_config"] = ConfigParser.SafeConfigParser(defaults)
        self._config.read(configuration)

        for section in [ "main", "apply", "daemon" ]:
            if not self._config.has_section(section):
                self._config.add_section(section)

    def __getitem__(self, key):
        section = "main"
        if key.count("."):
            section, key = key.split(".", 1)
        try:
            return self._config.get(section, key, raw = True)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return None

def _extract_defaults(parameters):
    return dict([ (item["options"][0][2:], item["default"]) for item in parameters if "default" in item ])

