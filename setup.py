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
        "sbin/singularity",
        ]
PARAMS["packages"] = [
        "singularity",
        "singularity.configurators",
        "singularity.parameters",
        ]
PARAMS["data_files"] = [
        ("share/doc/{P[name]}-{P[version]}".format(P = PARAMS), [
            "README",
            ]),
        ("share/doc/{P[name]}-{P[version]}/config".format(P = PARAMS), [
            "config/singularity.conf",
            "config/init.gentoo",
            ]),
        ]

PARAMS["requires"] = [
        "daemon",
        ]

if helpers.VIRTUAL == "xenU":
    PARAMS["requires"].append("xen")

setup(**PARAMS)

