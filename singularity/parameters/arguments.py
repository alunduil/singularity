# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import argparse
import copy

import singularity.information as info

logger = logging.getLogger("console") # pylint: disable=C0103

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

        self._parser = argparse.ArgumentParser(*args, **kwargs)
        
        self._parser.add_argument("--version", action = "version",
                version = "".join([
                    "%(prog)s-{version}\n",
                    "\n",
                    "Copyright {c} by {author} <{email}> and contributors.  ",
                    "This is free software; see the source for copying ",
                    "conditions. There is NO warranty; not even for ",
                    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.",
                    ]).format(version = info.VERSION, c = info.COPY_YEAR,
                        author = info.AUTHOR, email = info.AUTHOR_EMAIL)
                )

        import singularity.parameters

        common = argparse.ArgumentParser(add_help = False)
        for name, options in _extract_options(singularity.parameters.COMMON_PARAMETERS).iteritems(): # pylint: disable=C0301
            logger.debug("Adding option, %s, with options, %s and %s", name, options["args"], options["kwargs"]) # pylint: disable=C0301
            common.add_argument(*options["args"], **options["kwargs"]) # pylint: disable=W0142,C0301

        subparsers = self._parser.add_subparsers(
                title = "Available subcommands:",
                dest = "subcommand"
                )

        apply_parser = subparsers.add_parser('apply', parents = [common],
                help = "".join([
                    "Resets the configuration on the system based on the ",
                    "cached values (last known settings received from the ",
                    "hypervisor) and options passed to this command.",
                    ])
                )

        for name, options in _extract_options(singularity.parameters.APPLY_PARAMETERS).iteritems(): # pylint: disable=C0301
            logger.debug("Adding option, %s, with options, %s and %s", name, options["args"], options["kwargs"]) # pylint: disable=C0301
            apply_parser.add_argument(*options["args"], **options["kwargs"]) # pylint: disable=W0142,C0301

        daemon_parser = subparsers.add_parser('daemon', parents = [common],
                help = "".join([
                    "Watches for messages from the hypervisor and applies ",
                    "configuration changes as they are received.",
                    ])
                )

        for name, options in _extract_options(singularity.parameters.DAEMON_PARAMETERS).iteritems(): # pylint: disable=C0301
            logger.debug("Adding option, %s, with options, %s and %s", name, options["args"], options["kwargs"]) # pylint: disable=C0301
            daemon_parser.add_argument(*options["args"], **options["kwargs"]) # pylint: disable=W0142,C0301

        self._parsed_args = self._parser.parse_args()

    @property
    def parser(self):
        return self._parser

    @property
    def parsed_args(self):
        return self._parsed_args

    def __getitem__(self, key):
        if key.count("."):
            section, key = key.split('.', 1) # pylint: disable=W0612
        return getattr(self._parsed_args, key)

def _extract_options(parameters):
    parameters = copy.deepcopy(parameters)
    return dict([ (item["options"][0][2:], { "args": item.pop("options"), "kwargs": item }) for item in parameters ]) # pylint: disable=C0301

