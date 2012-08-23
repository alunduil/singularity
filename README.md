singularity
===========

Smaller (in code; memory is up for debate) and more configurable guest agent for Openstack

Dependencies
============

* xen-tools if using xen
* python-daemon
* pycrypto

Description
===========

Provides an alternative to openstack-guest-agents-unix that tries to accomplish
the following as well as provide as much functionality of the aforementioned as
well:

* Small \*nix style daemon without any other considerations
* Pluggable functionality for the configurations managed
* Modular design in the hypervisor communication mechanisms
* More configurable (ability to restrict managed items by singularity)

There are features that openstack-guest-agents-unix provides directly that we
delegate to other softwares to accomplish:

* Locked to a particular python environment -> handled by virtualenv

Command Line Interfaces
-----------------------

Provides two subcommands (apply and daemon).  The daemon command controls the
daemonization of the service and once started resspond to a few signals
(explained below).  The apply subcommand on the other hand takes cached items
and re-applies them to the live system.  See the help for singularity (and its
subcommands) for more information and options.

Nearly all options on the command line can be set in the appropriate section of
the configuration file (defaults to /etc/singularity/singularity.conf)

Signals Interface
-----------------

* SIGHUP -> daemon reload
* SIGTERM,SIGINT -> daemon stop

New Server Protocol
===================

The following is an example exchange between the hypervisor and guest for a
working openstack guest agent (the hypervisor is designated H and the guest, G):

    H: {"name":"version", "value":"agent"}
    G: {"message":"9999", "returncode":"0"}
    
    H: {"name":"features", "value":""}
    G: {"message":"resetnetwork,injectfile,version,password,features,keyinit", "returncode":"0"}
    
    H: {"name":"resetnetwork", "value":""}
    G: {"message":"", "returncode":"0"}
    
    H: {"name":"keyinit", "value":"126190143978468524724357084322869"}
    G: {"message":"152515189133785336521547047713056", "returncode":"D0"}
    
    H: {"name":"password", "value":"YXazuqvtFdagFYrwKoYhWAbaJoW9eB7f+ju7GSwhBh4="}
    G: {"message":"", "returncode":"0"}

