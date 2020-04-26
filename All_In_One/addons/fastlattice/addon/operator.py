import bpy

from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty

from .config import defaults as default
from . import interface, utilities


class fast_lattice(Operator):
    bl_idname = 'object.fast_lattice'
    bl_label = 'Create Lattice'
    bl_description = 'Create and edit a lattice that effects and conforms to the selection'
    bl_options = {'REGISTER', 'UNDO'}

    show_wire = BoolProperty(
        name = 'Wire',
        description = 'Add the object(s) wireframe over solid drawing',
        update = utilities.update,
        default = default['show_wire']
    )

    show_all_edges = BoolProperty(
        name = 'Draw All Edges',
        description = 'Draw all edges for mesh objects',
        update = utilities.update,
        default = default['show_all_edges']
    )

    @classmethod
    def poll(cls, context):

        return context.object and context.object.type == 'MESH' and context.object.mode == 'EDIT' and context.object.data.total_vert_sel > 2 and not context.area.spaces.active.local_view or context.object and context.object.type == 'MESH' and context.object.mode == 'OBJECT'


    def draw(self, context):

        interface.operator(self, context)


    def execute(self, context):

        self.mesh_object = context.object.name

        utilities.lattice(self, context)

        return {'FINISHED'}


class fast_lattice_cleanup(Operator):
    bl_idname = 'object.fast_lattice_cleanup'
    bl_label = 'Finished'
    bl_description = 'Finalize the fast lattice operation.'
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        utilities.cleanup(context)

        return {'FINISHED'}
