# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Module: export_mdc.py
# Description: MDC export interface.

from .mdc_modules.mdc_file import MDCFile
from .mdc_modules.blender_scene import BlenderScene
from .mdc_modules.converter import Converter
from .mdc_modules.verification import Verify
from .mdc_modules.options import ExportOptions

class MDCExport:

    def run(self, exportOptions):

        blenderScene = BlenderScene.read(exportOptions)

        isVerified, errMsg = Verify.blenderScene(blenderScene)
        if isVerified == False:
            return errMsg

        mdcFile = Converter.blenderSceneToMdcFile(blenderScene)

        isVerified, errMsg = Verify.mdcFile(mdcFile)
        if isVerified == False:
            return errMsg

        mdcFile.write(exportOptions)

        return None
