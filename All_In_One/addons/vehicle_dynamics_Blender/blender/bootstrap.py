"""
Auto-installation of dependencies that blender-addon needs

This file is part of inertial_to_blender project,
a Blender simulation generator from inertial sensor data on cars.

Copyright (C) 2018  Federico Bertani
Author: Federico Bertani
Credits: Federico Bertani, Stefano Sinigardi, Alessandro Fabbri, Nico Curti

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os
import sys
import urllib.request
import subprocess
import importlib
from production_requirements import requirements
from pathlib import Path

addon_path = str(Path(__file__).parent.parent)
blender_path = str(Path(sys.executable).parent)
# TODO detect version, make more flexible
# _, dirs, _ = next(os.walk(blender_path))
# blender_version_dir = dirs[0]
blender_version_dir = "2.79"
blender_python_dir = os.path.join(blender_path, blender_version_dir, "python")
posix_pip_location = os.path.join(blender_python_dir, "bin", "pip3")
windows_pip_location = os.path.join(blender_python_dir, "scripts", "pip3.exe")
pip_location = {
    'posix':posix_pip_location,
    'windows':windows_pip_location
}


def call_system_command(command):
    try:
        retcode = subprocess.call(command, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            return retcode
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)


def install_package(package_name, version):
    command = None
    # pip command differ by platform
    if (os.path.exists(pip_location['posix'])):
        command = r'"{}" install {}=={}'.format(pip_location['posix'], package_name,version)
    elif os.path.exists(pip_location['windows']):
        command = r'"{}" install {}=={}'.format(pip_location['windows'], package_name,version)
    if command:
        ret_code = call_system_command(command)
        if ret_code > 0:
            raise Exception("Error installing dependencies")
    else:
        raise Exception("Error on finding pip location")

def install_dependencies():
    # TODO handle permission errors

    print("Addon path " + addon_path)

    print("Blender path " + blender_path)

    # check if pip is not installed
    if not (os.path.exists(posix_pip_location) or os.path.exists(windows_pip_location)):
        print("Downloading pip")
        # download get pip
        pip_download_location = os.path.join(addon_path, "get_pip.py")
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py",
                                   filename=pip_download_location)
        # execute get_pip from shell
        python_bin = os.path.join(blender_python_dir, "bin")
        if (os.path.exists(os.path.join(python_bin, "python3.5m"))):
            python_interpreter = os.path.join(python_bin, "python3.5m")
        elif os.path.exists(os.path.join(python_bin, "python.exe")):
            python_interpreter = os.path.join(python_bin, "python.exe")
        command = r'"{}" "{}"'.format(python_interpreter, pip_download_location)
        print("Command: " + command)
        call_system_command(command)
    # check module existence
    for required_module in requirements:
        # if a required package is not installed
        if importlib.util.find_spec(required_module['name']) is None:
            # install it
            install_package(required_module['pip_name'],required_module['version'])
