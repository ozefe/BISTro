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

"""bistro.client._notifications

TODO: Module documentation.
"""
from bistro._models import Notification, NotificationPage
from bistro._API_endpoints import NOTIFICATION, NOTIFICATION_COUNT, MARK_AS_READ
import urllib.request
import urllib.parse
import logging

_logger = logging.getLogger(f'BISTro.{__name__}')


class Notifications:
    """Notification handler

    Provides methods for handling user notifications.
    """
    _logger = logging.getLogger(f'BISTro.{__name__}.Notifications')

    def get_unread_notification_count(self) -> int:
        """Requests for total number of unread notifications that user has

        Returns:
            Unread notification count as an integer

        Example:
            >>> client = Client(uuid.UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'))
            >>> client.get_unread_notification_count()
            10
        """
        _logger.debug('Getting unread notification count')

        return self.session.open(
            urllib.request.Request(NOTIFICATION_COUNT,
                                   headers={'Referer': 'https://datastore.borsaistanbul.com/user-notifications',
                                            'X-Auth-Token': str(self.access_token)})
        )

    def get_notification_page(self, *, index: int, items_count: int) -> NotificationPage:
        """Requests a page filled with notifications

        Keyword Arguments:
            index: Index of the page.
            items_count: Maximum number of notifications requested page should contain.

        Returns:
            NotificationPage

        See Also:
            - :class:`NotificationPage`
            - :class:`Notification`

        Example:
            Getting first (most recent) two notifications from the first (most recent) page:

            >>> client = Client(uuid.UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'))
            >>> client.get_notification_page(index=1, count=2)
            NotificationPage(
                index=1,
                items_count=2,
                notifications= [
                    Notification(
                        id=7664950,
                        type='NEW_PRODUCT',
                        state='READ',
                        title='Yeni Ürün',
                        title_en='New Product',
                        content='PP Piyasa Verileri Aboneliği (12 Ay)',
                        content_en='Market Data Subscription (12 Months)',
                        created_timestamp=1693615981840
                    ),
                    Notification(
                        id=7664808,
                        type='NEW_PRODUCT',
                        state='READ',
                        title='Yeni Ürün',
                        title_en='New Product',
                        content='PP Pay Bazında Veriler Aboneliği (12 Ay)',
                        content_en='Equity Based Data Subscription (12 Months)',
                        created_timestamp=1693615970100
                    )
                ]
            )
        """
        _logger.debug(f'Getting notification page with {index=} and {items_count=}')

        return NotificationPage(
            index=index,
            items_count=items_count,
            notifications=[
                Notification(
                    id=notification['id'],
                    type=notification['type'],
                    state=notification['state'],
                    title=notification['header'],
                    title_en=notification['headerEn'],
                    content=notification['name'],
                    content_en=notification['nameEn'],
                    created_timestamp=notification['createDate']
                )
                for notification in self.session.open(
                    urllib.request.Request(f'{NOTIFICATION}?page-index={index}&page-size={items_count}',
                                           headers={'Referer': 'https://datastore.borsaistanbul.com/user-notifications',
                                                    'X-Auth-Token': str(self.access_token)})
                )
            ]
        )

    def mark_all_as_read(self) -> None:
        """Marks every notification as read

        Note:
            - Seems like the brilliant minds behind the BIST DataStore API just passed their "Advanced Data Structures
              and Algorithms" course. That's probably why we're stuck with a system that can't even let us choose which
              notifications to mark as read.

        Example:
            >>> client = Client(uuid.UUID('c8ad200c-be04-4471-97f3-f7ad2c9dd230'))
            >>> client.mark_all_as_read()
        """
        _logger.debug(f'Marking every notification as read')

        self.session.open(
            urllib.request.Request(MARK_AS_READ,
                                   headers={'Referer': 'https://datastore.borsaistanbul.com/user-notifications',
                                            'X-Auth-Token': str(self.access_token)},
                                   method='PUT'),
            parse_json=False
        )
