#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

# <pep8 compliant>

bl_info = {
    "name": "Export Selected",
    "author": "dairin0d, rking",
    "version": (1, 4),
    "blender": (2, 6, 9),
    "location": "File > Export > Selected",
    "description": "Export selected objects to a chosen format",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"\
                "Scripts/Import-Export/Export_Selected",
    "tracker_url": "http://projects.blender.org/tracker/"\
                   "?func=detail&aid=30942",
    "category": "Learnbgame"
}
#============================================================================#

import bpy

from bpy_extras.io_utils import ExportHelper

join_before_export = {
    "export_mesh.ply",
}

bpy_props = {
    bpy.props.BoolProperty,
    bpy.props.BoolVectorProperty,
    bpy.props.IntProperty,
    bpy.props.IntVectorProperty,
    bpy.props.FloatProperty,
    bpy.props.FloatVectorProperty,
    bpy.props.StringProperty,
    bpy.props.EnumProperty,
    bpy.props.PointerProperty,
    bpy.props.CollectionProperty,
}

def is_bpy_prop(value):
    if isinstance(value, tuple) and (len(value) == 2):
        if (value[0] in bpy_props) and isinstance(value[1], dict):
            return True
    return False

def iter_public_bpy_props(cls, exclude_hidden=False):
    for key in dir(cls):
        if key.startswith("_"):
            continue
        value = getattr(cls, key)
        if is_bpy_prop(value):
            if exclude_hidden:
                options = value[1].get("options", "")
                if 'HIDDEN' in options:
                    continue
            yield (key, value)

def get_op(idname):
    category_name, op_name = idname.split(".")
    category = getattr(bpy.ops, category_name)
    return getattr(category, op_name)

class ToggleObjectMode:
    def __init__(self, mode='OBJECT', undo=False):
        if not isinstance(mode, str):
            mode = ('OBJECT' if mode else None)
        
        obj = bpy.context.object
        if obj and (obj.mode != mode):
            self.mode = mode
        else:
            self.mode = None
        self.undo = undo
    
    def __enter__(self):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            self.global_undo = edit_preferences.use_global_undo
            self.prev_mode = bpy.context.object.mode
            
            if self.prev_mode != self.mode:
                if self.undo is not None:
                    edit_preferences.use_global_undo = self.undo
                bpy.ops.object.mode_set(mode=self.mode)
        
        return self
    
    def __exit__(self, type, value, traceback):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            if self.prev_mode != self.mode:
                bpy.ops.object.mode_set(mode=self.prev_mode)
                edit_preferences.use_global_undo = self.global_undo

def iter_exporters():
    #categories = dir(bpy.ops)
    categories = ["export_anim", "export_mesh", "export_scene"]
    for category_name in categories:
        op_category = getattr(bpy.ops, category_name)
        
        for name in dir(op_category):
            total_name = category_name + "." + name
            
            if total_name == ExportSelected.bl_idname:
                continue
            
            if "export" in total_name:
                op = getattr(op_category, name)
                
                yield total_name, op

class CurrentFormatProperties(bpy.types.PropertyGroup):
    @classmethod
    def _clear_props(cls):
        keys_to_remove = list(cls._keys())
        
        for key in keys_to_remove:
            delattr(cls, key)
        
        CurrentFormatProperties.__dict = None
    
    @classmethod
    def _add_props(cls, template):
        for key, value in iter_public_bpy_props(template):
            setattr(cls, key, value)
        
        CurrentFormatProperties.__dict = {}
        for key in dir(template):
            value = getattr(template, key)
            if is_bpy_prop(value): continue
            CurrentFormatProperties.__dict[key] = value
    
    @classmethod
    def _keys(cls, exclude_hidden=False):
        for kv in iter_public_bpy_props(cls, exclude_hidden):
            yield kv[0]
    
    def __getattr__(self, name):
        return CurrentFormatProperties.__dict[name]
    
    def __setattr__(self, name, value):
        if hasattr(self.__class__, name) and (not name.startswith("_")):
            supercls = super(CurrentFormatProperties, self.__class__)
            supercls.__setattr__(self, name, value)
        else:
            CurrentFormatProperties.__dict[name] = value

