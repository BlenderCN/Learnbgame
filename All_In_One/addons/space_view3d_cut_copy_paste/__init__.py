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

bl_info = {
    "name": "Cut/Copy/Paste objects and elements",
    "description": "Cut/Copy/Paste objects and elements",
    "author": "dairin0d",
    "version": (0, 6, 6),
    "blender": (2, 7, 0),
    "location": "View3D -> Ctrl+X, Ctrl+C, Ctrl+V, Shift+Delete, Ctrl+Insert, Shift+Insert",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/CutCopyPaste3D",
    "tracker_url": "https://github.com/dairin0d/cut-copy-paste/issues",
    "category": "Learnbgame"
}
#============================================================================#

if "dairin0d" in locals():
    import imp
    imp.reload(dairin0d)

import bpy
import bmesh

from mathutils import Vector, Matrix, Quaternion, Euler, Color

from bpy_extras.view3d_utils import (region_2d_to_vector_3d,
                                     region_2d_to_location_3d,
                                     location_3d_to_region_2d)

import os
import shutil
import glob
import time
import json
import bz2
import base64
import struct
import io

from collections import deque

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_ui import NestedLayout, tag_redraw
from {0}dairin0d.utils_view3d import SmartView3D
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.bpy_inspect import prop, BlRna, BlEnums
from {0}dairin0d.utils_blender import ToggleObjectMode
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

addon = AddonManager()

#============================================================================#

"""
Feature requests / bugs:
* fix edit-mode copying (maybe try to make it even more general, for easier adjustment to the changes in API?)
    * in particular, there was a problem with freestyle-related data
* provide customization of keymaps and of the options with which the operators are invoked

Starting with some version, Blender has copy/paste (but not cut) for objects.
It can paste even in a different file, but it will always append everything
(i.e. each time an object is pasted, a copy of its materials is added).
"""

# Blender ~bugs:
# - Transform operator should revert to default snap mode if Ctrl status
#   is released (if Ctrl was held when the operator was called, it would
#   think that Ctrl is still pressed even when it's not)

# TODO: save copy/paste preferences?

# There is already a built-in copy/paste pose operator.
# Text edit mode also has copy/paste (plain text).
# There seems to be no meaningful copy/paste for particles/lattice
# Surface copy/paste is quite limited, since only whole patches can
# be safely pasted.
copy_paste_modes = {'OBJECT', 'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_ARMATURE', 'EDIT_METABALL'}

blender_tempdir = bpy.app.tempdir
if (blender_tempdir[-1] in "\\/"): blender_tempdir = blender_tempdir[:-1]
blender_tempdir = os.path.dirname(blender_tempdir)
# LOCAL is blender's executable location,
# and Blender must always start from ASCII path
# (at least until non-ASCII problems are fixed)
#blender_tempdir = bpy.utils.resource_path('LOCAL') # USER SYSTEM
def get_clipboards_dir():
    clipboards_path = os.path.normcase(os.path.join(blender_tempdir, "blender_clipboards"))
    return clipboards_path

def compress_b64(b):
    # Somewhat strangely, compresslevel=1 not just works twice as fast
    # than compresslevel=9, but also results in lower size %)
    # (Tested on Suzanne subsurfed 3 times)
    return base64.b64encode(bz2.compress(b, 1)).decode('ascii')

def decompress_b64(c):
    return bz2.decompress(base64.b64decode(c.encode('ascii')))

def def_read_funcs(_stream):
    read = _stream.read
    unpack = struct.unpack
    
    def read_H():
        return unpack('!H', read(2))[0]
    
    def read_I():
        return unpack('!I', read(4))[0]
    
    def read_i():
        return unpack('!i', read(4))[0]
    
    def read_f():
        return unpack('!f', read(4))[0]
    
    def read_d():
        return unpack('!d', read(8))[0]
    
    def read_bool():
        return unpack('!?', read(1))[0]
    
    def read_ddd():
        return unpack('!ddd', read(24))
    
    def read_str():
        return read(read_H()).decode('utf-8')
    
    def deserializer_float(elem, layer):
        elem[layer] = unpack('!f', read(4))[0]
    
    def deserializer_int(elem, layer):
        elem[layer] = unpack('!i', read(4))[0]
    
    def deserializer_string(elem, layer):
        # string layer is exposed as bytes, max len is 255
        elem[layer] = read(unpack('!B', read(1))[0])
    
    def deserializer_deform(elem, layer):
        dvert = elem[layer]
        if not hasattr(dvert, "items"): return # Blender supports this since some version
        count = unpack('!i', read(4))[0]
        for i in range(count):
            group_index = unpack('!i', read(4))[0]
            weight = unpack('!f', read(4))[0]
            dvert[group_index] = weight
    
    def deserializer_vector(elem, layer):
        elem[layer] = unpack('!ddd', read(24))
    
    def deserializer_color(elem, layer):
        elem[layer] = unpack('!fff', read(12))
    
    def deserializer_uv(elem, layer):
        elem[layer].pin_uv = unpack('!?', read(1))[0]
        elem[layer].uv = unpack('!ff', read(8))
    
    def deserializer_tex(elem, layer):
        facetex = elem[layer]
        if not hasattr(facetex, "image"):
            return # Blender supports this since some version
        else:
            pass # TODO
    
    def deserializer_skin(elem, layer):
        elem[layer].radius = unpack('!ff', read(8))
        elem[layer].use_loose = unpack('!?', read(1))[0]
        elem[layer].use_root = unpack('!?', read(1))[0]
    
    def deserializer_freestyle(elem, layer):
        pass # Not implemented as of Blender 2.74
    
    def deserializer_paint_mask(elem, layer):
        elem[layer].value = unpack('!f', read(4))[0]
    
    return {k:v for k, v in locals().items() if not k.startswith("_")}

