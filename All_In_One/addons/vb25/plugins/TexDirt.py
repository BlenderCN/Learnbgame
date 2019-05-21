#
# V-Ray/Blender
#
# http://vray.cgdo.ru
#
# Author: Andrei Izrantcev
# E-Mail: andrei.izrantcev@chaosgroup.com
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

# Blender modules
import bpy
from bpy.props import *

# V-Ray/Blender modules
from vb25.utils import *
from vb25.shaders import *
from vb25.ui import ui


TYPE = 'TEXTURE'

ID   = 'TexDirt'
NAME = 'Dirt'
PLUG = 'TexDirt'
DESC = "TODO."
PID  =  0

PARAMS = (
    'affect_reflection_elements', # false bool // true to add the occlusion to relection render elements when mode>0
    'affect_result_nodes', # list plugin
    'affect_result_nodes_inclusive', # false bool // if true the affect_result_nodes list is inclusive
    'bias_x', # 0 float
    'bias_y', # 0 float
    'bias_z', # 0 float
    'black_color', #  acolor texture
    'consider_same_object_only', # false bool
    'distribution', # 0 float
    'double_sided', # false bool // if true, the occlusion on both sides of the surface will be calculated
    'environment_occlusion', # false bool // true to compute the environment for unoccluded samples
    'falloff', # 0 float
    'glossiness', #  float texture // A texture for the glossiness when mode>0
    'ignore_for_gi', # true bool
    'ignore_self_occlusion', # false bool
    'invert_normal', # false bool
    'mode', # 0 integer // Mode (0 - ambient occlusion; 1 - Phong reflection occlusion; 2 - Blinn reflection occlusion; 3 - Ward reflection occlusion)
    'radius', # 10 float texture
    'render_nodes', # list plugin
    'render_nodes_inclusive', # false bool // if true the render_nodes list is inclusive
    'subdivs', # 8 integer
    'white_color', #  acolor texture
    'work_with_transparency', # false bool
)


