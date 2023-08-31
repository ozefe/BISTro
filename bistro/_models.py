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
"""
import dataclasses
import datetime
from _exceptions import InvalidTimestampError, OverflowTimestampError


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class UserSubscription:
    """Represents a data subscription that a :class:`User` has subscribed to.

    This dataclass encapsulates partial data subscription details for a :class:`User`. It provides information about the
    subscription's ID, price, name, and more. For complete data, refer to the :class:`Subscription`.

    Arguments:
        id: The unique identifier of the subscription.
        ref_id: The reference ID of the subscription.
        price: The subscription price in Turkish Lira (₺).
        available_period: The subscription period in months.
        category_code: The category code of the subscription.
        group_code: The group code of the subscription.
        subcategory_code: The subcategory code of the subscription.
        product_type_id: The product type ID of the subscription.
        profile_id: The associated profile ID.
        name: The name of the subscription in Turkish.
        name_en: The name of the subscription in English.
        created_timestamp: The creation timestamp in milliseconds.
        expiration_timestamp: The expiration timestamp in milliseconds or microseconds.
        created_date_text: The creation date in the `DD.MM.YYYY` format.
        expiration_date_text: The expiration date in the `DD.MM.YYYY` format.

    Attributes:
        created_datetime: The calculated creation date and time.
        expiration_datetime: The calculated expiration date and time.

    Raises:
        InvalidTimestampError: If provided timestamp is not convertible to a valid datetime.
        OverflowTimestampError: If :attr:`created_datetime` timestamp is larger than 32-bit integer.

    Notes:
        - This class is intended to be used as an immutable data container, hence the `frozen` attribute.
        - The `slots` attribute is enabled for optimized memory usage.
        - The `weakref_slot` attribute allows weak references.
        - The :attr:`profile_id` might differ from the user's ID, requiring further documentation.
        - Be cautious of potential timestamp overflow issues when handling large timestamps.

    See Also:
        - :class:`datetime.datetime`
        - :class:`InvalidTimestampError`
        - :class:`OverflowTimestampError`
        - :class:`Subscription`
        - :class:`User`

    Example:
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

    Todo:
        - :attr:`UserSubscription.profile_id` is not the same as :attr:`User.id`. Documentation required.
    """
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

    def __post_init__(self) -> None:
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


@dataclasses.dataclass(frozen=True, slots=True, weakref_slot=True)
class User:
    """Represents a user object.

    This class encapsulates information about a user, including identification, username, and email.

    Arguments:
        id: The unique identifier of the user.
        username: The username of the user.
        email: The email address associated with the user.
        email_confirmed: Indicates if the user's email has been confirmed.
        password_change_required: Indicates if a password change is required.
        endeks_notification_read: Indicates if the user has read the Endeks notification.
        state: The state or status of the user.
        family_name: The family name of the user.
        subscriptions: List of :class:`UserSubscription` instances for user's subscriptions.

    Notes:
        - This class is intended to be used as an immutable data container, hence the `frozen` attribute.
        - Use the `slots` attribute for optimized memory usage.
        - The `weakref_slot` attribute enables weak references.
        - Define :class:`UserSubscription` class before initializing :class:`User` instances with subscriptions.

    See Also:
        - :class:`UserSubscription`

    Example:
        Creating a :class:`User` instance:

        >>> subscription1 = UserSubscription(...)  # Initialize a UserSubscription instance
        >>> subscription2 = UserSubscription(...)  # Initialize another UserSubscription instance
        >>> user = User(
        ...     id=1,
        ...     username="johndoe",
        ...     email="johndoe@example.com",
        ...     email_confirmed=True,
        ...     password_change_required=False,
        ...     endeks_notification_read=True,
        ...     state="ACTIVE",
        ...     family_name="Doe",
        ...     subscriptions=[subscription1, subscription2]
        ... )

    Todo:
        - Clarify the purpose of :attr:`password_change_required` flag.
        - Investigate API call for changing :attr:`family_name`.
        - Provide comprehensive documentation on possible :attr:`state` values.
    """
    id: int
    username: str
    email: str
    email_confirmed: bool
    password_change_required: bool
    endeks_notification_read: bool
    state: str
    family_name: str = None
    subscriptions: list[UserSubscription] = dataclasses.field(default_factory=list)
