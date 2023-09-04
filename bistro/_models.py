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

"""bistro._models

TODO: Module documentation.
"""
import dataclasses
import datetime
import ipaddress
import uuid
from bistro._exceptions import InvalidTimestampError, OverflowTimestampError, UUIDError, IPAddressError


def _timestamp_to_datetime(timestamp: float, *, do_overflow: bool = True) -> datetime.datetime:
    """Converts provided timestamp to :class:`datetime.datetime` object.

    Tries to convert provided timestamp to :class:`datetime.datetime` object, raises appropriate errors if the provided
    timestamp is invalid. :attr:`do_overflow` flag allows for returning maximum supported timestamp value (`2**31 - 1`)
    instead of raising an error when timestamp is too big for conversion.

    Arguments:
        timestamp: UNIX timestamp for conversion

    Keyword Arguments:
        do_overflow: If set to `True`, raises an appropriate error when :attr:`timestamp` overflows. If set to `False`,
            returns :class:`datetime.datetime` object with maximum timestamp allowed.

    Returns:
        :class:`datetime.datetime` object

    Raises:
        InvalidTimestampError: If :attr:`timestamp` is not convertible to a valid datetime.
        OverflowTimestampError: If :attr:`timestamp` is larger than 32-bit integer.

    Note:
        - Be cautious of potential timestamp overflow issues when handling large timestamps.

    See Also:
        - :class:`datetime.datetime`
        - :meth:`datetime.datetime.fromtimestamp`
        - :class:`InvalidTimestampError`
        - :class:`OverflowTimestampError`

    Example:
        Converting a UNIX timestamp to datetime:

        >>> _timestamp_to_datetime(timestamp=1365152400.0)
        datetime.datetime(2013, 4, 5, 12, 0)
        >>> _timestamp_to_datetime(timestamp='BIST')
        InvalidTimestampError: Invalid timestamp='BIST'
        >>> _timestamp_to_datetime(timestamp=2**35, do_overflow=True)
        OverflowTimestampError: Provided timestamp=34359738368 is too big for conversion to `datetime.datetime`object.
        >>> _timestamp_to_datetime(timestamp=2**35, do_overflow=False)
        datetime.datetime(2038, 1, 19, 6, 14, 7)
    """
    try:
        return datetime.datetime.fromtimestamp(timestamp)
    except (TypeError, ValueError) as tb:
        raise InvalidTimestampError(f'Invalid {timestamp=}') from tb
    except (OverflowError, OSError) as tb:
        if do_overflow:
            raise OverflowTimestampError(f'Provided {timestamp=} is too big for conversion to `datetime.datetime`'
                                         'object.') from tb
        return datetime.datetime.fromtimestamp(2**31 - 1)


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class UserSubscription:
    """Represents a data subscription that a :class:`User` has subscribed to.

    This dataclass encapsulates partial data subscription details for a :class:`User`. It provides information about the
    subscription's ID, price, name, and more. For complete data, refer to the :class:`Subscription`.

    Keyword Arguments:
        id: Unique identifier of the subscription.
        ref_id: Reference ID of the subscription.
        price: Subscription price in Turkish Lira (₺).
        available_period: Subscription period in months.
        category_code: Category code of the subscription.
        group_code: Group code of the subscription.
        subcategory_code: Subcategory code of the subscription.
        product_type_id: Product type ID of the subscription.
        profile_id: Associated profile ID.
        name: Name of the subscription in Turkish.
        name_en: Name of the subscription in English.
        created_timestamp: Creation timestamp in milliseconds.
        expiration_timestamp: Expiration timestamp in milliseconds or microseconds.
        created_date_text: Creation date in the `DD.MM.YYYY` format.
        expiration_date_text: Expiration date in the `DD.MM.YYYY` format.

    Attributes:
        created_datetime: Calculated creation date and time.
        expiration_datetime: Calculated expiration date and time.

    Raises:
        InvalidTimestampError: If provided timestamp is not convertible to a valid datetime.
        OverflowTimestampError: If :attr:`created_timestamp` is larger than 32-bit integer.

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
    created_date_text: str = dataclasses.field(repr=False)
    created_datetime: datetime.datetime = dataclasses.field(init=False)
    expiration_timestamp: int = dataclasses.field(repr=False)
    expiration_date_text: str = dataclasses.field(repr=False)
    expiration_datetime: datetime.datetime = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Initialize calculated datetime fields."""
        # We don't need to check for overflows for `created_timestamp` since we can assume we're dealing with
        # relatively recent dates. Although if we have an overflow here too, raising an error and halting would be
        # better.
        object.__setattr__(self, 'created_datetime',
                           _timestamp_to_datetime(self.created_timestamp / 1_000.0))

        object.__setattr__(self, 'expiration_datetime',
                           _timestamp_to_datetime(self.expiration_timestamp / 1_000.0, do_overflow=False))


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class User:
    """Represents a user object.

    This class encapsulates information about a user, including identification, username, and email.

    Keyword Arguments:
        id: Unique identifier of the user.
        username: Username of the user.
        email: Email address associated with the user.
        email_confirmed: Indicates if the user's email has been confirmed.
        password_change_required: Indicates if a password change is required.
        endeks_notification_read: Indicates if the user has read the Endeks notification.
        state: State or status of the user.
        family_name: Family name of the user.
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


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class LoginSession:
    """Represents a login session object.

    Login session objects returned whenever we check our current login status or login with user credentials.

    Keyword Arguments:
        id: Unique identifier of the login session.
        user: Logged in :class:`User` object.
        state: State or status of the login session.
        new_user: Indicates whether the user is newly registered.
        access_token_text: UUID version 4 access token as string.
        login_ip_text: IPv4 address as string.
        created_timestamp: Creation timestamp in milliseconds.
        expiration_timestamp: Expiration timestamp in milliseconds or microseconds.

    Attributes:
        access_token: :class:`uuid.UUID` object representing UUID version 4 access token.
        login_ip: :class:`ipaddress.IPv4Address` object representing IP version 4 address that the login session was
            initiated with.
        created_datetime: Calculated creation date and time.
        expiration_datetime: Calculated expiration date and time.

    Raises:
        UUIDError: If :attr:`access_token_text` is not a valid UUID version 4 token.
        IPAddressError: If :attr:`login_ip_text` is not a valid IPv4 address.
        InvalidTimestampError: If provided timestamp is not convertible to a valid datetime.
        OverflowTimestampError: If :attr:`created_timestamp` is larger than 32-bit integer.

    Notes:
        - This class is intended to be used as an immutable data container, hence the `frozen` attribute.
        - Use the `slots` attribute for optimized memory usage.
        - The `weakref_slot` attribute enables weak references.

    See Also:
        - :class:`uuid.UUID`
        - :class:`ipaddress.IPv4Address`
        - :class:`UUIDError`
        - :class:`IPAddressError`
        - :class:`ipaddress.AddressValueError`
        - :class:`InvalidTimestampError`
        - :class:`OverflowTimestampError`

    Example:
        >>> user_subscription = UserSubscription(...)
        >>> user = User(...)
        >>> LoginSession(
        ...     id=7659617,
        ...     user=user,
        ...     state='ACTIVE',
        ...     new_user=False,
        ...     access_token_text='c8ad200c-be04-4471-97f3-f7ad2c9dd230',
        ...     login_ip_text='1.2.3.4',
        ...     created_timestamp=1693580433760,
        ...     expiration_timestamp=1696172433760
        ... )
        LoginSession(id=7659617,
                     user=User(...),
                     state='ACTIVE',
                     new_user=False,
                     access_token=UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'),
                     login_ip=IPv4Address('1.2.3.4'),
                     created_datetime=datetime.datetime(2023, 9, 1, 18, 0, 33, 760000),
                     expiration_datetime=datetime.datetime(2023, 10, 1, 18, 0, 33, 760000))

    Todo:
        - Provide comprehensive documentation on possible :attr:`state` values.
    """
    id: int
    user: User
    state: str
    new_user: bool
    access_token_text: str = dataclasses.field(repr=False)
    access_token: uuid.UUID = dataclasses.field(init=False)
    login_ip_text: str = dataclasses.field(repr=False)
    login_ip: ipaddress.IPv4Address = dataclasses.field(init=False)
    created_timestamp: int = dataclasses.field(repr=False)
    created_datetime: datetime.datetime = dataclasses.field(init=False)
    expiration_timestamp: int = dataclasses.field(repr=False)
    expiration_datetime: datetime.datetime = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Initialize calculated fields."""
        try:
            object.__setattr__(self, 'access_token', uuid.UUID(self.access_token_text))
        except ValueError as tb:
            raise UUIDError(f'Malformed or corrupted access token: {self.access_token_text}') from tb

        try:
            object.__setattr__(self, 'login_ip', ipaddress.IPv4Address(self.login_ip_text))
        except ipaddress.AddressValueError as tb:
            raise IPAddressError(f'Malformed or corrupted IP address: {self.login_ip_text}') from tb

        object.__setattr__(self, 'created_datetime',
                           _timestamp_to_datetime(self.created_timestamp / 1_000.0))

        object.__setattr__(self, 'expiration_datetime',
                           _timestamp_to_datetime(self.expiration_timestamp / 1_000.0, do_overflow=False))


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class Notification:
    """Represents a notification

    Keyword Arguments:
        id: Unique identifier of the notification.
        type: Type of the notification.
        state: Read/unread state of the notification.
        title: Turkish title or header text of the notification.
        title_en: English title or header text of the notification.
        content: Turkish content text of the notification.
        content_en: English content text of the notification.
        created_timestamp: Creation timestamp in milliseconds.

    Attributes:
        created_datetime: Calculated creation date and time.

    Raises:
        InvalidTimestampError: If provided timestamp is not convertible to a valid datetime.
        OverflowTimestampError: If :attr:`created_timestamp` is larger than 32-bit integer.

    Notes:
        - This class is intended to be used as an immutable data container, hence the `frozen` attribute.
        - Use the `slots` attribute for optimized memory usage.
        - The `weakref_slot` attribute enables weak references.

    See Also:
        - :class:`InvalidTimestampError`
        - :class:`OverflowTimestampError`
        - :class:`NotificationPage`

    Example:
        >>> Notification(
        ...     id=7664950,
        ...     type='NEW_PRODUCT',
        ...     state='READ',
        ...     title='Yeni Ürün',
        ...     title_en='New Product',
        ...     content='PP Piyasa Verileri Aboneliği (12 Ay)',
        ...     content_en='Market Data Subscription (12 Months)',
        ...     created_timestamp=1693615981840
        ... )
    """
    id: int
    type: str
    state: str
    title: str
    title_en: str
    content: str
    content_en: str
    created_timestamp: int = dataclasses.field(repr=False)
    created_datetime: datetime.datetime = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Initialize calculated datetime field."""
        object.__setattr__(self, 'created_datetime', _timestamp_to_datetime(self.created_timestamp / 1_000.0))


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class NotificationPage:
    """Represents a notification page that usually holds multiple notifications within

    Keyword Arguments:
        index: Index of the notification page.
        items_count: Total count of the notifications within.
        notifications: List of :class:`Notification` objects.

    Notes:
        - This class is intended to be used as an immutable data container, hence the `frozen` attribute.
        - Use the `slots` attribute for optimized memory usage.
        - The `weakref_slot` attribute enables weak references.

    See Also:
        - :class:`Notification`

    Example:
        >>> NotificationPage(
        ...     index=1,
        ...     items_count=2,
        ...     notifications= [
        ...         Notification(
        ...             id=7664950,
        ...             type='NEW_PRODUCT',
        ...             state='READ',
        ...             title='Yeni Ürün',
        ...             title_en='New Product',
        ...             content='PP Piyasa Verileri Aboneliği (12 Ay)',
        ...             content_en='Market Data Subscription (12 Months)',
        ...             created_timestamp=1693615981840
        ...         ),
        ...         Notification(
        ...             id=7664808,
        ...             type='NEW_PRODUCT',
        ...             state='READ',
        ...             title='Yeni Ürün',
        ...             title_en='New Product',
        ...             content='PP Pay Bazında Veriler Aboneliği (12 Ay)',
        ...             content_en='Equity Based Data Subscription (12 Months)',
        ...             created_timestamp=1693615970100
        ...         )
        ...     ]
        ... )
    """
    index: int
    items_count: int
    notifications: list[Notification]
