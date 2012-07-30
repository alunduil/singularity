# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# muaor is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import sys
import argparse

logger = logging.getLogger(__name__)

class SingularityArguments(object):
    def __init__(self, *args, **kwargs):
        """Initialize the Singularity argument parser.

        ### Arguments

        Argument | Description
        -------- | -----------
        args     | The arguments to pass to the internal ArgumentParser.
        kwargs   | The arguments to pass to the internal ArgumentParser.

        ### Description

        Reads the parameters from the command line and presents them as
        attributes of this class.

        """

        self.__dict__["_parser"] = argparse.ArgumentParser(*args, **kwargs)
        
        self._parser.add_argument("--version", action = "version", version = "".join([
            "%(prog)s-{i.VERSION}\n",
            "\n",
            "Copyright {i.COPY_YEAR} by {i.AUTHOR} <{i.AUTHOR_EMAIL}> and ",
            "contributors.  This is free software; see the source for copying ",
            "conditions. There is NO warranty; not even for MERCHANTABILITY ",
            "or FITNESS FOR A PARTICULAR PURPOSE.",
            ]))

        import singularity.parameters

        # TODO See which way provides the desired option parsing ...
        common = argparse.ArgumentParser(add_help = False)
        for name, options in _extract_options(singularity.parameters.COMMON_PARAMETERS).iteritems():
            logger.debug("Adding option, %s, with options, %s and %s", name, options["args"], options["kwargs"])
            common.add_argument(*options["args"], **options["kwargs"])

        #for name, options in _extract_options(singularity.parameters.COMMON_PARAMETERS).iteritems():
        #    logger.debug("Adding option, %s, with options, %s and %s", name, options["args"], options["kwargs"])
        #    self._parser.add_argument(*options["args"], **options["kwargs"])

        subparsers = self._parser.add_subparsers(
                title = "Available subcommands:",
                dest = "subcommand"
                )

        apply_parser = subparsers.add_parser('apply', parents = [common], help = "".join([
            "Resets the configuration on the system based on the cached ",
            "values (last known settings received from the hypervisor) and ",
            "options passed to this command.",
            ]))

        for name, options in _extract_options(singularity.parameters.APPLY_PARAMETERS).iteritems():
            logger.debug("Adding option, %s, with options, %s and %s", name, options["args"], options["kwargs"])
            apply_parser.add_argument(*options["args"], **options["kwargs"])

        daemon_parser = subparsers.add_parser('daemon', parents = [common], help = "".join([
            "Watches for messages from the hypervisor and applies ",
            "configuration changes as they are received.",
            ]))

        for name, options in _extract_options(singularity.parameters.DAEMON_PARAMETERS).iteritems():
            logger.debug("Adding option, %s, with options, %s and %s", name, options["args"], options["kwargs"])
            daemon_parser.add_argument(*options["args"], **options["kwargs"])

        self.__dict__["_parsed_args"] = self._parser.parse_args()

    @property
    def parser(self):
        return self._parser

    @property
    def parsed_args(self):
        return self._parsed_args

    # TODO Switch to dictionary style access to handle section.name parameters?
    def __getattr__(self, key):
        return getattr(self._parsed_args, key)

def _extract_options(parameters):
    return dict([ (item["options"][0][2:], { "args": item.pop("options"), "kwargs": item }) for item in parameters ])