def def_write_funcs(_stream):
    write = _stream.write
    pack = struct.pack
    
    def write_str(s):
        b = s.encode('utf-8')
        write(pack('!H', len(b)))
        write(b)
    
    def serializer_float(value):
        write(pack('!f', value))
    
    def serializer_int(value):
        write(pack('!i', value))
    
    def serializer_string(value):
        # string layer is exposed as bytes, max len is 255
        write(pack('!B', len(value)))
        write(value)
    
    def serializer_deform(value):
        if not hasattr(value, "items"):
            write(pack('!i', 0)) # Blender supports this since some version
        else:
            items = value.items()
            write(pack('!i', len(items)))
            for group_index, weight in items:
                write(pack('!i', group_index))
                write(pack('!f', weight))
    
    def serializer_vector(value):
        write(pack('!ddd', *value))
    
    def serializer_color(value):
        write(pack('!fff', *value))
    
    def serializer_uv(value):
        write(pack('!?', value.pin_uv))
        write(pack('!ff', *value.uv))
    
    def serializer_tex(value):
        if not hasattr(value, "image"):
            return # Blender supports this since some version
        else:
            pass # TODO
    
    def serializer_skin(value):
        write(pack('!ff', *value.radius))
        write(pack('!?', value.use_loose))
        write(pack('!?', value.use_root))
    
    def serializer_freestyle(value):
        pass # Not implemented as of Blender 2.74
    
    def serializer_paint_mask(value):
        write(pack('!f', value.value))
    
    return {k:v for k, v in locals().items() if not k.startswith("_")}

class ChunkWriter:
    def __init__(self, stream, name):
        self.stream = stream
        
        b = name.encode('utf-8')
        stream.write(struct.pack('!H', len(b)))
        stream.write(b)
        
        self.size_pos = stream.tell()
        stream.write(struct.pack('!I', 0))
        
        self.pos = stream.tell()
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pos = self.stream.tell()
        self.stream.seek(self.size_pos)
        self.stream.write(struct.pack('!I', pos - self.pos))
        self.stream.seek(pos)

class ChunkReader:
    def __init__(self, stream, expected_name=None):
        self.stream = stream
        
        read = stream.read
        unpack = struct.unpack
        
        try:
            n = unpack('!H', read(2))[0]
        except struct.error:
            n = None
        
        if n is None:
            assert not expected_name
            self.name = None
            self.size = 0
            self.end = stream.tell()
            return
        
        self.name = read(n).decode('utf-8')
        
        if expected_name:
            assert self.name == expected_name
        
        self.size = unpack('!I', read(4))[0]
        
        self.end = stream.tell() + self.size
    
    def __bool__(self):
        return self.stream.tell() < self.end
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.stream.seek(self.end)
    
    def skip(self):
        self.stream.seek(self.end)

def is_view3d(context):
    return ((context.area.type == 'VIEW_3D') and (context.region.type == 'WINDOW'))

def get_view_rotation(context):
    v3d = context.space_data
    rv3d = context.region_data
    if rv3d.view_perspective == 'CAMERA':
        return v3d.camera.matrix_world.to_quaternion()
    else:
        return rv3d.view_rotation

# We can't use the same clipboard file, because Blender keeps reference
# to a library after appending from it (-> forbids to save files with
# that filepath).
def make_clipboard_path():
    clipboards_path = get_clipboards_dir()
    
    lib_paths = set(os.path.normcase(bpy.path.abspath(lib.filepath))
                    for lib in bpy.data.libraries)
    
    startkey = str(int(time.clock())).replace(".", "_") + "_"
    i = 0
    while True:
        name = "clipboard.%s.blend" % (startkey + str(i))
        path = os.path.normcase(os.path.join(clipboards_path, name))
        if (path not in lib_paths) and (not os.path.exists(path)):
            return path
        i += 1

def remove_clipboard_files():
    clipboards_path = get_clipboards_dir()
    
    filemask = os.path.join(clipboards_path, "clipboard.*.blend")
    for path in glob.glob(filemask):
        os.remove(path)

def is_clipboard_path(path):
    clipboards_path = get_clipboards_dir()
    
    path = os.path.normcase(bpy.path.abspath(path))
    
    if path.startswith(clipboards_path):
        path = path[len(clipboards_path):]
        if path.startswith(os.path.sep):
            path = path[1:]
        if path.startswith("clipboard.") and path.endswith(".blend"):
            return True
    
    return False

def save_clipboard_file(filepath):
    remove_clipboard_files()
    dir_path = os.path.dirname(filepath)
    if not os.path.exists(dir_path): os.makedirs(dir_path)
    bpy.ops.wm.save_as_mainfile(filepath=filepath, check_existing=False, copy=True)

def data_clipboard_path():
    #resource_path = bpy.utils.resource_path('LOCAL') # USER SYSTEM
    resource_path = get_clipboards_dir()
    return os.path.normcase(os.path.join(resource_path, "clipboard.data"))

@addon.Panel(space_type='VIEW_3D', region_type='TOOLS', category="Tools", label="Copy/Paste")
class VIEW3D_PT_copy_paste:
    coordsystem_icons = {'GLOBAL':'WORLD', 'LOCAL':'MANIPUL'}
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        
        opts = addon.preferences
        
        with layout.row(True)(enabled=(context.mode in copy_paste_modes)):
            layout.prop(opts, "external", text="", icon='URL')
            layout.prop(opts, "append", text="", icon='LINK_BLEND')
            layout.prop(opts, "link_ghost_objects", text="", icon='GHOST_DISABLED')
            layout.prop(opts, "paste_at_cursor", text="", icon='CURSOR')
            layout.prop(opts, "move_to_mouse", text="", icon='RESTRICT_SELECT_OFF')
            layout.prop(opts, "align_to_view", text="", icon='CAMERA_DATA')
            
            coordsystem = opts.actual_coordsystem(context)
            icon = self.coordsystem_icons[coordsystem]
            layout.prop_menu_enum(opts, "coordinate_system", text="", icon=icon)

