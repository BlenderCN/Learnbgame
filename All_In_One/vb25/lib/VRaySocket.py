#
# V-Ray/Blender
#
# http://vray.cgdo.ru
#
# Author: Andrey M. Izrantsev (aka bdancer)
# E-Mail: izrantsev@cgdo.ru
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#

# VRay Standalone communication socket

# Python modules
import socket


class VRaySocket():
    socket  = None
    address = "localhost"
    port    = 4368


    def __init__(self, address):
        self.address = address


    def __init__(self):
        pass


    def __del__(self):
        self.disconnect()


    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.address, self.port))
        except socket.error:
            self.socket = None

        if self.socket is None:
            return False

        return None


    def isconnected(self):
        if self.socket is not None:
            return True
        return False


    def disconnect(self):
        if self.socket is None:
            return
        self.socket.close()
        self.socket = None


    def get_result(self):
        res = b''

        while True:
            r = self.socket.recv(1);
            if r == b'\0':
                break
            if r != b'\n':
                res += r;

        return res


    def send(self, cmd, result=True):
        if self.socket is None:
            res = self.connect()
            if res is not None:
                return

        sent_size = None
        sent_res  = None

        try:
            sent_size = self.socket.send(bytes(cmd+'\0', 'ascii'))
            if result:
                sent_res = self.get_result()
        except:
            return None

        return None


    def recv(self, size):
        if self.socket is None:
            res = self.connect()
            if res is not None:
                return None

        b = None
        try:
            b = self.socket.recv(size)
        except:
            pass
        return b
