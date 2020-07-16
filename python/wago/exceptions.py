# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import print_function, division, absolute_import


class WagoError(Exception):
    """A custom core Wago exception"""

    def __init__(self, message=None):

        message = 'There has been an error' \
            if not message else message

        super(WagoError, self).__init__(message)


class WagoNotImplemented(WagoError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = 'This feature is not implemented yet.' \
            if not message else message

        super(WagoNotImplemented, self).__init__(message)


class WagoAPIError(WagoError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = 'Error with Http Response from Wago API'
        else:
            message = 'Http response error from Wago API. {0}'.format(message)

        super(WagoAPIError, self).__init__(message)


class WagoApiAuthError(WagoAPIError):
    """A custom exception for API authentication errors"""
    pass


class WagoMissingDependency(WagoError):
    """A custom exception for missing dependencies."""
    pass


class WagoWarning(Warning):
    """Base warning for Wago."""


class WagoUserWarning(UserWarning, WagoWarning):
    """The primary warning class."""
    pass


class WagoSkippedTestWarning(WagoUserWarning):
    """A warning for when a test is skipped."""
    pass


class WagoDeprecationWarning(WagoUserWarning):
    """A warning for deprecated features."""
    pass