class ColladaEmulator:
    # Special case: Collada (built-in) -- has no explicitly defined Python properties
    apply_modifiers = bpy.props.BoolProperty(name="Apply Modifiers", description="Apply modifiers to exported mesh (non destructive)", default=False)
    #export_mesh_type=0 # couldn't find correspondence in the UI
    export_mesh_type_selection = bpy.props.EnumProperty(name="Type of modifiers", description="Modifier resolution for export", default='view', items=[('render', "Render", "Apply modifier's render settings"), ('view', "View", "Apply modifier's view settings")])
    selected = bpy.props.BoolProperty(name="Selection Only", description="Export only selected elements", default=False)
    include_children = bpy.props.BoolProperty(name="Include Children", description="Export all children of selected objects (even if not selected)", default=False)
    include_armatures = bpy.props.BoolProperty(name="Include Armatures", description="Export related armatures (even if not selected)", default=False)
    include_shapekeys = bpy.props.BoolProperty(name="Include Shape Keys", description="Export all Shape Keys from Mesh Objects", default=True)
    deform_bones_only = bpy.props.BoolProperty(name="Deform Bones only", description="Only export deforming bones with armatures", default=False)
    active_uv_only = bpy.props.BoolProperty(name="Only Active UV layer", description="Export textures assigned to the object UV maps", default=False)
    include_uv_textures = bpy.props.BoolProperty(name="Include UV Textures", description="Export textures assigned to the object UV maps", default=False)
    include_material_textures = bpy.props.BoolProperty(name="Include Material Textures", description="Export textures assigned to the object Materials", default=False)
    use_texture_copies = bpy.props.BoolProperty(name="Copy Textures", description="Copy textures to the same folder where .dae file is exported", default=True)
    triangulate = bpy.props.BoolProperty(name="Triangulate", description="Export Polygons (Quads & NGons) as Triangles", default=True)
    use_object_instantiation = bpy.props.BoolProperty(name="Use Object Instances", description="Instantiate multiple Objects from same Data", default=True)
    sort_by_name = bpy.props.BoolProperty(name="Sort by Object name", description="Sort exported data by Object name", default=False)
    #export_transformation_type=0 # couldn't find correspondence in the UI
    export_transformation_type_selection = bpy.props.EnumProperty(name="Transformation Type", description="Transformation type for translation, scale and rotation", default='matrix', items=[('both', "Both", "Use <matrix> AND <translate>, <rotate>, <scale> to specify transformations"), ('transrotloc', "TransLocRot", "Use <translate>, <rotate>, <scale> to specify transformations"), ('matrix', "Matrix", "Use <matrix> to specify transformations")])
    open_sim = bpy.props.BoolProperty(name="Export for OpenSim", description="Compatibility mode for OpenSim and compatible online worlds", default=False)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Export Data Options", icon='MESH_DATA')
        row = box.split(0.6)
        row.prop(self, "apply_modifiers")
        row.prop(self, "export_mesh_type_selection", text="")
        box.prop(self, "selected")
        box.prop(self, "include_children")
        box.prop(self, "include_armatures")
        box.prop(self, "include_shapekeys")
        
        box = layout.box()
        box.label(text="Texture Options", icon='TEXTURE')
        box.prop(self, "active_uv_only")
        box.prop(self, "include_uv_textures")
        box.prop(self, "include_material_textures")
        box.prop(self, "use_texture_copies", text="Copy")
        
        box = layout.box()
        box.label(text="Armature Options", icon='ARMATURE_DATA')
        box.prop(self, "deform_bones_only")
        box.prop(self, "open_sim")
        
        box = layout.box()
        box.label(text="Collada Options", icon='MODIFIER')
        box.prop(self, "triangulate")
        box.prop(self, "use_object_instantiation")
        row = box.split(0.6)
        row.label(text="Transformation Type")
        row.prop(self, "export_transformation_type_selection", text="")
        box.prop(self, "sort_by_name")

