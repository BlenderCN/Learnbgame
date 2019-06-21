'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
"""
Simple structured Delaunay triangulation in 2D with Bowyer-Watson algorithm.
Written by Jose M. Espadero ( http://github.com/jmespadero/pyDelaunay2D )
Based on code from Ayron Catteau. Published at http://github.com/ayron/delaunay
Just pretend to be simple and didactic. The only requisite is numpy.
Robust checks disabled by default. May not work in degenerate set of points.
"""

import bpy
from .utils.helper_functions import addon_name_lowercase
# from bpy.utils import register_class, unregister_class


class GarmentToolPreferences(bpy.types.AddonPreferences):
    bl_idname = 'garment_tool'
    update_exist: bpy.props.BoolProperty(name="Update Exist", description="There is new GroupPro update",  default=False)
    update_text: bpy.props.StringProperty(name="Update text",  default='')

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        box = layout.box()

        col = box.column()
        sub_row = col.row(align=True)
        sub_row.operator(addon_name_lowercase()+".check_for_update")
        sub_row.label(text=self.update_text)
        sub_row.separator()
        sub_row = col.row(align=True)
        if self.update_exist:
            sub_row.operator(addon_name_lowercase()+".update_addon", text='Install latest version').reinstall = False
        else:
            sub_row.operator(addon_name_lowercase()+".update_addon", text='Reinstall current version').reinstall = True
        sub_row.operator(addon_name_lowercase()+".rollback_addon")

 


def sewing_callback(scene, context):
    items = [
        ('LOC', "Location", ""),
        ('ROT', "Rotation", ""),
        ('SCL', "Scale", ""),
    ]
    ob = context.object
    if ob is not None:
        if ob.type == 'LAMP':
            items.append(('NRG', "Energy", ""))
            items.append(('COL', "Color", ""))

    return items


class SegmentIndexCollection(bpy.types.PropertyGroup):
    def test_obj_is_curve (self, context):
        if self.source_obj and self.source_obj.type != 'CURVE':
            self.source_obj = None
        if self.target_obj and self.target_obj.type != 'CURVE':
            self.target_obj = None
        
    source_obj: bpy.props.PointerProperty(name='Stitch source',  description='Stitch source', type=bpy.types.Object,  update=test_obj_is_curve)
    target_obj: bpy.props.PointerProperty(name='Stitch Target',  description='Stitch Target', type=bpy.types.Object, update=test_obj_is_curve)
    segment_id_from: bpy.props.IntProperty(name='Segment id', default=0, min=0, soft_max=32,  description='Seweing source segment ID')
    segment_id_to: bpy.props.IntProperty(name='Segment id', default=0, min=0, soft_max=32,  description='Seweing target segment ID')
    flip: bpy.props.BoolProperty(name='Flip', default=False, description='Flip sweing')


# register_class(GTOOL_PG_SegmentIndexCollection)

ITEMS_PATTERNS = [] #for keeping reference in python to items - fix enum bug in blender
ITEMS_STITCHES = [] #for keeping reference in python to items - fix enum bug in blender

class ClothPair(bpy.types.PropertyGroup):
    def test_obj_is_curve (self, context):
        garment = self.id_data.path_resolve(self.path_from_id().split('.')[0])
        current_garment_mesh = self.id_data.path_resolve(self.path_from_id()) # we skipp checking self with itself
        if self.pattern_obj.type != 'CURVE':
            self.pattern_obj = None
            print('Object is not curve')
            
        for pattern in garment.sewing_patterns:
            if pattern != current_garment_mesh and self.pattern_obj == pattern.pattern_obj:
                self.pattern_obj = None
                print('Pattern is already assigned to garment')
                break
        global ITEMS_PATTERNS
        ITEMS_PATTERNS.clear()
        for pattern in garment.sewing_patterns:
            if pattern.pattern_obj is not None:
                ITEMS_PATTERNS.append((pattern.pattern_obj.name, pattern.pattern_obj.name, ""))

        total_point_count = 0
        for pattern in garment.sewing_patterns:
            if pattern.pattern_obj:
                area = pattern.pattern_obj.dimensions.x * pattern.pattern_obj.dimensions.y
                total_point_count += area * garment.cloth_res * garment.cloth_res
        garment.output_vert_count = total_point_count

    pattern_obj: bpy.props.PointerProperty(name="Pattern", type=bpy.types.Object, update=test_obj_is_curve)
    add_lattice: bpy.props.BoolProperty(name="Generate Lattice", default=False, description="Generate Lattice")
    add_bend_deform: bpy.props.BoolProperty(name="Generate Bend Deform", default=False, description="Generate Bend Deform")

class PocketCurve(bpy.types.PropertyGroup):
    def pattern_sewing(self, context):
        global ITEMS_STITCHES
        if self.pocketObj is not None and len(self.pocketObj.data.splines[0].bezier_points) > 0:
            ITEMS_STITCHES.clear()
            for i in range(len(self.pocketObj.data.splines[0].bezier_points)):
                ITEMS_STITCHES.append((str(i), str(i), ""))
        return ITEMS_STITCHES
    pocketObj: bpy.props.PointerProperty(name="Pocket pattern", type=bpy.types.Object)
    target_pattern: bpy.props.PointerProperty(name="Target pattern", type=bpy.types.Object)
    pocket_sewing: bpy.props.EnumProperty(
        name="pocket sewing", description="pocket sewing", items=pattern_sewing, options={"ENUM_FLAG"})