@addon.Operator(idname="view3d.copy", label="Copy objects/elements", description="Copy objects/elements")
class OperatorCopy:
    force_copy = False | -prop()
    
    @classmethod
    def poll(cls, context):
        if context.mode not in copy_paste_modes: return False
        return context.selected_objects
    
    def write_object(self, json_data, context):
        wm = context.window_manager
        opts = addon.preferences
        
        self_is_clipboard = False
        
        self.force_copy |= opts.force_copy
        
        # Cut operation deletes objects from the scene after copying,
        # so we have to store them somewhere else (-> force_copy=True).
        if opts.external or self.force_copy:
            path = bpy.data.filepath
            if ((not path) or self.force_copy) and opts.append:
                path = make_clipboard_path()
                self_is_clipboard = True
            self_library = path
        else:
            self_library = ""
        
        libraries = {}
        libraries_inv = {}
        
        def library_id(obj):
            if obj.library:
                path = bpy.path.abspath(obj.library.filepath)
            else:
                path = self_library
            
            if path in libraries:
                return libraries[path]
            # JSON turns all keys into strings anyway
            id = str(len(libraries))
            libraries[path] = id
            libraries_inv[id] = path
            return id
        
        objects = {}
        matrices = {}
        parents = {}
        active_obj = context.object
        
        for obj in context.selected_objects:
            if obj == active_obj:
                json_data["active_object"] = obj.name
                json_data["active_object_library"] = library_id(obj)
            
            objects[obj.name] = library_id(obj)
            matrices[obj.name] = [tuple(v) for v in obj.matrix_world]
            
            if obj.parent:
                parents[obj.name] = (obj.parent.name, obj.parent_bone)
        
        json_data["objects"] = objects
        json_data["matrices"] = matrices
        json_data["parents"] = parents
        
        json_data["libraries"] = libraries_inv
        
        if self_library and (self_library in libraries):
            if self_is_clipboard:
                save_clipboard_file(self_library)
            """
            if self_is_clipboard:
                remove_clipboard_files()
                bpy.ops.wm.save_as_mainfile(filepath=self_library,
                    check_existing=False, copy=True)
            else:
                # make sure the file is up-to-date
                bpy.ops.wm.save_mainfile(check_existing=False)
            """
    
    def write_mesh(self, obj, stream):
        iofuncs = def_write_funcs(stream)
        # No faster way around. In Python 3.x, we have
        # to declare each local variable manually.
        write = iofuncs["write"]
        pack = iofuncs["pack"]
        write_str = iofuncs["write_str"]
        serializer_float = iofuncs["serializer_float"]
        serializer_int = iofuncs["serializer_int"]
        serializer_string = iofuncs["serializer_string"]
        serializer_deform = iofuncs["serializer_deform"]
        serializer_vector = iofuncs["serializer_vector"]
        serializer_color = iofuncs["serializer_color"]
        serializer_uv = iofuncs["serializer_uv"]
        serializer_tex = iofuncs["serializer_tex"]
        serializer_skin = iofuncs["serializer_skin"]
        serializer_freestyle = iofuncs["serializer_freestyle"]
        serializer_paint_mask = iofuncs["serializer_paint_mask"]
        
        serializers = {}
        serializers["verts.float"] = serializer_float
        serializers["verts.int"] = serializer_int
        serializers["verts.string"] = serializer_string
        serializers["verts.bevel_weight"] = serializer_float
        serializers["verts.deform"] = serializer_deform
        serializers["verts.shape"] = serializer_vector
        serializers["verts.skin"] = serializer_skin
        serializers["verts.paint_mask"] = serializer_paint_mask
        
        serializers["edges.float"] = serializer_float
        serializers["edges.int"] = serializer_int
        serializers["edges.string"] = serializer_string
        serializers["edges.bevel_weight"] = serializer_float
        serializers["edges.crease"] = serializer_float
        serializers["edges.freestyle"] = serializer_freestyle
        
        serializers["loops.float"] = serializer_float
        serializers["loops.int"] = serializer_int
        serializers["loops.string"] = serializer_string
        serializers["loops.color"] = serializer_color
        serializers["loops.uv"] = serializer_uv
        
        serializers["faces.float"] = serializer_float
        serializers["faces.int"] = serializer_int
        serializers["faces.string"] = serializer_string
        serializers["faces.tex"] = serializer_tex
        serializers["faces.freestyle"] = serializer_freestyle
        
        # A ~bug? Iterating layers.*.items() yields BMLayerItem,
        # and iterating layers.*.values() yields (item_name, BMLayerItem)
        
        # Seems like just removing all the unselected vertices is
        # the easiest way -- only the relevant edges, loops, faces
        # and layer data remain.
        # After removal, order of elements does not change,
        # and linked elements don't have to be checked for is_valid
        # (removed ones simply don't come up in the iteration).
        
        bm = bmesh.from_edit_mesh(obj.data).copy()
        
        i = 0
        with ChunkWriter(stream, "verts"):
            for v in bm.verts:
                if v.select:
                    write(pack('!ddd', *v.co))
                    v.index = i
                    i += 1
                else:
                    bm.verts.remove(v)
        
        i = 0
        with ChunkWriter(stream, "edges"):
            for e in bm.edges:
                for v in e.verts:
                    write(pack('!I', v.index))
                write(pack('!?', e.seam))
                write(pack('!?', e.smooth))
                e.index = i
                i += 1
        
        i = 0
        with ChunkWriter(stream, "faces"):
            for f in bm.faces:
                write(pack('!H', len(f.loops)))
                for l in f.loops:
                    write(pack('!I', l.vert.index))
                    write(pack('!I', l.edge.index))
                write(pack('!H', f.material_index))
                write(pack('!?', f.smooth))
                f.index = i
                i += 1
        
        select_types = {bmesh.types.BMVert:b'V',
                        bmesh.types.BMEdge:b'E',
                        bmesh.types.BMFace:b'F'}
        
        with ChunkWriter(stream, "select_history"):
            for elem in bm.select_history:
                write(select_types[type(elem)])
                write(pack('!I', elem.index))
        
        def serialize_loops():
            with ChunkWriter(stream, "loops"):
                for k in dir(bm.loops.layers):
                    if k.startswith("_"):
                        continue
                    
                    layers = getattr(bm.loops.layers, k)
                    
                    serializer = serializers["loops." + k]
                    
                    with ChunkWriter(stream, k):
                        for layer_name in layers.keys():
                            layer = layers[layer_name]
                            
                            with ChunkWriter(stream, layer_name):
                                for f in bm.faces:
                                    for l in f.loops:
                                        serializer(l[layer])
        
        with ChunkWriter(stream, "layers"):
            for seq_type in ("verts", "edges", "faces"):
                seq = getattr(bm, seq_type)
                seq_layers = seq.layers
                
                with ChunkWriter(stream, seq_type):
                    for k in dir(seq_layers):
                        if k.startswith("_"):
                            continue
                        
                        layers = getattr(seq_layers, k)
                        
                        serializer = serializers[seq_type + "." + k]
                        
                        with ChunkWriter(stream, k):
                            for layer_name in layers.keys():
                                layer = layers[layer_name]
                                
                                with ChunkWriter(stream, layer_name):
                                    for elem in seq:
                                        serializer(elem[layer])
                        
                        if seq_type == "faces":
                            # bm.loops (BMLoopsSeq) are not iterable %)
                            serialize_loops()
        
        bm.free()
    
    def write_curve(self, json_data, context):
        obj = context.object
        data = obj.data
        
        curve_buffers = {
            "splines":{
                "bezier_points":{
                    None:{"select":["select_control_point",
                                    "select_left_handle",
                                    "select_right_handle"]},
                    "co":None,
                    "handle_left":None,
                    "handle_left_type":None,
                    "handle_right":None,
                    "handle_right_type":None,
                    "radius":None,
                    "tilt":None,
                    "weight":None,
                },
                "material_index":None,
                "order_u":None,
                "order_v":None,
                "points":{
                    None:{"select":["select"]},
                    "co":None,
                    "radius":None,
                    "tilt":None,
                    "weight":None,
                    "weight_softbody":None,
                },
                "radius_interpolation":None,
                "resolution_u":None,
                "resolution_v":None,
                "tilt_interpolation":None,
                "type":None,
                "use_bezier_u":None,
                "use_bezier_v":None,
                "use_cyclic_u":None,
                "use_cyclic_v":None,
                "use_endpoint_u":None,
                "use_endpoint_v":None,
                "use_smooth":None,
            },
        }
        
        output = {"splines":[]}
        write_buffers(data, curve_buffers, output)
        
        # Remove splines without selected points
        spline = output["splines"][0]
        i = 0
        for j in range(len(spline["points"])):
            bezier_points = spline["bezier_points"][i]
            points = spline["points"][i]
            empty = not (bezier_points["co"] or points["co"])
            if empty:
                for k, v in spline.items():
                    v.pop(i)
            else:
                i += 1
        
        print()
        print(output)
        
        pass
    
    def write_meta(self, json_data, context):
        obj = context.object
        data = obj.data
        
        meta_buffers = {
            "elements":{
                # !!! Blender does not expose metaelement selection!
                #None:{"select":["select"]},
                "co":None,
                "radius":None,
                "rotation":None,
                "size_x":None,
                "size_y":None,
                "size_z":None,
                "stiffness":None,
                "type":None,
                "use_negative":None,
            },
        }
        
        output = {"elements":[]}
        write_buffers(data, meta_buffers, output)
        
        # Leave only active element
        element = output["elements"][0]
        i = 0
        for j in range(len(data.elements)):
            if data.elements[j] == data.elements.active:
                i += 1
            else:
                for k, v in element.items():
                    v.pop(i)
        
        print()
        print(output)
        
        pass
    
    def write_armature(self, json_data, context):
        obj = context.object
        data = obj.data
        
        armature_buffers = {
            "edit_bones":{
                #None:{"select":["select", "select_head", "select_tail"]},
                # No, better use just body selection status
                None:{"select":["select"]},
                "bbone_in":None,
                "bbone_out":None,
                "bbone_segments":None,
                "bbone_x":None,
                "bbone_z":None,
                "envelope_distance":None,
                "envelope_weight":None,
                "head":None,
                "head_radius":None,
                "layers":None,
                "lock":None,
                "matrix":None,
                "name":None,
                "parent":None,
                "roll":None,
                "show_wire":None,
                "tail":None,
                "tail_radius":None,
                "use_connect":None,
                "use_cyclic_offset":None,
                "use_deform":None,
                "use_envelope_multiply":None,
                "use_inherit_rotation":None,
                "use_inherit_scale":None,
                "use_local_location":None,
            },
        }
        
        output = {"edit_bones":[]}
        write_buffers(data, armature_buffers, output)
        
        print()
        print(output)
        
        pass
    
    def execute(self, context):
        wm = context.window_manager
        opts = addon.preferences
        
        json_data = {"content":"Blender 3D-clipboard"}
        
        json_data["cursor"] = tuple(context.space_data.cursor_location)
        
        if is_view3d(context):
            json_data["view"] = tuple(get_view_rotation(context))
        
        if 'EDIT' in context.mode:
            obj = context.object
            
            json_data["type"] = obj.type
            json_data["matrix"] = [tuple(v) for v in obj.matrix_world]
            
            if opts.external:
                stream = io.BytesIO()
            else:
                stream = open(data_clipboard_path(), "wb")
            
            if obj.type == 'MESH':
                self.write_mesh(obj, stream)
            elif obj.type in ('CURVE', 'SURFACE'):
                stream.close()
                return {'CANCELLED'} # for now
                self.write_curve(json_data, context)
            elif obj.type == 'META':
                stream.close()
                return {'CANCELLED'} # for now
                # !!! Since currently we can't access metaelement's
                # selection status from Python, copying metaelements
                # isn't very useful (though it might be worth to
                # at least make a crutch by copying the active element)
                #return {'CANCELLED'}
                self.write_meta(json_data, context)
            elif obj.type == 'ARMATURE':
                stream.close()
                return {'CANCELLED'} # for now
                self.write_armature(json_data, context)
            
            if opts.external:
                b = stream.getvalue()
                stream.close()
                json_data["data"] = compress_b64(b)
            else:
                stream.close()
        else:
            json_data["type"] = 'OBJECT'
            json_data["matrix"] = [tuple(v) for v in Matrix()]
            
            self.write_object(json_data, context)
        
        wm.clipboard = json.dumps(json_data, separators=(',',':'))
        
        if json_data["type"] == 'OBJECT':
            objs = json_data["objects"]
            if len(objs) > 1:
                self.report({'INFO'}, "Copy: {} objects".format(len(objs)))
            else:
                self.report({'INFO'}, "Copy: {}".format(tuple(objs)[0]))
        else:
            self.report({'INFO'}, "Copy: {} data".format(json_data["type"]))
        
        return {'FINISHED'}

