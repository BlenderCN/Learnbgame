# Addon Info
bl_info = {
    "name": "Grass Free",
    "description": "Low Poly Grass Models",
    "author": "Wolf",
    "version": (1, 1),
    "blender": (2, 77, 0),
    "location": "View 3D > Tool Shelf",
    "wiki_url": "http://wolfflow.weebly.com/grass.html",
    "tracker_url": "http://wolfflow.weebly.com/grass.html",
    "support": "OFFICIAL",
    "category": "Mesh"
    }


# Import
import os
import re
import bpy
from bpy.props import *
import bpy.utils.previews
from bpy.types import WindowManager


# Append
class OBJECT_OT_AddButton(bpy.types.Operator):
    bl_idname = "add.object"
    bl_label = "Add Object"

    def execute(self, context):
        selected_preview = bpy.data.window_managers["WinMan"].my_previews
        category = context.scene.grass.cat
        
        # Append Particle System
        bpy.ops.wm.append (directory = os.path.join(os.path.dirname(__file__), "Blends" + os.sep + category + ".blend" + os.sep + "ParticleSettings/"), filepath=category + ".blend", filename=selected_preview)

        return{'FINISHED'}


# Update
def update_category(self, context):
    enum_previews_from_directory_items(self, context)


# Drop Down Menu
class Categories(bpy.types.PropertyGroup):
    mode_options = [
        ("Grass", "Grass", '', 0),
        ("Weeds", "Weeds", '', 1)
        ]

    cat = bpy.props.EnumProperty(
        items=mode_options,
        description="Select a Category",
        default="Grass",
        update=update_category
    )


# Generate Previews
def enum_previews_from_directory_items(self, context):
    
    category = context.scene.grass.cat
    
    # Icons Directory
    directory = os.path.join(os.path.dirname(__file__), "Icons" + os.sep + category)

    # EnumProperty Callback
    enum_items = []

    if context is None:
        return enum_items

    wm = context.window_manager
    
    # Get the Preview Collection (defined in register func)
    pcoll = preview_collections["main"]
    
    if directory == pcoll.my_previews_dir:
        return pcoll.my_previews

    print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the Directory for PNG Files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(""):
                image_paths.append(fn)

        # For each image in the directory, load the thumb unless it has already been loaded
        for i, name in enumerate(image_paths):
            # Generate a Thumbnail Preview for a File.
            filepath = os.path.join(directory, name)
            
            if filepath in pcoll:
                enum_items.append((name, name, "", pcoll[filepath].icon_id, i))
            else:
                thumb = pcoll.load(filepath, filepath, 'IMAGE')
                enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory
    return pcoll.my_previews


# Panel
class PreviewsPanel(bpy.types.Panel):
    # Create a Panel in the Tool Shelf
    bl_category = "Grass"
    bl_label = "Grass Free"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    # Draw
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        # Drop Down Menu
        col = layout.column()
        col.prop(context.scene.grass, "cat", text="Category")
        
        # Previews
        row = layout.row()
        row.template_icon_view(wm, "my_previews", show_labels=True)
        
        # Add Button
        row = layout.row()
        row.operator("add.object", icon="ZOOMIN", text="Add")

preview_collections = {}

#####################################################################

# Register
def register():
    
    bpy.utils.register_module(__name__)
   
    WindowManager.my_previews_dir = StringProperty(
            name = "Folder Path",
            subtype = 'DIR_PATH',
            default = "")

    WindowManager.my_previews = EnumProperty(
            items = enum_previews_from_directory_items)

    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()

    preview_collections["main"] = pcoll
    bpy.types.Scene.grass = bpy.props.PointerProperty(type=Categories)


# Unregister
def unregister():

    del WindowManager.my_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.grass


if __name__ == "__main__":
    register()
