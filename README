singularity
===========

Smaller and more configurable guest agent for Openstack

Dependencies
============

* xen-tools

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

    commonoptions = [
    x  --loglevel=LEVEL
    x  --configuration=FILE
      --cache=DIR
    x  --logfile=FILE (syslog, file, - STDOUT)
      --functions=FUNCIONS
      --backups
    x  --help
    x  --version
    ]
    
    options = [
      commonoptions
      --force
      --dry-run
      ]
    singularity apply [options] [all] :: DEFAULT
    singularity apply [options] [network]
    singularity apply [options] [hosts]
    singularity apply [options] [resolvers]
    singularity apply [options] [reboot]
    singularity apply [options] [password]
    
    options = [
      commonoptions
      --pidfile=PIDFILE
      --uid=USER
      --gid=GROUP
      --core=on|off -> DEFAULT = off
      ]
    singularity daemon [options] [start] :: DEFAULT
    singularity daemon [options] [stop]
    singularity daemon [options] [restart]
    singularity daemon [options] [reload]
    
    Signals Interface
    -----------------
    
    SIGNALS = [
      SIGHUP -> dameon restart
      SIGINT -> daemon stop
      SIGTERM -> daemon stop
      SIGUSR1 -> daemon reload
    ]
    
