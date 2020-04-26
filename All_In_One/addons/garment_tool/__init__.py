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

#TODO: ability to pull verts? By hooks? Dependency loop?
#TODO: make pattern from flattened faces... (do uv, shake key, triangulate, defrom back)

bl_info = {
    "name": "Garment Tool",
    "description": "Garment making tool for Blender",
    "author": "Bartosz Styperek",
    "version": (1, 0, 4),
    "blender": (2, 80, 0),
    "location": "Right 3d View Panel -> Garment ",
    "warning": "",
    "wiki_url": "https://joseconseco.github.io/GarmentToolDocs/",
    "tracker_url": "https://discord.gg/cxZDbqH",
    "category": "Object",
}
# load and reload submodules
##################################
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python37\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb


if "bpy" in locals():
    import importlib
    importlib.reload(helper_functions)
    importlib.reload(fsm_oper)
    importlib.reload(bind_mesh)
    importlib.reload(cloth_properties)
    importlib.reload(triangulate_curve_pattern)
    importlib.reload(cloth_ui)
    importlib.reload(mesh_cloth_functions)
    importlib.reload(edit_sewing)
    importlib.reload(edit_pockets)
    importlib.reload(edit_pins)
    importlib.reload(spline_modeling_tools)
    importlib.reload(update_addon)
else:
    from .utils import helper_functions
    from .utils import fsm_oper
    from . import bind_mesh
    from . import cloth_properties
    from . import triangulate_curve_pattern
    from . import cloth_ui
    from . import mesh_cloth_functions
    from . import edit_sewing
    from . import edit_pockets
    from . import edit_pins
    from . import spline_modeling_tools
    from . import update_addon



import bpy
from . import auto_load

auto_load.init()


from .cloth_properties import SceneObjectGarment
from .bind_mesh import ProjectObjectProps

def develte_vert_menu(self, context):
    self.layout.separator()
    self.layout.operator("curve.curve_del_vert_gt")

def subdivide_segment_menu(self, context):
    self.layout.separator()
    self.layout.operator("curve.curve_subdivide_gt")
    self.layout.operator('curve.curve_split_gm')

    
def register():
    auto_load.register()
    bpy.types.Scene.cloth_garment_data = bpy.props.CollectionProperty(type=SceneObjectGarment)
    bpy.types.Scene.shape_project = bpy.props.PointerProperty(type=ProjectObjectProps)
    bpy.types.VIEW3D_MT_edit_curve_delete.append(develte_vert_menu)
    bpy.types.VIEW3D_MT_edit_curve_context_menu.append(subdivide_segment_menu)


def unregister():
    auto_load.unregister()
    del bpy.types.Scene.cloth_garment_data
    del bpy.types.Scene.shape_project
    bpy.types.VIEW3D_MT_edit_curve_delete.remove(develte_vert_menu)
    bpy.types.VIEW3D_MT_edit_curve_context_menu.remove(subdivide_segment_menu)



