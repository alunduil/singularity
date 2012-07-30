# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

"""Root Namespace for Singularity.

### Description

This module is not intended to provide any generic classes that would be useful
outside of a run of singularity itself (those types of functions have been
pushed to external projects as much as possible) but if a module that is useful
is found; feel free to fork said module into another project.  We simply ask
that you alert us so we can start working with you as an upstream provider for
the now separated functionality.

Classes and Features of this namespace:

Name          | Description
----          | -----------
Application   | Main driver for calling singularity from the command-line.
Parameters    | Abstraction overtop of the arguments passed on the CLI as well as the configuration file
Configurators | The work-horses, provides the content for configuration files on the system
Information   | Meta-information about the project itself (i.e. version, author, etc).

"""