@addon.Operator(idname="view3d.paste", label="Paste objects/elements", description="Paste objects/elements")
class OperatorPaste:
    data_types = {'OBJECT', 'MESH', 'CURVE', 'SURFACE', 'META', 'ARMATURE'}
    
    @classmethod
    def poll(cls, context):
        return context.mode in copy_paste_modes
    
    def read_clipboard_object(self, json_data, context):
        self.active_object = json_data.get("active_object", "")
        assert isinstance(self.active_object, str)
        
        active_object_library = json_data.get("active_object_library", "")
        active_object_library = str(active_object_library)
        
        self.parents = json_data.get("parents", {})
        assert isinstance(self.parents, dict)
        for k, v in self.parents.items():
            assert len(v) == 2
            assert isinstance(v[0], str) and isinstance(v[1], str)
        
        matrices = json_data.get("matrices", {})
        assert isinstance(matrices, dict)
        self.matrices = {}
        for k, v in matrices.items():
            self.matrices[k] = Matrix(matrices[k])
        
        objects = json_data["objects"]
        assert isinstance(objects, dict) and objects
        
        libraries = json_data["libraries"]
        assert isinstance(libraries, dict) and libraries
        
        # Make sure library paths are absolute and
        # that this file is marked a special way
        this_path = os.path.normcase(bpy.data.filepath)
        for id, lib_path in list(libraries.items()):
            assert isinstance(lib_path, str)
            if not lib_path:
                continue
            lib_path = os.path.normcase(bpy.path.abspath(lib_path))
            libraries[id] = ("" if lib_path == this_path else lib_path)
        
        self.active_object_library = libraries.get(active_object_library, None)
        
        # Gather all objects under their respective libraries
        self.libraries = {}
        for obj_name, id in objects.items():
            assert isinstance(obj_name, str)
            lib_path = libraries[str(id)]
            obj_names = self.libraries.get(lib_path)
            if not obj_names:
                obj_names = set()
                self.libraries[lib_path] = obj_names
            obj_names.add(obj_name)
    
    def read_clipboard(self, context):
        wm = context.window_manager
        
        json_data = json.loads(wm.clipboard)
        assert json_data["content"] == "Blender 3D-clipboard"
        
        self.data_type = json_data["type"]
        assert self.data_type in self.data_types
        
        self.matrix = Matrix(json_data["matrix"])
        assert len(self.matrix) == 4
        
        self.cursor = Vector(json_data.get("cursor", (0, 0, 0)))
        assert len(self.cursor) == 3
        
        self.view = Quaternion(json_data.get("view", Quaternion()))
        
        if self.data_type == 'OBJECT':
            self.read_clipboard_object(json_data, context)
        else:
            try:
                self.serialized_data = json_data.get("data")
                if self.serialized_data:
                    self.serialized_data = decompress_b64(self.serialized_data)
            except Exception as exc:
                # TODO: see what actual exceptions can appear
                print(exc)
                raise ValueError
        
        return json_data
    
    def add_pivot(self, p, active):
        p = p.to_3d()
        if self.pivot_count == 0:
            self.pivot_min = list(p)
            self.pivot_max = list(p)
        else:
            for i in range(3):
                self.pivot_min[i] = min(self.pivot_min[i], p[i])
                self.pivot_max[i] = max(self.pivot_max[i], p[i])
        self.pivot_average += p
        self.pivot_count += 1
        if active:
            self.pivot_active += p
            self.pivot_active_count += 1
    
    def calc_transform(self, context, obj):
        opts = addon.preferences
        coordsystem = opts.actual_coordsystem(context)
        not_local = (coordsystem != 'LOCAL')
        if not_local:
            transform = self.matrix * obj.matrix_world.inverted()
            transform_pivot = self.matrix
        else:
            transform = Matrix()
            transform_pivot = obj.matrix_world
        return not_local, transform, transform_pivot
    
    def process_object(self, context):
        if context.mode != 'OBJECT':
            self.report({'WARNING'},
                        "To paste objects, you must be in the Object mode")
            return True
        
        bpy.ops.object.select_all(action='DESELECT')
        
        opts = addon.preferences
        
        scene = context.scene
        
        old_to_new = {}
        new_to_old = {}
        
        def add_obj(new_obj, obj_name, lib_path):
            scene.objects.link(new_obj)
            
            new_obj.select = True
            
            if self.active_object_library is not None:
                if ((obj_name == self.active_object) and
                    (lib_path == self.active_object_library)):
                        scene.objects.active = new_obj
            
            old_to_new[obj_name] = new_obj
            new_to_old[new_obj] = obj_name
        
        load = bpy.data.libraries.load
        
        for lib_path, obj_names in self.libraries.items():
            if not lib_path:
                link = not opts.append
                for obj_name in obj_names:
                    try:
                        obj = scene.objects[obj_name]
                    except KeyError:
                        continue
                    new_obj = obj.copy()
                    if opts.append and obj.data:
                        new_obj.data = obj.data.copy()
                    add_obj(new_obj, obj_name, lib_path)
                continue
            
            if not os.path.isfile(lib_path):
                continue # report a warning?
            
            link = not (opts.append or is_clipboard_path(lib_path))
            
            obj_names = list(obj_names)
            
            with load(lib_path, link) as (data_from, data_to):
                data_to.objects = list(obj_names) # <-- ALWAYS COPY!
            
            for i, new_obj in enumerate(data_to.objects):
                if new_obj is not None:
                    add_obj(new_obj, obj_names[i], lib_path)
        
        scene.update()
        
        # Restore parent relations (Blender actually adds a relationship
        # if both parent and child are imported, but for some reason
        # the imported parent doesn't affect the imported children.
        # Also, on re-parenting the matrix has to be restored.)
        for obj, old_name in new_to_old.items():
            parent_info = self.parents.get(old_name, None)
            if parent_info:
                parent = old_to_new.get(parent_info[0])
                if parent:
                    obj.parent = parent
                    obj.parent_bone = parent_info[1]
            
            obj.matrix_world = self.matrices[old_name]
            
            is_active = (obj == scene.objects.active)
            self.add_pivot(obj.matrix_world.translation, is_active)
        
        # In Object mode the coordsystem option is not used
        # (ambiguous and the same effects can be achieved relatively easily)
        
        if opts.link_ghost_objects:
            # make sure all groups' objects are present at least in 1 scene (so that they can be deleted)
            # (to circumvent the [intentional] Blender behavior reported in https://developer.blender.org/T44890)
            for group in bpy.data.groups:
                for obj in group.objects:
                    if not obj: continue # apparently this can happen
                    if obj.users_scene: continue
                    scene.objects.link(obj)
    
    def process_mesh(self, context, stream):
        if context.mode not in {'OBJECT', 'EDIT_MESH', 'EDIT_CURVE'}:
            self.report({'WARNING'}, "Mesh data can be pasted only in Object, Edit Mesh and Edit Curve modes")
            return True
        
        if context.mode == 'EDIT_CURVE':
            bpy.ops.curve.select_all(action='DESELECT')
            
            obj = context.object
            self.process_mesh_curve(obj, context, stream)
        else:
            if context.mode == 'OBJECT':
                bpy.ops.object.select_all(action='DESELECT')
                
                mesh = bpy.data.meshes.new("PastedMesh")
                obj = bpy.data.objects.new("PastedMesh", mesh)
                if context.object:
                    obj.matrix_world = context.object.matrix_world.copy()
                
                context.scene.objects.link(obj)
                context.scene.update()
                context.scene.objects.active = obj
                obj.select = True
                
                with ToggleObjectMode('EDIT'):
                    self.process_mesh_mesh(obj, context, stream)
            else:
                bpy.ops.mesh.select_all(action='DESELECT')
                
                obj = context.object
                self.process_mesh_mesh(obj, context, stream)
    
    def process_mesh_curve(self, obj, context, stream):
        not_local, transform, transform_pivot = self.calc_transform(context, obj)
        
        iofuncs = def_read_funcs(stream)
        read = iofuncs["read"]
        unpack = iofuncs["unpack"]
        read_str = iofuncs["read_str"]
        read_H = iofuncs["read_H"]
        read_I = iofuncs["read_I"]
        read_bool = iofuncs["read_bool"]
        read_ddd = iofuncs["read_ddd"]
        
        verts = []
        with ChunkReader(stream, "verts") as chunk:
            while chunk:
                verts.append(read_ddd())
        
        connections = [[] for v in verts]
        
        edges = []
        with ChunkReader(stream, "edges") as chunk:
            while chunk:
                ei = len(edges)
                vi0 = read_I()
                connections[vi0].append(ei)
                vi1 = read_I()
                connections[vi1].append(ei)
                edges.append((vi0, vi1))
                read_bool() # seam
                read_bool() # smooth
        
        faces = []
        with ChunkReader(stream, "faces") as chunk:
            while chunk:
                f = []
                faces.append(f)
                n_loops = read_H()
                for i in range(n_loops):
                    f.append((read_I(), read_I()))
                read_H() # material_index
                read_bool() # smooth
        
        active_vertex = -1
        with ChunkReader(stream, "select_history") as chunk:
            elem_type = read(1)
            elem_id = read_I()
            if elem_type == b'V':
                active_vertex = elem_id
        
        used_edges = [False] * len(edges)
        
        splines = []
        cyclic_splines = []
        
        for f in faces:
            spline = []
            cyclic_splines.append(spline)
            
            for vi, ei in f:
                used_edges[ei] = True
                spline.append(vi)
        
        def other_vert(ei, vi):
            e = edges[ei]
            if e[0] == vi:
                return e[1]
            elif e[1] == vi:
                return e[0]
            return -1
        
        def other_edge(vi, ei):
            c = connections[vi]
            if len(c) != 2:
                return -1
            if c[0] == ei:
                return c[1]
            elif c[1] == ei:
                return c[0]
            return -1
        
        # link non-cyclic edges
        for vi, c in enumerate(connections):
            if len(c) == 2:
                continue
            
            vi0 = vi
            
            for ei in c:
                if used_edges[ei]:
                    continue
                
                spline = []
                splines.append(spline)
                
                vi = vi0
                while True:
                    spline.append(vi)
                    if ei == -1:
                        break
                    used_edges[ei] = True
                    vi = other_vert(ei, vi)
                    ei = other_edge(vi, ei)
        
        # link cyclic edges
        for vi, c in enumerate(connections):
            if (len(c) != 2) or used_edges[c[0]] or used_edges[c[1]]:
                continue
            
            ei = c[0]
            
            spline = []
            cyclic_splines.append(spline)
            
            while True:
                spline.append(vi)
                if (ei == -1) or used_edges[ei]:
                    break
                used_edges[ei] = True
                vi = other_vert(ei, vi)
                ei = other_edge(vi, ei)
        
        def set_point(point, vi):
            co = Vector(verts[vi])
            p = transform_pivot * co
            self.add_pivot(p, vi == active_vertex)
            if not_local:
                co = transform * co
            point.co = co.to_4d()
            point.select = True
        
        for s in cyclic_splines:
            spline = obj.data.splines.new('POLY')
            spline.use_cyclic_u = True
            points = spline.points
            points.add(len(s) - 1)
            for i, vi in enumerate(s):
                set_point(points[i], vi)
        
        for s in splines:
            spline = obj.data.splines.new('POLY')
            points = spline.points
            points.add(len(s) - 1)
            for i, vi in enumerate(s):
                set_point(points[i], vi)
    
    def process_mesh_mesh(self, obj, context, stream):
        not_local, transform, transform_pivot = self.calc_transform(context, obj)
        
        iofuncs = def_read_funcs(stream)
        read = iofuncs["read"]
        unpack = iofuncs["unpack"]
        read_str = iofuncs["read_str"]
        read_H = iofuncs["read_H"]
        read_I = iofuncs["read_I"]
        read_bool = iofuncs["read_bool"]
        read_ddd = iofuncs["read_ddd"]
        deserializer_float = iofuncs["deserializer_float"]
        deserializer_int = iofuncs["deserializer_int"]
        deserializer_string = iofuncs["deserializer_string"]
        deserializer_deform = iofuncs["deserializer_deform"]
        deserializer_vector = iofuncs["deserializer_vector"]
        deserializer_color = iofuncs["deserializer_color"]
        deserializer_uv = iofuncs["deserializer_uv"]
        deserializer_tex = iofuncs["deserializer_tex"]
        deserializer_skin = iofuncs["deserializer_skin"]
        deserializer_freestyle = iofuncs["deserializer_freestyle"]
        deserializer_paint_mask = iofuncs["deserializer_paint_mask"]
        
        deserializers = {}
        deserializers["verts.float"] = deserializer_float
        deserializers["verts.int"] = deserializer_int
        deserializers["verts.string"] = deserializer_string
        deserializers["verts.bevel_weight"] = deserializer_float
        deserializers["verts.deform"] = deserializer_deform
        deserializers["verts.shape"] = deserializer_vector
        deserializers["verts.skin"] = deserializer_skin
        deserializers["verts.paint_mask"] = deserializer_paint_mask
        
        deserializers["edges.float"] = deserializer_float
        deserializers["edges.int"] = deserializer_int
        deserializers["edges.string"] = deserializer_string
        deserializers["edges.bevel_weight"] = deserializer_float
        deserializers["edges.crease"] = deserializer_float
        deserializers["edges.freestyle"] = deserializer_freestyle
        
        deserializers["loops.float"] = deserializer_float
        deserializers["loops.int"] = deserializer_int
        deserializers["loops.string"] = deserializer_string
        deserializers["loops.color"] = deserializer_color
        deserializers["loops.uv"] = deserializer_uv
        
        deserializers["faces.float"] = deserializer_float
        deserializers["faces.int"] = deserializer_int
        deserializers["faces.string"] = deserializer_string
        deserializers["faces.tex"] = deserializer_tex
        deserializers["faces.freestyle"] = deserializer_freestyle
        
        if 'EDIT' in obj.mode:
            bm = bmesh.from_edit_mesh(obj.data)
        else:
            bm = bmesh.new()
        
        verts = []
        edges = []
        faces = []
        
        with ChunkReader(stream, "verts") as chunk:
            while chunk:
                v = bm.verts.new(read_ddd())
                verts.append(v)
                v.select = True
        
        with ChunkReader(stream, "edges") as chunk:
            while chunk:
                vi0 = read_I()
                vi1 = read_I()
                e = bm.edges.new((verts[vi0], verts[vi1]))
                edges.append(e)
                e.select = True
                e.seam = read_bool()
                e.smooth = read_bool()
        
        with ChunkReader(stream, "faces") as chunk:
            while chunk:
                f = bm.faces.new(verts[(read_I(), read_I())[0]]
                                 for i in range(read_H()))
                faces.append(f)
                f.select = True
                f.material_index = read_H()
                f.smooth = read_bool()
        
        active_verts = ()
        
        bm.select_history.clear()
        with ChunkReader(stream, "select_history") as chunk:
            while chunk:
                elem_type = read(1)
                elem_id = read_I()
                if elem_type == b'V':
                    elem = verts[elem_id]
                    active_verts = (elem,)
                elif elem_type == b'E':
                    elem = edges[elem_id]
                    active_verts = elem.verts
                elif elem_type == b'F':
                    elem = faces[elem_id]
                    active_verts = elem.verts
                bm.select_history.add(elem)
        
        chunk = ChunkReader(stream)
        if chunk.name == "layers":
            elems = {"verts":verts, "edges":edges, "faces":faces}
            chunk_layers = chunk
            
            while chunk_layers:
                chunk_seq = ChunkReader(stream)
                seq_type = chunk_seq.name
                seq = getattr(bm, seq_type)
                seq_layers = seq.layers
                
                while chunk_seq:
                    chunk_k = ChunkReader(stream)
                    k = chunk_k.name
                    
                    if (seq_type == "faces") and (k == "loops"):
                        chunk_loops = chunk_k
                        while chunk_loops:
                            chunk_k = ChunkReader(stream)
                            k = chunk_k.name
                            
                            layers = getattr(bm.loops.layers, k)
                            deserializer = deserializers["loops." + k]
                            
                            while chunk_k:
                                chunk_layer = ChunkReader(stream)
                                layer_name = chunk_layer.name
                                layer = layers.get(layer_name)
                                if not layer:
                                    #layer = layers.new(layer_name)
                                    chunk_layer.skip()
                                    continue
                                
                                while chunk_layer:
                                    for f in faces:
                                        for l in f.loops:
                                            deserializer(l, layer)
                        continue
                    
                    layers = getattr(seq_layers, k)
                    deserializer = deserializers[seq_type + "." + k]
                    
                    while chunk_k:
                        chunk_layer = ChunkReader(stream)
                        layer_name = chunk_layer.name
                        layer = layers.get(layer_name)
                        if not layer:
                            # Creating a new layer invalidates old elements!
                            #layer = layers.new(layer_name)
                            chunk_layer.skip()
                            continue
                        
                        while chunk_layer:
                            for elem in elems[seq_type]:
                                deserializer(elem, layer)
        
        for v in verts:
            # ATTENTION!
            # Vector can be transformed only via M*V, not V*M!
            p = transform_pivot * v.co
            if not_local:
                v.co = transform * v.co
            self.add_pivot(p, v in active_verts)
        
        bm.normal_update()
        
        if 'EDIT' not in obj.mode:
            bm.to_mesh(obj.data)
            bm.free()
    
    def process_curve(self, context):
        if context.mode not in {'OBJECT', 'EDIT_MESH', 'EDIT_CURVE'}:
            self.report({'WARNING'}, "Curve data can be pasted only in Object, Edit Mesh and Edit Curve modes")
            return True
    
    def process_surface(self, context):
        if context.mode not in {'OBJECT', 'EDIT_SURFACE'}:
            self.report({'WARNING'}, "Surface data can be pasted only in Object and Edit Surface modes")
            return True
    
    def process_meta(self, context):
        if context.mode not in {'OBJECT', 'EDIT_MESH', 'EDIT_METABALL'}:
            self.report({'WARNING'}, "Metaelement data can be pasted only in Object, Edit Mesh and Edit Meta modes")
            return True
    
    def process_armature(self, context):
        if context.mode not in {'OBJECT', 'EDIT_MESH', 'EDIT_ARMATURE'}:
            self.report({'WARNING'}, "Armature data can be pasted only in Object, Edit Mesh and Edit Armature modes")
            return True
    
    def execute(self, context):
        try:
            json_data = self.read_clipboard(context)
        except (TypeError, KeyError, ValueError, AssertionError):
            self.report({'WARNING'}, "Incompatible format of clipboard data")
            return {'CANCELLED'}
        
        opts = addon.preferences
        
        pivot_mode = context.space_data.pivot_point
        self.pivot_count = 0
        self.pivot_min = None
        self.pivot_max = None
        self.pivot_average = Vector()
        self.pivot_active = Vector()
        self.pivot_active_count = 0
        
        bpy.ops.ed.undo_push(message="Before Paste")
        
        if self.data_type == 'OBJECT':
            if self.process_object(context):
                bpy.ops.ed.undo()
                return {'CANCELLED'}
        else:
            handler = getattr(self, "process_" + self.data_type.lower())
            
            if self.serialized_data:
                stream = io.BytesIO(self.serialized_data)
            else:
                stream = open(data_clipboard_path(), "rb")
                #stream = io.BufferedReader(stream)
            
            if handler(context, stream):
                stream.close()
                bpy.ops.ed.undo()
                return {'CANCELLED'}
            stream.close()
            
            """
            try:
                if handler(context):
                    bpy.ops.ed.undo()
                    return {'CANCELLED'}
            except Exception as exc:
                # TODO: catch specific exceptions
                print(exc)
                bpy.ops.ed.undo()
                self.report({'WARNING'},
                            "Incompatible format of clipboard data")
                return {'CANCELLED'}
            """
        
        if self.pivot_count == 0:
            # No objects were added %)
            #bpy.ops.ed.undo()
            return {'CANCELLED'}
        
        pivot = (Vector(self.pivot_min) + Vector(self.pivot_max)) * 0.5
        if pivot_mode == 'ACTIVE_ELEMENT':
            if self.pivot_active_count:
                pivot = self.pivot_active * (1.0 / self.pivot_active_count)
        elif pivot_mode in ('MEDIAN_POINT', 'INDIVIDUAL_ORIGINS'):
            pivot = self.pivot_average * (1.0 / self.pivot_count)
        elif pivot_mode == 'CURSOR':
            pivot = self.cursor
        
        do_transform = opts.append or ("" in self.libraries)
        
        if is_view3d(context) and do_transform:
            if opts.paste_at_cursor:
                v3d = context.space_data
                cursor = v3d.cursor_location
                bpy.ops.transform.translate(value=(cursor - pivot), proportional='DISABLED')
                pivot = cursor
            
            if opts.align_to_view:
                view = get_view_rotation(context)
                dq = view * self.view.inverted()
                axis, angle = dq.to_axis_angle()
                bpy.ops.transform.rotate('EXEC_SCREEN', value=angle, axis=axis, proportional='DISABLED')
            
            if opts.move_to_mouse:
                region = context.region
                rv3d = context.region_data
                coord = self.mouse_coord
                dest = region_2d_to_location_3d(region, rv3d, coord, pivot)
                bpy.ops.transform.translate(value=(dest - pivot), proportional='DISABLED')
        
        bpy.ops.ed.undo_push(message="Paste")
        
        if json_data["type"] == 'OBJECT':
            objs = json_data["objects"]
            if len(objs) > 1:
                self.report({'INFO'}, "Paste: {} objects".format(len(objs)))
            else:
                self.report({'INFO'}, "Paste: {}".format(tuple(objs)[0]))
        else:
            self.report({'INFO'}, "Paste: {} data".format(json_data["type"]))
        
        if do_transform:
            return bpy.ops.transform.transform('INVOKE_DEFAULT')
        else:
            return {'FINISHED'}
    
    def invoke(self, context, event):
        self.mouse_coord = Vector((event.mouse_region_x, event.mouse_region_y))
        return self.execute(context)

