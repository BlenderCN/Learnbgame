#
# V-Ray For Blender
#
# http://www.chaosgroup.com
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

import bpy

from bpy.props import *

from vb25.utils import p


TYPE = 'SETTINGS'
ID   = 'SettingsVFB'
NAME = 'Lens Effects'
DESC = "Lens effects"

PARAMS = (
    'bloom_on',
    'bloom_fill_edges',
    'bloom_weight',
    'bloom_size',
    'bloom_shape',
    'bloom_mode',
    'bloom_mask_intensity_on',
    'bloom_mask_intensity',
    'bloom_mask_objid_on',
    'bloom_mask_objid',
    'bloom_mask_mtlid_on',
    'bloom_mask_mtlid',
    'glare_on',
    'glare_fill_edges',
    'glare_weight',
    'glare_size',
    'glare_type',
    'glare_mode',
    # 'glare_image_path',
    # 'glare_obstacle_image_path',
    'glare_diffraction_on',
    'glare_use_obstacle_image',
    'glare_cam_blades_on',
    'glare_cam_num_blades',
    'glare_cam_rotation',
    'glare_cam_fnumber',
    'glare_mask_intensity_on',
    'glare_mask_intensity',
    'glare_mask_objid_on',
    'glare_mask_objid',
    'glare_mask_mtlid_on',
    'glare_mask_mtlid',
    'interactive',
)


