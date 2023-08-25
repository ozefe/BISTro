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

"""bistro._models

TODO: Module documentation.

:copyright: (C) 2023 by Efe Özyay.
:license: GNU General Public License 3.0, see LICENSE for more details.
"""
import dataclasses
import datetime


class InvalidTimestampError(ValueError):
    """Raised for invalid timestamp conversion."""


class OverflowTimestampError(OverflowError):
    """Raised for converting timestamps bigger than signed 32-bit integer to :class:`datetime.datetime` objects"""


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class UserSubscription:
    """Represents a data subscription that user has subscribed.

    :class:`UserSubscription` encapsulates partial data subscription details, indicating the specific information to
    which a :class:`User` has already subscribed. It provides information about the subscription's ID, price, name, and
    more. Use :class:`UserSubscription` for basic subscription information; for complete data, refer to the
    :class:`Subscription`.

    :param int id: The unique identifier of the subscription.
    :param int ref_id: The reference ID of the subscription.
    :param float price: The price of the subscription in Turkish Lira (₺).
    :param int available_period: The available period of the subscription in months.
    :param str category_code: The category code of the subscription.
    :param str group_code: The group code of the subscription.
    :param str subcategory_code: The subcategory code of the subscription.
    :param int product_type_id: The product type ID of the subscription.
    :param int profile_id: The profile ID associated with the subscription.
    :param str name: The Turkish name of the subscription.
    :param str name_en: The English name of the subscription.
    :param int created_timestamp: The UNIX timestamp of subscription creation in milliseconds
                                     (1'000 milliseconds = 1 second).
    :param int expiration_timestamp: The UNIX timestamp of subscription expiration in milliseconds
                                     (1'000 milliseconds = 1 second) or in microseconds
                                     (1'000'000 microseconds = 1 second).
    :param str created_date_text: The creation date of the subscription in the `DD.MM.YYYY` format.
    :param str expiration_date_text: The expiration date of the subscription in the `DD.MM.YYYY` format.

    :ivar datetime.datetime created_datetime: The creation date and time of the subscription (calculated).
    :ivar datetime.datetime expiration_datetime: The expiration date and time of the subscription (calculated).

    :raises InvalidTimestampError: If any provided timestamp is not convertible to a valid datetime.
    :raises OverflowTimestampError: If provided timestamp for `UserSubscription.created_datetime` is bigger than signed
                                    32-bit integer.

    :note:
        The `profile_id` might not be the same as the user's ID. More documentation needed.

    :warning:
        Be aware of potential timestamp overflow issues when working with extremely large timestamps.

    :example:
        Creating a :class:`UserSubscription` instance:

        >>> subscription = UserSubscription(
        ...     id=7612669,
        ...     ref_id=100849,
        ...     price=0.0,
        ...     available_period=12,
        ...     category_code="PPB",
        ...     # ... (other parameters)
        ...     created_timestamp=1661395200000,
        ...     expiration_timestamp=1692931200000,
        ...     created_date_text="25.08.2022",
        ...     expiration_date_text="25.08.2023"
        ... )
        >>> print(subscription.name)
        "PP Piyasa Verileri Aboneliği (12 Ay)"
        >>> print(subscription.created_datetime)
        2022-08-25 00:00:00
    """

    # TODO: `UserSubscription`.profile_id is not the same as `User`.id and I have no idea why. It seems the difference
    #  between two of these IDs is 920. Write a more comprehensive documentation for this attribute.

    id: int
    ref_id: int
    price: float
    available_period: int
    category_code: str
    group_code: str
    subcategory_code: str
    product_type_id: int
    profile_id: int
    name: str
    name_en: str
    created_timestamp: int = dataclasses.field(repr=False)
    expiration_timestamp: int = dataclasses.field(repr=False)
    created_date_text: str = dataclasses.field(repr=False)
    expiration_date_text: str = dataclasses.field(repr=False)
    created_datetime: datetime.datetime = dataclasses.field(init=False)
    expiration_datetime: datetime.datetime = dataclasses.field(init=False)

    def __post_init__(self):
        """Initialize calculated datetime fields."""
        # The BIST DataStore employs timestamps in milliseconds and supports subscription periods of up to 999999
        # months, equivalent to 833 years and 10 months. It appears that they use larger integer types, probably i64,
        # rather than the conventional signed 32-bit integer. This creates an issue because CPython and
        # `datetime.datetime` still utilize the `localtime()` and `gmtime()`, which in turn may or may not allow bigger
        # values than the maximum of signed 32-bit integer. Consequently, converting timestamps from BIST DataStore to
        # `datetime.datetime` objects could lead to overflows.
        #
        # To address this, we perform an initial check to determine if the timestamp exceeds the range of a signed
        # 32-bit integer. If it does, we cap it at the maximum value representable by a signed 32-bit integer: 2**31 - 1

        # We don't need to check for overflows for `created_timestamp` since we can assume we're dealing with
        # relatively recent dates. Although if we have an overflow here too, raising an error and halting would be
        # better.
        try:
            object.__setattr__(self, 'created_datetime',
                               datetime.datetime.fromtimestamp(self.created_timestamp / 1_000.0))
        except ValueError as tb:
            raise InvalidTimestampError('Invalid timestamp provided.') from tb
        except OverflowError as tb:
            raise OverflowTimestampError('Provided timestamp is too big for conversion to `datetime.datetime`'
                                         'object.') from tb
        except OSError as tb:
            raise InvalidTimestampError('Encountered an error while trying to convert provided timestamp to '
                                        '`datetime.datetime` object.') from tb

        # Try to convert `expiration_timestamp` to `datetime.datetime` object. Failure means we overflowed, and then
        # we can just max it out.
        try:
            object.__setattr__(self, 'expiration_datetime',
                               datetime.datetime.fromtimestamp(self.expiration_timestamp / 1_000.0))
        except (OverflowError, OSError):
            object.__setattr__(self, 'expiration_datetime',
                               datetime.datetime.fromtimestamp(2 ** 31 - 1))
        except ValueError as tb:
            raise InvalidTimestampError('Invalid timestamp provided.') from tb
