'''
Copyright (C) 2015 Patrick Moore
patrick.moore.bu@gmail.com


Created by Patrick Moore

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

bl_info = {
    "name":        "Cut Mesh",
    "description": "Tools for cutting and trimming mesh objects",
    "author":      "Patrick Moore",
    "version":     (0, 0, 1),
    "blender":     (2, 7, 8),
    "location":    "View 3D > Tool Shelf",
    "warning":     "",  # used for warning icon and text in addons panel
    "wiki_url":    "https://github.com/patmo141/cut_mesh/wiki",
    "tracker_url": "https://github.com/patmo141/cut_mesh/issues",
    "category":    "3D View"
    }

# Blender imports
import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty
#TODO Preferences
#TODO Menu

#Tools
# from .op_polytrim.polytrim_modal import CutMesh_Polytrim
from .op_polytrim.polytrim import CutMesh_Polytrim
from .op_poly_geopath.p_geopath_modal import CutMesh_PGeopath
from .op_geopath.geopath_modal import CGC_Geopath
from .op_slice.slice_modal import CGC_Slice
from .op_triangle_fill import TriangleFill
from .polytrim_instance import Custom_Polytrim
from .convenience import CUTMESH_OT_delete_strokes, CUTMESH_OT_hide_strokes, CUTMESH_OT_join_strokes
from . import ambient_occlusion

#addon preferences
class CutMeshPreferences(AddonPreferences):
    bl_idname = __name__

    addons = bpy.context.user_preferences.addons
    
    #Segmentation Editor Behavior
    spline_preview_tess = IntProperty(name = 'Spline Teseslation', default = 20, min = 3, max = 100)
    sketch_fit_epsilon = FloatProperty(name = 'Sketch Epsilon', default = 0.25, min = 0.001, max = 10)
    patch_boundary_fit_epsilon = FloatProperty(name = 'Boundary Epsilon', default = 0.35, min = .001, max = 10)
    spline_tessellation_epsilon = FloatProperty(name = 'Spline Epsilon', default = 0.1, min = .001, max = 10)
    
    destructive = EnumProperty(name = 'Geometry Mode', items = [('DESTRUCTIVE', 'DESTRUCTIVE', 'DESTRUCTIVE'),('NON_DESTRUCTIVE','NON_DESTRUCTIVE','NON_DESTRUCTIVE')], default = 'DESTRUCTIVE')
    #2D Interaction Behavior
    non_man_snap_pxl_rad = IntProperty(name = 'Snap Radius Pixel', default = 20, min =5, max = 150)
    sel_pxl_rad = IntProperty(name = 'Select Radius Pixel', default = 10, min = 3, max = 100)
    loop_close_pxl_rad = IntProperty(name = 'Select Radius Pixel', default = 10, min = 3, max = 100)

    #Menu Colors
    menu_bg_color = FloatVectorProperty(name="Mennu Backgrounng Color", description="FLoating Menu color", min=0, max=1, default=(.3,.3,.3), subtype="COLOR")
    menu_border_color = FloatVectorProperty(name="Menu Border Color", description="FLoating menu border colro", min=0, max=1, default=(.1,.1,.1), subtype="COLOR")
    deact_button_color = FloatVectorProperty(name="Button Color", description="Deactivated button color", min=0, max=1, default=(.5,.5,.5), subtype="COLOR")
    act_button_color = FloatVectorProperty(name="Active Button Color", description="Activated button color", min=0, max=1, default=(.2,.2,1), subtype="COLOR")
    
    
    #Geometry Colors
    act_point_color = FloatVectorProperty(name="Active Point Color", description="Selected/Active point color", min=0, max=1, default=(.2,.7,.2), subtype="COLOR")
    act_patch_color = FloatVectorProperty(name="Active Patch Color", description="Selected/Active patch color", min=0, max=1, default=(.2,.7,.2), subtype="COLOR")
    spline_default_color = FloatVectorProperty(name="Spline Color", description="Spline color", min=0, max=1, default=(.2,.2,.7), subtype="COLOR")
    hint_color = FloatVectorProperty(name="Hint Color", description="Hint Geometry color", min=0, max=1, default=(.5,1,.5), subtype="COLOR")
    bad_segment_color = FloatVectorProperty(name="Active Button Color", description="Activated button color", min=0, max=1, default=(1,.6,.2), subtype="COLOR")
    bad_segment_hint_color = FloatVectorProperty(name="Bad Segment Hint", description="Bad segment hint color", min=0, max=1, default=(1,0,0), subtype="COLOR")
    
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Cut Mesh Preferences")
        #layout.prop(self, "mat_lib")
        
        
        

        ## Visualization 
        row = layout.row(align=True)
        row.label("Visualization Settings")

        row = layout.row(align=True)
        row.prop(self, "menu_bg_color")
        row.prop(self, "menu_border_color")
        row.prop(self, "deact_button_color")
        row.prop(self, "act_button_color")
        
        
        ## Operator Defaults
        #box = layout.box().column(align=False)
        row = layout.row()
        row.label(text="Operator Defaults")
        
        ##### Fit and Thickness ####
        row = layout.row()
        row.label('Thickness, Fit and Retention')
        row = layout.row()
        row.prop(self, "def_shell_thickness")
        row.prop(self, "def_passive_radius")
        row.prop(self, "def_blockout_radius")
    
def register(): 
    bpy.utils.register_class(CutMeshPreferences) #TODO
    #bpy.utils.register_class(CutMesh_panel)  #TODO
    #bpy.utils.register_class(CutMesh_menu)  #TODO
    ambient_occlusion.register()
    bpy.utils.register_class(CutMesh_Polytrim)
    bpy.utils.register_class(Custom_Polytrim)
    bpy.utils.register_class(CGC_Geopath)
    bpy.utils.register_class(CGC_Slice)
    bpy.utils.register_class(TriangleFill)
    bpy.utils.register_class(CutMesh_PGeopath)
    bpy.utils.register_class(CUTMESH_OT_delete_strokes)
    bpy.utils.register_class(CUTMESH_OT_hide_strokes)
    bpy.utils.register_class(CUTMESH_OT_join_strokes)
    
def unregister():
    bpy.utils.register_class(CutMeshPreferences)  #TODO
    #bpy.utils.register_class(CutMesh_panel)  #TODO
    #bpy.utils.register_class(CutMesh_menu)  #TODO
    ambient_occlusion.unregister()
    bpy.utils.unregister_class(CutMesh_Polytrim)
    bpy.utils.unregister_class(Custom_Polytrim)
    bpy.utils.unregister_class(CGC_Geopath)
    bpy.utils.unregister_class(CGC_Slice)
    bpy.utils.unregister_class(TriangleFill)
    bpy.utils.unregister_class(CutMesh_PGeopath)
    bpy.utils.unregister_class(CUTMESH_OT_delete_strokes)
    bpy.utils.unregister_class(CUTMESH_OT_hide_strokes)
    bpy.utils.unregister_class(CUTMESH_OT_join_strokes)