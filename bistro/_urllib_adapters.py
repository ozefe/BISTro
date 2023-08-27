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

"""bistro._urllib_adapters

TODO: Module documentation.

:copyright: (C) 2023 by Efe Özyay.
:license: GNU General Public License 3.0, see LICENSE for more details.
"""
import urllib.request
import urllib.error
import http.cookiejar
import http.client
import os


class CookieFileError(OSError):
    """Raised for errors encountered while trying to read from the provided cookie file"""


class CookieFileLoadError(http.cookiejar.LoadError):
    """Raised for errors generated when trying to read and load from provided cookie file."""


class DownloadError(Exception):
    """Raised for download-related errors."""


class Session:
    def __init__(self, cookies: list[http.cookiejar.Cookie] | os.PathLike = None, proxies: dict[str, str] = None):
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
                raise CookieFileError(f'Error reading from provided cookie file: ({cookies})')

        self.opener.add_handler(urllib.request.HTTPCookieProcessor(self.cookie_jar))

    def open(self, request: urllib.request.Request) -> http.client.HTTPResponse:
        return self.opener.open(request)

    def download(self, request: urllib.request.Request, file_path: os.PathLike, expected_file_size: int = None,
                 max_retries: int = 3) -> tuple[int, os.PathLike]:
        """Downloads a file from a given URL using the provided :class:`urllib.request.Request` and saves it to the
        specified `file_path`.

        :param urllib.request.Request request: An object containing the URL and headers for the download.
        :param os.PathLike file_path: The file path where the downloaded file will be saved.
        :param int expected_file_size: The expected size of the file in bytes, if known. Defaults to `None`.
        :param int max_retries: Maximum number of retries in case of download failures. Defaults to `3`.

        :return: A tuple containing two values:
                 1. The actual size of the downloaded file in bytes.
                 2. The file path where the downloaded content has been saved.
        :rtype: tuple[int, os.PathLike]

        :raises DownloadError: If any of these errors occur during the download process:
                               1. If there are connection-related errors, such as :class:`urllib.error.URLError`.
                               2. If the provided `request` object is invalid or if there are data processing errors,
                                  i.e., :class:`ValueError`, :class:`TypeError`.
                               3. If there are file system errors during file operations, i.e. :class:`PermissionError`.
                               4. If there are unexpected errors that cannot be categorized.

        .. note::
            - The `Session.download()` employs `Session.open()` to handle requests. Consequently, any supplementary
              arguments included in the request (such as cookies or headers) will supersede the default :class:`Session`
              parameters. This circumstance bears the potential of giving rise to unanticipated errors that lack proper
              documentation.

        .. warning::
            - Ensure that the provided `file_path` specifies a valid and writable file path in the filesystem.

        :Example:
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

        # TODO: We need a proper internal logging utility to make actual error handling and monitoring possible.

        retries = 0
        while retries <= max_retries:
            try:
                with open(file_path, 'wb') as file, self.open(request) as response:
                    downloaded_bytes = 0

                    # Reading and writing 1MB (1024B * 1024B = 1MB) chunks each time to prevent memory overflow.
                    while chunk := response.read(1024 * 1024):
                        file.write(chunk)
                        downloaded_bytes += len(chunk)

                if not expected_file_size:
                    expected_file_size = int(response.getheader('Content-Length', 0))

                # If the `expected_file_size` was absent and the response lacked a `Content-Length` header, we encounter
                # a situation where it becomes impossible to determine the integrity of the downloaded file.
                # Consequently, we are compelled to assume that the file is not corrupted due to the absence of relevant
                # information.
                if downloaded_bytes < expected_file_size and expected_file_size > 0:
                    raise DownloadError('Downloaded data is incomplete or malformed.')

                return expected_file_size, file_path
            except (urllib.error.URLError, http.client.HTTPException, ConnectionError) as tb:
                raise DownloadError(f'Error connecting to the host: {request}') from tb
            except (ValueError, TypeError) as tb:
                raise DownloadError(f'Error processing data or malformed request: {request}') from tb
            except OSError as tb:
                raise DownloadError(f'File system error while working with the file: {file_path}') from tb
            except Exception as tb:
                raise DownloadError(f'Unknown error encountered: {request}') from tb
            finally:
                retries += 1

        raise DownloadError(f'{max_retries=} reached for {request.get_full_url()=} and {file_path=}')
