# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "F3b",
    "author" : "Riccardo Balbo",
    "version": (1,0,0),
    "description" : "",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category": "Learnbgame",
}

import os,sys,bpy

#Load dependencies
_modules_path = os.path.join(os.path.dirname(__file__), "libs")
for path in os.listdir(_modules_path):
    p=os.path.join(_modules_path,path)
    print("Load library ",p)
    sys.path.append(p)
del _modules_path
print(sys.path)



def register():
    try:
        unregister()
    except (RuntimeError, ValueError):
        pass
    print("f3b exporter: Init")
    from . import F3bExporterOperator
    F3bExporterOperator.register()
    from .tools import F3bTools
    F3bTools.register()


def unregister():
    print("f3b exporter: Destroy")
    from . import F3bExporterOperator
    F3bExporterOperator.unregister()
    from .tools import F3bTools
    F3bTools.unregister()

# def main():
#     try:
#         unregister()
#     except (RuntimeError, ValueError):
#         pass
#     register()


# if __name__ == "__main__":
#     main()
