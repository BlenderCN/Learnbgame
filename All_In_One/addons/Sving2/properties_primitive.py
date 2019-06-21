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

# <pep8 compliant>

import bpy
from . import sculpty


class PrimitivePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_primitive"
    bl_label = "Primitive Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(self, context):
        return (context.object.prim.type != 'PRIM_TYPE_NONE')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        prim = obj.prim
        prim_type = prim.type[10:]
        advanced = prim_type in ['TORUS', 'TUBE', 'RING']
        layout.prop(prim, 'type')
        if prim_type == 'SCULPT':
            layout.prop(prim, 'sculpt_type')
            row = layout.row()
            row.prop(prim, 'sculpt_invert')
            row.prop(prim, 'sculpt_mirror')
            mesh = obj.data
            if not mesh.uv_textures:
                layout.label("No UV layouts", "ERROR")
            elif 'sculptie' not in mesh.uv_textures:
                layout.label("No 'sculptie' UV layout", "ERROR")
            else:
                uvtex = bpy.context.active_object.data.uv_textures
                if len(uvtex['sculptie'].data):
                    uvface = uvtex['sculptie'].data[0]
                    if uvface.image is None:
                        layout.label(
                            "No image assigned to 'sculptie' UV", "ERROR")
                    else:
                        img = uvface.image
                        x = img.size[0]
                        y = img.size[1]
                        box = layout.box()
                        box.label("Sculpt Map: " + img.name)
                        box.label("Image Size: %s x %s" % (x, y))
                        for i in [3, 2, 1, 0]:
                            box.label("LOD %s: " % (i) + \
                                "%s x %s" % sculpty.lod_size(x, y, i))
                    #layout.template_image(face, 'image', face)
                else:
                    layout.label("Can't display in edit mode", "INFO")
        else:
            layout.prop(prim, 'hole_shape')
            split = layout.split(0.33)
            split.label("Hollow")
            split.prop(prim, 'hollow', text='')
            split = layout.split(0.33)
            split.label("Path Cut")
            col = split.column()
            col.prop(prim, 'cut_start', text='Start')
            col.prop(prim, 'cut_end', text='End')
            if advanced:
                split = layout.split(0.33)
                split.label("Profile Cut")
                col = split.column()
                col.prop(prim, 'profile_cut_start', text='Start')
                col.prop(prim, 'profile_cut_end', text='End')
                split = layout.split(0.33)
                split.label("Hole Size")
                col = split.column()
                col.prop(prim, 'hole_size_x', text='X')
                col.prop(prim, 'hole_size_y', text='Y')
            if prim_type == 'SPHERE':
                split = layout.split(0.33)
                split.label("Dimple")
                col = split.column()
                col.prop(prim, 'dimple_start', text='Start')
                col.prop(prim, 'dimple_end', text='End')
            else:
                split = layout.split(0.33)
                split.label("Shear")
                col = split.column()
                col.prop(prim, 'shear_x', text='X')
                col.prop(prim, 'shear_y', text='Y')
                split = layout.split(0.33)
                split.label("Taper")
                col = split.column()
                col.prop(prim, 'taper_x', text='X')
                col.prop(prim, 'taper_y', text='Y')
            split = layout.split(0.33)
            split.label("Twist")
            col = split.column()
            col.prop(prim, 'twist_x', text='X')
            col.prop(prim, 'twist_y', text='Y')
            if advanced:
                split = layout.split(0.33)
                split.label("Revolutions")
                split.prop(prim, 'revolutions', text='')
                split = layout.split(0.33)
                split.label("Radius Offset")
                split.prop(prim, 'radius_offset', text='')
                split = layout.split(0.33)
                split.label("Skew")
                split.prop(prim, 'skew', text='')


