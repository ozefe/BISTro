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
    """Invalid timestamp conversion"""


class OverflowTimestampError(BISTroBaseException):
    """Cannot convert timestamps bigger than signed 32-bit integer to :class:`datetime.datetime` objects"""


class CookieFileError(BISTroBaseException):
    """Cannot read from the provided cookie file"""


class CookieFileLoadError(BISTroBaseException):
    """Cannot read and load from provided cookie file"""


class DownloadError(BISTroBaseException):
    """Download-related errors"""