class TexDirt(bpy.types.PropertyGroup):
    double_sided = BoolProperty(
        name        = "Double Sided",
        description = "If true, the occlusion on both sides of the surface will be calculated",
        default     = False
    )

    render_nodes = bpy.props.StringProperty(
        name        = "Render nodes",
        description = "Render node list",
        default     = ''
    )

    render_nodes_inclusive = bpy.props.BoolProperty(
        name        = "Inclusive",
        description = "Render node list is inclusive",
        default     = False
    )

    affect_result_nodes = bpy.props.StringProperty(
        name        = "Affect nodes",
        description = "Affect node list",
        default     = ''
    )

    affect_result_nodes_inclusive = bpy.props.BoolProperty(
        name        = "Inclusive",
        description = "Affect node list is inclusive",
        default     = False
    )

    white_color= FloatVectorProperty(
        name= "Unoccluded color",
        description= "Unoccluded color",
        subtype= 'COLOR',
        min= 0.0,
        max= 1.0,
        soft_min= 0.0,
        soft_max= 1.0,
        default= (1.0,1.0,1.0)
    )

    white_color_tex= StringProperty(
        name= "Unoccluded color texture",
        description= "Unoccluded color texture",
        default= ""
    )

    black_color= FloatVectorProperty(
        name= "Occluded color",
        description= "Occluded color",
        subtype= 'COLOR',
        min= 0.0,
        max= 1.0,
        soft_min= 0.0,
        soft_max= 1.0,
        default= (0.0,0.0,0.0)
    )

    black_color_tex= StringProperty(
        name= "Occluded color texture",
        description= "Occluded color texture",
        default= ""
    )

    radius= FloatProperty(
        name= "Radius",
        description= "Radius",
        min= 0.0,
        max= 1000.0,
        soft_min= 0.0,
        soft_max= 100.0,
        precision= 3,
        default= 0.1
    )

    radius_tex= StringProperty(
        name= "Radius Texture",
        description= "Radius Texture",
        default= ""
    )

    distribution= FloatProperty(
        name= "Distribution",
        description= "Distribution",
        min= 0.0,
        max= 100.0,
        soft_min= 0.0,
        soft_max= 10.0,
        precision= 3,
        default= 0
    )

    falloff= FloatProperty(
        name= "Falloff",
        description= "Falloff",
        min= 0.0,
        max= 100.0,
        soft_min= 0.0,
        soft_max= 10.0,
        precision= 3,
        default= 0
    )

    subdivs= IntProperty(
        name= "Subdivs",
        description= "Subdivs",
        min= 0,
        max= 100,
        soft_min= 0,
        soft_max= 10,
        default= 8
    )

    bias_x= FloatProperty(
        name= "Bias X",
        description= "Bias Z",
        min= -100.0,
        max= 100.0,
        soft_min= -10.0,
        soft_max= 10.0,
        precision= 3,
        default= 0
    )

    bias_y= FloatProperty(
        name= "Bias Y",
        description= "Bias Y",
        min= -100.0,
        max= 100.0,
        soft_min= -10.0,
        soft_max= 10.0,
        precision= 3,
        default= 0
    )

    bias_z= FloatProperty(
        name= "Bias Z",
        description= "Bias Z",
        min= -100.0,
        max= 100.0,
        soft_min= -10.0,
        soft_max= 10.0,
        precision= 3,
        default= 0
    )

    ignore_for_gi= BoolProperty(
        name= "Ignore for GI",
        description= "Ignore for GI",
        default= True
    )

    consider_same_object_only= BoolProperty(
        name= "Consider same object only",
        description= "Consider same object only",
        default= False
    )

    invert_normal= BoolProperty(
        name= "Invert normal",
        description= "Invert normal",
        default= False
    )

    work_with_transparency= BoolProperty(
        name= "Work with transparency",
        description= "Work with transparency",
        default= False
    )

    ignore_self_occlusion= BoolProperty(
        name= "Ignore self occlusion",
        description= "Ignore self occlusion",
        default= False
    )

    mode= EnumProperty(
        name= "Mode",
        description= "Mode",
        items= (
            ('AO',"Ambient occlusion",""),
            ('PHONG',"Phong reflection occlusion",""),
            ('BLINN',"Blinn reflection occlusion",""),
            ('WARD',"Ward reflection occlusion","")
        ),
        default= 'AO'
    )

    environment_occlusion= BoolProperty(
        name= "Environment occlusion",
        description= "Compute the environment for unoccluded samples",
        default= False
    )

    affect_reflection_elements= BoolProperty(
        name= "Affect reflection elements",
        description= "Add the occlusion to relection render elements when mode>0",
        default= False
    )

    glossiness= FloatProperty(
        name= "Glossiness",
        description= "The spread of the rays traced for reflection occlusion",
        min= 0.0,
        max= 100.0,
        soft_min= 0.0,
        soft_max= 10.0,
        precision= 3,
        default= 1.0
    )


def add_properties(VRayTexture):
    VRayTexture.TexDirt = PointerProperty(
        name        = "TexDirt",
        type        =  TexDirt,
        description = "V-Ray TexDirt settings"
    )


def write(bus):
    MODE = {
        'AO'    : 0,
        'PHONG' : 1,
        'BLINN' : 2,
        'WARD'  : 3
    }

    scene = bus['scene']
    ofile = bus['files']['textures']

    slot     = bus['mtex']['slot']
    texture  = bus['mtex']['texture']
    tex_name = bus['mtex']['name']

    TexDirt = getattr(texture.vray, PLUG)

    mapped_params = write_sub_textures(bus, TexDirt, ('white_color_tex', 'black_color_tex', 'radius_tex'))

    radiusTexture      = None
    radiusTextureFloat = None
    if 'radius_tex' in mapped_params:
        radiusTexture = tex_name + "Radius"
        radiusTextureFloat = radiusTexture + "::product"

        ofile.write("\nTexFloatOp %s {" % radiusTexture)
        ofile.write("\n\tfloat_a=%s::out_intensity;" % mapped_params['radius_tex'])
        ofile.write("\n\tfloat_b=%s;" % a(scene, TexDirt.radius))
        ofile.write("\n}\n")

    ofile.write("\n%s %s {"%(PLUG, tex_name))
    for param in PARAMS:
        if not hasattr(TexDirt, param):
            debug(scene, "Unimplemented parameter: %s" % (param))
            continue
        
        value = getattr(TexDirt, param)
        
        if param == 'mode':
            value = MODE[TexDirt.mode]
        if param in ('render_nodes', 'affect_result_nodes'):
            nodeGroups = getattr(TexDirt, param)
            if not nodeGroups:
                continue
            value = "List(%s)" % ",".join([get_name(ob, prefix='OB') for ob in generate_object_list(None, nodeGroups)])
            ofile.write("\n\t%s=%s;" % (param, value))
            continue
        elif param == 'radius':
            if radiusTexture:
                ofile.write("\n\tradius=%s;" % radiusTextureFloat)
        elif param in ('white_color','black_color'):
            tex_key = param+'_tex'
            if tex_key in mapped_params:
                ofile.write("\n\t%s=%s;"%(param, mapped_params[tex_key]))
                continue
            else:
                pass
        ofile.write("\n\t%s=%s;"%(param, a(scene, value)))
    ofile.write("\n}\n")

    return tex_name



