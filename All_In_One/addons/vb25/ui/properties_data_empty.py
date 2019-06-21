'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy

''' vb modules '''
from vb25.utils import *
from vb25.ui.ui import *


class VRAY_DP_empty(VRayDataPanel, bpy.types.Panel):
    bl_label   = "Override"
    bl_options = {'DEFAULT_CLOSED'}

    COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'EMPTY' and engine_poll(__class__, context))

    def draw(self, context):
        wide_ui = context.region.width > narrowui
        layout  = self.layout
        
        VRayObject = context.object.vray

        box = layout.box()

        box.prop(VRayObject, 'overrideWithScene')

        if VRayObject.overrideWithScene:
            split = box.split()
            col = split.column()
            col.prop(VRayObject, 'sceneFilepath')
            col.prop(VRayObject, 'sceneDirpath')
            
            split = box.split()
            col = split.column()
            col.prop(VRayObject, 'sceneReplace')
            col.prop(VRayObject, 'sceneUseTransform')
            
            split = box.split()
            col = split.column()
            col.prop(VRayObject, 'sceneAddNodes')
            col.prop(VRayObject, 'sceneAddMaterials')
            col.prop(VRayObject, 'sceneAddLights')
            if wide_ui:
                col = split.column()
            col.prop(VRayObject, 'sceneAddCameras')
            col.prop(VRayObject, 'sceneAddEnvironment')


def GetRegClasses():
    return (
        VRAY_DP_empty,
    )


def register():
    for regClass in GetRegClasses():
        bpy.utils.register_class(regClass)


def unregister():
    for regClass in GetRegClasses():
        bpy.utils.unregister_class(regClass)
