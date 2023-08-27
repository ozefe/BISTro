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
import urllib.error
import urllib.request
import http.cookiejar
import http.client
import os


class CookieFileError(OSError):
    """Raised for errors encountered while trying to read from the provided cookie file"""


class CookieFileLoadError(http.cookiejar.LoadError):
    """Raised for errors generated when trying to read and load from provided cookie file."""


class DownloadError(Exception):
    """Raised for errors generated when trying to download a file"""


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

    def download(self, request: urllib.request.Request, file_path: os.PathLike, file_size: int = None, max_retries: int = 3) -> tuple[int, os.PathLike]:
        retries = 0
        while retries <= max_retries:
            try:
                with open(file_path, 'wb') as file, self.open(request) as response:
                    downloaded_size = 0
                    while chunk := response.read(1024):
                        file.write(chunk)
                        downloaded_size += len(chunk)

                if not file_size:
                    file_size = int(response.getheader('Content-Length', 0))
                if downloaded_size < file_size and file_size > 0:
                    print(f'{downloaded_size=} {response.length=}')
                    raise DownloadError('Download malformed.')

                return file_size, file_path
            # self.open exception
            except (urllib.error.URLError, http.client.HTTPException, ConnectionError) as tb:
                # raise DownloadError(f'Error trying to connect to the host: {request}') from tb
                pass
            except (ValueError, TypeError) as tb:
                # raise DownloadError(f'Data processing error occurred, provided Request object could be malformed: {request}') from tb
                pass
            # file open error
            except OSError as tb:
                # raise DownloadError(f'File system error occurred while trying to work with the provided file: {file_path}') from tb
                pass
            # catch-all
            except Exception as tb:
                raise DownloadError(f'Unknown error encountered: {request}') from tb
            finally:
                print(f'Retries so far for {request=} and {file_path=}: {retries}')
                retries += 1

        raise DownloadError(f'{max_retries=} reached for {request=} and {file_path=}')