class GarmentPin(bpy.types.PropertyGroup):
    source_obj: bpy.props.PointerProperty(name='Pin source',  description='Pin source', type=bpy.types.Object)
    target_obj: bpy.props.PointerProperty(name='Pin Target',  description='Pin Target', type=bpy.types.Object)
    source_co: bpy.props.FloatVectorProperty(name="", description="", default=(0.0, 0.0, 0.0))
    target_co: bpy.props.FloatVectorProperty(name="", description="", default=(0.0, 0.0, 0.0))


class MergeVertexGroups(bpy.types.PropertyGroup):
    def pattern_items(self, context):
        # parent_garment_idx = int(self.path_from_id()[19]) #gives cloth_garment_data[0].generated_vgroups[1]
        global ITEMS_PATTERNS
        garment = self.id_data.path_resolve(self.path_from_id().split('.')[0])
        # if len(garment.sewing_patterns) != len(ITEMS_PATTERNS): #WTF. why it was here
        ITEMS_PATTERNS.clear()
        for pattern in garment.sewing_patterns:
            if pattern.pattern_obj is not None:
                ITEMS_PATTERNS.append((pattern.pattern_obj.name, pattern.pattern_obj.name, ""))
        return ITEMS_PATTERNS

    name: bpy.props.StringProperty(name="Group", description="New vertex group name", default='cloth_vg')
    vgroups_patterns: bpy.props.EnumProperty(name="Choose Patterns", description="Choose patterns that will receive this vertex group", items=pattern_items, options={"ENUM_FLAG"})
    add_bend_deform: bpy.props.BoolProperty(name="Generate Bend Deform", default=False, description="Generate Bend Deform")
    add_lattice: bpy.props.BoolProperty(name="Generate Lattice", default=False, description="Generate Lattice")
    # add_bend_deform: bpy.props.BoolProperty(name="Add Bend Deform", default=False, description="Add Bend Deform")


class SceneObjectGarment(bpy.types.PropertyGroup):
    def check_res(self,context):
        total_point_count = 0
        for pattern in self.sewing_patterns:
            if pattern.pattern_obj:
                area = pattern.pattern_obj.dimensions.x * pattern.pattern_obj.dimensions.y
                total_point_count += area * self.cloth_res * self.cloth_res 
        self.output_vert_count = total_point_count

    name: bpy.props.StringProperty(name="Garment name", default="Shirt")
    tri_convert_ok: bpy.props.BoolProperty(name="Last tri conversion went ok?", default=True)
    expand_garment: bpy.props.BoolProperty(name="Expand", default=True, description="Expand")
    smooth_strength: bpy.props.IntProperty(name="Smooth", description="Smoothing applied to garment, when converting to mesh (default-10 works best)", default=10, min=0, max=10, step=1)
    sim_time: bpy.props.IntProperty(name="Sim time", description="Sim time", default=50, min=10, soft_max=150, step=1)
    output_vert_count: bpy.props.IntProperty(name="Predicted cloth point count", description='Predicted cloth point count' )
    cloth_res: bpy.props.IntProperty(name="Cloth Resolution", description='Triangulation resolution - N points / meter. \
        \nVery low values often give corrupted triangulation result \
        \nTriangle icons - warns that ouput polycount is high (converting to mesh may take some time)', default=25, min=2, soft_max=80, update = check_res)
    triangulation_method: bpy.props.EnumProperty(name="Triangulation Method", default="FAST",
                                      items=(("FAST", "Fast (LQ)", "2x Faster but sometimes give corrupted triangulation"),
                                             ("SLOW", "Slower (HQ)", "Slower but more stable than 'Fast'"),
                                            #  ("EDGE", "Edge wire", "Wont work on thin ribbons, but other that that it dosent break geo")
                                             ))
    merge_patterns: bpy.props.BoolProperty(name='Merge Generated Patterns', description='Merge Generated Patterns and sewing after convertign them to meshes',  default=True)
    expand_patterns:  bpy.props.BoolProperty(name='Expand patterns', default=True, description='Expand')
    sewing_patterns: bpy.props.CollectionProperty(name='Sewing Patterns', type=ClothPair)
    expand_pockets:  bpy.props.BoolProperty(
        name='Expand Pocekts', default=False, description='Project selected 2D curve on target pattern. Target pattern has to be member garment patterns list')
    enable_pockets:  bpy.props.BoolProperty(name='Enable Pockets', default=True, description='Enable Pockets')
    pockets: bpy.props.CollectionProperty(type=PocketCurve)
    expand_pins:  bpy.props.BoolProperty(
        name='Expand Pins', default=False, description='Connect two points on pattern surface with edge. Works only on 2D curve patters, are members garment patterns list')
    enable_pins:  bpy.props.BoolProperty(name='Enable pins', default=True, description='Enable pins')
    pins: bpy.props.CollectionProperty(type=GarmentPin)
    expand_vgroups:  bpy.props.BoolProperty(name='Expand vertex groups', default=False, description='Assing vertex group, to selected garment patterns.')
    generated_vgroups: bpy.props.CollectionProperty(type=MergeVertexGroups)
    new_vgroups: bpy.props.CollectionProperty(type=MergeVertexGroups)
    expand_sewings:  bpy.props.BoolProperty(name='Expand sewings', default=False, description='Stitches define edges that will connect garment patterns together.')
    garment_sewings: bpy.props.CollectionProperty(type=SegmentIndexCollection)
    add_border_mask:  bpy.props.BoolProperty(name='Create Border Mask', default=True, description='Generate border vertex group mask')
    add_non_border_mask:  bpy.props.BoolProperty(name='Create non Border Mask', default=True, description='Generate non border vertex group Mask')

# bpy.utils.register_class(GTOOL_PG_ObjectGarment)

# bpy.types.Scene.cloth_garment_data = bpy.props.CollectionProperty(type=GTOOL_PG_ObjectGarment)
