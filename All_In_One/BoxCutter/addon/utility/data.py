import bpy
import bmesh

from mathutils import Vector

from . import addon, lattice, mesh, modifier, update

from .. interface.operator import last


def create(ot, context, event):
    mesh.create.shape(ot, context, event)

    lattice.create(ot, context, event)


#TODO: select perimeter of selection after cut
def clean(ot, all=False, dead=False, init=False):
    from . import object

    global last

    preference = addon.preference()

    if not dead and not all:
        update.modal.display_modifiers(ot, display=True)
        original_mode = bpy.context.workspace.tools_mode

        if original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            addon.log(value='Changed to object mode', indent=2)

        last['origin'] = ot.origin
        last['coord']['points'] = [Vector(point.co_deform) for point in ot.datablock['lattice'].data.points]

        for mod in ot.datablock['shape'].modifiers:
            if mod.type == 'ARRAY':
                offsets = [abs(o) for o in mod.relative_offset_displace]
                if sum(offsets) < 0.0005:
                    ot.datablock['shape'].modifiers.remove(mod)
                    continue

                index = offsets.index(max(offsets))
                last['modifier']['offset'] = mod.relative_offset_displace[index]
                last['modifier']['count'] = mod.count

            elif mod.type == 'BEVEL':
                if mod.width < 0.001:
                    ot.datablock['shape'].modifiers.remove(mod)
                    continue

                last['modifier']['width'] = mod.width if mod.width > last['modifier']['width'] else last['modifier']['width']
                last['modifier']['segments'] = mod.segments

        if not ot.repeat:
            duplicate = object.duplicate(ot.datablock['shape'], link=False)

            modifier.apply(obj=duplicate)
            last['coord']['geometry']['verts'] = [vertex.co.copy() for vertex in duplicate.data.vertices]
            last['coord']['geometry']['edges'] = duplicate.data.edge_keys[:]
            last['coord']['geometry']['faces'] = [face.vertices[:] for face in duplicate.data.polygons]

            bpy.data.meshes.remove(duplicate.data)

        modifier.apply(obj=ot.datablock['shape'], exclude=[mod for mod in ot.datablock['shape'].modifiers if (mod.type == 'ARRAY' or mod.type == 'BEVEL') and not ot.mode == 'KNIFE'])

        if preference.display_wires:
            for obj in ot.datablock['targets']:
                obj.show_wire = not obj.show_wire
                obj.show_all_edges = not obj.show_all_edges

            for obj in ot.datablock['slices']:
                obj.show_wire = not obj.show_wire
                obj.show_all_edges = not obj.show_all_edges

        if ot.mode == 'KNIFE':
            original_active = bpy.context.active_object
            original_selected = bpy.context.selected_objects[:]

            for obj in original_selected:
                obj.select_set(False)

            dat = bpy.data.meshes.new(name='Duplicate')

            duplicate = bpy.data.objects.new(name='Duplicate', object_data=dat)
            bpy.data.collections['Cutters'].objects.link(duplicate)
            duplicate.select_set(True)
            bpy.context.view_layer.objects.active = duplicate

            for obj in ot.datablock['targets']:
                bm = bmesh.new()

                bm.from_mesh(ot.datablock['shape'].data)
                bm.verts.ensure_lookup_table()

                obj_matrix = obj.matrix_world.copy()
                shape_matrix = ot.datablock['shape'].matrix_world.copy()
                shape_matrix.translation -= obj_matrix.translation
                obj_matrix.translation = Vector((0, 0, 0))

                for v in bm.verts:
                    v.tag = True
                    v.co = shape_matrix @ v.co

                bm.from_mesh(obj.data)
                bm.verts.ensure_lookup_table()

                indices = {v.index for v in bm.verts if v.tag}

                for v in bm.verts:
                    v.select = v.tag

                    if not v.tag:
                        v.co = obj_matrix @ v.co

                    v.co = obj_matrix.inverted() @ v.co

                bm.select_flush(False)

                bm.to_mesh(duplicate.data)
                duplicate.data.validate()
                bm.free()

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.scene.tool_settings.mesh_select_mode = (True, False, False)
                bpy.ops.mesh.intersect()
                bpy.ops.mesh.select_all(action='DESELECT')

                bpy.ops.object.mode_set(mode='OBJECT')

                for index in indices:
                    duplicate.data.vertices[index].select = True

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_linked()
                bpy.ops.mesh.delete()

                bpy.ops.object.mode_set(mode='OBJECT')

                old_name = obj.data.name
                obj.data.bc.removeable = True
                obj.data = duplicate.data
                obj.data.name = old_name
                obj.data.use_auto_smooth = True

                duplicate.data = bpy.data.meshes.new(name='Duplicate')

            bpy.context.view_layer.objects.active = original_active
            bpy.data.objects.remove(duplicate)
            bpy.data.objects.remove(ot.datablock['shape'])

            for obj in original_selected:
                obj.select_set(True)

        elif ot.behavior == 'DESTRUCTIVE' and not ot.show_shape and ot.datablock['targets']:
            for obj in ot.datablock['targets']:
                modifier.apply(obj, mod=modifier.shape_bool(ot, obj))

            if ot.datablock['slices']:

                for obj in ot.datablock['slices']:
                    modifier.apply(obj, mod=modifier.shape_bool(ot, obj))

            bpy.data.objects.remove(ot.datablock['shape'])

            addon.log(value='Applied cutter', indent=2)

        elif ot.mode != 'KNIFE':
            ot.datablock['shape'].bc.applied = True
            ot.datablock['shape'].hide_viewport = not ot.show_shape
            ot.datablock['shape'].show_all_edges = False
            ot.datablock['shape'].show_in_front = False

        addon.log(value=F'Removed lattice object: {ot.datablock["lattice"].name}', indent=2)
        bpy.data.objects.remove(ot.datablock['lattice'])

        addon.log(value=F'Removed plane object: {ot.datablock["plane"].name}', indent=2)
        bpy.data.objects.remove(ot.datablock['plane'])

        for mesh in bpy.data.meshes:
            if mesh.bc.removeable:
                addon.log(value=F'Removed mesh data: {mesh.name}', indent=2)
                bpy.data.meshes.remove(mesh)

        for lat in bpy.data.lattices:
            if lat.bc.removeable:
                addon.log(value=F'Removed lattice data: {lat.name}', indent=2)
                bpy.data.lattices.remove(lat)

        if original_mode == 'EDIT_MESH':
            for obj in ot.datablock['slices']:
                obj.hide_viewport = False

            addon.log(value='Displayed slice objects', indent=2)

            if addon.preference().use_multi_edit:
                for obj in ot.datablock['slices']:
                    obj.select_set(state=True)
                addon.log(value='Selecting slice objects for mult-edit', indent=2)

            bpy.ops.object.mode_set(mode='EDIT')
            addon.log(value='Changed mode back to edit', indent=2)

    elif all:
        addon.log(value=F'Removed shape object: {ot.datablock["shape"].name}', indent=2)
        bpy.data.objects.remove(ot.datablock['shape'])

        for obj in ot.datablock['slices']:
            addon.log(value=F'Removed slice object: {obj.name}', indent=2)
            bpy.data.objects.remove(obj)

        for obj in ot.datablock['targets']:
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN' and not mod.object:
                    addon.log(value=F'Removed dead modifier: {mod.name}', indent=2)
                    obj.modifiers.remove(mod)

    # we want to run this each time as a cleanup routine so each
    # time clean is called which is invoke, execute and cancel
    if 'Cutters' in bpy.data.collections and not bpy.data.collections['Cutters'].objects:
        bpy.data.collections.remove(bpy.data.collections['Cutters'])

    if 'Slices' in bpy.data.collections and not bpy.data.collections['Slices'].objects:
        bpy.data.collections.remove(bpy.data.collections['Slices'])

    for obj in bpy.data.objects:
        if hasattr(obj, 'data') and hasattr(obj.data, 'bc') and obj.data.bc.removeable:
            bpy.data.objects.remove(obj)

    for mesh in bpy.data.meshes:
        if mesh.bc.removeable:
            bpy.data.meshes.remove(mesh)

    for lattice in bpy.data.lattices:
        if lattice.bc.removeable:
            bpy.data.lattices.remove(lattice)

    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and not mod.object:
                obj.modifiers.remove(mod)

    for obj in bpy.data.objects:
        if obj.bc.slice:
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN' and not mod.object:
                    bpy.data.meshes.remove(obj.data)
                    bpy.data.objects.remove(obj)

    # return toolbar state
    if not init:
        update.property.toolbar(bpy.context, 'mode', ot.last['start_mode'])
        update.property.toolbar(bpy.context, 'operation', ot.last['start_operation'])

