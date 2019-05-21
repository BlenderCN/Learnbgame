'''
Created by Marcin Zielinski, Doug Hammond, Thomas Ludwig, Nicholas Chapman, Yves Colle

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
    "name": "Blendigo - Indigo Exporter",
    "description": "This Addon will allow you to render your scenes with the Indigo render engine.",
    "author": "Glare Technologies Ltd.",
    "version": (4, 2, 3),
    "blender": (2, 78, 0),
    "location": "View3D",
    "wiki_url": "",
    "category": "Learnbgame"
}


import bpy

# updater ops import, all setup in this file
from . import addon_updater_ops

# demo bare-bones preferences
class IndigoPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # addon updater preferences

    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
        )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
        )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    def draw(self, context):
        layout = self.layout
        # col = layout.column() # works best if a column, or even just self.layout
        mainrow = layout.row()
        col = mainrow.column()

        # updater draw function
        # could also pass in col as third arg
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # col.operator("wm.url_open","Open webpage ").url=addon_updater_ops.updater.website

# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# register
##################################

import traceback

def register():
    # addon updater code and configurations
    # in case of broken version, try to register the updater first
    # so that users can revert back to a working version
    addon_updater_ops.register(bl_info)
    from .addon_updater import Updater as updater
    updater.user = "glaretechnologies"
    updater.repo = "blendigo"
    updater.addon = "blendigo"
    # updater.include_branche_list = ["master", "dev"]
    updater.subfolder_path = "sources/indigo_exporter/"

    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    
    from . properties.render_settings import Indigo_Engine_Properties
    bpy.types.Scene.indigo_engine = bpy.props.PointerProperty(name="Indigo Engine Properties", type = Indigo_Engine_Properties)
    
    from . properties.camera import Indigo_Camera_Properties
    bpy.types.Camera.indigo_camera = bpy.props.PointerProperty(name="Indigo Camera Properties", type = Indigo_Camera_Properties)
    
    from . properties.environment import Indigo_Lightlayers_Properties
    bpy.types.Scene.indigo_lightlayers = bpy.props.PointerProperty(name="Indigo Lightlayers Properties", type = Indigo_Lightlayers_Properties)
    
    from . properties.lamp import Indigo_Lamp_Sun_Properties, Indigo_Lamp_Hemi_Properties
    bpy.types.Lamp.indigo_lamp_sun = bpy.props.PointerProperty(name="Indigo Lamp Sun Properties", type = Indigo_Lamp_Sun_Properties)
    bpy.types.Lamp.indigo_lamp_hemi = bpy.props.PointerProperty(name="Indigo Lamp Hemi Properties", type = Indigo_Lamp_Hemi_Properties)
    
    from . properties.material import Indigo_Material_Properties, Indigo_Texture_Properties
    bpy.types.Material.indigo_material = bpy.props.PointerProperty(name="Indigo Material Properties", type = Indigo_Material_Properties)
    bpy.types.Texture.indigo_texture = bpy.props.PointerProperty(name="Indigo Texture Properties", type = Indigo_Texture_Properties)
    
    from . properties.medium import Indigo_Material_Medium_Properties
    bpy.types.Scene.indigo_material_medium = bpy.props.PointerProperty(name="Indigo Material Medium Properties", type = Indigo_Material_Medium_Properties)
    bpy.types.Material.indigo_material_medium = bpy.props.PointerProperty(name="Indigo Material Medium Properties", type = Indigo_Material_Medium_Properties)
    
    from . properties.object import Indigo_Mesh_Properties
    bpy.types.Mesh.indigo_mesh = bpy.props.PointerProperty(name="Indigo Mesh Properties", type = Indigo_Mesh_Properties)
    bpy.types.SurfaceCurve.indigo_mesh = bpy.props.PointerProperty(name="Indigo Mesh Properties", type = Indigo_Mesh_Properties)
    bpy.types.TextCurve.indigo_mesh = bpy.props.PointerProperty(name="Indigo Mesh Properties", type = Indigo_Mesh_Properties)
    bpy.types.Curve.indigo_mesh = bpy.props.PointerProperty(name="Indigo Mesh Properties", type = Indigo_Mesh_Properties)
    
    from . properties.tonemapping import Indigo_Tonemapping_Properties
    bpy.types.Camera.indigo_tonemapping = bpy.props.PointerProperty(name="Indigo Tonemapping Properties", type = Indigo_Tonemapping_Properties)
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