def add_properties(rna_pointer):
    class SettingsVFB(bpy.types.PropertyGroup):
        use = BoolProperty(
            name        = "Use Lens Effects",
            description = "",
            default     = False
        )

        # bloom_on
        bloom_on= BoolProperty(
            name= "bloom on",
            description= "",
            default= False
        )

        # bloom_fill_edges
        bloom_fill_edges= BoolProperty(
            name= "bloom fill edges",
            description= "",
            default= True
        )

        # bloom_weight
        bloom_weight= FloatProperty(
            name= "bloom weight",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 20
        )

        # bloom_size
        bloom_size= FloatProperty(
            name= "bloom size",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 20
        )

        # bloom_shape
        bloom_shape= FloatProperty(
            name= "bloom shape",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 4
        )

        # bloom_mode
        bloom_mode= EnumProperty(
            name= "bloom mode",
            description= "mode",
            items=(
                ('0', "Image", ""),
                ('1', "Image And Buffer", ""),
                ('2', "Buffer", ""),
            ),
            default= '0'
        )

        # bloom_mask_intensity_on
        bloom_mask_intensity_on= BoolProperty(
            name= "bloom mask intensity on",
            description= "",
            default= False
        )

        # bloom_mask_intensity
        bloom_mask_intensity= FloatProperty(
            name= "bloom mask intensity",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 3
        )

        # bloom_mask_objid_on
        bloom_mask_objid_on= BoolProperty(
            name= "bloom mask objid on",
            description= "",
            default= False
        )

        # bloom_mask_objid
        bloom_mask_objid= IntProperty(
            name= "bloom mask objid",
            description= "",
            min= 0,
            max= 100,
            soft_min= 0,
            soft_max= 10,
            default= 0
        )

        # bloom_mask_mtlid_on
        bloom_mask_mtlid_on= BoolProperty(
            name= "bloom mask mtlid on",
            description= "",
            default= False
        )

        # bloom_mask_mtlid
        bloom_mask_mtlid= IntProperty(
            name= "bloom mask mtlid",
            description= "",
            min= 0,
            max= 100,
            soft_min= 0,
            soft_max= 10,
            default= 0
        )

        # glare_on
        glare_on= BoolProperty(
            name= "glare on",
            description= "",
            default= False
        )

        # glare_fill_edges
        glare_fill_edges= BoolProperty(
            name= "glare fill edges",
            description= "",
            default= True
        )

        # glare_weight
        glare_weight= FloatProperty(
            name= "glare weight",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 50
        )

        # glare_size
        glare_size= FloatProperty(
            name= "glare size",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 20
        )

        # glare_type
        glare_type= EnumProperty(
            name= "glare type",
            description= "",
            items=(
                ('0', "From Image", ""),
                ('1', "From Render Camera", ""),
                ('2', "From Camera Params", ""),
            ),
            default= '0'
        )

        # glare_mode
        glare_mode= EnumProperty(
            name= "glare mode",
            description= "mode",
            items=(
                ('0', "Image", ""),
                ('1', "Image And Buffer", ""),
                ('2', "Buffer", ""),
            ),
            default= '0'
        )

        # glare_image_path
        glare_image_path= StringProperty(
            name= "glare image path",
            description= "",
            subtype='FILE_PATH',
            default= ""
        )

        # glare_obstacle_image_path
        glare_obstacle_image_path= StringProperty(
            name= "glare obstacle image path",
            description= "",
            subtype='FILE_PATH',
            default= ""
        )

        # glare_diffraction_on
        glare_diffraction_on= BoolProperty(
            name= "glare diffraction on",
            description= "",
            default= False
        )

        # glare_use_obstacle_image
        glare_use_obstacle_image= BoolProperty(
            name= "glare use obstacle image",
            description= "",
            default= False
        )

        # glare_cam_blades_on
        glare_cam_blades_on= BoolProperty(
            name= "glare cam blades on",
            description= "",
            default= True
        )

        # glare_cam_num_blades
        glare_cam_num_blades= IntProperty(
            name= "glare cam num blades",
            description= "",
            min= 0,
            max= 100,
            soft_min= 0,
            soft_max= 10,
            default= 6
        )

        # glare_cam_rotation
        glare_cam_rotation= FloatProperty(
            name= "glare cam rotation",
            description= "Rotation in degrees from 0.0 - 360.0",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 0
        )

        # glare_cam_fnumber
        glare_cam_fnumber= FloatProperty(
            name= "glare cam fnumber",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 8
        )

        # glare_mask_intensity_on
        glare_mask_intensity_on= BoolProperty(
            name= "glare mask intensity on",
            description= "",
            default= False
        )

        # glare_mask_intensity
        glare_mask_intensity= FloatProperty(
            name= "glare mask intensity",
            description= "",
            min= 0.0,
            max= 100.0,
            soft_min= 0.0,
            soft_max= 10.0,
            precision= 3,
            default= 3
        )

        # glare_mask_objid_on
        glare_mask_objid_on= BoolProperty(
            name= "glare mask objid on",
            description= "",
            default= False
        )

        # glare_mask_objid
        glare_mask_objid= IntProperty(
            name= "glare mask objid",
            description= "",
            min= 0,
            max= 100,
            soft_min= 0,
            soft_max= 10,
            default= 0
        )

        # glare_mask_mtlid_on
        glare_mask_mtlid_on= BoolProperty(
            name= "glare mask mtlid on",
            description= "",
            default= False
        )

        # glare_mask_mtlid
        glare_mask_mtlid= IntProperty(
            name= "glare mask mtlid",
            description= "",
            min= 0,
            max= 100,
            soft_min= 0,
            soft_max= 10,
            default= 0
        )

        # interactive
        interactive= BoolProperty(
            name= "interactive",
            description= "",
            default= True
        )

    bpy.utils.register_class(SettingsVFB)

    rna_pointer.SettingsVFB = bpy.props.PointerProperty(
        name        = "SettingsVFB",
        type        =  SettingsVFB,
        description = "SettingsVFB"
    )


def write(bus):
    ofile = bus['files']['scene']
    scene = bus['scene']

    rna_pointer = getattr(scene.vray, ID)

    if not rna_pointer.use:
        return

    ofile.write("\n%s %s {" % (ID, ID))
    for param in PARAMS:
        value = getattr(rna_pointer, param)
        ofile.write("\n\t%s=%s;"%(param, p(value)))
    ofile.write("\n}\n")
