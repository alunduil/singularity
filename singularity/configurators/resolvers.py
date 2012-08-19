# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import re

from singularity.configurators import SingularityConfigurator

logger = logging.getLogger(__name__) # pylint: disable=C0103

class ResolversConfigurator(SingularityConfigurator):
    @property
    def resolvconf_path(self): # pylint: disable=R0201
        return os.path.join(os.path.sep, "etc", "resolv.conf")

    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration items to be applied (dict)

        ### Description

        We should be able to run if the following conditions are true:
        * An /etc/resolv.conf file is writable
        * We recieved the resolvers
        * The resolver entries don't already exist

        """

        if "resolvers" not in configuration:
            logger.info("Must be passed resolver information in the message")
            return False

        if not os.access(self.resolvconf_path, os.W_OK):
            logger.info("Must be able to write %s", self.resolvconf_path)
            return False

        existing_resolvers = set()
        with open(self.resolvconf_path, "r") as resolvconf:
            for line in resolvconf:
                match = re.search(r"nameserver.*(?P<ip>(?:\d{1,3}\.){3}\d{1,3})", line) # pylint: disable=C0301
                if not match:
                    continue
                existing_resolvers.add(match.group("ip"))
        if existing_resolvers >= set([ resolver[0] for resolver in configuration["resolvers"] ]): # pylint: disable=C0301
            logger.info("The passed resolvers are already in use.")
            return False

        logger.info("ResolverConfigurator is runnable!")
        return True

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.
        
        ### Arguments

        Argument      | Description
        --------      | -----------
        configuration | Configuration settings to be applied by this configurator (dict)

        ### Description

        Merge the resolver information from the configuration into the existing
        resolvers information.

        """

        lines = []

        if "hostname" in configuration:
            domain = ".".join(configuration["hostname"].split(".")[-2:])

        with open(self.resolvconf_path, "r") as resolvconf:
            lines.extend([ line.strip() for line in resolvconf.readlines() ])

            if "hostname" in configuration and "domain" not in "".join(lines):
                lines.append("domain {0}".format(domain))

            if "hostname" in configuration and "search" not in "".join(lines):
                lines.append("search {0}".format(domain))

            for resolver in configuration["resolvers"]:
                if resolver[0] not in "".join(lines):
                    lines.append("nameserver {0}".format(resolver[0]))

        return { self.resolvconf_path: lines }