@addon.Operator(idname="view3d.cut", label="Cut objects/elements", description="Cut objects/elements")
class OperatorCut:
    @classmethod
    def poll(cls, context):
        return bpy.ops.view3d.copy.poll()
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Before Cut")
        bpy.ops.view3d.copy(force_copy=True)
        
        if 'EDIT' in context.mode:
            obj = bpy.context.object
            
            if obj.type == 'MESH':
                bm = bmesh.from_edit_mesh(obj.data)
                
                for v in bm.verts:
                    if v.select:
                        can_remove = True
                        for e in v.link_edges:
                            if not e.select:
                                can_remove = False
                                break
                        if can_remove:
                            for f in v.link_faces:
                                if not f.select:
                                    can_remove = False
                                    break
                            if can_remove:
                                bm.verts.remove(v)
                
                for e in bm.edges:
                    if e.select:
                        can_remove = True
                        for f in e.link_faces:
                            if not f.select:
                                can_remove = False
                                break
                        if can_remove:
                            bm.edges.remove(e)
                
                for f in bm.faces:
                    if f.select:
                        bm.faces.remove(f)
        else:
            # Maybe just use Delete operator? (if it doesn't create Undo entry)
            for obj in list(context.selected_objects):
                context.scene.objects.unlink(obj)
                # Don't remove if they have zero users, since they are still needed for appending/linking
                if obj.users == 0:
                    bpy.data.objects.remove(obj)
        
        bpy.ops.ed.undo_push(message="Cut")
        
        context.area.tag_redraw()
        
        return {'FINISHED'}

