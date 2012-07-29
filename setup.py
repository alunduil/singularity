# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# muaor is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from distutils.core import setup

try:
    from singularity import information
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from singularity import information

PARAMS = {}
PARAMS["name"] = information.name
PARAMS["version"] = information.version
PARAMS["description"] = information.description
PARAMS["long_description"] = information.long_description
PARAMS["author"] = information.author
PARAMS["author_email"] = information.author_email
PARAMS["url"] = information.url
PARAMS["license"] = information.license

PARAMS["scripts"] = [
        "bin/singularity",
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
        ]

setup(**PARAMS)

