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

#============================================================================#

import bpy

import time
import json

from mathutils import Vector

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_view3d import SmartView3D, Pick_Base
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, tag_redraw, find_ui_area, ui_context_under_coord
from {0}dairin0d.bpy_inspect import prop, BlRna, BlEnums, BpyOp
from {0}dairin0d.utils_accumulation import Aggregator, VectorAggregator, PatternRenamer
from {0}dairin0d.utils_blender import ChangeMonitor, Selection, SelectionSnapshot, ToggleObjectMode, IndividuallyActiveSelected, BlUtil
from {0}dairin0d.utils_addon import AddonManager, UIMonitor
""".format(dairin0d_location))

addon = AddonManager()

idnames_separator = "\t"

change_monitor = ChangeMonitor(update=False) # used in batch_repeat_actions operator

def LeftRightPanel(cls=None, **kwargs):
    def AddPanels(cls, kwargs):
        doc = cls.__doc__
        name = kwargs.get("bl_idname") or kwargs.get("idname") or cls.__name__
        
        # expected either class or function
        if not isinstance(cls, type):
            cls = type(name, (), dict(__doc__=doc, draw=cls))
        
        def is_panel_left():
            if not addon.preferences: return False
            return addon.preferences.use_panel_left
        def is_panel_right():
            if not addon.preferences: return False
            return addon.preferences.use_panel_right
        
        @addon.Panel(**kwargs)
        class LeftPanel(cls):
            bl_idname = name + "_left"
            bl_region_type = 'TOOLS'
        
        @addon.Panel(**kwargs)
        class RightPanel(cls):
            bl_idname = name + "_right"
            bl_region_type = 'UI'
        
        poll = getattr(cls, "poll", None)
        if poll:
            LeftPanel.poll = classmethod(lambda cls, context: is_panel_left() and poll(cls, context))
            RightPanel.poll = classmethod(lambda cls, context: is_panel_right() and poll(cls, context))
        else:
            LeftPanel.poll = classmethod(lambda cls, context: is_panel_left())
            RightPanel.poll = classmethod(lambda cls, context: is_panel_right())
        
        return cls
    
    if cls: return AddPanels(cls, kwargs)
    return (lambda cls: AddPanels(cls, kwargs))

def convert_selection_to_mesh():
    # Scene is expected to be in OBJECT mode
    try:
        bpy.ops.object.convert(target='MESH')
    except Exception as exc:
        active_obj = bpy.context.object
        selected_objs = bpy.context.selected_objects
        print((exc, active_obj, selected_objs))

def bake_location_rotation_scale(location=False, rotation=False, scale=False):
    if not (location or rotation or scale): return
    try:
        bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)
    except Exception as exc:
        active_obj = bpy.context.object
        selected_objs = bpy.context.selected_objects
        print((exc, active_obj, selected_objs))

# see http://www.elysiun.com/forum/showthread.php?304199-Apply-Shape-Keys-in-2-68
def apply_shapekeys(obj):
    if not hasattr(obj.data, "shape_keys"): return
    if not obj.data.shape_keys: return
    if len(obj.data.shape_keys.key_blocks) == 0: return
    
    if obj.data.users > 1: obj.data = obj.data.copy() # don't affect other objects
    
    # bake current shape in a new key (and remove it last)
    shape_key = obj.shape_key_add(name="Key", from_mix=True)
    shape_key.value = 1.0 # important
    
    # DON'T use "all=True" option, it removes in the wrong order
    n_keys = len(obj.data.shape_keys.key_blocks)
    for i in range(n_keys):
        # remove base key, then next one will become base, an so on
        obj.active_shape_key_index = 0
        # This seems to be the only way to remove a shape key
        bpy.ops.object.shape_key_remove(all=False)

def apply_modifiers(objects, scene, idnames, options=(), apply_as='DATA'):
    active_obj = scene.objects.active
    
    covert_to_mesh = ('CONVERT_TO_MESH' in options)
    make_single_user = ('MAKE_SINGLE_USER' in options)
    remove_disabled = ('REMOVE_DISABLED' in options)
    delete_operands = ('DELETE_OPERANDS' in options)
    apply_shape_keys = ('APPLY_SHAPE_KEYS' in options)
    visible_only = ('VISIBLE_ONLY' in options)
    
    objects_to_delete = set()
    
    for obj in objects:
        scene.objects.active = obj
        
        # Users will probably want shape keys to be applied regardless of whether there are modifiers
        if apply_shape_keys: apply_shapekeys(obj) # also makes single-user
        
        if not obj.modifiers: continue
        
        if (obj.type != 'MESH') and covert_to_mesh:
            # "Error: Cannot apply constructive modifiers on curve"
            if obj.data.users > 1: obj.data = obj.data.copy() # don't affect other objects
            convert_selection_to_mesh()
        elif make_single_user:
            # "Error: Modifiers cannot be applied to multi-user data"
            if obj.data.users > 1: obj.data = obj.data.copy() # don't affect other objects
        
        for md in tuple(obj.modifiers):
            if (idnames is not None) and (md.type not in idnames): continue
            
            obj_to_delete = None
            if delete_operands and (md.type == 'BOOLEAN'):
                obj_to_delete = md.object
            
            successfully_applied = False
            is_disabled = False
            
            if visible_only and not md.show_viewport:
                is_disabled = True
            else:
                try:
                    bpy.ops.object.modifier_apply(modifier=md.name, apply_as=apply_as) # not type or idname!
                    successfully_applied = True
                except RuntimeError as exc:
                    #print(repr(exc))
                    exc_msg = exc.args[0].lower()
                    # "Error: Modifier is disabled, skipping apply"
                    is_disabled = ("disab" in exc_msg) or ("skip" in exc_msg)
            
            if is_disabled and remove_disabled:
                obj.modifiers.remove(md)
            
            if successfully_applied and obj_to_delete:
                objects_to_delete.add(obj_to_delete)
    
    if active_obj in objects_to_delete: active_obj = None
    
    for obj in objects_to_delete:
        scene.objects.unlink(obj)
    
    scene.objects.active = active_obj
    
    return objects_to_delete

def add_potential_duplis(objs, parent):
    if parent.dupli_type == 'GROUP':
        if not parent.dupli_group: return
        for obj in parent.dupli_group.objects:
            objs.add(obj)
            add_potential_duplis(objs, obj)
    elif parent.dupli_type in {'VERTS', 'FACES'}:
        for obj in parent.children:
            objs.add(obj)
            add_potential_duplis(objs, obj)

# GROUP: layers don't matter, hide status is correct
# VERTS/FACES: objects on invisible layers don't get
#   included into dupli_list, hide status is False
#   even if the object is hidden (a bug?)
def add_actual_duplis(objs, obj, context, ignore_hide):
    if obj.dupli_list: obj.dupli_list_clear()
    obj.dupli_list_create(context.scene, 'VIEWPORT')
    for dupli in obj.dupli_list:
        if ignore_hide or (not dupli.object.hide):
            objs.add(dupli.object)
    obj.dupli_list_clear()

def iterate_workset(search_in, context=None, obj_types=None, include_duplis=None):
    if include_duplis is None: include_duplis = addon.preferences.include_duplis
    if (not include_duplis) or (search_in == 'FILE'):
        yield from BlUtil.Object.iterate(search_in, context, obj_types)
    else:
        if context is None: context = bpy.context
        objs = set()
        for obj in BlUtil.Object.iterate(search_in, context, None):
            if ((obj_types is None) or (obj.type in obj_types)): objs.add(obj)
            if obj.dupli_type in {'NONE', 'FRAMES'}: continue
            if search_in == 'VISIBLE':
                add_actual_duplis(objs, obj, context, False)
            elif search_in == 'LAYER':
                add_actual_duplis(objs, obj, context, True)
            else:
                add_potential_duplis(objs, obj)
        yield from objs

#============================================================================#

@addon.Operator(idname="object.batch_repeat_actions", options={'INTERNAL'}, label="Repeat action(s)", description="Repeat action(s) for selected objects")
class Operator_batch_repeat_actions:
    exclude_active = True | prop()
    operations = [False] | prop()
    max_shown_actions = 32
    search_in = 'SELECTION' | prop("Filter", items=[
        ('SELECTION', "Selection", "Apply to the selected objects", 'RESTRICT_SELECT_OFF'),
        ('VISIBLE', "Visible", "Apply to the visible objects", 'RESTRICT_VIEW_OFF'),
        ('LAYER', "Layer", "Apply to the objects in the visible layers", 'RENDERLAYERS'),
        ('SCENE', "Scene", "Apply to the objects in the current scene", 'SCENE_DATA'),
        #('FILE', "File", "Apply to all objects in this file", 'FILE_BLEND'), # not very applicable to batch-repeat-actions
    ])
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
    
    def invoke(self, context, event):
        cls = self.__class__
        
        mouse_context = ui_context_under_coord(event.mouse_x, event.mouse_y)
        info_context = find_ui_area('INFO')
        context_override = info_context or mouse_context
        
        reports = []
        if mouse_context:
            if context_override and context_override.get("area"):
                reports = change_monitor.get_reports(context, **context_override)
        
        self.operations.clear() # important!
        cls.compiled = []
        for i, report in enumerate(reversed(reports)):
            try:
                # unlike "exec", "single" prevents code without statements
                cls.compiled.append(compile(report, filename="info reports", mode="single"))
            except SyntaxError:
                continue
            
            item = self.operations.add()
            item.name = report
            item.value = (i == 0)
            
            if len(cls.compiled) >= cls.max_shown_actions: break
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        cls = self.__class__
        
        compiled = cls.compiled
        cls.compiled = None
        
        if not any(item.value for item in self.operations): return {'CANCELLED'}
        
        if self.exclude_active:
            active_obj = context.active_object
            selected_objs = tuple(obj for obj in BlUtil.Object.iterate(self.search_in, context) if obj != active_obj)
        else:
            selected_objs = tuple(BlUtil.Object.iterate(self.search_in, context))
        
        bpy.ops.ed.undo_push(message="Batch Repeat")
        
        for obj in IndividuallyActiveSelected(selected_objs):
            for i in range(len(self.operations)-1, -1, -1):
                item = self.operations[i]
                if not item.value: continue
                code = compiled[i]
                try:
                    exec(code)
                except Exception as exc:
                    print("Trying to execute {} resulted in {}".format(item.name, exc))
        
        return {'FINISHED'}
    
    def cancel(self, context):
        cls = self.__class__
        cls.compiled = None
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        layout.prop(self, "search_in", text="Filter")
        layout.prop(self, "exclude_active", text="Exclude active object")
        with layout.column(True):
            for item in self.operations:
                layout.prop(item, "value", text=item.name, toggle=True)

@addon.Operator(idname="object.batch_clear_slots_and_layers", options={'REGISTER', 'UNDO'}, label="Clear slots/layers", description="Clear material slots & data layers")
class Operator_batch_clear_slots_and_layers:
    globally = False | prop("Clear in the whole file (instead of just in the selection)", "Globally")
    clear_material_slots = True | prop("Clear material slots", "Clear material slots")
    clear_vertex_groups = True | prop("Clear vertex groups", "Clear vertex groups")
    clear_shape_keys = True | prop("Clear shape keys", "Clear shape keys")
    clear_uv_maps = True | prop("Clear UV maps", "Clear UV maps")
    clear_vertex_colors = True | prop("Clear vertex colors", "Clear vertex colors")
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Batch clear material slots/vertex groups")
        
        objects = (bpy.data.objects if self.globally else context.selected_objects)
        
        for obj in IndividuallyActiveSelected(objects):
            if not obj.data: continue
            data = obj.data
            
            if self.clear_material_slots and hasattr(data, "materials"):
                data.materials.clear(True)
            
            if self.clear_vertex_groups and obj.vertex_groups:
                obj.vertex_groups.clear()
            
            if self.clear_shape_keys and hasattr(data, "shape_keys"):
                if data.shape_keys: bpy.ops.object.shape_key_remove(all=True)
            
            if obj.type == 'MESH':
                if self.clear_uv_maps:
                    while data.uv_layers:
                        bpy.ops.mesh.uv_texture_remove()
                
                if self.clear_vertex_colors:
                    while data.vertex_colors:
                        data.vertex_colors.remove(data.vertex_colors[0])
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        layout.prop(self, "globally")
        layout.prop(self, "clear_material_slots")
        layout.prop(self, "clear_vertex_groups")
        layout.prop(self, "clear_shape_keys")
        layout.prop(self, "clear_uv_maps")
        layout.prop(self, "clear_vertex_colors")

@addon.Operator(idname="object.batch_streamline_meshes", options={'REGISTER', 'UNDO'}, label="Streamline mesh(es)", description="Streamline mesh(es)", mode={'OBJECT', 'EDIT_MESH'})
class Operator_batch_streamline_meshes:
    globally = False | prop("Apply to all objects (instead of just in the selection)", "Globally")
    convert_to_mesh = False | prop("Convert non-meshes to meshes", "Convert to mesh(es)")
    clear_animation = False | prop("Clear animation", "Clear animation")
    bake_location = False | prop("Bake location", "Apply location")
    bake_rotation = False | prop("Bake rotation", "Apply rotation")
    bake_scale = False | prop("Bake scale", "Apply scale")
    
    # see also MeshLint, PrintToolbox?
    # TODO (low priority): after operator is performed, show statistics of what modifications were actually done (e.g. removed N vertices, etc., etc.)
    
    # Apply modifiers
    apply_modifiers = False | prop("Apply all modifiers", "Apply modifiers")
    apply_modifiers_make_single_user = True | prop("Make single user", "Make single user")
    apply_modifiers_remove_disabled = True | prop("Remove disabled", "Remove disabled")
    apply_modifiers_delete_operands = False | prop("Delete the remaining boolean operands", "Delete operands")
    apply_modifiers_shape_keys = True | prop("Apply shape keys before applying the modifiers", "Apply shape keys")
    
    # Symmetry
    symmetry_snap = False | prop("Snap vertex pairs to their mirrored locations", "Snap to symmetry")
    symmetry_snap_direction = BlRna.to_bpy_prop(bpy.ops.mesh.symmetry_snap, "direction")
    symmetry_snap_threshold = BlRna.to_bpy_prop(bpy.ops.mesh.symmetry_snap, "threshold")
    symmetry_snap_factor = BlRna.to_bpy_prop(bpy.ops.mesh.symmetry_snap, "factor")
    symmetry_snap_use_center = BlRna.to_bpy_prop(bpy.ops.mesh.symmetry_snap, "use_center")
    
    symmetrize = False | prop("Enforce a symmetry (both form and topological) across an axis", "Symmetrize")
    symmetrize_direction = BlRna.to_bpy_prop(bpy.ops.mesh.symmetrize, "direction")
    symmetrize_threshold = BlRna.to_bpy_prop(bpy.ops.mesh.symmetrize, "threshold")
    
    # Fix degenerate geometry
    dissolve_degenerate = False | prop("Dissolve zero area faces and zero length edges", "Dissolve degenerate")
    dissolve_degenerate_threshold = BlRna.to_bpy_prop(bpy.ops.mesh.dissolve_degenerate, "threshold")
    
    remove_doubles = False | prop("Remove duplicate vertices", "Remove doubles")
    remove_doubles_threshold = BlRna.to_bpy_prop(bpy.ops.mesh.remove_doubles, "threshold")
    remove_doubles_use_unselected = BlRna.to_bpy_prop(bpy.ops.mesh.remove_doubles, "use_unselected")
    
    face_split_by_edges = False | prop("Split faces by loose edges", "Split by edges")
    
    beautify_fill = False | prop("Rearrange some faces to try to get less degenerate geometry", "Beautify faces")
    beautify_fill_angle_limit = BlRna.to_bpy_prop(bpy.ops.mesh.beautify_fill, "angle_limit")
    
    # Fix topology
    fill_holes = False | prop("Fill in holes (boundary edge loops)", "Fill holes")
    fill_holes_sides = BlRna.to_bpy_prop(bpy.ops.mesh.fill_holes, "sides")
    
    intersect = False | prop("Cut an intersection into faces", "Intersect")
    if BpyOp("mesh.intersect"):
        intersect_mode = BlRna.to_bpy_prop(bpy.ops.mesh.intersect, "mode") | prop(default='SELECT')
        if "separate_mode" in BlRna(bpy.ops.mesh.intersect).properties: # instead of use_separate (since 2.78.4)
            intersect_separate_mode = BlRna.to_bpy_prop(bpy.ops.mesh.intersect, "separate_mode")
        else:
            intersect_use_separate = BlRna.to_bpy_prop(bpy.ops.mesh.intersect, "use_separate")
        intersect_threshold = BlRna.to_bpy_prop(bpy.ops.mesh.intersect, "threshold") | prop(name="Merge Distance")
    else:
        intersect_mode = 'SELECT' | prop(items=[('SELECT_UNSELECT', "Selected/Unselected"), ('SELECT', "Self intersect")])
        intersect_use_separate = False | prop(name="Separate")
        intersect_threshold = 1e-6 | prop(name="Merge Distance")
    
    normals = False | prop("Recalculate normals", "Recalculate normals")
    normals_type = 'OUTSIDE' | prop("Recalculate normals", items=[
        ('OUTSIDE', "Outside"),
        ('INSIDE', "Inside"),
        ('FLIP', "Flip"),
    ])
    
    #Outer shell (intersect -> remove internal parts) ? (not in Blender)
    
    # Delete loose geometry
    delete_loose = False | prop("Delete loose vertices/edges/faces", "Delete loose")
    delete_loose_use_verts = True | prop("Vertices", "Vertices")
    delete_loose_use_edges = True | prop("Edges", "Edges")
    delete_loose_use_faces = False | prop("Faces", "Faces")
    
    # Flatness/smoothness/planarity/curvature
    dissolve_limited = False | prop("Dissolve edges/verts, limited by angle of surrounding geometry", "Dissolve by angle")
    dissolve_limited_angle_limit = BlRna.to_bpy_prop(bpy.ops.mesh.dissolve_limited, "angle_limit")
    dissolve_limited_use_dissolve_boundaries = BlRna.to_bpy_prop(bpy.ops.mesh.dissolve_limited, "use_dissolve_boundaries")
    dissolve_limited_delimit = BlRna.to_bpy_prop(bpy.ops.mesh.dissolve_limited, "delimit")
    
    vert_connect_nonplanar = False | prop("Split non-planar faces that exceed the angle threshold", "Split non-planar faces")
    vert_connect_nonplanar_angle_limit = BlRna.to_bpy_prop(bpy.ops.mesh.vert_connect_nonplanar, "angle_limit")
    
    shade = False | prop("Face shade", "Face shade")
    shade_type = 'SMOOTH' | prop("Face shade", items=[
        ('SMOOTH', "Smooth"),
        ('FLAT', "Flat"),
    ])
    
    # Tris/Quads
    quads_convert_to_tris = False | prop("Triangulate faces", "Triangulate faces")
    quads_convert_to_tris_quad_method = BlRna.to_bpy_prop(bpy.ops.mesh.quads_convert_to_tris, "quad_method")
    quads_convert_to_tris_ngon_method = BlRna.to_bpy_prop(bpy.ops.mesh.quads_convert_to_tris, "ngon_method")
    
    tris_convert_to_quads = False | prop("Join triangles into quads", "Tris to quads")
    if "limit" in BlRna(bpy.ops.mesh.tris_convert_to_quads).properties: # removed in 2.74
        tris_convert_to_quads_limit = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "limit")
    if "face_threshold" in BlRna(bpy.ops.mesh.tris_convert_to_quads).properties: # added in 2.74
        tris_convert_to_quads_face_threshold = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "face_threshold")
    if "shape_threshold" in BlRna(bpy.ops.mesh.tris_convert_to_quads).properties: # added in 2.74
        tris_convert_to_quads_shape_threshold = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "shape_threshold")
    tris_convert_to_quads_uvs = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "uvs")
    tris_convert_to_quads_vcols = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "vcols")
    if "seam" in BlRna(bpy.ops.mesh.tris_convert_to_quads).properties: # added in 2.74
        tris_convert_to_quads_seam = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "seam")
    tris_convert_to_quads_sharp = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "sharp")
    tris_convert_to_quads_materials = BlRna.to_bpy_prop(bpy.ops.mesh.tris_convert_to_quads, "materials")
    
    poke = False | prop("Split faces into fans", "Poke faces")
    poke_offset = BlRna.to_bpy_prop(bpy.ops.mesh.poke, "offset")
    poke_use_relative_offset = BlRna.to_bpy_prop(bpy.ops.mesh.poke, "use_relative_offset")
    poke_center_mode = BlRna.to_bpy_prop(bpy.ops.mesh.poke, "center_mode")
    
    # Sorting
    sort = False | prop("Sort", "Sort")
    sort_type = BlRna.to_bpy_prop(bpy.ops.mesh.sort_elements, "type")
    sort_verts = True | prop("Vertices", "Vertices")
    sort_edges = False | prop("Edges", "Edges")
    sort_faces = False | prop("Faces", "Faces")
    sort_reverse = BlRna.to_bpy_prop(bpy.ops.mesh.sort_elements, "reverse")
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        
        with layout.row()(alignment='LEFT'):
            layout.prop(self, "globally")
            layout.prop(self, "convert_to_mesh")
            layout.prop(self, "clear_animation")
            layout.prop(self, "bake_location")
            layout.prop(self, "bake_rotation")
            layout.prop(self, "bake_scale")
        
        with layout.column():
            layout.label("Modifiers")
            with layout.split(0.25):
                with layout.column(True):
                    layout.prop(self, "apply_modifiers", toggle=True)
                with layout.column(True):
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "apply_modifiers_make_single_user")
                        layout.prop(self, "apply_modifiers_remove_disabled")
                        layout.prop(self, "apply_modifiers_delete_operands")
                        layout.prop(self, "apply_modifiers_shape_keys")
            
            layout.label("Symmetry")
            with layout.split(0.25):
                with layout.column(True):
                    layout.prop(self, "symmetry_snap", toggle=True)
                    layout.prop(self, "symmetrize", toggle=True)
                with layout.column(True):
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "symmetry_snap_direction", text="")
                        layout.prop(self, "symmetry_snap_threshold")
                        layout.prop(self, "symmetry_snap_factor")
                        layout.prop(self, "symmetry_snap_use_center")
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "symmetrize_direction", text="")
                        layout.prop(self, "symmetrize_threshold")
            
            layout.label("Degenerate")
            with layout.split(0.25):
                with layout.column(True):
                    layout.prop(self, "dissolve_degenerate", toggle=True)
                    layout.prop(self, "remove_doubles", toggle=True)
                    layout.prop(self, "face_split_by_edges", toggle=True)
                    layout.prop(self, "beautify_fill", toggle=True)
                with layout.column(True):
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "dissolve_degenerate_threshold")
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "remove_doubles_threshold")
                        layout.prop(self, "remove_doubles_use_unselected")
                    with layout.row()(alignment='LEFT'):
                        layout.label("") # face_split_by_edges has no parameters
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "beautify_fill_angle_limit")
            
            layout.label("Topology")
            with layout.split(0.25):
                with layout.column(True):
                    layout.prop(self, "fill_holes", toggle=True)
                    layout.prop(self, "intersect", toggle=True)
                    layout.prop(self, "normals", toggle=True)
                    layout.prop(self, "delete_loose", toggle=True)
                with layout.column(True):
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "fill_holes_sides")
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "intersect_mode", text="")
                        layout.prop(self, "intersect_threshold")
                        if hasattr(self, "intersect_separate_mode"):
                            layout.prop(self, "intersect_separate_mode", text="")
                        else:
                            layout.prop(self, "intersect_use_separate")
                    with layout.row()(alignment='LEFT'):
                        layout.prop_enum(self, "normals_type", 'OUTSIDE')
                        layout.prop_enum(self, "normals_type", 'INSIDE')
                        layout.prop_enum(self, "normals_type", 'FLIP')
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "delete_loose_use_verts")
                        layout.prop(self, "delete_loose_use_edges")
                        layout.prop(self, "delete_loose_use_faces")
            
            layout.label("Curvature")
            with layout.split(0.25):
                with layout.column(True):
                    layout.prop(self, "dissolve_limited", toggle=True)
                    layout.prop(self, "vert_connect_nonplanar", toggle=True)
                    layout.prop(self, "shade", toggle=True)
                with layout.column(True):
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "dissolve_limited_angle_limit")
                        layout.prop_menu_enum(self, "dissolve_limited_delimit")
                        layout.prop(self, "dissolve_limited_use_dissolve_boundaries")
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "vert_connect_nonplanar_angle_limit")
                    with layout.row()(alignment='LEFT'):
                        layout.prop_enum(self, "shade_type", 'SMOOTH')
                        layout.prop_enum(self, "shade_type", 'FLAT')
            
            layout.label("Tris, Quads")
            with layout.split(0.25):
                with layout.column(True):
                    layout.prop(self, "quads_convert_to_tris", toggle=True)
                    layout.prop(self, "tris_convert_to_quads", toggle=True)
                    layout.prop(self, "poke", toggle=True)
                with layout.column(True):
                    with layout.row()(alignment='EXPAND'):
                        layout.prop(self, "quads_convert_to_tris_quad_method", text="Quad")
                        layout.prop(self, "quads_convert_to_tris_ngon_method", text="Ngon")
                    with layout.row()(alignment='LEFT'):
                        if hasattr(self, "tris_convert_to_quads_limit"):
                            layout.prop(self, "tris_convert_to_quads_limit")
                        if hasattr(self, "tris_convert_to_quads_face_threshold"):
                            layout.prop(self, "tris_convert_to_quads_face_threshold")
                        if hasattr(self, "tris_convert_to_quads_shape_threshold"):
                            layout.prop(self, "tris_convert_to_quads_shape_threshold")
                        layout.prop(self, "tris_convert_to_quads_uvs", text="UVs")
                        layout.prop(self, "tris_convert_to_quads_vcols", text="VCols")
                        if hasattr(self, "tris_convert_to_quads_seam"):
                            layout.prop(self, "tris_convert_to_quads_seam")
                        layout.prop(self, "tris_convert_to_quads_sharp", text="Sharp")
                        layout.prop(self, "tris_convert_to_quads_materials", text="Materials")
                    with layout.row()(alignment='EXPAND'):
                        with layout.row()(scale_x=1.1):
                            layout.prop(self, "poke_center_mode", text="Center")
                        layout.prop(self, "poke_offset")
                        layout.prop(self, "poke_use_relative_offset")
            
            layout.label("Sorting")
            with layout.split(0.25):
                with layout.column(True):
                    layout.prop(self, "sort", toggle=True)
                with layout.column(True):
                    with layout.row()(alignment='LEFT'):
                        layout.prop(self, "sort_type", text="")
                        layout.prop(self, "sort_reverse")
                        layout.prop(self, "sort_verts")
                        layout.prop(self, "sort_edges")
                        layout.prop(self, "sort_faces")
    
    def apply(self, context, select_all=True):
        #if select_all: bpy.ops.mesh.select_all(action='SELECT') # after each operation
        
        # Symmetry
        if self.symmetrize:
            bpy.ops.mesh.symmetrize(
                direction=self.symmetrize_direction,
                threshold=self.symmetrize_threshold,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        elif self.symmetry_snap:
            bpy.ops.mesh.symmetry_snap(
                direction=self.symmetry_snap_direction,
                threshold=self.symmetry_snap_threshold,
                factor=self.symmetry_snap_factor,
                use_center=self.symmetry_snap_use_center,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        # Degenerate
        if self.dissolve_degenerate:
            bpy.ops.mesh.dissolve_degenerate(
                threshold=self.dissolve_degenerate_threshold,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.remove_doubles:
            bpy.ops.mesh.remove_doubles(
                threshold=self.remove_doubles_threshold,
                use_unselected=self.remove_doubles_use_unselected,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.face_split_by_edges:
            bpy.ops.mesh.face_split_by_edges()
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.beautify_fill:
            bpy.ops.mesh.beautify_fill(
                angle_limit=self.beautify_fill_angle_limit,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        # Topology
        if self.fill_holes:
            bpy.ops.mesh.fill_holes(
                sides=self.fill_holes_sides,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.intersect and BpyOp("mesh.intersect"):
            kwargs = dict(
                    mode=self.intersect_mode,
                    threshold=self.intersect_threshold,
            )
            if hasattr(self, "intersect_separate_mode"):
                kwargs["separate_mode"] = self.intersect_separate_mode
            else:
                kwargs["use_separate"] = self.intersect_use_separate
            bpy.ops.mesh.intersect(**kwargs)
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.normals:
            if self.normals_type == 'OUTSIDE':
                bpy.ops.mesh.normals_make_consistent(inside=False)
            elif self.normals_type == 'INSIDE':
                bpy.ops.mesh.normals_make_consistent(inside=True)
            elif self.normals_type == 'FLIP':
                bpy.ops.mesh.flip_normals()
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.delete_loose:
            bpy.ops.mesh.delete_loose(
                use_verts=self.delete_loose_use_verts,
                use_edges=self.delete_loose_use_edges,
                use_faces=self.delete_loose_use_faces,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        # Curvature
        if self.dissolve_limited:
            bpy.ops.mesh.dissolve_limited(
                angle_limit=self.dissolve_limited_angle_limit,
                delimit=self.dissolve_limited_delimit,
                use_dissolve_boundaries=self.dissolve_limited_use_dissolve_boundaries,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.vert_connect_nonplanar:
            bpy.ops.mesh.vert_connect_nonplanar(
                angle_limit=self.vert_connect_nonplanar_angle_limit,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.shade:
            if self.shade_type == 'SMOOTH':
                bpy.ops.mesh.faces_shade_smooth()
            elif self.shade_type == 'FLAT':
                bpy.ops.mesh.faces_shade_flat()
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        # Tris, Quads
        if self.quads_convert_to_tris:
            bpy.ops.mesh.quads_convert_to_tris(
                quad_method=self.quads_convert_to_tris_quad_method,
                ngon_method=self.quads_convert_to_tris_ngon_method,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.tris_convert_to_quads:
            kwargs = dict(
                uvs=self.tris_convert_to_quads_uvs,
                vcols=self.tris_convert_to_quads_vcols,
                sharp=self.tris_convert_to_quads_sharp,
                materials=self.tris_convert_to_quads_materials,
            )
            if hasattr(self, "tris_convert_to_quads_limit"):
                kwargs["limit"] = self.tris_convert_to_quads_limit
            if hasattr(self, "tris_convert_to_quads_face_threshold"):
                kwargs["face_threshold"] = self.tris_convert_to_quads_face_threshold
            if hasattr(self, "tris_convert_to_quads_shape_threshold"):
                kwargs["shape_threshold"] = self.tris_convert_to_quads_shape_threshold
            if hasattr(self, "tris_convert_to_quads_seam"):
                kwargs["seam"] = self.tris_convert_to_quads_seam
            bpy.ops.mesh.tris_convert_to_quads(**kwargs)
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        if self.poke:
            bpy.ops.mesh.poke(
                center_mode=self.poke_center_mode,
                offset=self.poke_offset,
                use_relative_offset=self.poke_use_relative_offset,
            )
            if select_all: bpy.ops.mesh.select_all(action='SELECT')
        
        # Sorting
        if self.sort:
            sort_elements = set()
            if self.sort_verts: sort_elements.add('VERT')
            if self.sort_edges: sort_elements.add('EDGE')
            if self.sort_faces: sort_elements.add('FACE')
            bpy.ops.mesh.sort_elements(
                type=self.sort_type,
                reverse=self.sort_reverse,
                elements=sort_elements,
            )
            #if select_all: bpy.ops.mesh.select_all(action='SELECT') # no need
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT') or (context.mode == 'EDIT_MESH')
    
    def invoke(self, context, event):
        # Note: changing operator parameters here will have no effect on the popup
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=700)
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Batch streamline meshes")
        
        active_obj = context.active_object
        
        if active_obj and (active_obj.type == 'MESH') and (active_obj.mode == 'EDIT'):
            mesh = active_obj.data
            total_sel = (mesh.total_vert_sel + mesh.total_edge_sel + mesh.total_face_sel)
            if total_sel == 0: bpy.ops.mesh.select_all(action='SELECT')
            
            self.apply(context, (total_sel == 0))
            
            if total_sel == 0: bpy.ops.mesh.select_all(action='DESELECT')
        elif active_obj and (active_obj.mode != 'OBJECT'):
            return {'CANCELLED'}
        else:
            scene = context.scene
            objects = (bpy.data.objects if self.globally else context.selected_objects)
            
            if self.apply_modifiers:
                apply_modifiers_options = set()
                if self.convert_to_mesh: apply_modifiers_options.add('CONVERT_TO_MESH')
                if self.apply_modifiers_make_single_user: apply_modifiers_options.add('MAKE_SINGLE_USER')
                if self.apply_modifiers_remove_disabled: apply_modifiers_options.add('REMOVE_DISABLED')
                if self.apply_modifiers_delete_operands: apply_modifiers_options.add('DELETE_OPERANDS')
                if self.apply_modifiers_shape_keys: apply_modifiers_options.add('APPLY_SHAPE_KEYS')
                deleted_objects = apply_modifiers(objects, scene, None, apply_modifiers_options)
                objects = set(objects).difference(deleted_objects)
            
            for obj in IndividuallyActiveSelected(objects, make_visble=True):
                if obj.type not in BlEnums.object_types_geometry: continue
                
                if obj.type != 'MESH':
                    if self.convert_to_mesh: convert_selection_to_mesh()
                
                if self.clear_animation:
                    obj.animation_data_clear()
                    if obj.data: obj.data.animation_data_clear()
                
                bake_location_rotation_scale(self.bake_location, self.bake_rotation, self.bake_scale)
                
                if obj.type != 'MESH': continue
                
                # can fail if object not currently visible in the scene!
                bpy.ops.object.mode_set(mode='EDIT')
                
                bpy.ops.mesh.select_all(action='SELECT')
                
                self.apply(context)
                
                bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}

@LeftRightPanel(idname="VIEW3D_PT_batch_operations", space_type='VIEW_3D', category="Batch", label="Batch Operations")
class Panel_Batch_Operations:
    def draw_header(self, context):
        layout = NestedLayout(self.layout)
        prefs = addon.preferences
        with layout.row(True)(scale_x=0.9):
            layout.prop(prefs, "show_operations_as_list", text="", icon='COLLAPSEMENU', emboss=False)
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        prefs = addon.preferences
        if prefs.show_operations_as_list:
            with layout.row(True):
                layout.operator("object.batch_repeat_actions", text="Repeat", icon='PLAY')
                layout.operator("object.batch_clear_slots_and_layers", text="Clear", icon='GROUP_VCOL')
                layout.operator("object.batch_streamline_meshes", text="Streamline", icon='EDITMODE_HLT')
        else:
            with layout.column(True)(alignment='LEFT'):
                layout.operator("object.batch_repeat_actions", icon='PLAY')
                layout.operator("object.batch_clear_slots_and_layers", icon='GROUP_VCOL')
                layout.operator("object.batch_streamline_meshes", icon='EDITMODE_HLT')

#============================================================================#

@addon.Operator(idname="object.batch_hide", options={'INTERNAL', 'REGISTER'}, label="Visibile", description="Restrict viewport visibility")
def Operator_Hide(self, context, event, idnames="", state=False):
    if event is not None:
        if event.shift: state = False # Shift -> force show
        elif event.ctrl: state = True # Ctrl -> force hide
    idnames = set(idnames.split(idnames_separator))
    bpy.ops.ed.undo_push(message="Batch Restrict Visibility")
    for obj in context.scene.objects:
        if obj.name in idnames: obj.hide = state
    return {'FINISHED'}

@addon.Operator(idname="object.batch_hide_select", options={'INTERNAL', 'REGISTER'}, label="Selectable", description="Restrict viewport selection")
def Operator_Hide_Select(self, context, event, idnames="", state=False):
    if event is not None:
        if event.shift: state = False # Shift -> force show
        elif event.ctrl: state = True # Ctrl -> force hide
    idnames = set(idnames.split(idnames_separator))
    bpy.ops.ed.undo_push(message="Batch Restrict Selection")
    for obj in context.scene.objects:
        if obj.name in idnames: obj.hide_select = state
    return {'FINISHED'}

@addon.Operator(idname="object.batch_hide_render", options={'INTERNAL', 'REGISTER'}, label="Renderable", description="Restrict rendering")
def Operator_Hide_Render(self, context, event, idnames="", state=False):
    if event is not None:
        if event.shift: state = False # Shift -> force show
        elif event.ctrl: state = True # Ctrl -> force hide
    idnames = set(idnames.split(idnames_separator))
    bpy.ops.ed.undo_push(message="Batch Restrict Rendering")
    for obj in context.scene.objects:
        if obj.name in idnames: obj.hide_render = state
    return {'FINISHED'}

@addon.Operator(idname="object.batch_set_layers", options={'INTERNAL', 'REGISTER'}, label="Set layers", description="Set layers")
class Operator_Set_Layers:
    idnames = "" | prop()
    layers = (False,)*20 | prop("Set layers", "Set layers")
    layers_same = (False,)*20 | prop()
    
    def invoke(self, context, event):
        idnames = set(self.idnames.split(idnames_separator))
        aggr = VectorAggregator(len(self.layers), 'BOOL', {"same", "mean"})
        for obj in context.scene.objects:
            if obj.name in idnames: aggr.add(obj.layers)
        self.layers = aggr.get("mean", False, False)
        self.layers_same = aggr.same
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=220)
    
    def execute(self, context):
        idnames = set(self.idnames.split(idnames_separator))
        bpy.ops.ed.undo_push(message="Batch Set Layers")
        for obj in context.scene.objects:
            if obj.name in idnames: obj.layers = self.layers
        return {'FINISHED'}
    
    def draw_row(self, layout, i_start):
        with layout.row(True):
            for i in range(i_start, i_start+5):
                same = self.layers_same[i]
                layout.row(True)(alert=not same).prop(self, "layers", index=i, text="", icon='BLANK1', toggle=True)
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        with layout.row():
            with layout.column(True):
                self.draw_row(layout, 0)
                self.draw_row(layout, 10)
            with layout.column(True):
                self.draw_row(layout, 5)
                self.draw_row(layout, 15)

@addon.Operator(idname="object.batch_parent_to_empty", options={'INTERNAL', 'REGISTER'}, label="Parent To Empty", description=
"Click: Parent To Empty (+Ctrl: place parent at 3D cursor)")
def Operator_Parent_To_Empty(self, context, event, idnames="", category_idnames=""):
    # ? options: at active obj, at cursor, at average, at center
    idnames = set(idnames.split(idnames_separator))
    objs_matrices = tuple((obj, obj.matrix_world.copy()) for obj in context.scene.objects if obj.name in idnames)
    
    bpy.ops.ed.undo_push(message="Batch Parent To Empty")
    
    parent_name = category_idnames.replace(idnames_separator, "+")
    
    if event and event.ctrl:
        parent_pos = Vector(context.scene.cursor_location)
    else:
        parent_pos = sum((m.translation.copy() for obj, m in objs_matrices), Vector()) * (1.0 / len(objs_matrices))
    
    old_empty_parents = set()
    for obj, m in objs_matrices:
        if obj.parent and (obj.parent.type == 'EMPTY'):
            if obj.parent.parent is None:
                old_empty_parents.add(obj.parent)
        obj.parent_type = 'OBJECT'
        obj.parent = None
        obj.parent_bone = ""
        obj.use_slow_parent = False
        obj.matrix_world = m
    
    old_empty_parents.discard(obj for obj, m in objs_matrices)
    
    for old_parent in old_empty_parents:
        if old_parent.children: continue
        context.scene.objects.unlink(old_parent)
        if old_parent.users == 0:
            bpy.data.objects.remove(old_parent)
    context.scene.update()
    
    # Create after deleting old parents to reduce the possibility of name conflicts
    new_parent = bpy.data.objects.new(parent_name, None)
    new_parent.location = parent_pos
    new_parent.show_name = True
    #new_parent.show_x_ray = True # X-ray disables SSAO, so probably not very useful
    context.scene.objects.link(new_parent)
    context.scene.update() # update to avoid glitches
    
    for obj, m in objs_matrices:
        obj.parent = new_parent
        obj.matrix_world = m
    context.scene.update()
    
    return {'FINISHED'}

def make_category(globalvars, idname_attr="name", **kwargs):
    Category_Name = globalvars["Category_Name"]
    CATEGORY_NAME = Category_Name.upper()
    category_name = Category_Name.lower()
    Category_Name_Plural = globalvars["Category_Name_Plural"]
    CATEGORY_NAME_PLURAL = Category_Name_Plural.upper()
    category_name_plural = Category_Name_Plural.lower()
    category_icon = globalvars["category_icon"]
    
    BatchOperations = globalvars["BatchOperations"]
    
    aggregate_attrs = kwargs.get("aggregate_attrs", [])
    _nongeneric_actions = kwargs.get("nongeneric_actions", [])
    quick_access_default = kwargs.get("quick_access_default", set())
    menu_options_extra = kwargs.get("menu_options_extra", [])
    options_mixin = kwargs.get("options_mixin", object)
    copy_paste_contexts = kwargs.get("copy_paste_contexts", ())
    is_ID = kwargs.get("is_ID", False) # is ID datablock
    
    @addon.Menu(idname="OBJECT_MT_batch_{}_add".format(category_name), description=
    "Add {}(s)".format(Category_Name))
    def Menu_Add(self, context):
        layout = NestedLayout(self.layout)
        if is_ID:
            #op = layout.operator("object.batch_{}_add".format(category_name), text="<Create new>", icon=category_icon)
            op = layout.operator("object.batch_{}_add".format(category_name), text="<Create new>", icon='NEW')
            op.create = True
        for item in CategoryPG.remaining_items:
            idname = item[0]
            name = item[1]
            icon_kw = BatchOperations.icon_kwargs(idname, False)
            op = layout.operator("object.batch_{}_add".format(category_name), text=name, **icon_kw)
            op.idnames = idname
    
    @addon.Operator(idname="view3d.pick_{}".format(category_name_plural), options={'INTERNAL', 'REGISTER'}, description=
    "Pick {}(s) from the object under mouse".format(Category_Name))
    class Operator_Pick(Pick_Base):
        @classmethod
        def poll(cls, context):
            return (context.mode == 'OBJECT')
        
        def obj_to_info(self, obj):
            txt = ", ".join(BatchOperations.iter_names(obj))
            return (txt or "<No {}>".format(category_name))
        
        def on_confirm(self, context, obj):
            category = get_category()
            options = get_options()
            bpy.ops.ed.undo_push(message="Pick {}".format(Category_Name_Plural))
            BatchOperations.copy(obj)
            self.report({'INFO'}, "{} copied".format(Category_Name_Plural))
            BatchOperations.paste(options.iterate_objects(context), options.paste_mode)
            category.tag_refresh()
    
    # NOTE: only when 'REGISTER' is in bl_options and {'FINISHED'} is returned,
    # the operator will be recorded in wm.operators and info reports
    
    @addon.Operator(idname="object.batch_{}_copy".format(category_name), options={'INTERNAL'}, description=
    "Click: Copy")
    def Operator_Copy(self, context, event, object_name=""):
        active_obj = (bpy.data.objects.get(object_name) if object_name else context.object)
        if not active_obj: return
        
        category = get_category()
        options = get_options()
        
        if not options.synchronized:
            BatchOperations.copy(active_obj, CategoryPG.excluded)
            self.report({'INFO'}, "{} copied".format(Category_Name_Plural))
        else:
            addon.preferences.sync_copy(active_obj)
            self.report({'INFO'}, "{} copied".format(addon.preferences.sync_names()))
        
        #return {'FINISHED'}
    
    @addon.Operator(idname="object.batch_{}_paste".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
    "Click: Paste (+Ctrl: Override, +Shift: Add, +Alt: Filter)")
    def Operator_Paste(self, context, event):
        category = get_category()
        options = get_options()
        
        paste_mode = options.paste_mode
        if event is not None:
            if event.shift: paste_mode = 'OR'
            elif event.ctrl: paste_mode = 'SET'
            elif event.alt: paste_mode = 'AND'
        
        if not options.synchronized:
            bpy.ops.ed.undo_push(message="Batch Paste {}".format(Category_Name_Plural))
            BatchOperations.paste(options.iterate_objects(context), paste_mode)
            category.tag_refresh()
        else:
            bpy.ops.ed.undo_push(message="Batch Paste {}".format(addon.preferences.sync_names()))
            addon.preferences.sync_paste(context, paste_mode)
        
        return {'FINISHED'}
    
    @addon.Operator(idname="object.batch_{}_add".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
    "Click: Add")
    def Operator_Add(self, context, event, idnames="", create=False):
        category = get_category()
        options = get_options()
        bpy.ops.ed.undo_push(message="Batch Add {}".format(Category_Name_Plural))
        if is_ID and create: idnames = BatchOperations.new(Category_Name)
        BatchOperations.add(options.iterate_objects(context), idnames)
        category.tag_refresh()
        return {'FINISHED'}
    
    @addon.Operator(idname="object.batch_{}_assign".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
    "Click: Assign menu, Alt+Click: Alt-Assign action, Shift+Click: Shift-Assign action".format(category_name))
    def Operator_Assign(self, context, event, idnames="", index=0, title=""):
        category = get_category()
        options = get_options()
        
        if event.alt or event.shift:
            operator_assign = getattr(bpy.ops.object, "batch_{}_assign_action".format(category_name))
            operator_assign(src_idnames="", dst_idnames=idnames, globally=event.ctrl,
                assign_mode=(options.action_assign_alt if event.alt else options.action_assign_shift))
        else:
            globally = event.ctrl
            
            def draw_popup_menu(self, context):
                layout = NestedLayout(self.layout)
                
                # maybe use operator_enum(operator, property) ?
                for assign_item in BatchOperations.assign_modes:
                    op = layout.operator("object.batch_{}_assign_action".format(category_name), text=assign_item[1], icon='SPACE2')
                    op.src_idnames = ""
                    op.dst_idnames = idnames
                    op.globally = globally
                    op.assign_mode = assign_item[0]
                    op.all_if_empty = (assign_item[0] == 'REPLACE')
                
                layout.label("Replace {} with:".format(title))
                for item in BatchOperations.enum_all():
                    idname = item[0]
                    name = item[1]
                    op = layout.operator("object.batch_{}_assign_action".format(category_name), text=name, icon=category_icon)
                    op.src_idnames = idnames
                    op.dst_idnames = idname
                    op.globally = globally
                    op.assign_mode = 'REPLACE'
                    op.all_if_empty = True
            
            context.window_manager.popup_menu(draw_popup_menu, title="{}: assign menu".format(title), icon=category_icon)
    
    @addon.Operator(idname="object.batch_{}_assign_action".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
    "Click: Perform the corresponding action (+Ctrl: globally)".format(category_name))
    def Operator_Assign_Action(self, context, event, src_idnames="", dst_idnames="", globally=False, all_if_empty=True,
                               assign_mode=('ADD' | prop(items=BatchOperations.assign_modes))):
        category = get_category()
        options = get_options()
        
        if event is not None: globally |= event.ctrl # ? maybe XOR?
        globally |= options.is_globally
        from_file = globally
        purge = globally
        
        if not src_idnames:
            src_idnames = (category.all_idnames if all_if_empty else None)
        
        active_obj = context.object
        objects = options.iterate_objects(context, globally)
        
        mode_name = CategoryOptionsPG.assign_mode_names[assign_mode]
        
        bpy.ops.ed.undo_push(message="Batch {} {}".format(mode_name, Category_Name_Plural))
        BatchOperations.assign(assign_mode, active_obj, objects, src_idnames, dst_idnames, from_file, purge)
        
        category.tag_refresh()
        return {'FINISHED'}
    
    @addon.Operator(idname="object.batch_{}_name".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
    "Click: Select objects, Shift+Click: (De)select row (+Ctrl: set other rows), Ctrl+Click: Rename, Alt+Click: Assign action (+Ctrl: globally)")
    def Operator_Name(self, context, event, idnames="", index=0, title=""):
        category = get_category()
        options = get_options()
        preferences = addon.preferences
        
        if event.alt:
            assign_mode = options.action_name_alt
            all_if_empty = (assign_mode == 'REPLACE')
            operator_assign = getattr(bpy.ops.object, "batch_{}_assign_action".format(category_name))
            operator_assign(src_idnames="", dst_idnames=idnames, globally=event.ctrl, assign_mode=assign_mode, all_if_empty=all_if_empty)
            return
        elif event.shift:
            category = get_category()
            toggled_idname = category.items[index].idname
            excluded_state = CategoryPG.is_excluded(toggled_idname)
            toggled_state = not excluded_state
            
            if event.ctrl:
                CategoryPG.set_excluded("", excluded_state)
                CategoryPG.set_excluded(toggled_idname, toggled_state)
            else:
                CategoryPG.toggle_excluded(toggled_idname)
            
            if options.synchronize_selection:
                included_idnames = CategoryPG.prev_idnames.difference(CategoryPG.excluded)
                bpy.ops.ed.undo_push(message="Batch Select {}".format(Category_Name_Plural))
                #BatchOperations.select(context, included_idnames, 'OR')
                BatchOperations.select(context, toggled_idname, 'OR')
                # if deselected, make sure objects are deselected too
                if toggled_state: BatchOperations.select(context, idnames, 'AND!')
        elif event.ctrl:
            if index == 0: # All -> aggregate
                if len(category.items) > 2:
                    aggr = Aggregator('STRING', {'subseq', 'subseq_starts', 'subseq_ends'})
                    for i in range(1, len(category.items)):
                        aggr.add(category.items[i].name)
                    pattern = PatternRenamer.make(aggr.subseq, aggr.subseq_starts, aggr.subseq_ends)
                else:
                    pattern = category.items[1].name
            else:
                pattern = category.items[index].name
            
            if preferences.use_rename_popup:
                # if everything is deselected, rename won't affect anything anyway
                if not CategoryPG.is_excluded(""):
                    operator_rename = getattr(bpy.ops.object, "batch_{}_rename".format(category_name))
                    operator_rename('INVOKE_DEFAULT', idnames=idnames, rename=pattern)
                CategoryPG.rename_id = -1
            else:
                if CategoryPG.rename_id != index:
                    CategoryPG.rename_id = -1 # disable side-effects
                    CategoryPG.src_pattern = pattern
                    category.rename = pattern
                    CategoryPG.rename_id = index # side-effects are enabled now
        else:
            bpy.ops.ed.undo_push(message="Batch Select {}".format(Category_Name_Plural))
            BatchOperations.select(context, idnames or category.all_idnames)
        
        category.tag_refresh()
        return {'FINISHED'}
    
    @addon.Operator(idname="object.batch_{}_rename".format(category_name), options={'INTERNAL', 'REGISTER'}, label="Batch rename", description="Batch rename")
    class Operator_Rename:
        idnames = "" | prop()
        rename = "" | prop()
        src_pattern = "" | prop()
        
        def invoke(self, context, event):
            self.src_pattern = self.rename
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=220)
        
        def execute(self, context):
            category = get_category()
            options = get_options()
            idnames = self.idnames or category.all_idnames
            bpy.ops.ed.undo_push(message="Batch Rename {}".format(category_name))
            BatchOperations.set_attr("name", self.rename, options.iterate(context, selected=(not is_ID)), idnames, src_pattern=self.src_pattern)
            category.tag_refresh()
            return {'FINISHED'}
        
        def draw(self, context):
            layout = NestedLayout(self.layout)
            layout.prop(self, "rename", text="")
    
    @addon.Operator(idname="object.batch_{}_remove".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
    "Click: Remove (+Ctrl: globally), Alt+Click: Purge")
    def Operator_Remove(self, context, event, idnames="", index=0, title=""):
        category = get_category()
        options = get_options()
        if event.alt:
            bpy.ops.ed.undo_push(message="Purge {}".format(Category_Name_Plural))
            BatchOperations.purge(True, idnames)
        else:
            bpy.ops.ed.undo_push(message="Batch Remove {}".format(Category_Name_Plural))
            BatchOperations.remove(options.iterate_objects(context, event.ctrl), idnames, options.is_globally)
        category.tag_refresh()
        return {'FINISHED'}
    
    @addon.PropertyGroup
    class CategoryOptionsPG(options_mixin):
        def update_synchronized(self, context):
            addon.preferences.sync_add(self, category_name_plural)
        synchronized = True | prop("Synchronize options", "Synchronized", update=update_synchronized)
        
        def update(self, context):
            addon.preferences.sync_update(self, category_name_plural)
            category = get_category()
            category.tag_refresh()
        
        synchronize_selection = True | prop("Synchronize object/row selections", "Synchronize selection", update=update)
        
        prioritize_selection = True | prop("Affect all objects in the filter only if nothing is selected", "Prioritize selection", update=update)
        
        autorefresh = True | prop("Auto-refresh", update=update)
        
        aggregate_mode = 'mean' | prop("Toggle summary criterion", update=update, items=[('min', "All", "Display as 'On' only if all are 'On'"),
            ('max', "Any", "Display as 'On' if at least one is 'On'"), ('mean', "Majority", "Display as 'On' if the majority is 'On'")])
        
        paste_mode_icons = {'SET':'ROTACTIVE', 'OR':'ROTATECOLLECTION', 'AND':'ROTATECENTER'}
        paste_mode = 'OR' | prop("Paste mode", update=update, items=[
            ('SET', "Override", "Override objects' {}(s) with the copied ones".format(category_name), 'ROTACTIVE'),
            ('OR', "Add", "Add copied {}(s) to objects".format(category_name), 'ROTATECOLLECTION'),
            ('AND', "Filter", "Remove objects' {}(s) that are not among the copied".format(category_name), 'ROTATECENTER'),
        ])
        
        search_in_icons = {'SELECTION':'RESTRICT_SELECT_OFF', 'VISIBLE':'RESTRICT_VIEW_OFF',
            'LAYER':'RENDERLAYERS', 'SCENE':'SCENE_DATA', 'FILE':'FILE_BLEND'}
        search_in = 'FILE' | prop("Filter", update=update, items=[
            ('SELECTION', "Selection", "Display {}(s) of the selection".format(category_name), 'RESTRICT_SELECT_OFF'),
            ('VISIBLE', "Visible", "Display {}(s) of the visible objects".format(category_name), 'RESTRICT_VIEW_OFF'),
            ('LAYER', "Layer", "Display {}(s) of the objects in the visible layers".format(category_name), 'RENDERLAYERS'),
            ('SCENE', "Scene", "Display {}(s) of the objects in the current scene".format(category_name), 'SCENE_DATA'),
            ('FILE', "File", "Display all {}(s) in this file".format(category_name), 'FILE_BLEND'),
        ])
        
        is_globally = property(lambda self: (not self.prioritize_selection) and (self.search_in == 'FILE'))
        
        # These are intentionally not synchronized, since user will likely want them to stay different for each category
        assign_mode_names = {item[0]:item[1] for item in BatchOperations.assign_modes}
        action_name_alt = BatchOperations.assign_mode_default | prop("Action for Alt+Click on the name button", items=BatchOperations.assign_modes)
        action_assign_shift = BatchOperations.assign_mode_default1 | prop("Action for Shift+Click on the assign button", items=BatchOperations.assign_modes)
        action_assign_alt = BatchOperations.assign_mode_default2 | prop("Action for Alt+Click on the assign button", items=BatchOperations.assign_modes)
        
        def iterate(self, context=None, globally=False, selected=None, search_in=None):
            if search_in is None:
                if not context: context = bpy.context
                if selected is None: selected = self.prioritize_selection
                search_in = ('SELECTION' if selected and context.selected_objects else self.search_in)
                search_in = ('FILE' if globally else search_in)
            return BatchOperations.iterate(search_in, context)
        def iterate_objects(self, context=None, globally=False, selected=None, search_in=None):
            if search_in is None:
                if not context: context = bpy.context
                if selected is None: selected = self.prioritize_selection
                search_in = ('SELECTION' if selected and context.selected_objects else self.search_in)
                search_in = ('FILE' if globally else search_in)
            return BatchOperations.iterate_objects(search_in, context)
    
    class AggregateInfo:
        idname_attr = None
        aggr_infos = {}
        aggr_infos_objs = {}
        
        def __init__(self, idname, name):
            self.idname = idname
            self.name = name
            self.count = 0
            self.obj_names = []
            
            self.aggrs = {}
            for name, params in self.aggr_infos.items():
                self.aggrs[name] = Aggregator(*params["init"])
            
            self.aggrs_obj = {}
            for name, params in self.aggr_infos_objs.items():
                self.aggrs_obj[name] = Aggregator(*params["init"])
        
        def fill_item(self, item, query):
            item.name = self.name
            item.idname = self.idname
            item.count = self.count
            item.obj_names = idnames_separator.join(self.obj_names)
            for name, params in self.aggr_infos.items():
                self.fill_aggr(item, name, False, query, params.get("fallback"))
            for name, params in self.aggr_infos_objs.items():
                self.fill_aggr(item, name, True, query, params.get("fallback"))
            item.user_editable = True
        
        def fill_aggr(self, item, name, from_obj, query, fallback=None):
            aggr = (self.aggrs_obj[name] if from_obj else self.aggrs[name])
            setattr(item, name, aggr.get(query, fallback))
            item[name+":same"] = aggr.same
        
        @classmethod
        def collect_info(cls, items, count_users=False):
            infos = {}
            
            for item in items:
                cls.extract_info(infos, item, "", count_users=count_users)
                cls.extract_info(infos, item, count_users=count_users)
            
            for obj, idname in BatchOperations.iter_scene_objs_idnames(bpy.context.scene):
                if idname not in infos: continue # ignore object not in Filter
                cls.extract_info_obj(infos, obj, "")
                cls.extract_info_obj(infos, obj, idname)
            
            return infos
        
        @classmethod
        def extract_info_obj(cls, infos, obj, idname):
            info = infos[idname]
            info.obj_names.append(obj.name)
            for name, params in cls.aggr_infos_objs.items():
                value = getattr(obj, name)
                if params.get("invert", False): value = not value
                info.aggrs_obj[name].add(value)
        
        @classmethod
        def extract_info(cls, infos, item, idname=None, count_users=False):
            if idname is None: idname = getattr(item, cls.idname_attr)
            
            info = infos.get(idname)
            if info is None:
                name = (BatchOperations.clean_name(item) if idname else "")
                infos[idname] = info = cls(idname, name) # double assign
            
            if count_users:
                if not idname:
                    info.count += item.users # All
                else:
                    info.count = item.users
            else:
                info.count += 1
            
            for name, params in cls.aggr_infos.items():
                value = getattr(item, name)
                if params.get("invert", False): value = not value
                info.aggrs[name].add(value)
    
    @addon.PropertyGroup
    class CategoryItemPG:
        sort_id = 0 | prop()
        user_editable = False | prop()
        count = 0 | prop()
        idname = "" | prop()
        obj_names = "" | prop()
    
    AggregateInfo.idname_attr = idname_attr
    
    def make_update(name, from_obj, invert=False):
        def update(self, context):
            if not self.user_editable: return
            category = get_category()
            options = get_options()
            message = self.bl_rna.properties[name].description
            value = getattr(self, name)
            if invert and isinstance(value, bool): value = not value
            bpy.ops.ed.undo_push(message=message)
            globally = UIMonitor.ctrl
            if from_obj:
                objects = bpy.data.objects
                for idname in self.obj_names.split(idnames_separator):
                    obj = objects.get(idname)
                    if obj: setattr(obj, name, value)
            else:
                objects = options.iterate_objects(context, globally=globally)
                idnames = self.idname or category.all_idnames
                BatchOperations.set_attr(name, value, objects, idnames)
            category.tag_refresh()
        return update
    
    if is_ID:
        aggregate_attrs.append(("use_fake_user", dict(tooltip="Keep this datablock even if it has no users (adds an extra fake user)")))
        _nongeneric_actions.append(("aggregate_toggle", dict(property="use_fake_user", text="Keep datablock(s)", icons=('PINNED', 'UNPINNED'))))
    
    _nongeneric_actions.append(("operator", dict(operator="object.batch_{}_assign".format(category_name), text="Assign Action", icon=category_icon)))
    quick_access_default.add("object.batch_{}_assign".format(category_name))
    
    aggregate_attrs.append(("hide", dict(tooltip="Restrict viewport visibility", from_obj=True, invert=True)))
    _nongeneric_actions.append(("aggregate_toggle", dict(property="hide", text="Visibile", icons=('RESTRICT_VIEW_OFF', 'RESTRICT_VIEW_ON'), from_obj=True, after_name=True)))
    quick_access_default.add("hide")
    
    aggregate_attrs.append(("hide_select", dict(tooltip="Restrict viewport selection", from_obj=True, invert=True)))
    _nongeneric_actions.append(("aggregate_toggle", dict(property="hide_select", text="Selectable", icons=('RESTRICT_SELECT_OFF', 'RESTRICT_SELECT_ON'), from_obj=True, after_name=True)))
    quick_access_default.add("hide_select")
    
    aggregate_attrs.append(("hide_render", dict(tooltip="Restrict rendering", from_obj=True, invert=True)))
    _nongeneric_actions.append(("aggregate_toggle", dict(property="hide_render", text="Renderable", icons=('RESTRICT_RENDER_OFF', 'RESTRICT_RENDER_ON'), from_obj=True, after_name=True)))
    quick_access_default.add("hide_render")
    
    _nongeneric_actions.append(("operator", dict(operator="object.batch_set_layers", text="Set layers", icon='RENDERLAYERS', from_obj=True, after_name=True)))
    
    _nongeneric_actions.append(("operator", dict(operator="object.batch_parent_to_empty", text="Parent To Empty", icon='OUTLINER_OB_EMPTY', from_obj=True, after_name=True))) # or 'OOPS' ?
    
    _nongeneric_actions.append(("operator", dict(operator="object.batch_{}_remove".format(category_name), text="Remove", icon='X', after_name=True, use_affect=True)))
    quick_access_default.add("object.batch_{}_remove".format(category_name))
    
    quick_access_items = []
    nongeneric_actions = []
    nongeneric_actions_no_text = []
    
    for cmd, cmd_kwargs in _nongeneric_actions:
        from_obj = cmd_kwargs.get("from_obj", False)
        cmd_kwargs.pop("from_obj", None)
        
        after_name = cmd_kwargs.get("after_name", False)
        cmd_kwargs.pop("after_name", None)
        
        use_affect = cmd_kwargs.get("use_affect", False)
        cmd_kwargs.pop("use_affect", None)
        
        if cmd == "operator":
            action_idname = cmd_kwargs.get("operator")
        else:
            action_idname = cmd_kwargs.get("property")
        action_name = cmd_kwargs.get("text", action_idname)
        quick_access_items.append((action_idname, action_name, action_name))
        
        if cmd == "aggregate_toggle":
            icons = cmd_kwargs.get("icons")
            if icons is None: icons = ('CHECKBOX_HLT', 'CHECKBOX_DEHLT')
            elif isinstance(icons, str): icons = (icons, icons)
            cmd_kwargs["icons"] = icons
        
        nongeneric_actions.append((cmd, cmd_kwargs, action_idname, from_obj, use_affect, after_name))
        
        cmd_kwargs = dict(cmd_kwargs)
        cmd_kwargs["text"] = ""
        nongeneric_actions_no_text.append((cmd, cmd_kwargs, action_idname, from_obj, use_affect, after_name))
    
    for name, params in aggregate_attrs:
        from_obj = params.get("from_obj", False)
        invert = params.get("invert", False)
        
        prop_kwargs = params.get("prop")
        if prop_kwargs is None: prop_kwargs = {}
        if "default" not in prop_kwargs:
            prop_kwargs["default"] = False
        if "tooltip" in params:
            prop_kwargs["description"] = params["tooltip"]
        if "update" not in prop_kwargs:
            prop_kwargs["update"] = params.get("update") or make_update(name, from_obj, invert)
        setattr(CategoryItemPG, name, None | prop(**prop_kwargs))
        
        aggr = params.get("aggr")
        if aggr is None: aggr = dict(init=('BOOL', {"same", "min", "max", "mean"}), fallback=False, invert=invert)
        (AggregateInfo.aggr_infos_objs if from_obj else AggregateInfo.aggr_infos)[name] = aggr
    
    CategoryOptionsPG.quick_access = quick_access_default | prop("Quick access", "Quick access", items=quick_access_items)
    
    def aggregate_toggle(layout, item, property, icons, text="", emboss=True):
        icon = (icons[0] if getattr(item, property) else icons[1])
        with layout.row(True)(alert=not item[property+":same"]):
            layout.prop(item, property, icon=icon, text=text, toggle=True, emboss=emboss)
    
    def draw_toggle_or_action(layout, item, item_idnames, title, icon_novalue, cmd, cmd_kwargs, from_obj, emboss=True):
        if cmd == "aggregate_toggle":
            aggregate_toggle(layout, item, emboss=emboss, **cmd_kwargs)
        elif cmd == "operator":
            if "icon" in cmd_kwargs:
                op = layout.operator(emboss=emboss, **cmd_kwargs)
            else:
                op = layout.operator(icon=icon_novalue, emboss=emboss, **cmd_kwargs)
            
            if from_obj:
                op.idnames = item.obj_names
                if hasattr(op, "category_idnames"): op.category_idnames = item_idnames
            else:
                op.idnames = item_idnames
                op.index = item.sort_id
                op.title = title
    
    @addon.PropertyGroup
    class CategoryPG:
        prev_idnames = set()
        excluded = set()
        idnames_in_selected = set()
        is_anything_selected = False
        
        def update_rename(self, context):
            if CategoryPG.rename_id < 0: return
            category = get_category()
            options = get_options()
            # The bad thing is, undo seems to not be pushed from an update callback
            bpy.ops.ed.undo_push(message="Rename {}".format(category_name))
            idnames = category.items[CategoryPG.rename_id].idname or category.all_idnames
            BatchOperations.set_attr("name", self.rename, options.iterate(context, selected=(not is_ID)), idnames, src_pattern=CategoryPG.src_pattern)
            CategoryPG.rename_id = -1 # Auto switch off
            category.tag_refresh()
        
        rename_id = -1
        src_pattern = ""
        rename = "" | prop("Rename", "", update=update_rename)
        
        was_drawn = False | prop()
        next_refresh_time = -1.0 | prop()
        
        needs_refresh = True | prop()
        def tag_refresh(self):
            self.needs_refresh = True
            tag_redraw()
        
        all_idnames = property(lambda self: idnames_separator.join(
            item.idname for item in self.items
            if item.idname and not CategoryPG.is_excluded(item.idname)))
        
        items = [CategoryItemPG] | prop()
        
        remaining_items = []
        
        @classmethod
        def is_excluded(cls, idname):
            if not idname:
                return (cls.prev_idnames == cls.excluded)
            else:
                return idname in cls.excluded
        
        @classmethod
        def set_excluded(cls, idname, value):
            if not idname:
                category = get_category()
                for i in range(1, len(category.items)):
                    idname = category.items[i].idname
                    if value:
                        cls.excluded.add(idname)
                    else:
                        cls.excluded.discard(idname)
            else:
                if value:
                    cls.excluded.add(idname)
                else:
                    cls.excluded.discard(idname)
        
        @classmethod
        def toggle_excluded(cls, idname):
            if not idname:
                category = get_category()
                for i in range(1, len(category.items)):
                    idname = category.items[i].idname
                    if idname in cls.excluded:
                        cls.excluded.discard(idname)
                    else:
                        cls.excluded.add(idname)
            else:
                if idname in cls.excluded:
                    cls.excluded.discard(idname)
                else:
                    cls.excluded.add(idname)
        
        selection_info = (0, "")
        default_select_state = None
        
        def refresh(self, context, needs_refresh=False):
            cls = self.__class__
            options = get_options()
            preferences = addon.preferences
            
            active_obj = context.scene.objects.active
            selection_info = (len(context.selected_objects), (active_obj.name if active_obj else ""))
            needs_refresh |= (selection_info != cls.selection_info)
            
            needs_refresh |= self.needs_refresh
            needs_refresh |= options.autorefresh and (time.clock() > self.next_refresh_time)
            if not needs_refresh: return
            self.next_refresh_time = time.clock() + preferences.refresh_interval
            cls.selection_info = selection_info
            
            processing_time = time.clock()
            
            infos = AggregateInfo.collect_info(options.iterate(context, selected=False), is_ID and (options.search_in == 'FILE'))
            
            curr_idnames = set(infos.keys())
            curr_idnames.discard("") # necessary for comparison with idnames_in_selected
            if (curr_idnames != cls.prev_idnames) or (preferences.default_select_state != cls.default_select_state):
                # remember excluded state while idnames are the same
                if preferences.default_select_state:
                    cls.excluded.clear()
                else:
                    cls.excluded = set(curr_idnames)
                cls.default_select_state = preferences.default_select_state
                CategoryPG.rename_id = -1
            cls.prev_idnames = curr_idnames
            
            cls.is_anything_selected = bool(context.selected_objects)
            cls.idnames_in_selected = set(name for obj in options.iterate_objects(context, search_in='SELECTION')
                for name in BatchOperations.iter_idnames(obj))
            
            if options.synchronize_selection:
                cls.excluded = curr_idnames.difference(cls.idnames_in_selected)
            
            cls.remaining_items = [enum_item
                for enum_item in BatchOperations.enum_all()
                if enum_item[0] not in curr_idnames]
            cls.remaining_items.sort(key=lambda item:item[1])
            
            self.items.clear()
            for i, key in enumerate(sorted(infos.keys())):
                item = self.items.add()
                item.sort_id = i
                infos[key].fill_item(item, options.aggregate_mode)
            
            processing_time = time.clock() - processing_time
            # Disable autorefresh if it takes too much time
            #if processing_time > 0.05: options.autorefresh = False
            
            self.needs_refresh = False
        
        def draw(self, layout):
            self.was_drawn = True
            self.refresh(bpy.context)
            
            if not self.items: return
            
            options = get_options()
            
            all_idnames = self.all_idnames
            
            with layout.column(True):
                for item in self.items:
                    if item.sort_id == 0:
                        is_excluded = (self.prev_idnames == self.excluded)
                        is_in_selected = (self.prev_idnames == self.idnames_in_selected) # here, prev is same as curr
                        can_affect = bool(self.prev_idnames.intersection(self.idnames_in_selected))
                    else:
                        is_excluded = (item.idname in self.excluded)
                        is_in_selected = (item.idname in self.idnames_in_selected)
                        can_affect = is_in_selected
                    
                    can_affect |= (not options.prioritize_selection)
                    if not self.is_anything_selected: can_affect = True
                    
                    with layout.row(True)(active=not is_excluded):
                        emboss = is_in_selected
                        
                        title = item.name or "(All)"
                        icon_kw = BatchOperations.icon_kwargs(item.idname)
                        icon_novalue = BatchOperations.icon_kwargs(item.idname, False)["icon"]
                        
                        op = layout.operator("object.batch_{}_extras".format(category_name), text="", icon='DOTSDOWN', emboss=emboss)
                        op.idnames = item.idname or all_idnames
                        op.index = item.sort_id
                        op.title = title
                        
                        for cmd, cmd_kwargs, action_idname, from_obj, use_affect, after_name in nongeneric_actions_no_text:
                            if after_name: continue
                            if action_idname not in options.quick_access: continue
                            with layout.row(True)(alert=use_affect and (not can_affect)):
                                draw_toggle_or_action(layout, item, (item.idname or all_idnames), title, icon_novalue, cmd, cmd_kwargs, from_obj, emboss)
                        
                        if self.rename_id == item.sort_id:
                            layout.prop(self, "rename", text="", emboss=emboss)
                        else:
                            #icon_kw = BatchOperations.icon_kwargs(idname, False)
                            text = "{} ({})".format(title, item.count)
                            op = layout.operator("object.batch_{}_name".format(category_name), text=text, emboss=emboss)
                            op.idnames = item.idname or all_idnames
                            op.index = item.sort_id
                        
                        for cmd, cmd_kwargs, action_idname, from_obj, use_affect, after_name in nongeneric_actions_no_text:
                            if not after_name: continue
                            if action_idname not in options.quick_access: continue
                            with layout.row(True)(alert=use_affect and (not can_affect)):
                                draw_toggle_or_action(layout, item, (item.idname or all_idnames), title, icon_novalue, cmd, cmd_kwargs, from_obj, emboss)
    
    CategoryPG.Category_Name = Category_Name
    CategoryPG.CATEGORY_NAME = CATEGORY_NAME
    CategoryPG.category_name = category_name
    CategoryPG.Category_Name_Plural = Category_Name_Plural
    CategoryPG.CATEGORY_NAME_PLURAL = CATEGORY_NAME_PLURAL
    CategoryPG.category_name_plural = category_name_plural
    CategoryPG.category_icon = category_icon
    CategoryPG.BatchOperations = BatchOperations
    
    @addon.Operator(idname="object.batch_{}_extras".format(category_name), options={'INTERNAL'}, description="Extras")
    def Operator_Extras(self, context, event, idnames="", index=0, title=""):
        category = get_category()
        options = get_options()
        
        CategoryPG.rename_id = -1 # just for convenience (it might be hard to cancel the renaming mode otherwise)
        
        item = category.items[index]
        icon_novalue = BatchOperations.icon_kwargs(item.idname, False)["icon"]
        
        def draw_popup_menu(self, context):
            layout = NestedLayout(self.layout)
            for cmd, cmd_kwargs, action_idname, from_obj, use_affect, after_name in nongeneric_actions:
                draw_toggle_or_action(layout, item, idnames, title, icon_novalue, cmd, cmd_kwargs, from_obj)
        
        context.window_manager.popup_menu(draw_popup_menu, title="{} extras".format(title), icon='DOTSDOWN')
    
    @addon.Menu(idname="VIEW3D_MT_batch_{}_options_paste_mode".format(category_name_plural), label="Paste mode", description="Paste mode")
    def Menu_PasteMode(self, context):
        layout = NestedLayout(self.layout)
        options = get_options()
        layout.props_enum(options, "paste_mode")
    
    @addon.Menu(idname="VIEW3D_MT_batch_{}_options_search_in".format(category_name_plural), label="Filter", description="Filter")
    def Menu_SearchIn(self, context):
        layout = NestedLayout(self.layout)
        options = get_options()
        layout.props_enum(options, "search_in")
    
    if is_ID:
        @addon.Operator(idname="object.batch_{}_purge_unused".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
        "Click: Purge unused (+Ctrl: even those with use_fake_users)", label="Purge unused")
        def Operator_Purge_Unused(self, context, event):
            category = get_category()
            options = get_options()
            bpy.ops.ed.undo_push(message="Purge Unused {}".format(Category_Name_Plural))
            BatchOperations.purge(event.ctrl)
            category.tag_refresh()
            return {'FINISHED'}
        menu_options_extra.append(("operator", dict(operator="object.batch_{}_purge_unused".format(category_name), icon='GHOST_DISABLED')))
        
        @addon.Operator(idname="object.batch_{}_merge_identical".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
        "Click: Merge identical", label="Merge identical")
        def Operator_Merge_Identical(self, context, event):
            category = get_category()
            options = get_options()
            bpy.ops.ed.undo_push(message="Merge Identical {}".format(Category_Name_Plural))
            BatchOperations.merge_identical()
            category.tag_refresh()
            return {'FINISHED'}
        menu_options_extra.append(("operator", dict(operator="object.batch_{}_merge_identical".format(category_name), icon='AUTOMERGE_ON')))
    
    @addon.Menu(idname="VIEW3D_MT_batch_{}_options".format(category_name_plural), label="Options", description="Options")
    def Menu_Options(self, context):
        layout = NestedLayout(self.layout)
        options = get_options()
        layout.menu("VIEW3D_MT_batch_{}_options_search_in".format(category_name_plural), icon='VIEWZOOM')
        layout.menu("VIEW3D_MT_batch_{}_options_paste_mode".format(category_name_plural), icon='PASTEDOWN')
        layout.prop_menu_enum(options, "aggregate_mode", text="Summary mode", icon='INFO')
        layout.prop_menu_enum(options, "quick_access", text="Quick access", icon='VISIBLE_IPO_ON')
        layout.prop_menu_enum(options, "action_name_alt", text="Alt+Click on name", icon='HAND')
        layout.prop_menu_enum(options, "action_assign_shift", text="Shift+Click on assign", icon='HAND')
        layout.prop_menu_enum(options, "action_assign_alt", text="Alt+Click on assign", icon='HAND')
        layout.prop(options, "autorefresh", text="Auto refresh")
        layout.prop(options, "synchronized", text="Sync options")
        layout.prop(options, "synchronize_selection", text="Sync selection")
        layout.prop(options, "prioritize_selection", text="Affect selection")
        for cmd, cmd_kwargs in menu_options_extra:
            getattr(layout, cmd)(**cmd_kwargs)
    
    @addon.Operator(idname="object.batch_{}_refresh".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
    "Click: Force refresh, Ctrl+Click: Toggle auto-refresh")
    def Operator_Refresh(self, context, event):
        category = get_category()
        options = get_options()
        if event.ctrl:
            options.autorefresh = not options.autorefresh
        else:
            category.refresh(context, True)
        return {'FINISHED'}
    
    @LeftRightPanel(idname="VIEW3D_PT_batch_{}".format(category_name_plural), context="objectmode", space_type='VIEW_3D', category="Batch", label="Batch {}".format(Category_Name_Plural))
    class Panel_Category:
        def draw_header(self, context):
            layout = NestedLayout(self.layout)
            category = get_category()
            options = get_options()
            with layout.row(True)(scale_x=0.9):
                icon = CategoryOptionsPG.search_in_icons[options.search_in]
                layout.prop_menu_enum(options, "search_in", text="", icon=icon)
                icon = CategoryOptionsPG.paste_mode_icons[options.paste_mode]
                layout.prop_menu_enum(options, "paste_mode", text="", icon=icon)
        
        def draw(self, context):
            layout = NestedLayout(self.layout)
            category = get_category()
            options = get_options()
            
            with layout.row():
                with layout.row(True):
                    layout.menu("OBJECT_MT_batch_{}_add".format(category_name), icon='ZOOMIN', text="")
                    layout.operator("view3d.pick_{}".format(category_name_plural), icon='EYEDROPPER', text="")
                    layout.operator("object.batch_{}_copy".format(category_name), icon='COPYDOWN', text="")
                    layout.operator("object.batch_{}_paste".format(category_name), icon='PASTEDOWN', text="")
                
                icon = ('PREVIEW_RANGE' if options.autorefresh else 'FILE_REFRESH')
                layout.operator("object.batch_{}_refresh".format(category_name), icon=icon, text="")
                
                icon = ('SCRIPTPLUGINS' if options.synchronized else 'SCRIPTWIN')
                layout.menu("VIEW3D_MT_batch_{}_options".format(category_name_plural), icon=icon, text="")
            
            category.draw(layout)
    
    setattr(addon.External, category_name_plural, CategoryPG | -prop())
    get_category = eval("lambda: addon.external.{}".format(category_name_plural))
    
    setattr(addon.Preferences, category_name_plural, CategoryOptionsPG | prop())
    get_options = eval("lambda: addon.preferences.{}".format(category_name_plural))
    
    prefs_categories = getattr(addon.Preferences, "categories", None)
    if prefs_categories is None:
        prefs_categories = []
        addon.Preferences.categories = prefs_categories
    prefs_categories.append(CategoryPG)
    
    prefs_copy_paste_contexts = getattr(addon.Preferences, "copy_paste_contexts", None)
    if prefs_copy_paste_contexts is None:
        prefs_copy_paste_contexts = {}
        addon.Preferences.copy_paste_contexts = prefs_copy_paste_contexts
    prefs_copy_paste_contexts.update((context, CategoryPG) for context in copy_paste_contexts)
    
    globalvars.update(locals())
