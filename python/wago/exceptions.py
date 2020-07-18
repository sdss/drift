# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date: 2017-12-05 12:01:21
# @Last modified by: Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32


class WAGOError(Exception):
    """A custom core Wago exception"""

    def __init__(self, message=None):

        message = 'There has been an error.' if not message else message

        super(WAGOError, self).__init__(message)


class WAGOWarning(Warning):
    """Base warning for WAGO."""


class WAGOUserWarning(UserWarning, WAGOWarning):
    """The primary warning class."""