'''
  GUI
'''
class TEXTURE_PT_TexDirt(ui.VRayTexturePanel, bpy.types.Panel):
    bl_label = NAME

    COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

    @classmethod
    def poll(cls, context):
        tex = context.texture
        if not tex:
            return False
        VRayTexture = tex.vray
        engine = context.scene.render.engine
        return ((tex and tex.type == 'VRAY' and VRayTexture.type == ID) and (ui.engine_poll(__class__, context)))
    
    def draw(self, context):
        tex  = context.texture
        TexDirt = getattr(tex.vray, PLUG)
        
        wide_ui = context.region.width > ui.narrowui

        layout = self.layout

        layout.prop(TexDirt, 'mode')

        split = layout.split()
        col = split.column(align=True)
        col.prop(TexDirt, 'white_color')
        col.prop_search(TexDirt, 'white_color_tex',
                        bpy.data, 'textures',
                        text="")
        if wide_ui:
            col = split.column(align=True)
        col.prop(TexDirt,'black_color')
        col.prop_search(TexDirt, 'black_color_tex',
                        bpy.data, 'textures',
                        text="")

        layout.separator()

        split = layout.split()
        col = split.column()
        sub_radius = col.column(align=True)
        sub_radius.prop(TexDirt,'radius')
        sub_radius.prop_search(TexDirt, 'radius_tex',
                               bpy.data, 'textures',
                               text="")
        col.prop(TexDirt,'distribution')
        if TexDirt.mode != 'AO':
            col.prop(TexDirt, 'glossiness')
        if wide_ui:
            col = split.column()
        col.prop(TexDirt, 'falloff')
        col.prop(TexDirt, 'subdivs')
        if TexDirt.mode != 'AO':
            col.prop(TexDirt, 'affect_reflection_elements')

        layout.separator()

        split = layout.split()
        row = split.row(align=True)
        row.prop(TexDirt, 'bias_x')
        row.prop(TexDirt, 'bias_y')
        row.prop(TexDirt, 'bias_z')

        layout.separator()

        split = layout.split()
        col = split.column()
        col.prop(TexDirt, 'invert_normal')
        col.prop(TexDirt, 'ignore_for_gi')
        col.prop(TexDirt, 'ignore_self_occlusion')
        col.prop(TexDirt, 'consider_same_object_only')
        if wide_ui:
            col = split.column()
        col.prop(TexDirt, 'work_with_transparency')
        col.prop(TexDirt, 'environment_occlusion')
        col.prop(TexDirt, 'double_sided')        

        layout.separator()

        split = layout.split()
        col = split.column()
        col.prop_search(TexDirt,  'render_nodes',
                        bpy.data, 'groups',
                        text="Exclude")
        col.prop(TexDirt, 'render_nodes_inclusive')

        split = layout.split()
        col = split.column()
        col.prop_search(TexDirt,  'affect_result_nodes',
                        bpy.data, 'groups',
                        text="Result Affect")
        col.prop(TexDirt, 'affect_result_nodes_inclusive')


def GetRegClasses():
    return (
        TEXTURE_PT_TexDirt,
        TexDirt,
    )


def register():
    for regClass in GetRegClasses():
        bpy.utils.register_class(regClass)


def unregister():
    for regClass in GetRegClasses():
        bpy.utils.unregister_class(regClass)
