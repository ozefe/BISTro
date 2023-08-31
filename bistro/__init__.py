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

"""BISTro

TODO: Package documentation.
"""
import logging

_logger = logging.getLogger('BISTro')
_logger.setLevel(logging.DEBUG)

_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_formatter)
_logger.addHandler(_stream_handler)

_file_handler = logging.FileHandler('BISTro.log', encoding='UTF-8')
_file_handler.setFormatter(_formatter)
_logger.addHandler(_file_handler)

_logger.debug('Started logging.')
