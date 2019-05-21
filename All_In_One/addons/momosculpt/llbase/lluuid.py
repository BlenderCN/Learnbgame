# file: lluuid.py
# author: Phoenix
#
# $LicenseInfo:firstyear=2004&license=mit$
#
# Copyright (c) 2004-2009, Linden Research, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# $/LicenseInfo$

"""
Python UUID helpers.
"""

from . import uuid
try:
    # Python 2.6
    from hashlib import md5
except ImportError:
    # Python 2.5 and earlier
    from md5 import new as md5

# Regular expression string to slap into your code when you need to
# find a regular expression somewhere.
REGEX_STR = r'\b(?:[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12})\b'

# Either make one yourself or use this one when you need a null uuid.
NULL = uuid.UUID(int=0)


def generate():
    """
    Return an md5 hash of a newly generated random uuid. This matches
    the behavior of Linden Lab's c++ implementation of
    LLUUID::generate() so we provide it here.

    :returns: Returns a fully random and anonymized uuid.UUID instance.
    """
    m = md5()
    m.update(uuid.uuid1().bytes)
    return uuid.UUID(bytes=m.digest())


def is_str_uuid(id_str):
    """
    Check if a passed in string can be interpreted as a UUID. Returns
    True on success and False otherwise.

    This function essentially strips the hypens so both
    589EF487-197B-4822-911A-811BB011716A and
    589EF487197B4822911A811BB011716A will be treated as valid uuids.

    This function is also tolerant of case change, so
    589ef487-197b-4822-911a-811bb011716a will also evalute as a uuid.

    This function is not tolerant of leading or trailing garbage so
    leading or trailing whitespace will fail to evaluate as a uuid.

    :param uuid_str: The string to test

    :returns: Returns True if the input string can be converted to a
       uuid. Otherwise returns False.
    """
    try:
        the_id = uuid.UUID(id_str)
    except ValueError:
        return False
    return True
