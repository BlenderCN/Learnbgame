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
from vb25.utils   import *
from vb25.ui      import ui
from vb25.plugins import *
from vb25.texture import *
from vb25.uvwgen  import *


TYPE = 'TEXTURE'
ID   = 'TexMeshVertexColorChannel'
PLUG = 'TexMeshVertexColorChannel'
NAME = 'Vertex Color'
DESC = "TexMeshVertexColorChannel"
PID  =  25

PARAMS = (
    'channelIndex',
)


def add_properties(rna_pointer):
    class TexMeshVertexColorChannel(bpy.types.PropertyGroup):
        channelIndex = bpy.props.IntProperty(
            name = "Сhannel Index",
            description = "Сhannel Index",
            min = 0,
            max = 100,
            soft_min = 0,
            soft_max = 10,
            default = 1
        )

    bpy.utils.register_class(TexMeshVertexColorChannel)

    rna_pointer.TexMeshVertexColorChannel= PointerProperty(
        name= "TexMeshVertexColorChannel",
        type=  TexMeshVertexColorChannel,
        description= "V-Ray TexMeshVertexColorChannel settings"
    )


def write(bus):
    scene = bus['scene']
    ofile = bus['files']['textures']

    slot     = bus['mtex']['slot']
    texture  = bus['mtex']['texture']
    tex_name = bus['mtex']['name']

    TexMeshVertexColorChannel = getattr(texture.vray, PLUG)
    
    ofile.write("\nTexMeshVertexColorChannel %s {"%(tex_name))
    ofile.write("\n\tchannelIndex=%s;" % p(TexMeshVertexColorChannel.channelIndex))
    ofile.write("\n}\n")

    return tex_name


'''
  GUI
'''
class VRAY_TP_TexMeshVertexColorChannel(ui.VRayTexturePanel, bpy.types.Panel):
    bl_label       = NAME

    COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

    @classmethod
    def poll(cls, context):
        tex= context.texture
        return tex and tex.type == 'VRAY' and tex.vray.type == ID and ui.engine_poll(cls, context)

    def draw(self, context):
        wide_ui = context.region.width > ui.narrowui
        layout  = self.layout

        tex = context.texture
        TexMeshVertexColorChannel = getattr(tex.vray, PLUG)

        layout.prop(TexMeshVertexColorChannel, 'channelIndex')


def GetRegClasses():
    return (
        VRAY_TP_TexMeshVertexColorChannel,
    )


def register():
    for regClass in GetRegClasses():
        bpy.utils.register_class(regClass)


def unregister():
    for regClass in GetRegClasses():
        bpy.utils.unregister_class(regClass)