class PrimitiveSettings(bpy.types.PropertyGroup):
    type = bpy.props.EnumProperty(
        items=(
            ('PRIM_TYPE_NONE', 'None', 'Not a primitive'),
            ('PRIM_TYPE_SCULPT', 'Sculpt', 'Sculpt Primitive'),
            ('PRIM_TYPE_TUBE', 'Tube', 'Tube Primitive'),
            ('PRIM_TYPE_TORUS', 'Torus', 'Torus Primitive'),
            ('PRIM_TYPE_SPHERE', 'Sphere', 'Sphere Primitive'),
            ('PRIM_TYPE_RING', 'Ring', 'Ring Primitive'),
            ('PRIM_TYPE_PRISM', 'Prism', 'Prism Primitive'),
            ('PRIM_TYPE_CYLINDER', 'Cylinder', 'Cylinder Primitive'),
            ('PRIM_TYPE_BOX', 'Box', 'Box Primitive')),
        name="Prim Type",
        description="Primitive Mesh Type",
        default='PRIM_TYPE_NONE')
    sculpt_type = bpy.props.EnumProperty(
        items=(
            ('PRIM_SCULPT_TYPE_TORUS', 'Torus', 'Torus mapping'),
            ('PRIM_SCULPT_TYPE_SPHERE', 'Sphere', 'Spherical mapping'),
            ('PRIM_SCULPT_TYPE_PLANE', 'Plane', 'Planar mapping'),
            ('PRIM_SCULPT_TYPE_CYLINDER', 'Cylinder', 'Cylindrical mapping')),
        name="Sculpt Type",
        description="Sculpt Mapping Type",
        default='PRIM_SCULPT_TYPE_PLANE')
    sculpt_invert = bpy.props.BoolProperty(
        name="Inverted",
        description="Render inside out (invert normals)")
    sculpt_mirror = bpy.props.BoolProperty(
        name="Mirrored",
        description="Render an X axis mirror of the sculpty")
    hole_shape = bpy.props.EnumProperty(
        items=(
            ('PRIM_HOLE_TRIANGLE', 'Triangle', 'Triangular hole'),
            ('PRIM_HOLE_SQUARE', 'Square', 'Square hole'),
            ('PRIM_HOLE_CIRCLE', 'Circle', 'Circular hole'),
            ('PRIM_HOLE_DEFAULT', 'Default', 'Default hole')),
        name="Hole Shape",
        description="Primitive hole shape",
        default='PRIM_HOLE_DEFAULT')
    hollow = bpy.props.FloatProperty(
        name="Hollow",
        description="Hollow center out with hole shape",
        step=1,
        soft_min=0.0,
        soft_max=0.95,
        default=0.0)
    cut_start = bpy.props.FloatProperty(
        name="Path Cut Start",
        description="Path Cut Start (must be 0.05 less than cut end)",
        soft_min=0.0,
        soft_max=1.0,
        default=0.0)
    cut_end = bpy.props.FloatProperty(
        name="Path Cut End",
        description="Path Cut End",
        soft_min=0.0,
        soft_max=1.0,
        default=1.0)
    profile_cut_start = bpy.props.FloatProperty(
        name="Profile Cut Start",
        description="Profile Cut Start (must be 0.05 less than cut end)",
        soft_min=0.0,
        soft_max=1.0,
        default=0.0)
    profile_cut_end = bpy.props.FloatProperty(
        name="Profile Cut End",
        description="Profile Cut End",
        soft_min=0.0,
        soft_max=1.0,
        default=1.0)
    dimple_start = bpy.props.FloatProperty(
        name="Dimple Start",
        description="Dimple Start (must be 0.05 less than dimple end)",
        soft_min=0.0,
        soft_max=1.0,
        default=0.0)
    dimple_end = bpy.props.FloatProperty(
        name="Dimple End",
        description="Dimple End",
        soft_min=0.0,
        soft_max=1.0,
        default=1.0)
    shear_x = bpy.props.FloatProperty(
        name="Shear X",
        description="Shear X",
        soft_min=-0.5,
        soft_max=0.5,
        default=0.0)
    shear_y = bpy.props.FloatProperty(
        name="Shear Y",
        description="Shear Y",
        soft_min=-0.5,
        soft_max=0.5,
        default=0.0)
    taper_x = bpy.props.FloatProperty(
        name="Taper X",
        description="Taper X",
        soft_min=-1.0,
        soft_max=1.0,
        default=1.0)
    taper_y = bpy.props.FloatProperty(
        name="Taper Y",
        description="Taper Y",
        soft_min=-1.0,
        soft_max=1.0,
        default=1.0)
    # TODO: Twist min and max changes with the prim type
    # -180 to 180 box, cylinder, prism
    # -360 to 360 sphere, torus, tube, ring
    twist_x = bpy.props.FloatProperty(
        name="Twist X",
        description="Twist X",
        step=100,
        soft_min=-180.0,
        soft_max=180.0,
        default=0.0)
    twist_y = bpy.props.FloatProperty(
        name="Twist Y",
        description="Twist Y",
        step=100,
        soft_min=-180.0,
        soft_max=180.0,
        default=0.0)
    hole_size_x = bpy.props.FloatProperty(
        name="Hole Size X",
        description="Hole Size X",
        soft_min=0.05,
        soft_max=1.0,
        default=1.0)
    hole_size_y = bpy.props.FloatProperty(
        name="Hole Size Y",
        description="Hole Size Y",
        soft_min=0.05,
        soft_max=0.5,
        default=0.5)
    revolutions = bpy.props.FloatProperty(
        name="Revolutions",
        description="Revolutions",
        soft_min=1.0,
        soft_max=4.0,
        default=1.0)
    skew = bpy.props.FloatProperty(
        name="Skew",
        description="Skew",
        soft_min=-0.95,
        soft_max=0.95,
        default=0.0)
    radius_offset = bpy.props.FloatProperty(
        name="Radius Offset",
        description="Radius Offset",
        # TODO: min and max depend on hole_size_y and revolutions
        soft_min=-1.0,
        soft_max=1.0,
        default=0.0)
