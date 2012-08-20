# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import itertools
import os
import glob

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
        """The list of files in the cache."""
        logger.debug("Files in the cache: %s", list(self.iterfiles()))
        return list(self.iterfiles())

    def iterfiles(self):
        """Generator of list of files in the cache."""
        return itertools.chain(*[ [ os.path.join(file_[0], name) for name in file_[2] ] for file_ in os.walk(SingularityParameters()["main.cache"]) if len(file_[2]) ]) # pylint: disable=C0301

    def __len__(self):
        """Number of files in the cache."""
        return len(self.files)

    def __getitem__(self, key):
        """Retrieve an item from the cache.

        ### Description

        Given a key of the form function.abs_path, we retrive the contents of
        the associated file.

        ### Examples

        Keys:
        * network./etc.conf.d/net
        * resolvers./etc/resolve.conf

        """

        function, filename = key.split('.', 1)

        logger.info("Retrieving item with function, %s, and filename, %s", function, filename) # pylint: disable=C0301

        with open(cache_path(function, filename), "r") as cachefile:
            return [ line.strip() for line in cachefile.readlines() ]

    def __setitem__(self, key, value):
        """Set the contents of a specified file in the cache.

        ### Description

        Given a key (see __getitem__ for description and examples), set the
        contents of the cache file to the list of lines passed (value).

        """

        function, filename = key.split('.', 1)

        logger.info("Setting item with function, %s, and filename, %s", function, filename) # pylint: disable=C0301

        if not os.path.exists(os.path.dirname(cache_path(function, filename))):
            os.makedirs(os.path.dirname(cache_path(function, filename)))

        # TODO Check for conflicts.

        with open(cache_path(function, filename), "w") as cachefile:
            cachefile.write("\n".join(value) + "\n")

    def __delitem__(self, key):
        """Delete a file from the cache."""
        function, filename = key.split('.', 1)

        logger.info("Deleting item with function, %s, and filename, %s", function, filename) # pylint: disable=C0301

        if os.access(cache_path(function, filename), os.W_OK):
            os.unlink(cache_path(function, filename))

    def __iter__(self):
        for file_ in self.iterfiles():
            logger.debug("key: %s", file_.replace(SingularityParameters()["main.cache"] + "/", "").replace("/", "./", 1)) # pylint: disable=C0301
            yield file_.replace(SingularityParameters()["main.cache"] + "/", "").replace("/", "./", 1)

    def keys(self):
        """Files in the cache in key format."""
        return list(self.iterkeys())

    def iterkeys(self):
        return self.__iter__()

    def iter(self):
        return self.__iter__()

    def clear(self):
        """Delete all files in the cache."""
        for path in glob.glob(SingularityParameters()["main.cache"] + "/*"):
            os.removedirs(path)

    def __contains__(self, key):
        return key in list(self.iterkeys())

    def items(self):
        """Contents of files and their filenames."""
        return list(self.iteritems())

    def iteritems(self):
        for key in self.iterkeys():
            yield (key, self[key])

    def values(self):
        """The contents of files."""
        return list(self.itervalues())

    def itervalues(self):
        for key in self.iterkeys():
            yield self[key]

def cache_path(function, filename):
    return os.path.join(SingularityParameters()["main.cache"], function, filename[1:]) # pylint: disable=C0301

