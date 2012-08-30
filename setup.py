# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from distutils.core import setup

try:
    from singularity import information
    from singularity import helpers
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from singularity import information
    from singularity import helpers

PARAMS = {}
PARAMS["name"] = information.NAME
PARAMS["version"] = information.VERSION
PARAMS["description"] = information.DESCRIPTION
PARAMS["long_description"] = information.LONG_DESCRIPTION
PARAMS["author"] = information.AUTHOR
PARAMS["author_email"] = information.AUTHOR_EMAIL
PARAMS["url"] = information.URL
PARAMS["license"] = information.LICENSE

PARAMS["scripts"] = [
        "bin/singularity",
        ]
PARAMS["packages"] = [
        "singularity",
        "singularity.configurators",
        "singularity.configurators.gentoo",
        "singularity.communicators",
        "singularity.helpers",
        "singularity.parameters",
        ]
PARAMS["data_files"] = [
        ("share/doc/{P[name]}-{P[version]}".format(P = PARAMS), [
            "README.md",
            ]),
        ("share/doc/{P[name]}-{P[version]}/config".format(P = PARAMS), [
            "config/singularity.conf",
            "config/init.gentoo",
            ]),
        ("share/man/man8", [
            "doc/man/man8/singularity.8",
            "doc/man/man8/singularity-apply.8",
            "doc/man/man8/singularity-daemon.8",
            ]),
        ("share/man/man5", [
            "doc/man/man8/singularity.conf.5",
            ]),
        ]

PARAMS["requires"] = [
        "daemon",
        "Crypto",
        ]

if helpers.VIRTUAL == "xenU":
    PARAMS["requires"].append("xen")

setup(**PARAMS)

