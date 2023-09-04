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

"""bistro.client

TODO: Module documentation.
"""
from bistro.client._auth import Auth
from bistro.client._notifications import Notifications
import logging

_logger = logging.getLogger(f'BISTro.{__name__}')


class Client(Auth, Notifications):
    """Represents main BISTro client

    Instead of defining every class and function in here, we're defining them in their own modules for easier
    maintenance and increased readability.

    See Also:
        - :class:`Auth`
        - :class:`Notifications`

    Todo:
        - Implement other BIST DataStore API calls.
    """
