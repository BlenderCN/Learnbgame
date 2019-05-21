"""BlenderFDS, simplify Blender interface at start"""

import bpy
from bpy.types import Panel, Header, Menu

DEBUG = False

def less_space_properties():
    """Simplify SpaceProperties header (less contexts)"""

    print("BFDS: Simplify SpaceProperties header")

    sp_items = (
        ('SCENE','Scene','Scene','SCENE_DATA',1),
        ('OBJECT','Object','Object','OBJECT_DATA',3),
        ('MATERIAL','Material','Material','MATERIAL',5),
        ('MODIFIER','Modifiers','Object modifiers','MODIFIER',10),
    )

    def sp_item_update(self, context):
        if self.bf_sp_context == context.space_data.context: return # no update needed, also for second update
        # print(self.bf_sp_context, context.space_data.context)
        for trial in (self.bf_sp_context,'OBJECT','MATERIAL','SCENE'):  # try several ordered choices
            try: context.space_data.context = trial
            except TypeError: continue
            else:
                self.bf_sp_context = trial
                break

    # Add bf_sp_context 
    bpy.types.WindowManager.bf_sp_context = bpy.props.EnumProperty(items=sp_items, update=sp_item_update)

    # Rewrite the PROPERTIES_HT_header draw method
    def PROPERTIES_HT_header_draw(self, context):
        layout = self.layout
        row = layout.row()
        row.template_header()
        row.prop(context.window_manager, "bf_sp_context", expand=True, icon_only=True)

    bpy.types.PROPERTIES_HT_header.draw = PROPERTIES_HT_header_draw

def header_draw(self, context):
    """Used to rewire header draw."""
    layout = self.layout
    row = layout.row(align=True)
    row.template_header()

def unregister_unused_classes():
    """Unregister unused classes, kill unused headers (eg. panels)"""

    print("BFDS: Unregister unused classes")
 
    # Init
    always_allowed_bl_space_type = (
        "TEXTEDITOR", "TEXT_EDITOR", "USER_PREFERENCES", "CONSOLE",
        "FILE_BROWSER", "INFO", "OUTLINER",
    )
    always_allowed_panels = (
        'Panel', 'SCENE_PT_BF_DUMP', 'SCENE_PT_BF_HEAD', 'SCENE_PT_BF_MISC',
        'SCENE_PT_BF_REAC', 'SCENE_PT_BF_TIME', 'OBJECT_PT_BF', 'MATERIAL_PT_BF',
        'DATA_PT_modifiers', 'RENDER_PT_render',
    )

    not_allowed_panels = ( # FIXME investigate why they are still there
        "VIEW3D_PT_view3d_shading", "VIEW3D_PT_view3d_motion_tracking",
        "VIEW3D_PT_transform_orientations", "VIEW3D_PT_view3d_name",
        "VIEW3D_PT_context_properties", "CyclesScene_PT_simplify",
        "CyclesObject_PT_ray_visibility", "CyclesObject_PT_motion_blur",
        "Cycles_PT_context_material", "CyclesMaterial_PT_preview", 
        "CyclesMaterial_PT_settings", "CyclesMaterial_PT_surface",
    )

    always_allowed_headers = (
        'Header', 'PROPERTIES_HT_header', 'VIEW3D_HT_header',
    )

    allowed_bl_space_type = "PROPERTIES", "VIEW_3D"
    allowed_bl_category = (
        "Tools", "Create", "Relations", "Options", "Grease Pencil",
    )
    allowed_bl_region_type = "UI"

    # Search and unregister
    for bpy_type in dir(bpy.types):
        bpy_type_class = getattr(bpy.types, bpy_type)

        # Get class attributes
        bl_space_type = getattr(bpy_type_class, "bl_space_type", None)    
        bl_context = getattr(bpy_type_class, "bl_context", None)
        bl_category = getattr(bpy_type_class, "bl_category", None)
        bl_region_type = getattr(bpy_type_class, "bl_region_type", None)

        # Always ok
        if bl_space_type in always_allowed_bl_space_type: continue

        # Is it a panel?
        if issubclass(bpy_type_class, Panel):
            # Is it allowed?
            if bpy_type in always_allowed_panels: continue
            elif bpy_type in not_allowed_panels: pass
            elif bl_space_type in allowed_bl_space_type:
                if bl_category and bl_category in allowed_bl_category: continue
                elif bl_region_type and bl_region_type in allowed_bl_region_type: continue
            # Unregister it            
            if DEBUG: print("BFDS: Remove panel:", bl_space_type, bl_region_type, bl_context, bl_category, bpy_type)
            bpy.utils.unregister_class(bpy_type_class)
            continue
            
        # Is it an header?
        elif issubclass(bpy_type_class, Header):
            if bpy_type in always_allowed_headers: continue
            # Rewire it
            if DEBUG: print("BFDS: Rewire header:", bl_space_type, bl_region_type, bl_context, bl_category, bpy_type)
            bpy_type_class.draw = header_draw
            continue

# Rewrite help menu

class INFO_MT_help(Menu):
    bl_label = "Help"

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.url_open", text="Blender Manual", icon='HELP').url = "http://www.blender.org/manual"
        layout.operator("wm.url_open", text="BlenderFDS Manual", icon='HELP').url = "https://code.google.com/p/blenderfds/wiki/Wiki_Home"
        layout.separator()

        layout.operator("wm.url_open", text="Blender Website", icon='URL').url = "http://www.blender.org"
        layout.operator("wm.url_open", text="BlenderFDS Website", icon='URL').url = "http://www.blenderfds.org"

# Rewrite add menu

class INFO_MT_add(Menu):
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_REGION_WIN'
        layout.menu("INFO_MT_mesh_add", icon='OUTLINER_OB_MESH')
        layout.operator("object.empty_add", text="Empty", icon='OUTLINER_OB_EMPTY')

# Rewrite tools > create > add mesh

def VIEW3D_PT_tools_add_object_draw(self, context):
    layout = self.layout

    col = layout.column(align=True)
    self.draw_add_mesh(col, label=True)

bpy.types.VIEW3D_PT_tools_add_object.draw = VIEW3D_PT_tools_add_object_draw

