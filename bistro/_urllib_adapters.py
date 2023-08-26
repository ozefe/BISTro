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
import http.cookiejar
import os


class Session:
    def __init__(self, cookies: list[http.cookiejar.Cookie] | str = None, proxies: dict[str, str] = None):
        self.opener = urllib.request.build_opener()

        self.opener.addheaders = [
            ('User-Agent',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 '
             'Safari/537.36')
        ]

        if proxies:
            self.opener.add_handler(urllib.request.ProxyHandler(proxies))

        if isinstance(cookies, list):
            self.cookie_jar = http.cookiejar.CookieJar()
            for cookie in cookies:
                self.cookie_jar.set_cookie(cookie)
        elif isinstance(cookies, os.PathLike):
            self.cookie_jar = http.cookiejar.LWPCookieJar(cookies)
            try:
                self.cookie_jar.load()
            except FileNotFoundError as e:
                raise e

        self.opener.add_handler(urllib.request.HTTPCookieProcessor(self.cookie_jar))

    def open(self, request: urllib.request.Request):
        raise NotImplementedError

    def download(self, request: urllib.request.Request, file_path: os.PathLike):
        raise NotImplementedError