class ExportSelected(bpy.types.Operator, ExportHelper):
    '''Export selected objects to a chosen format'''
    bl_idname = "export_scene.selected"
    bl_label = "Export Selected"
    
    filename_ext = bpy.props.StringProperty(
        default="",
        options={'HIDDEN'},
        )
    
    filter_glob = bpy.props.StringProperty(
        default="*.*",
        options={'HIDDEN'},
        )
    
    selection_mode = bpy.props.EnumProperty(
        name="Selection Mode",
        description="Limit/expand the selection",
        default='SELECTED',
        items=[
            ('SELECTED', "Selected", ""),
            ('VISIBLE', "Visible", ""),
            ('ALL', "All", ""),
        ],
        )
    
    include_children = bpy.props.BoolProperty(
        name="Include Children",
        description="Keep children even if they're not selected",
        default=True,
        )
    
    remove_orphans = bpy.props.BoolProperty(
        name="Remove Orphans",
        description="Remove datablocks that have no users",
        default=True,
        )
    
    keep_materials = bpy.props.BoolProperty(
        name="Keep Materials",
        description="Keep Materials",
        default=True,
        )
    
    keep_textures = bpy.props.BoolProperty(
        name="Keep Textures",
        description="Keep Textures",
        default=True,
        )
    
    keep_world_textures = bpy.props.BoolProperty(
        name="Keep World Textures",
        description="Keep World Textures",
        default=False,
        )
    
    object_types = bpy.props.EnumProperty(
        name="Object types",
        description="Object type(s) to export",
        default={'ALL'},
        items=[
            ('ALL', "All", ""),
            ('MESH', "Mesh", ""),
            ('CURVE', "Curve", ""),
            ('SURFACE', "Surface", ""),
            ('META', "Meta", ""),
            ('FONT', "Font", ""),
            ('ARMATURE', "Armature", ""),
            ('LATTICE', "Lattice", ""),
            ('EMPTY', "Empty", ""),
            ('CAMERA', "Camera", ""),
            ('LAMP', "Lamp", ""),
            ('SPEAKER', "Speaker", ""),
        ],
        options={'ENUM_FLAG'},
        )
    
    visible_name = bpy.props.StringProperty(
        name="Visible name",
        description="Visible name",
        options={'HIDDEN'},
        )
    
    format = bpy.props.StringProperty(
        name="Format",
        description="Export format",
        options={'HIDDEN'},
        )
    
    format_props = bpy.props.PointerProperty(
        type=CurrentFormatProperties,
        options={'HIDDEN'},
        )
    
    props_initialized = bpy.props.BoolProperty(
        options={'HIDDEN'},
        default=False,
        )
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.objects) != 0
    
    def fill_props(self):
        if self.props_initialized: return
        
        CurrentFormatProperties._clear_props()
        
        if self.format:
            op = get_op(self.format)
            op_class = type(op.get_instance())
            
            if self.format == "wm.collada_export":
                op_class = ColladaEmulator
            
            CurrentFormatProperties._add_props(op_class)
        else:
            self.visible_name = "Blend"
            self.filename_ext = ".blend"
            self.filter_glob = "*.blend"
        
        self.props_initialized = True
    
    def invoke(self, context, event):
        self.fill_props()
        self.filepath = context.object.name + self.filename_ext
        return ExportHelper.invoke(self, context, event)
    
    def clear_world(self, context):
        bpy.ops.ed.undo_push(message="Delete unselected")
        
        for scene in bpy.data.scenes:
            if scene != context.scene:
                bpy.data.scenes.remove(scene)
        
        scene = context.scene
        
        objs = set()
        
        def add_obj(obj):
            if self.object_types.intersection({'ALL', obj.type}):
                objs.add(obj)
            
            if self.include_children:
                for child in obj.children:
                    add_obj(child)
        
        for obj in scene.objects:
            if (self.selection_mode == 'SELECTED') and obj.select:
                add_obj(obj)
            elif (self.selection_mode == 'VISIBLE') and obj.is_visible(scene):
                obj.hide_select = False
                add_obj(obj)
            elif (self.selection_mode == 'ALL'):
                obj.hide_select = False
                add_obj(obj)
        
        for obj in scene.objects:
            if obj in objs:
                obj.select = True
            else:
                scene.objects.unlink(obj)
                bpy.data.objects.remove(obj)
        scene.update()
        
        if not self.format:
            if not self.keep_materials:
                for material in bpy.data.materials:
                    material.user_clear()
                    bpy.data.materials.remove(material)
            
            if not self.keep_textures:
                for world in bpy.data.worlds:
                    for i in range(len(world.texture_slots)):
                        world.texture_slots.clear(i)
                for material in bpy.data.materials:
                    for i in range(len(material.texture_slots)):
                        material.texture_slots.clear(i)
                for brush in bpy.data.brushes:
                    brush.texture = None
                for texture in bpy.data.textures:
                    texture.user_clear()
                    bpy.data.textures.remove(texture)
            elif not self.keep_world_textures:
                for world in bpy.data.worlds:
                    for i in range(len(world.texture_slots)):
                        world.texture_slots.clear(i)
            
            if self.remove_orphans:
                datablocks_cleanup_order = [
                    #"window_managers",
                    #"screens",
                    "scenes",
                    "worlds",
                    
                    "grease_pencil",
                    "fonts",
                    "scripts",
                    "texts",
                    "movieclips",
                    "actions",
                    "speakers",
                    "sounds",
                    "brushes",
                    
                    "node_groups",
                    "groups",
                    "objects",
                    
                    "armatures",
                    "cameras",
                    "lamps",
                    "lattices",
                    "shape_keys",
                    "meshes",
                    "metaballs",
                    "particles",
                    "curves",
                    
                    "materials",
                    "textures",
                    "images",
                    
                    "libraries",
                ]
                for datablocks_name in datablocks_cleanup_order:
                    datablocks = getattr(bpy.data, datablocks_name)
                    if type(datablocks).__name__ == "bpy_prop_collection":
                        for datablock in datablocks:
                            if datablock.users == 0:
                                datablocks.remove(datablock)
        
        if self.format in join_before_export:
            bpy.ops.object.convert()
            bpy.ops.object.join()
    
    def execute(self, context):
        with ToggleObjectMode(undo=None):
            self.clear_world(context)
            
            if self.format:
                props = {}
                for key in CurrentFormatProperties._keys():
                    props[key] = getattr(self.format_props, key)
                props["filepath"] = self.filepath
                
                op = get_op(self.format)
                
                op(**props)
            else:
                bpy.ops.wm.save_as_mainfile(
                    filepath=self.filepath,
                    copy=True,
                )
            
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message="Export Selected")
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        
        layout.label("Export " + self.visible_name)
        
        layout.prop(self, "selection_mode", text="")
        layout.prop(self, "include_children")
        layout.prop_menu_enum(self, "object_types")
        
        layout.box()
        
        if not self.format:
            layout.prop(self, "remove_orphans")
            layout.prop(self, "keep_materials")
            layout.prop(self, "keep_textures")
            sublayout = layout.row()
            sublayout.enabled = self.keep_textures
            sublayout.prop(self, "keep_world_textures")
            return
        
        op = get_op(self.format)
        op_class = type(op.get_instance())
        
        if self.format == "wm.collada_export":
            op_class = ColladaEmulator
        
        if hasattr(op_class, "draw"):
            self.format_props.layout = layout
            op_class.draw(self.format_props, context)
        else:
            for key in CurrentFormatProperties._keys(True):
                if key == 'filepath': continue
                layout.prop(self.format_props, key)

