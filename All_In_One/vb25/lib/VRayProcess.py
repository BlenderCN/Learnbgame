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


# Python modules
import os
import re
import struct
import socket
import subprocess
import signal
import sys
import tempfile
import time

# V-Ray/Blender modules
import vb25
from vb25.lib import VRaySocket

if sys.platform != 'win32':
    import fcntl


def Quotes(path):
    if sys.platform != 'win32':
        return '"%s"' % (path)
    return path


class VRayProcess():
    # V-Ray process
    process    = None
    exit_ready = None
    params     = None

    # V-Ray command socket
    socket = None

    # Executable parameters
    sceneFile     = None
    imgFile       = None
    showProgress  = None
    progressUseCR = None
    verboseLevel  = None
    cmdMode       = None

    bus = None
    scene = None

    VRayScene    = None
    VRayExporter = None
    VRayDR       = None


    def __init__(self):
        self.socket = VRaySocket()

        self.params = []

        self.verboseLevel = '1'
        self.showProgress = '2'


    def __del__(self):
        pass


    def set_params(self, bus=None, params=None):
        self.bus = bus

        self.VRayScene    = self.scene.vray
        self.VRayExporter = self.VRayScene.exporter
        self.VRayDR       = self.VRayScene.VRayDR

        self.params = []
        self.params.append(vb25.utils.get_vray_standalone_path(self.scene))

        self.params.append('-sceneFile=')
        self.params.append(self.sceneFile)
        self.params.append('-imgFile=')
        self.params.append(self.imgFile)

        if self.VRayExporter.use_progress:
            # We need only progress info
            self.params.append('-verboseLevel=')
            self.params.append('3')

            # Always show progress
            self.params.append('-showProgress=')
            self.params.append('2')

            # Use log line breaks
            self.params.append('-progressUseCR=')
            self.params.append('0')

        else:
            self.params.append('-verboseLevel=')
            self.params.append(self.verboseLevel)
            self.params.append('-showProgress=')
            self.params.append(self.showProgress)

        if self.VRayDR.on:
            if len(self.VRayDR.nodes):
                self.params.append('-distributed=1')
                self.params.append('-portNumber=%i' % self.VRayDR.port)
                self.params.append('-renderhost=%s' % Quotes(';'.join([n.address for n in self.VRayDR.nodes])))
                self.params.append('-include=%s' % Quotes(self.bus['filenames']['DR']['shared_dir'] + os.sep))

        # Setup command mode
        # Disable VFB
        self.params.append('-display=')
        self.params.append('0')

        # Enable command socket
        self.params.append('-cmdMode=')
        self.params.append('1')

        if not self.VRayExporter.autorun:
            vb25.utils.debug(self.scene, "Enable \"Autorun\" option to start V-Ray automatically after export.")
            vb25.utils.debug(self.scene, "Command: %s" % ' '.join(self.params))


    def run(self):
        if not self.VRayExporter.autorun:
            return

        if self.VRayExporter.use_progress:
            self.process = subprocess.Popen(self.params, bufsize=256, stdout=subprocess.PIPE)

            if vb25.utils.PLATFORM != 'win32':
                fd = self.process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        else:
            self.process = subprocess.Popen(self.params)

        self.exit_ready = False

        time.sleep(0.25)
        self.socket.connect()


    def is_running(self):
        if self.process is None:
            return False
        if self.process.poll() is None:
            return True
        return False


    def kill(self):
        self.quit()

        if self.is_running():
            self.process.terminate()

        self.process = None


    def get_progress(self):
        msg  = None
        prog = None

        if not self.exit_ready:
            if self.process and self.is_running():
                stdout_lines = None
                try:
                    self.process.stdout.flush()
                    stdout_lines = self.process.stdout.readlines(256)
                except:
                    pass

                if stdout_lines:
                    for stdout_line in stdout_lines:
                        line = stdout_line.decode('ascii').strip()

                        if self.VRayExporter.debug:
                            print(line)

                        if line.find("Building light cache") != -1:
                            msg = "Light cache"
                        elif line.find("Prepass") != -1:
                            prepass_num = line[line.find("Prepass")+7:line.find("of")].strip()
                            msg = "Irradiance map (prepass %s)" % (prepass_num)
                        elif line.find("Rendering image") != -1:
                            msg = "Rendering"
                        elif line.find("Building caustics") != -1:
                            msg = "Caustics"
                        elif line.find("Frame took") != -1:
                            self.exit_ready = True

                        if msg is None:
                            continue

                        p_start = line.find("...: ") + 5
                        p_end   = line.find("%")

                        if p_start != -1 and p_end != -1 and p_end > p_start:
                            p_str = line[p_start:p_end].strip()
                            if len(p_str):
                                prog = float(p_str) / 100.0
                                break

        return msg, prog


    def load_scene(self):
        if not self.sceneFile:
            vb25.utils.vb25.utils.debug(None, "Scene file is not set", error=True)
            return 'Scene file is not set'

        self.socket.send("load %s" % self.sceneFile)

        return None


    def unload_scene(self):
        self.socket.send("unload")
        return None


    def reload_scene(self):
        self.unload_scene()
        self.load_scene()
        return None


    def render(self):
        self.socket.send("render", result=False)
        return None


    def quit(self):
        self.socket.send("stop")
        self.socket.send("quit")
        self.socket.disconnect()
        return None


    def recieve_image(self, progressFile):
        jpeg_image = None
        jpeg_size  = 0
        buff  = []

        if not self.is_running():
            self.exit_ready = True
            return 'V-Ray is not running'

        # Request image
        self.socket.send("getImage 90 1", result=False)

        # Read image stream size
        jpeg_size_bytes = self.socket.recv(4)

        # Check if 'fail' recieved
        if jpeg_size_bytes == b'fail':
            self.socket.recv(3) # Read 'e', 'd', '\0'
            self.exit_ready = True
            return 'getImage failed'

        try:
            # Get stream size in bytes
            jpeg_size = struct.unpack("<L", jpeg_size_bytes)[0]

            # print("JPEG stream size = %i"%(jpeg_size))

            # Read JPEG stream
            jpeg_image = self.socket.recv(jpeg_size)

            # Write stream to file
            open(progressFile, 'wb').write(jpeg_image)
        except:
            return 'JPEG stream recieve fail'

        return None
