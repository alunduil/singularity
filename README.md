singularity
===========

Smaller and more configurable guest agent for Openstack

Command Line Interfaces
-----------------------

commonoptions = [
  --loglevel=LEVEL
  --configuration=FILE
  --cache=DIR
  --logfile=FILE (syslog, file, - STDOUT)
  --functions=FUNCIONS
  --help
  --version
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
  --chroot=DIR
  --core=on|off -> DEFAULT = off
  ]
singularity daemon [options] [start] :: DEFAULT
singularity daemon [options] [stop]
singularity daemon [options] [restart]
singularity daemon [options] [reload]

SIGNALS = [
  SIGHUP -> dameon restart
  SIGINT -> daemon stop
  SIGTERM -> daemon stop
  SIGUSR1 -> daemon reload
]
