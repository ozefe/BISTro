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
import http.cookiejar


class InvalidTimestampError(ValueError):
    """Raised for invalid timestamp conversion."""


class OverflowTimestampError(OverflowError):
    """Raised for converting timestamps bigger than signed 32-bit integer to :class:`datetime.datetime` objects"""


class CookieFileError(OSError):
    """Raised for errors encountered while trying to read from the provided cookie file"""


class CookieFileLoadError(http.cookiejar.LoadError):
    """Raised for errors generated when trying to read and load from provided cookie file."""


class DownloadError(Exception):
    """Raised for download-related errors."""
