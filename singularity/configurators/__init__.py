# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import re
import sys
import inspect
import copy

from singularity.parameters import SingularityParameters

logger = logging.getLogger(__name__) # pylint: disable=C0103

class SingularityConfigurator(object):
    def __init__(self):
        """Initalize any common properties of SingularityConfigurators."""
        pass

    @property
    def functions(self):
        """Name of the functions this configurator fulfills.

        ### Description

        Returns the function this configurator fulfills and allows Singularity
        to determine (along with SingularityConfigurator.filename) which
        configurators to run.

        ### Values

        Legal values that can be returned from this function are the following:
        * "network"
        * "hosts"
        * "hostname"
        * "resolvers"
        * "password"
        * "version" Not generally used as it returns the version of singularity
          on the server; not the version of the particular configurator.

        All other values are ignored and disqualify the configurator from being
        run.  Other values may be added in later incarnations of Singularity.

        ### Default Value

        A default value of the lowercase class name without any Configurator
        part is returned.  
        
        #### Examples
        
        Configurator Name    | Default Return Value
        -----------------    | --------------------
        PasswordConfigurator | ["password"]
        FooBarConfigurator   | ["foobar"]
        FooBar               | ["foobar"]

        """

        logger.debug("Probable function: %s", self.__class__.__name__.replace("Configurator", "").lower()) # pylint: disable=C0301
        return [self.__class__.__name__.replace("Configurator", "").lower()]

    def runnable(self, configuration):
        """True if configurator can run on this system and in this context.

        ### Arguments

        Argument           | Description
        --------           | -----------
        [configuration][1] | Configuration items to be applied (dict)

        [1]: The configuration dictionary may contain the
        [keys listed below][2] but this function's responsibility is not only
        to determine the runnability on the given system but also for the given
        configuration items.  If the configurator does not have all of the
        values it needs in the configuration dictionary it should alert
        Singularity that it is not runnable.

        TODO Change tuples to dicts?

        [2]: Available keys in configuration:
        * ips ::= dict(interface: list(tuple(ip, version)))
        * routes ::= dict(interface: list(tuple(network, ip, version)))
        * resolvers ::= list(tuple(ip, version, interface))
        * hostname ::= str(hostname)
        * password ::= str(administrator password)
        * function ::= str(system command to run)
        * arguments ::= str(arguments to command)
        
        ### Description

        Returns the runnability of this configurator.  If this property is true
        the configurator is eligible for being run on the system.

        ### Notes

        This method is not defined in the base class and *must* be implemented
        in specific configurators.

        """

        raise NotImplementedError("class {0} does not implement 'runnable(self, configuration)'".format(self.__class__.__name__)) # pylint: disable=C0301

    def content(self, configuration):
        """Generated content of this configurator as a dictionary.
        
        ### Arguments

        Argument           | Description
        --------           | -----------
        [configuration][1] | Configuration settings to be applied by this configurator (dict)

        [1]: See SingularityConfigurator.runnable for more information.

        The configuration dict may have but must be tested for 

        ### Description

        Dictionary mapping filenames being written to the content of the files
        provided by the SingularityConfigurator.

        ### Examples

        If we were creating a file (i.e. /etc/conf.d/hostname) the content
        would be the following data structure:

        >>> SingularityConfigurator.content()
        {'/etc/conf.d/hostname': '# Set to the hostname of this machine', 'hostname="host.example.com"}

        If the key "message" is returned this gets passed back to the host as
        a message in response to the passed configuration.

        ### Notes

        The default implementation of this class is to convert
        SingularityConfigurator.iter_content to a list and should not be
        over-written in subclasses.

        """

        raise NotImplementedError("class {0} does not implement 'iter_content(self)'".format(self.__class__.__name__)) # pylint: disable=C0301

class SingularityConfigurators(object): # pylint: disable=R0903
    """Dictionary style object for interacting with the configurators.

    ### Description

    SingularityConfigurators acts like a read only list-like object.

    There is one readable property, path, that specifies the path the
    SingularityConfigurators searched for the configurators it contains.

    ### Examples

    >>> configurators = SingularityConfigurators()
    >>> configurators.path
    ['/usr/lib/python2.7/site-packages/singularity/configurators', '/usr/local/lib/python2.7/site-packages/singularity/configurators']

    """

    def __init__(self):
        """Initialize and find all Configurators in the configurator path(s).

        ### Description

        Populates this structure with the configurators found in the default
        path plus any other directories specified.  The extra directories are
        expected to come in via the CLI or the configuration file.

        """

        self._configurators = {}

        mydir = os.path.abspath(os.path.dirname(__file__)) # Module's Directory
        self.path = [
                mydir,
                re.sub(r"usr/", r"usr/local/", mydir),
                os.path.join(SingularityParameters()["main.configuration"], "configurators"), # pylint: disable=C0301
                ]

        logger.debug("Extra directories passed: %s", SingularityParameters()["daemon.configurators"]) # pylint: disable=C0301
        logger.debug("Type of daemon.configurators: %s", type(SingularityParameters()["daemon.configurators"])) # pylint: disable=C0301
        self.path.extend(SingularityParameters()["daemon.configurators"] or [])

        logger.debug("SingularityConfigurator.path: %s", self.path)

        for directory in self.path:
            logger.info("Searching %s for SingularityConfigurators ...", directory) # pylint: disable=C0301

            if not os.access(directory, os.R_OK):
                continue

            if directory not in sys.path:
                sys.path.insert(0, directory)

            logger.debug("Files in current directory, %s: %s", directory, os.listdir(directory)) # pylint: disable=C0301

            module_names = list(set([ re.sub(r"\.py.?", "", filename) for filename in os.listdir(directory) if not filename.startswith("_") ])) # pylint: disable=C0301

            logger.debug("Potential modules found: %s", module_names)

            modules = []

            for module_name in module_names:
                try:
                    modules.append(__import__(module_name, globals(), locals(), [], -1)) # pylint: disable=C0301
                except ImportError:
                    logger.warning("Module, %s, not able to be imported", module_name) # pylint: disable=C0301
                    continue

            for module in modules:
                logger.debug("Classes found in Module, %s: %s", module.__name__, inspect.getmembers(module, inspect.isclass)) # pylint: disable=C0301

                for object_ in [ class_() for name, class_ in inspect.getmembers(module, inspect.isclass) if issubclass(class_, SingularityConfigurator) and class_ != SingularityConfigurator]: # pylint: disable=C0301,W0612
                    logger.debug("Found appropriate object, %s", object_)
                    self._configurators[object_.__class__.__name__] = object_

        logger.debug("Type of self._configurators: %s", type(self._configurators)) # pylint: disable=C0301

        self._configurators = self._configurators.values()

        logger.info("SingularityConfigurators found: %s", self._configurators) # pylint: disable=C0301

    def __len__(self):
        return len(self._configurators)

    def __getitem__(self, key):
        return self._configurators[key]

    def __iter__(self):
        for configurator in self._configurators:
            yield configurator

    def __reversed__(self):
        tmp = copy.deepcopy(self._configurators)
        tmp.reverse()
        return tmp

    def __contains__(self, item):
        return item in self._configurators

