import bmesh

from mathutils import Vector
from mathutils.bvhtree import BVHTree as BVH

from . import update, addon, data, modifier, object
from . view3d import *


class cast:


    #TODO: need to only apply modifiers in edit mode that are visible and effect cage
    def object(ot, x, y, objects=[]):

        bm = bmesh.new()

        objects = ot.datablock['targets'] if not objects else objects

        for obj in objects:
            new = object.duplicate(obj, name='Duplicate')

            modifier.apply(obj=new, visible=bpy.context.workspace.tools_mode == 'EDIT_MESH')

            new.data.transform(obj.matrix_world)
            new.data.bc.removeable = True
            new.modifiers.clear()

            bm.from_mesh(new.data)

        addon.log(value='Duplicated selected objects and created ray geometry', indent=2)

        dat = bpy.data.meshes.new(name='Duplicate')
        bm.to_mesh(dat)
        dat.bc.removeable = True

        new = bpy.data.objects.new(name='Duplicate', object_data=dat)
        ot.datablock['duplicate'] = new

        if ot.datablock['dimensions'] == Vector((0, 0, 0)):
            ot.datablock['dimensions'] = Vector((new.dimensions.x, new.dimensions.y, new.dimensions.z))
            addon.log(value=F'Collected geometry dimensions: {ot.datablock["dimensions"]}', indent=2)

        matrix = new.matrix_world

        ray_origin = matrix.inverted() @ location2d_to_origin3d(x, y)
        ray_direction = matrix.inverted().to_3x3() @ location2d_to_vector3d(x, y)

        addon.log(value=F'Ray direction @ {ray_direction}', indent=2)

        bvh = BVH.FromBMesh(bm)

        location, normal, index, distance = bvh.ray_cast(ray_origin, ray_direction)

        if location:
            addon.log(value=F'Casted ray and found location @ {location}', indent=2)
            addon.log(value=F'Normal @ {normal}', indent=2)
            addon.log(value=F'Distance @ {distance}', indent=2)
            return matrix @ location, matrix.to_3x3() @ normal, index, distance
        else:
            addon.log(value='Casted ray and found nothing', indent=2)
            return None, None, None, None
