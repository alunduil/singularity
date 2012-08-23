# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
#
# singularity is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import binascii
import os
import hashlib
import Crypto.Cipher.AES
import base64

logger = logging.getLogger(__name__) # pylint: disable=C0103

_BASE = 5
_PRIME = 162259276829213363391578010288127

PRIVATE_KEY = None
PUBLIC_KEY = None
SHARED_KEY = None
AES_KEYS = None

def private_key():
    """Creates a private key for communicating with the host.

    ### Description

    Not sure what the effect of using a different key from upstream is; using
    the same key as upstream until we can see the whole algorithm.

    """

    return int(binascii.b2a_hex(os.urandom(16)), 16)

def encode(base, exponent):
    """I have no idea but I'm not toying with it."""

    result = 1

    while exponent:
        if exponent & 1:
            result = result*base % _PRIME
        exponent >>= 1
        base = base**2 % _PRIME

    return result

def public_key(priv_key):
    """Creates a public key for a given private key.

    ### Description

    Again, not sure of the implications of using a different algorithm from
    upstream; using the same algorithm as a result.

    """

    return encode(_BASE, priv_key)

def shared_key(priv_key, pub_key):
    """Creates a shared key for the given public and private keys.

    ### Description

    Again, not sure so let's go with it.

    """

    return encode(pub_key, priv_key)

def aes_keys(shar_key):
    """Generates an AES key from the shared_key.
    
    ### Description
    
    Seems to create two keys but the description of the isv has been lost to 
    time it seems ...
    
    """

    hash_ = hashlib.md5() # pylint: disable=E1101
    hash_.update(str(shar_key))

    aes_key = hash_.digest()

    hash_ = hashlib.md5() # pylint: disable=E1101
    hash_.update(aes_key)
    hash_.update(str(shar_key))

    aes_iv = hash_.digest()

    return aes_key, aes_iv

def generate_keys(remote_public_key):
    """Generate the local keys based on the remote public key.

    ### Description

    Creates the following module constants:
    * PRIVATE_KEY
    * PUBLIC_KEY
    * SHARED_KEY
    * AES_KEYS # WHY?

    """

    global PRIVATE_KEY # pylint: disable=W0603
    global PUBLIC_KEY # pylint: disable=W0603
    global SHARED_KEY # pylint: disable=W0603
    global AES_KEYS # pylint: disable=W0603

    remote_public_key = long(remote_public_key) # We know we're getting a string ... # pylint: disable=C0301

    PRIVATE_KEY = private_key()

    logger.debug("PRIVATE_KEY: %s", PRIVATE_KEY)

    PUBLIC_KEY = public_key(PRIVATE_KEY)

    logger.debug("PUBLIC_KEY: %s", PUBLIC_KEY)

    SHARED_KEY = shared_key(PRIVATE_KEY, PUBLIC_KEY)

    logger.debug("SHARED_KEY: %s", SHARED_KEY)

    AES_KEYS = aes_keys(SHARED_KEY)

    logger.debug("AES_KEYS: %s", AES_KEYS)
    
def decrypt(string):
    """Return the plain-text version of the passed string."""

    cipher = Crypto.Cipher.AES.new(AES_KEYS[0], Crypto.Cipher.AES.MODE_CBC, AES_KEYS[1]) # pylint: disable=C0301

    string = cipher.decrypt(base64.b64decode(string))

    logger.debug("Decoded string: %s", string)
    logger.debug("Decoded string (str): %s", str(string))
    logger.debug("Decoded string (unicode): %s", unicode(string))

    # TODO Check for invalid data?
    # Upstream uses the cutoff (the ord result) and checks that it is
    # not larger than 16 and the string is at least 16 characters in length.

    logger.debug("Cutoff size: %s", -ord(string[-1]))
    logger.debug("Cut string: %s", string[:-ord(string[-1])])

    return string[:-ord(string[-1])].strip()

