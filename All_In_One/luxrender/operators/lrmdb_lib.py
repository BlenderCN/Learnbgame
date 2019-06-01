# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
"""
Non-blender specific LRMDB interface handlers should go in here
"""

import xmlrpc.client, http.client, http.cookiejar, urllib.request, os

from ..extensions_framework import util as efutil


def make_cookie_filename():
    fc = []
    for p in efutil.config_paths:
        if os.path.exists(p) and os.path.isdir(p) and os.access(p, os.W_OK):
            fc.append('/'.join([p, 'luxrender_lrmdb_cookies.txt']))

    if len(fc) < 1:
        return None

    try:
        cookie_file = fc[0]
        if not os.path.exists(cookie_file):
            cf = open(cookie_file, 'w')
            cf.write("#LWP-Cookies-2.0\n\n")
            cf.close()
        return cookie_file
    except:
        print(
            'WARNING: Cannot write cookie file; LuxRender LRMDB sessions will not be saved between Blender executions.')
        return None


class CookieTransport(xmlrpc.client.Transport):
    # Custom user-agent string for this Transport
    user_agent = 'LuxBlend25'

    def __init__(self, *args, **kwargs):
        self.cookiejar = http.cookiejar.LWPCookieJar(
            make_cookie_filename()
        )
        super().__init__(*args, **kwargs)

    def cookie_request(self, host):
        return urllib.request.Request('http://%s/' % host)

    # This method is almost identical to Transport.request
    def request(self, host, handler, request_body, verbose=False):
        # issue XML-RPC request
        http_conn = self.send_request(host, handler, request_body, verbose)
        resp = http_conn.getresponse()

        # Extract cookies from response
        ck_req = self.cookie_request(host)
        self.cookiejar.extract_cookies(resp, ck_req)

        try:
            # Save the cookies to file if we have a valid path
            self.cookiejar.save()
        except ValueError:
            # nevermind, just means that cookies won't be persistent
            pass

        if resp.status != 200:
            raise xmlrpc.client.ProtocolError(
                host + handler,
                resp.status, resp.reason,
                dict(resp.getheaders())
            )

        self.verbose = verbose

        return self.parse_response(resp)

    # This method is identical to Transport.send_request
    def send_request(self, host, handler, request_body, debug):
        host, extra_headers = self.get_host_info(host)[0:2]
        connection = http.client.HTTPConnection(host)

        if debug:
            connection.set_debuglevel(1)

        headers = {
            "Content-Type": "text/xml",
            "User-Agent": self.user_agent
        }

        if extra_headers:
            headers.update(extra_headers)

        try:
            # Try to load cookies from file, if possible
            self.cookiejar.load()
        except ValueError:
            # nevermind, just means that cookies won't be persistent
            pass

        # Insert cookie headers
        ck_req = self.cookie_request(host)
        self.cookiejar.add_cookie_header(ck_req)
        headers.update(ck_req.header_items())

        connection.request("POST", handler, request_body, headers)
        return connection


class lrmdb_client(object):
    # static
    server = None
    loggedin = False
    username = ''

    @classmethod
    def reset(cls):
        cls.server = None
        cls.loggedin = False
        cls.username = ''

    @classmethod
    def server_instance(cls):
        if cls.server is None:
            cls.server = xmlrpc.client.ServerProxy(
                "http://www.luxrender.net/lrmdb2/ixr",
                transport=CookieTransport()
            )

        return cls.server

    def check_login(self):
        un = self.server_instance().user.current()
        if un:
            self.loggedin = True
            self.username = un
        else:
            self.loggedin = False
            self.username = ''
        return self.loggedin
