# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

logger = logging.getLogger(__name__)

class SingularityConfigurator(object):
    def __init__(self):
        """Initalize any common properties of SingularityConfigurators."""
        pass

    @property
    def filename(self):
        """Name of the file this configurator provides content for.
        
        ### Description

        Returns the name of the file that this SingularityConfigurator provides
        content for.

        This property coupled with SingularityConfigurator.function allows
        Singularity to determine which of the runnable (see 
        SingularityConfigurator.runnable) configurators to apply to the system.

        ### Notes

        This attribute is not defined in the base class and *must* be
        implemented in specific configurators.
        
        """

        raise AttributeError("class {0} has no attribute 'filename'".format(self.__class__.__name__))

    @property
    def function(self):
        """Name of the function this configurator fulfills.

        ### Description

        Returns the function this configurator fulfills and allows Singularity
        to determine (along with SingularityConfigurator.filename) which
        configurators to run.

        ### Values

        Legal values that can be returned from this function are the following:
        * "network"
        * "hosts"
        * "resolvers"
        * "reboot"
        * "password"

        All other values are ignored and disqualify the configurator from being
        run.  Other values may be added in later incarnations of Singularity.

        ### Notes

        This attribute is not defined in the base class and *must* be
        implemented in specific configurators.

        """

        raise AttributeError("class {0} has no attribute 'function'".format(self.__class__.__name__))

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

        [2]: Available keys in configuration:
        * ips ::= dict(interface: tuple(ip, version))
        * routes ::= dict(interface: tuple(network, ip, version))
        * resolvers ::= list(tuple(ip, version))
        * hostname ::= str(hostname)
        * password ::= str(administrator password)
        
        ### Description

        Returns the runnability of this configurator.  If this property is true
        the configurator is eligible for being run on the system.

        ### Notes

        This method is not defined in the base class and *must* be implemented
        in specific configurators.

        """

        raise NotImplementedError("class {0} does not implement 'runnable(self, configuration)'".format(self.__class__.__name__))

    def content(self, configuration):
        """Generated content of this configurator as a list.
        
        ### Arguments

        Argument           | Description
        --------           | -----------
        [configuration][1] | Configuration settings to be applied by this configurator (dict)

        [1]: See SingularityConfigurator.runnable for more information.

        The configuration dict may have but must be tested for 

        ### Description

        List of lines that will make up the content of the file provided by
        this SingularityConfigurator.

        Typically this can be implemented as a list conversion of
        SingularityConfigurator.iter_content().

        ### Examples

        If we were creating a file (i.e. /etc/conf.d/hostname) the content
        would be the following data structure:

        >>> SingularityConfigurator.content()
        ['# Set to the hostname of this machine', 'hostname="host.example.com"]

        ### Notes

        The default implementation of this class is to convert
        SingularityConfigurator.iter_content to a list and should not be
        over-written in subclasses.

        ### See Also

        SingularityConfigurator.iter_content

        """

        return list(self.iter_content())

    def iter_content(self):
        """Generated content of this configurator as a generator.
        
        ### Description

        Generates lines for that will make up the content of the file provided
        by this SingularityConfigurator.

        ### Examples

        >>> SingularityConfigurator.iter_content()
        <generator object iter_content at 0xXXXXXXX>

        ### Notes

        This method is not defined in the base class and *must* be implemented
        in specific configurators.

        ### See Also

        SingularityConfigurator.content
        
        """

        raise NotImplementedError("class {0} does not implement 'iter_content(self)'".format(self.__class__.__name__))

class SingularityConfigurators(object):
    """Dictionary style object for interacting with the configurators.

    ### Description

    SingularityConfigurators acts like a read only list-like object.

    There is one readable property, path, that specifies the path the
    SingularityConfigurators searched for the configurators it contains.

    ### Examples

    >>> configurators = SingularityConfigurators(os.path.join(os.path.sep, "etc", "singularity", "configurators"))
    >>> configurators = SingularityConfigurators()
    >>> configurators.path
    ['/usr/lib/python2.7/site-packages/singularity/configurators', '/usr/local/lib/python2.7/site-packages/singularity/configurators']

    """

    def __init__(self, *directories):
        """Initialize and find all Configurators in the configurator path(s).

        ### Arguments

        Argument    | Description
        --------    | -----------
        directories | List of other directories to search for configurators (list)

        ### Description

        Populates this structure with the configurators found in the default
        path plus any other directories specified.

        ### Examples

        >>> SingularityConfiguration()
        <singularity.configurators.SingularityConfigurators instance at 0xXXXXXXX>

        >>> SingularityConfiguration("dir1", "dir2")
        <singularity.configurators.SingularityConfigurators instance at 0xXXXXXXX>

        """

        self._configurators = {}

        self.path = [
                os.path.join(os.path.abspath(os.path.dirname(__file__))), # Module's Directory
                os.path.join(re.sub(r"usr/", r"usr/local/", os.path.join(os.path.abspath(os.path.dirname(__file__))))), # Corresponding /usr/local location of Module's Directory
                ]

        logger.debug("Extra directories passed: %s", directories)

        self.path.extend(directories)

        logger.debug("SingularityConfigurator.path: %s", self.path)

        for directory in self.path:
            logger.info("Searching %s for SingularityConfigurators ...", directory)

            if not os.access(directory, os.R_OK):
                continue

            if directory not in sys.path:
                sys.path.append(directory)

            logger.debug("Files in current directory, %s: %s", directory, os.listdir(directory))

            module_names = list(set([ re.sub(r"\.py.?", "", filename) for filename in os.listdir(directory) if not filename.startswith("_") ]))

            logger.debug("Potential modules found: %s", module_names)

            modules = []

            for module_name in module_names:
                try:
                    modules.append(__import__(module_name, globals(), locals(), [], -1))
                except ImportError as error:
                    logger.warning("Module, %s, not able to be imported", module_name)
                    continue

            for module in modules:
                log.debug("Classes found in Module, %s: %s", module.__name__, inspect.getmembers(module, inspect.isclass))

                for object_ in [ object_() for name, object_ in inspect.getmembers(module, inspect.isclass) if issubclass(object_.__class__, SingularityConfigurator) and object_.__class__ != SingularityConfigurator]:
                    self._commands[object_.__class__.__name__] = object_

            self._commands = self._commands.values()

            logger.info("SingularityConfigurators found: %s", self._commands)

    def __len__(self):
        return len(self._commands)

    def __getitem__(self, key):
        return self._commands[key]

    def __iter__(self):
        for command in self._commands:
            yield command

    def __reversed__(self):
        tmp = copy.copy(self._commands)
        tmp.reverse()
        return tmp

    def __contains__(self, item):
        return item in self._commands

