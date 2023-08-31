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

"""bistro._urllib_adapters

TODO: Module documentation.
"""
import urllib.request
import urllib.error
import http.cookiejar
import http.client
import logging
import os
from _exceptions import CookieFileError, CookieFileLoadError, DownloadError

_logger = logging.getLogger(f'BISTro.{__name__}')


class Session:
    """A session management class for making HTTP requests with custom cookies and proxies.

    This class facilitates creating and managing an HTTP session with customizable cookies and proxies. You can provide
    cookies as a list of :class:`http.cookiejar.Cookie` objects or load them from a cookie file specified by the
    :attr:`cookies` parameter. Proxies can be set using the :attr:`proxies` parameter.

    Arguments:
        cookies: A list of :class:`http.cookiejar.Cookie` objects or a :class:`os.PathLike` object pointing to a cookie
            file.
        proxies: A dictionary of proxy settings where keys are protocols (e.g., 'https') and values are proxy URLs.

    Raises:
        CookieFileError: If there's an error reading from the provided cookie file.
        CookieFileLoadError: If there's an error loading cookies from the provided cookie file.

    Notes:
        - The `User-Agent` for the session is set to mimic the Google Chrome browser.
        - Provided :attr:`proxies` should support the HTTPS protocol. This is important because we're sending
          unencrypted and unhashed sensitive user login information through this connection.
        - :class:`Session` is not thread-safe. Use separate instances for different threads.

    See Also:
        - :class:`CookieFileError`
        - :class:`CookieFileLoadError`
        - :class:`http.cookiejar.Cookie`
        - :class:`http.cookiejar.CookieJar`
        - :class:`http.cookiejar.LWPCookieJar`
        - :class:`urllib.request.Request`
        - :class:`urllib.request.OpenerDirector`

    Example:
        Creating a session with cookies and proxies:

        >>> import pathlib
        >>> session = Session(cookies=pathlib.Path('./cookies.txt'), proxies={'https': 'localhost'})
        >>> list(session.cookie_jar)
        [Cookie(version=0, name='test_cookie', value='1337', port=None, port_specified=False,
         domain='httpbin.org', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
         secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={}, rfc2109=False)]
        >>> session.opener.handlers[0].proxies
        {'https': 'localhost'}

    Todo:
        - :class:`Session` should have an ability to save cookies to a file.
    """
    def __init__(self, cookies: list[http.cookiejar.Cookie] | os.PathLike = None,
                 proxies: dict[str, str] = None) -> None:
        self._logger = logging.getLogger(f'BISTro.{__name__}.Session')
        self.opener = urllib.request.build_opener()

        self.opener.addheaders = [
            ('User-Agent',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 '
             'Safari/537.36')
        ]

        if proxies:
            self.opener.add_handler(urllib.request.ProxyHandler(proxies))

        self.cookie_jar = http.cookiejar.CookieJar()
        if isinstance(cookies, list):
            for cookie in cookies:
                self.cookie_jar.set_cookie(cookie)
        elif isinstance(cookies, os.PathLike):
            self.cookie_jar = http.cookiejar.LWPCookieJar(cookies)
            try:
                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
            except http.cookiejar.LoadError as tb:
                raise CookieFileLoadError(f'Error loading cookies from provided cookie file: ({cookies})') from tb
            except OSError as tb:
                raise CookieFileError(f'Error reading from provided cookie file: ({cookies})') from tb

        self.opener.add_handler(urllib.request.HTTPCookieProcessor(self.cookie_jar))

        self._logger.debug(f'`Session` object has been initialized with {cookies=} and {proxies=}')

    def open(self, request: urllib.request.Request) -> http.client.HTTPResponse:
        """Open an HTTP request using the :class:`Session`'s settings.

        This method opens an HTTP request using the :class:`Session`'s configured settings, including cookies and
        proxies. It returns the corresponding HTTP response object.

        Arguments:
            request: :class:`urllib.request.Request` object representing the HTTP request.

        Returns:
            HTTP Response object.

        Note:
            - This method uses the :class:`Session`'s opener to send the request and receive the response. Thus, various
              parameters in :attr:`request` can override the :class:`Session.opener`'s configurations.

        See Also:
            - :attr:`Session.opener`
            - :class:`Session`
            - :class:`urllib.request.Request`
            - :class:`http.client.HTTPResponse`

        Example:
            Opening a request with cookies:

            >>> s = Session()
            >>> response = s.open(urllib.request.Request('https://httpbin.org/cookies/set?test_cookie=1337'))
            >>> print(response.read().decode('UTF-8'))
            {
              "cookies": {
                "test_cookie": "1337"
              }
            }
            >>> list(s.cookie_jar)
            [Cookie(version=0, name='test_cookie', value='1337', port=None, port_specified=False,
             domain='httpbin.org', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
             secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={}, rfc2109=False)]
        """
        self._logger.debug(f'Opening {request.get_full_url()=}')

        return self.opener.open(request)

    def download(self, request: urllib.request.Request, file_path: os.PathLike, expected_file_size: int = None,
                 max_retries: int = 3) -> tuple[int, os.PathLike]:
        """Download a file from a given URL using the provided :attr:`request` and save it to the specified
        :attr:`file_path`.

        Arguments:
            request: :class:`urllib.request.Request` object representing the HTTP request.
            file_path: File path where the downloaded file will be saved.
            expected_file_size: Expected size of the file in bytes, if known.
            max_retries: Maximum number of retries in case of download failures.

        Returns:
            A tuple containing two values:
                1. The actual size of the downloaded file in bytes.
                2. The file path where the downloaded content has been saved.

        Raises:
            DownloadError:
                If any of these errors occur during the download process:
                    1. If there are connection-related errors, such as :class:`urllib.error.URLError`.
                    2. If the provided :attr:`request` object is invalid or if there are data processing errors,
                    i.e., :class:`ValueError`, :class:`TypeError`.
                    3. If there are file system errors during file operations, i.e. :class:`PermissionError`.
                    4. If there are unexpected errors that cannot be categorized.

        Notes:
            - :meth:`Session.download` employs :meth:`Session.open` to handle requests. Consequently, any supplementary
              arguments included in the request (such as cookies or headers) will supersede the default :class:`Session`
              parameters. This circumstance bears the potential of giving rise to unanticipated errors that lack proper
              documentation.
            - Ensure that the provided :attr:`file_path` specifies a valid and writable file path in the filesystem.

        See Also:
            - :meth:`Session.open`
            - :class:`DownloadError`
            - :class:`Session`
            - :class:`urllib.request.Request`
            - :class:`os.PathLike`

        Example:
            Downloading an image file:

            >>> import pathlib
            >>> session = Session()
            >>> try:
            ...     downloaded_size, downloaded_path = session.download(
            ...         urllib.request.Request('https://httpbin.org/image/jpeg'),
            ...         pathlib.Path('./wolf.jpeg')
            ...     )
            ...     print(f'Download successful. File size: {downloaded_size} bytes. Saved at: {downloaded_path}')
            ... except DownloadError as e:
            ...     print(f'Error occurred during download: {e}')
        """
        self._logger.debug(f'Downloading {request.get_full_url()=} to {file_path=} with {expected_file_size} bytes')

        retries = 0
        while retries <= max_retries:
            try:
                with open(file_path, 'wb') as file, self.open(request) as response:
                    downloaded_bytes = 0

                    # Reading and writing 1MB (1024B * 1024B = 1MB) chunks each time to prevent memory overflow.
                    while chunk := response.read(1024 * 1024):
                        file.write(chunk)
                        downloaded_bytes += len(chunk)
                        self._logger.debug(f'{downloaded_bytes=} for {request.get_full_url()=} so far')

                if not expected_file_size:
                    expected_file_size = int(response.getheader('Content-Length', 0))

                # If the `expected_file_size` was absent and the response lacked a `Content-Length` header, we encounter
                # a situation where it becomes impossible to determine the integrity of the downloaded file.
                # Consequently, we are compelled to assume that the file is not corrupted due to the absence of relevant
                # information.
                if downloaded_bytes < expected_file_size and expected_file_size > 0:
                    raise DownloadError('Downloaded data is incomplete or malformed.')

                self._logger.debug(f'{request.get_full_url()=} successfully downloaded to {file_path=} with '
                                   f'{expected_file_size=} bytes')

                return expected_file_size, file_path
            except (urllib.error.URLError, http.client.HTTPException, ConnectionError):
                DownloadError(f'Error connecting to the host: {request.get_full_url()}', exc_info=False)
            except (ValueError, TypeError):
                DownloadError(f'Error processing data or malformed request for host: {request.get_full_url()}',
                              exc_info=False)
            except OSError:
                DownloadError(f'File system error while working with the file: {file_path}', exc_info=False)
            except:
                DownloadError(f'Unknown error encountered: {request.get_full_url()}', exc_info=False)
            finally:
                retries += 1

            self._logger.debug(f'{retries=} for {request.get_full_url()=} so far')

        raise DownloadError(f'{max_retries=} reached for {request.get_full_url()=} and {file_path=}')
