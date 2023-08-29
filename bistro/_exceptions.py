# BISTro - BISTro allows you to fetch, filter and parse financial data from Borsa Istanbul
#
# Copyright (C) 2023  Efe Özyay
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""bistro._exceptions

TODO: Module documentation.

:copyright: (C) 2023 by Efe Özyay.
:license: GNU General Public License 3.0, see LICENSE for more details.
"""
import logging

_logger = logging.getLogger(f'BISTro.{__name__}')


class BISTroBaseException(Exception):
    """Base exception for BISTro

    Represents a base exception for us to handle both logging and raising custom exceptions.
    """
    def __init__(self, message: str, exc_info: bool = True):
        super().__init__(message, exc_info)

        _logger.error(message, exc_info=exc_info)


class InvalidTimestampError(BISTroBaseException):
    """Raised for invalid timestamp conversion"""


class OverflowTimestampError(BISTroBaseException):
    """Raised for converting timestamps bigger than signed 32-bit integer to :class:`datetime.datetime` objects"""


class CookieFileError(BISTroBaseException):
    """Raised for errors encountered while trying to read from the provided cookie file"""


class CookieFileLoadError(BISTroBaseException):
    """Raised for errors generated when trying to read and load from provided cookie file"""


class DownloadError(BISTroBaseException):
    """Raised for download-related errors"""
