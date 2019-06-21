import bpy
import bmesh

from math import radians
from statistics import median

from mathutils import Matrix, Vector

from bpy.types import Operator

from . shader import snap
from ... utility import addon, object, ray, modifier, modal


class BC_OT_display_snap(Operator):
    bl_idname = 'bc.display_snap'
    bl_label = 'Snap'
    bl_description = 'Snap'
    bl_options = {'INTERNAL'}

    hit: bool = False
    index: int = 0
    highlight: bool = False
    highlight_indices: list = []

    view_fallback: bool = False
    bc_start: bool = False

    location: Vector = (0, 0, 0)

    active_point = None
    original_region = None


    def invoke(self, context, event):
        preference = addon.preference()
        self.original_region = bpy.context.region

        bc = bpy.context.window_manager.bc

        if bc.running:
            return {'CANCELLED'}

        bc.snap.display = True

        align_to_view = False
        active_only = False
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')
                align_to_view = option.align_to_view
                active_only = True if len(context.selected_objects) > 1 and option.active_only else False

        bc.snap.grid = preference.surface in {'CURSOR', 'CENTER'} or align_to_view
        surface = preference.surface == 'OBJECT' and not bc.snap.grid

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        if bc.snap.display:
            hit = False

            if surface and context.active_object and context.active_object.select_get() and context.active_object.type == 'MESH':
                bc.snap.grid = False
                bc.snap.object = context.active_object if not active_only else [obj for obj in context.selected_objects if obj != context.active_object][-1]

                bc.snap.mesh = bc.snap.object.to_mesh(bpy.context.depsgraph, apply_modifiers=True)

            else:
                bc.snap.grid = True
                bc.snap.mesh = bpy.data.meshes.new(name='snap_mesh')

                bm = bmesh.new()
                bmesh.ops.create_grid(bm, x_segments=21, y_segments=21, size=10.0)

                bm.to_mesh(bc.snap.mesh)
                bm.free()

                axis = preference.cursor_axis
                current = {
                    'X': 'Y',
                    'Y': 'X',
                    'Z': 'Z'}

                if preference.surface == 'CURSOR':
                    matrix = context.scene.cursor.rotation_euler.to_matrix().to_4x4()
                    matrix.translation = context.scene.cursor.location

                    rotation = Matrix.Rotation(radians(-90 if axis in {'X', 'Y'} else 90), 4, current[axis])

                    matrix = matrix @ rotation

                else:
                    matrix = Matrix.Rotation(radians(-90 if axis in {'X', 'Y'} else 90), 4, current[axis])

                bc.snap.mesh.transform(matrix)

            hit, location, self.normal, self.index = ray.cast.objects(*self.mouse, mesh=bc.snap.mesh, snap=True)

            if (not hit or align_to_view) and context.selected_objects: # view aligned
                bc.snap.object = None
                bc.snap.grid = True
                bc.snap.mesh = bpy.data.meshes.new(name='snap_mesh')
                box = None

                bm = bmesh.new()
                bmesh.ops.create_grid(bm, x_segments=21, y_segments=21, size=10.0)

                bm.to_mesh(bc.snap.mesh)
                bm.free()

                if context.active_object:
                    box = bpy.data.objects.new(name='Box', object_data=bc.snap.mesh)
                    bpy.context.scene.collection.objects.link(box)

                    mod = box.modifiers.new(name='Displace', type='DISPLACE')

                    obj = context.active_object
                    mod.strength = max(dimension for dimension in Vector((obj.dimensions.x, obj.dimensions.y, obj.dimensions.z))) * 1.75
                    modifier.apply(obj=box, mod=mod)

                    del mod

                    bpy.data.meshes.remove(bc.snap.mesh)
                    bc.snap.mesh = box.data

                bc.snap.mesh.transform(context.region_data.view_rotation.to_euler().to_matrix().to_4x4())

                if context.active_object:
                    matrix = Matrix()
                    matrix.translation = context.active_object.matrix_world @ object.center(context.active_object)

                    bc.snap.mesh.transform(matrix)

                hit, location, self.normal, self.index = ray.cast.objects(*self.mouse, mesh=bc.snap.mesh, snap=True)

                if box:
                    bpy.data.objects.remove(box)

                    del box

        if bc.snap.object or bc.snap.mesh:
            modal.snap.collect(self, bc.snap)
            modal.snap.update(self, bc.snap)

        context.window_manager.modal_handler_add(self)
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(snap, (self, context), 'WINDOW', 'POST_PIXEL')

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        bc = context.window_manager.bc
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        update = bool(bc.snap.object) or bool(bc.snap.mesh)
        bc_reset = update and (bc.running and not self.bc_start)

        if not event.ctrl or context.region != self.original_region or bc.running:
            self.exit()

            return {'CANCELLED'}

        elif event.type == 'MOUSEMOVE' and not self.highlight or bc_reset:
            hit, location, self.normal, self.index = ray.cast.objects(self.mouse.x, self.mouse.y, mesh=bc.snap.mesh, snap=True)

            if not hit and bc.snap.points or bc_reset:
                bc.snap.points.clear()

            if update and self.index != bc.snap.index or bc_reset:
                modal.snap.collect(self, bc.snap)

        if update or bc_reset:
            modal.snap.update(self, bc.snap)

        if bc_reset:
            self.bc_start = True

        if self.bc_start and not bc.running:
            self.bc_start = False

        if event.type in {'N', 'Z'}:
            self.exit()

            pointers = {
                'original_active': '',
                'lattice': '',
                'slice': '',
                'inset': '',
                'plane': '',
                'stored_shape': '',
                'stored_collection': '',
                'collection': '',
                'shape': '',
                'targets': []}

            for pointer in pointers:

                if pointer != 'targets':
                    pointers[pointer] = getattr(bc, pointer).name if getattr(bc, pointer) else ''
                    setattr(bc, pointer, None)

                else:
                    for obj in [obj for obj in bpy.data.objects[:] if obj.type == 'MESH' and obj.bc.target]:
                        pointers['targets'].append((obj.name, obj.bc.target.name))

            bc.snap.object = None
            bc.snap.mesh = None

            if event.type == 'Z':
                bpy.ops.ed.undo()

                for name in pointers:
                    if name not in {'collection', 'stored_collection', 'targets'} and pointers[name] in bpy.data.objects:
                        setattr(bc, pointer, bpy.data.objects[pointers[name]])

                    elif name == 'targets':
                        for target in pointers['targets']:

                            if target[0] in bpy.data.objects and target[1] in bpy.data.objects:
                                bpy.data.objects[target[0]].bc.target = bpy.data.objects[target[1]]

                    elif pointers[name] in bpy.data.collections:
                        setattr(bc, pointer, bpy.data.collections[pointers[name]])
            else:
                bpy.ops.wm.read_homefile('INVOKE_DEFAULT')

            del pointers

            return {'CANCELLED'}

        context.area.tag_redraw()

        return {'PASS_THROUGH'}


    def exit(self):
        bc = bpy.context.window_manager.bc
        bc.snap.display = False

        self.active_point = None

        bc.snap.hit = False
        bc.snap.location = (0.0, 0.0, 0.0)
        bc.snap.normal = Vector()
        bc.snap.object = None

        if bc.snap.mesh:
            bpy.data.meshes.remove(bc.snap.mesh)

        bc.snap.mesh = None
        bc.snap.index = int()
        bc.snap.points.clear()

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')

        del self.draw_handler
        del self.original_region
