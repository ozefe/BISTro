# BISTro - BISTro allows you to fetch, filter and parse historical financial data from Borsa Istanbul DataStore
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


class UnknownError(BISTroBaseException):
    """Errors that are unknown"""


class InvalidTimestampError(BISTroBaseException):
    """Invalid timestamp conversion"""


class OverflowTimestampError(BISTroBaseException):
    """Cannot convert timestamps bigger than signed 32-bit integer to :class:`datetime.datetime` objects"""


class CookieFileError(BISTroBaseException):
    """Cannot read from the provided cookie file"""


class CookieFileLoadError(BISTroBaseException):
    """Cannot read and load from provided cookie file"""


class URLOpenError(BISTroBaseException):
    """Errors related to opening a URL"""


class DownloadError(BISTroBaseException):
    """Download-related errors"""


class DownloadMaxRetriesReachedError(BISTroBaseException):
    """Maximum retries has been reached for provided URL to be downloaded"""


class UTFDecodeError(BISTroBaseException):
    """Errors related to UTF-8, UTF-16 or UTF-32 decoding"""


class JSONDeserializationError(BISTroBaseException):
    """Errors related to JSON deserialization"""


class UUIDError(BISTroBaseException):
    """Badly formed hexadecimal UUID string"""


class IPAddressError(BISTroBaseException):
    """Errors related to crafting :class:`ipaddress.IPv4Address` objects"""


class AuthenticationError(BISTroBaseException):
    """Errors related to authenticating using user's credentials"""
