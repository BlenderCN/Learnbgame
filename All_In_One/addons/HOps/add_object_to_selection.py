import bpy
import bmesh
from mathutils import Vector, Matrix


# Old
######################################################################


class HOPS_OT_SelectedToSelection(bpy.types.Operator):
    bl_idname = "object.to_selection"
    bl_label = "To selection"

    def execute(self, context):

        obj_list = []
        bpy.ops.object.mode_set(mode='OBJECT')
        ref_obj = bpy.context.active_object

        obj1, obj2 = context.selected_objects
        second_obj = obj1 if obj2 == ref_obj else obj2

        obj_list.append(second_obj.name)
        bpy.data.objects[second_obj.name].select_set(False)
        bpy.ops.object.duplicate_move()
        bpy.context.active_object.name = "Dummy"
        obj = context.active_object
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        copy_cursor = bpy.context.scene.cursor.location.copy()

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        selected_faces = [f for f in bm.faces if f.select]

        for face in selected_faces:

            face_location = face.calc_center_median()

            loc_world_space = obj.matrix_world @ Vector(face_location)

            z = Vector((0, 0, 1))

            angle = face.normal.angle(z)
            axis = z.cross(face.normal)

            matrix = Matrix.Rotation(angle, 3, axis)

            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = bpy.data.objects[second_obj.name]
            bpy.data.objects[second_obj.name].select_set(True)
            bpy.ops.object.duplicate()
            bpy.context.scene.cursor.location = loc_world_space
            bpy.ops.view3d.snap_selected_to_cursor()

            bpy.ops.transform.rotate(value=angle, orient_matrix=matrix)
            obj_list.append(context.object.name)

        bm.to_mesh(obj.data)

        bm.free()

        bpy.context.scene.cursor.location = copy_cursor
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects["Dummy"]
        bpy.data.objects["Dummy"].select_set(True)
        bpy.ops.object.delete(use_global=False)

        bpy.context.view_layer.objects.active = bpy.data.objects[obj_list[0]]

        for obj in obj_list:
            bpy.data.objects[obj].select_set(True)
            bpy.ops.make.link()  # custom link called from operators module

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[ref_obj.name]
        bpy.data.objects[second_obj.name].select_set(True)
        bpy.data.objects[ref_obj.name].select_set(True)

        bpy.ops.object.mode_set(mode='EDIT')
        del(obj_list[:])

        return {'FINISHED'}


def add_primitive():

    # Primitives
    if bpy.context.window_manager.choose_primitive == 'cube':
        bpy.ops.mesh.primitive_cube_add(radius=1)

    # Cylinders
    elif bpy.context.window_manager.choose_primitive == "cylinder_8":
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == 'placeholder':
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == 'cylinder_24':
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == "cylinder_32":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == "cylinder_64":
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1, depth=2)


def create_object_to_selection(self, context):

    if not bpy.context.object:
        add_primitive()
#        bpy.ops.object.orientationvariable(variable="LOCAL")

    elif context.object.mode == 'EDIT':
        # Duplicate the mesh, apply his transform and perform the code to add object on it
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate_move()
        bpy.context.active_object.name = "Dummy"
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        list_insert_meshes = []
        obj = bpy.context.active_object
        saved_location = bpy.context.scene.cursor.location.copy()

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        selected_faces = [f for f in bm.faces if f.select]

        for face in selected_faces:
            face_location = face.calc_center_median()
            loc_world_space = obj.matrix_world * Vector(face_location)
            z = Vector((0, 0, 1))
            angle = face.normal.angle(z)
            axis = z.cross(face.normal)

            bpy.context.scene.cursor.location = loc_world_space

            add_primitive()

            bpy.ops.transform.rotate(value=angle, axis=axis)

            list_insert_meshes.append(context.active_object.name)

        bm.to_mesh(obj.data)
        bm.free()
        bpy.context.scene.cursor.location = saved_location

        # Deselect all the objects, select the dummy object and delete it
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects["Dummy"]

        bpy.context.object.select_set(True)
        bpy.ops.object.delete(use_global=False)

        # Select inserted meshes
        for obj in list_insert_meshes:
            bpy.context.view_layer.objects.active = bpy.data.objects[obj]
            bpy.data.objects[obj].select_set(True)
            if len(list_insert_meshes) > 1:
                bpy.ops.object.make_links_data(type='OBDATA') # Make link

        del(list_insert_meshes[:])
#        bpy.ops.object.orientationvariable(variable="LOCAL")

    else:
        saved_location = bpy.context.scene.cursor.location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()

        add_primitive()

        bpy.context.scene.cursor.location = saved_location
#        bpy.ops.object.orientationvariable(variable="LOCAL")"""