class OBJECT_MT_selected_export(bpy.types.Menu):
    bl_idname = "OBJECT_MT_selected_export"
    bl_label = "Selected"
    
    def draw(self, context):
        layout = self.layout
        
        def def_op(visible_name, total_name="", layout=layout):
            if visible_name.lower().startswith("export "):
                visible_name = visible_name[len("export "):]
            
            if total_name:
                op = get_op(total_name)
                if not op.poll():
                    layout = layout.row()
                    layout.enabled = False
            
            op_info = layout.operator(
                ExportSelected.bl_idname,
                text=visible_name,
                )
            op_info.format = total_name
            op_info.visible_name = visible_name
            
            return op_info
        
        # Special case: export to .blend (the default)
        def_op("Blend")
        
        # Special case: Collada is built-in, resides
        # in an unconventional category, and has no
        # explicit ext/glob properties defined
        op_info = def_op("Collada", "wm.collada_export")
        op_info.filename_ext = ".dae"
        op_info.filter_glob = "*.dae"
        
        for total_name, op in iter_exporters():
            op_class = type(op.get_instance())
            rna = op.get_rna()
            
            op_info = def_op(rna.rna_type.name, total_name)
            
            if hasattr(op_class, "filename_ext"):
                op_info.filename_ext = op_class.filename_ext
            
            if hasattr(rna, "filter_glob"):
                op_info.filter_glob = rna.filter_glob

def menu_func_export(self, context):
    self.layout.menu("OBJECT_MT_selected_export", text="Selected")

def register():
    bpy.utils.register_class(CurrentFormatProperties)
    bpy.utils.register_class(ExportSelected)
    bpy.utils.register_class(OBJECT_MT_selected_export)
    bpy.types.INFO_MT_file_export.prepend(menu_func_export)

def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(OBJECT_MT_selected_export)
    bpy.utils.unregister_class(ExportSelected)
    bpy.utils.unregister_class(CurrentFormatProperties)

if __name__ == "__main__":
    register()

