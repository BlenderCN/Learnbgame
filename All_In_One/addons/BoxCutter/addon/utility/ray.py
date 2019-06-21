import bpy

from . view3d import location2d_to_origin3d, location2d_to_vector3d


class cast:


    def objects(x, y, obj=None, mesh=None, snap=False):
        bc = bpy.context.window_manager.bc

        origin = location2d_to_origin3d(x, y)
        direction = location2d_to_vector3d(x, y)

        if obj:
            hit, location, normal, index = obj.ray_cast(origin, direction, depsgraph=bpy.context.depsgraph)

            return hit, location, normal, index

        if mesh:
            obj = bpy.data.objects.new(name='TMP', object_data=mesh)

            if snap and bool(bc.snap.object):
                obj.data = obj.data.copy()
                obj.data.bc.removeable = True

                obj.data.transform(bc.snap.object.matrix_world)

            original_active = bpy.context.active_object
            bpy.context.scene.collection.objects.link(obj)
            bpy.context.view_layer.objects.active = obj

            bpy.context.scene.update()

            hit, location, normal, index = obj.ray_cast(origin, direction, depsgraph=bpy.context.depsgraph)

            bpy.data.objects.remove(obj)

            del obj

            bpy.context.view_layer.objects.active = original_active

            return hit, location, normal, index

        original_visible = bpy.context.visible_objects[:]
        display = [(obj, obj.display_type) for obj in bpy.context.selected_objects if obj.type == 'MESH']
        hide = [obj for obj in original_visible if not obj.select_get() or obj.type != 'MESH']

        for obj in hide:
            obj.hide_set(True)

        for obj in display:
            obj[0].display_type = 'SOLID'

        bpy.context.scene.update()

        hit, location, normal, index, object, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer, origin, direction)

        for obj in hide:
            obj.hide_set(False)

        for obj in display:
            obj[0].display_type = obj[1]

        del original_visible
        del display
        del hide

        return hit, location, normal, index, object, matrix
