# ##### BEGIN MIT LICENSE BLOCK #####
# MIT License
# 
# Copyright (c) 2018 Insma Software
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ##### END MIT LICENSE BLOCK #####

# ----------------------------------------------------------
# Author: Maciej Klemarczyk (mklemarczyk)
# ----------------------------------------------------------
import bpy
from bpy.types import Operator, PropertyGroup, Object, Panel
from bpy.props import FloatProperty, CollectionProperty
from .archlab_utils import *
from .archlab_utils_mesh_generator import *

# ------------------------------------------------------------------------------
# Create main object for the bench.
# ------------------------------------------------------------------------------
def create_bench(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create main object and mesh for bench
    benchmesh = bpy.data.meshes.new("Bench")
    benchobject = bpy.data.objects.new("Bench", benchmesh)
    benchobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(benchobject)
    benchobject.ArchLabBenchGenerator.add()

    benchobject.ArchLabBenchGenerator[0].bench_height = self.bench_height
    benchobject.ArchLabBenchGenerator[0].bench_width = self.bench_width
    benchobject.ArchLabBenchGenerator[0].bench_depth = self.bench_depth
    
    # we shape the mesh.
    shape_bench_mesh(benchobject, benchmesh)

    # we select, and activate, main object for the bench.
    benchobject.select = True
    bpy.context.scene.objects.active = benchobject

# ------------------------------------------------------------------------------
# Shapes mesh and creates modifier solidify (the modifier, only the first time).
# ------------------------------------------------------------------------------
def shape_bench_mesh(mybench, tmp_mesh, update=False):
    sp = mybench.ArchLabBenchGenerator[0]  # "sp" means "bench properties".
    # Create bench mesh data
    update_bench_mesh_data(tmp_mesh, sp.bench_width, sp.bench_height, sp.bench_depth)
    mybench.data = tmp_mesh

    remove_doubles(mybench)
    set_normals(mybench)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != mybench.name:
            o.select = False

# ------------------------------------------------------------------------------
# Creates bench mesh data.
# ------------------------------------------------------------------------------
def update_bench_mesh_data(mymesh, width, height, depth):
    (myvertices, myedges, myfaces) = generate_mesh_from_library(
        'BenchN',
        size=(width, depth, height)
    )

    mymesh.from_pydata(myvertices, myedges, myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Update bench mesh.
# ------------------------------------------------------------------------------
def update_bench(self, context):
    # When we update, the active object is the main object of the bench.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that bench object to not delete it.
    o.select = False
    # and we create a new mesh for the bench:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_bench_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the bench.
    o.select = True
    bpy.context.scene.objects.active = o

# -----------------------------------------------------
# Property definition creator
# -----------------------------------------------------
def bench_height_property(callback=None):
    return FloatProperty(
            name='Height',
            soft_min=0.001,
            default=0.45, precision=3, unit = 'LENGTH',
            description='Bench height', update=callback,
            )

def bench_width_property(callback=None):
    return FloatProperty(
            name='Width',
            soft_min=0.001,
            default=1.20, precision=3, unit = 'LENGTH',
            description='Bench width', update=callback,
            )

def bench_depth_property(callback=None):
    return FloatProperty(
            name='Depth',
            soft_min=0.001,
            default=0.34, precision=3, unit = 'LENGTH',
            description='Bench depth', update=callback,
            )

# ------------------------------------------------------------------
# Define property group class to create or modify a benchs.
# ------------------------------------------------------------------
class ArchLabBenchProperties(PropertyGroup):
    bench_height = bench_height_property(callback=update_bench)
    bench_width = bench_width_property(callback=update_bench)
    bench_depth = bench_depth_property(callback=update_bench)

bpy.utils.register_class(ArchLabBenchProperties)
Object.ArchLabBenchGenerator = CollectionProperty(type=ArchLabBenchProperties)

# ------------------------------------------------------------------
# Define panel class to modify benchs.
# ------------------------------------------------------------------
class ArchLabBenchGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_bench_generator"
    bl_label = "Bench"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'ArchLab'

    # -----------------------------------------------------
    # Verify if visible
    # -----------------------------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        act_op = context.active_operator
        if o is None:
            return False
        if 'ArchLabBenchGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_bench'):
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabBenchGenerator', this panel is not created.
        try:
            if 'ArchLabBenchGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            bench = o.ArchLabBenchGenerator[0]
            row = layout.row()
            row.prop(bench, 'bench_width')
            row = layout.row()
            row.prop(bench, 'bench_height')
            row = layout.row()
            row.prop(bench, 'bench_depth')

# ------------------------------------------------------------------
# Define operator class to create benchs
# ------------------------------------------------------------------
class ArchLabBench(Operator):
    bl_idname = "mesh.archlab_bench"
    bl_label = "Add Bench"
    bl_description = "Generate bench mesh"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    bench_height = bench_height_property()
    bench_width = bench_width_property()
    bench_depth = bench_depth_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            row = layout.row()
            row.prop(self, 'bench_width')
            row = layout.row()
            row.prop(self, 'bench_height')
            row = layout.row()
            row.prop(self, 'bench_depth')
        else:
            row = layout.row()
            row.label("Warning: Operator does not work in local view mode", icon='ERROR')

    # -----------------------------------------------------
    # Execute
    # -----------------------------------------------------
    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            space = bpy.context.space_data
            if not space.local_view:
                create_bench(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
