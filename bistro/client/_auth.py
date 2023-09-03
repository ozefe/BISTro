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

"""bistro.client._auth

TODO: Module documentation.
"""
from bistro._urllib_adapters import Session
from bistro._models import UserSubscription, User, LoginSession
from bistro._API_endpoints import LOGIN_CONTROL, LOGOUT
from bistro._exceptions import AuthenticationError
import functools
import urllib.request
import logging
import uuid

_logger = logging.getLogger(f'BISTro.{__name__}')


class Auth:
    """Authentication handler

    Provides methods for user authentication using either a username and password pair or an access token.

    Args:
        username: The user's username.
        password: The user's password.
        access_token: The user's access token.
        session: An optional :class:`Session` object for making HTTP requests.

    Raises:
        AuthenticationError: If either username or password is missing or not a string.
        NotImplementedError: Authentication with username and password pair is not supported yet.

    See Also:
        - :class:`AuthenticationError`

    Examples:
        Authenticating with user access token:

        >>> auth = Auth(uuid.UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'))
        >>> auth._login_control()
        LoginSession(id=7659617,
                     user=User(...),
                     state='ACTIVE',
                     new_user=False,
                     access_token=UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'),
                     login_ip=IPv4Address('1.2.3.4'),
                     created_datetime=datetime.datetime(2023, 9, 1, 18, 0, 33, 760000),
                     expiration_datetime=datetime.datetime(2023, 10, 1, 18, 0, 33, 760000))

    Todo:
        - Implement a way to authenticate users with username and password. Since this needs captcha solving and 3rd
          party libraries it's not a priority.
        - Implement registering.
        - Replace the abysmal `singledispatchmethod` with a robust implementation of true multiple dispatch.
    """
    _logger = logging.getLogger(f'BISTro.{__name__}.Auth')

    @functools.singledispatchmethod
    def __init__(self, *args) -> None:
        raise AuthenticationError('Please provide either username and password pair or an access token.',
                                  exc_info=False)

    @__init__.register
    def _(self, username: str, password: str) -> None:
        if not all({username, password}):
            raise AuthenticationError('Both username and password must be provided.', exc_info=False)
        elif not isinstance(password, str):
            raise AuthenticationError('Both username and password must be string.', exc_info=False)

        raise NotImplementedError

    @__init__.register
    def _(self, access_token: uuid.UUID, session: Session = Session()) -> None:
        self.access_token = access_token
        self.session = session

        self._logger.debug('`Auth` object has been initialized')

    def _login_control(self) -> LoginSession:
        """Checks current login session

        Gets information about the current login session using user's access token and returns it.

        Returns:
            :class:`LoginSession` object containing information about current login session.

        Raises:
            KeyError: When returned response body contains unexpected or unrelated content to current login session.

        See Also:
            - :class:`UserSubscription`
            - :class:`User`
            - :class:`LoginSession`

        Examples:
        Authenticating with user access token:

        >>> auth = Auth(uuid.UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'))
        >>> auth._login_control()
        LoginSession(id=7659617,
                     user=User(...),
                     state='ACTIVE',
                     new_user=False,
                     access_token=UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'),
                     login_ip=IPv4Address('1.2.3.4'),
                     created_datetime=datetime.datetime(2023, 9, 1, 18, 0, 33, 760000),
                     expiration_datetime=datetime.datetime(2023, 10, 1, 18, 0, 33, 760000))

        Todo:
            - Better error handling is needed.
        """
        self._logger.debug('Checking login session...')

        response = self.session.open(urllib.request.Request(LOGIN_CONTROL,
                                                            headers={'X-Auth-Token': str(self.access_token)}))
        return LoginSession(
            id=response['id'],
            user=User(
                id=response['user']['id'],
                username=response['user']['name'],
                email=response['user']['email'],
                email_confirmed=response['user']['emailConfirmed'],
                password_change_required=response['user']['passwordChangeRequired'],
                endeks_notification_read=response['user']['_endeks_notification_read'],
                state=response['user']['state'],
                family_name=response['user']['surname'],
                subscriptions=[
                    UserSubscription(
                        id=subscription['id'],
                        ref_id=subscription['referenceId'],
                        price=subscription['price'],
                        available_period=subscription['period'],
                        category_code=subscription['categoryCode'],
                        group_code=subscription['groupCode'],
                        subcategory_code=subscription['subcategoryCode'],
                        product_type_id=subscription['subsProductTypeId'],
                        profile_id=subscription['profileId'],
                        name=subscription['name'],
                        name_en=subscription['nameEn'],
                        created_timestamp=subscription['createDate'],
                        created_date_text=subscription['createDateText'],
                        expiration_timestamp=subscription['expirationDate'],
                        expiration_date_text=subscription['expirationDateText']
                    )
                    for subscription in response['user']['subscriptions']
                ]
            ),
            state=response['state'],
            new_user=response['newUser'],
            access_token_text=response['accessToken'],
            login_ip_text=response['userLoginIp'],
            created_timestamp=response['creationDate'],
            expiration_timestamp=response['validUntil']
        )

    def _logout(self) -> None:
        """Logs out the user thus closing the current login session

        Raises:
            URLOpenError: When logging out fails. This could be result of:
                1. HTTP Error
                2. Login session is already closed

        Note:
            - After logging out, user's access token becomes unusable and needs to be renewed.

        Example:
            >>> auth = Auth(uuid.UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'))
            >>> auth._logout()
        """
        self._logger.debug('Logging out')

        self.session.open(
            urllib.request.Request(LOGOUT,
                                   headers={'X-Auth-Token': str(self.access_token)},
                                   method='PUT'),
            parse_json=False
        )

        self._logger.debug('Logged out successfully')
