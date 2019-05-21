import bpy
import bmesh


def delete_all_objects():
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def make_suzanne():
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # bpy.ops.view3d.snap_cursor_to_center()
    mesh = bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
    bpy.ops.object.armature_add(location=(0, 0, 0))

    mesh = bpy.context.scene.objects['Suzanne']
    armature = bpy.context.scene.objects['Armature']

    mesh.select = True
    bpy.context.scene.objects.active = mesh

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)

    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
    bm.to_mesh(mesh.data)
    bm.free()

    material = bpy.data.materials.new('Placeholder')
    mesh.data.materials.append(material)

    mesh.select = True
    armature.select = True
    bpy.context.scene.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')