@addon.Preferences.Include
class ThisAddonPreferences:
    external = True | prop("Allow copy/paste to/from other file(s)", "External")
    append = True | prop("Append new objects (instead of link)", "Append")
    link_ghost_objects = True | prop("When pasting, link to current scene all group objects that aren't linked to any scene", "Link ghost objects")
    paste_at_cursor = True | prop("Paste at the Cursor (instead of the coordinate system origin)", "Paste at Cursor")
    move_to_mouse = True | prop("Align pivot of pasted objects to the mouse location", "Move to mouse")
    align_to_view = False | prop("Rotate pasted objects to match their orientation relative to view when they were copied", "Align to view")
    coordinate_system = 'CONTEXT' | prop("A coordinate system to copy/paste in (ignored in Object mode)", "Coordinate System", items=[
        ('CONTEXT', "Context", "Local in Edit mode, Global otherwise"),
        ('GLOBAL', "Global", "Global"),
        ('LOCAL', "Local", "Local"),
    ])
    
    force_copy = True | prop("Always save clipbuffer to disk", "Force full copy")
    
    def actual_coordsystem(self, context=None):
        if self.coordinate_system == 'CONTEXT':
            is_edit = ('EDIT' in (context or bpy.context).mode)
            return ('LOCAL' if is_edit else 'GLOBAL')
        return self.coordinate_system
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        layout.prop(self, "force_copy")

def register():
    addon.register()
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.copy', 'C', 'PRESS', ctrl=True)
        kmi = km.keymap_items.new('view3d.paste', 'V', 'PRESS', ctrl=True)
        kmi = km.keymap_items.new('view3d.cut', 'X', 'PRESS', ctrl=True)
        kmi = km.keymap_items.new('view3d.copy', 'INSERT', 'PRESS', ctrl=True)
        kmi = km.keymap_items.new('view3d.paste', 'INSERT', 'PRESS', shift=True)
        kmi = km.keymap_items.new('view3d.cut', 'DEL', 'PRESS', shift=True)

def unregister():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # Note: if we remove from non-addon keyconfigs, the keymap registration
        # won't work on the consequent addon enable/reload (until Blender restarts)
        KeyMapUtils.remove("view3d.copy", place=kc)
        KeyMapUtils.remove("view3d.paste", place=kc)
        KeyMapUtils.remove("view3d.cut", place=kc)
    
    addon.unregister()
