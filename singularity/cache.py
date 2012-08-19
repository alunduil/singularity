# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import itertools
import os

from singularity.parameters import SingularityParameters

# TODO Check if this should be "console"
logger = logging.getLogger(__name__) # pylint: disable=C0103

class SingularityCache(object): # pylint: disable=R0903
    """Dict-like interface for the cache directory for singularity.

    ### Description

    Provides a dict-like interface for interacting with the cache
    locations.  The keys for this dictionary are strings with the following
    form: "function.abs_path".

    ### Examples

    Keys:
    * network./etc/conf.d/net
    * hosts./etc/hosts
   
    """

    @property
    def files(self):
        return list(self.iterfiles())

    def iterfiles(self):
        return itertools.chain(*[ [ os.path.join(file_[0], name) for name in file_[2] ] for file_ in os.walk(SingularityParameters["main.cache"]) if len(file_[2]) ]) # pylint: disable=C0301

    def __len__(self):
        return len(self.files)

    def __getitem__(self, key):
        function, filename = key.split('.', 1)

        logger.info("Retrieving item with function, %s, and filename, %s", function, filename) # pylint: disable=C0301

        with open(cache_path(function, filename), "r") as cachefile:
            return cachefile.readlines()

    def __setitem__(self, key, value):
        function, filename = key.split('.', 1)

        logger.info("Setting item with function, %s, and filename, %s", function, filename) # pylint: disable=C0301

        if not os.path.exists(os.path.dirname(cache_path(function, filename))):
            os.makedirs(os.path.dirname(cache_path(function, filename)))

        # TODO Check for conflicts.

        with open(cache_path(function, filename), "w") as cachefile:
            cachefile.write("\n".join(value))

    def __delitem__(self, key):
        function, filename = key.split('.', 1)

        logger.info("Deleting item with function, %s, and filename, %s", function, filename) # pylint: disable=C0301

        if os.access(cache_path(function, filename), os.W_OK):
            os.unlink(cache_path(function, filename))

def cache_path(function, filename):
    return os.path.join(SingularityParameters()["main.cache"], function, filename[1:]) # pylint: disable=C0301

