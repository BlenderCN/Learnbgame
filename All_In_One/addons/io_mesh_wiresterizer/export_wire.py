import os

from . import lib_wire

import bpy
import mathutils
import bpy_extras.io_utils

from progress_report import ProgressReport, ProgressReportSubstep


def mesh_triangulate(mesh):
    import bmesh
    temp_mesh = bmesh.new()
    temp_mesh.from_mesh(mesh)
    bmesh.ops.triangulate(temp_mesh, faces=temp_mesh.faces)
    temp_mesh.to_mesh(mesh)
    temp_mesh.free()


def write_file(filepath, wire_opts, objects, scene,
               EXPORT_APPLY_MODIFIERS=True,
               EXPORT_APPLY_MODIFIERS_RENDER=False,
               EXPORT_GLOBAL_MATRIX=None,
               EXPORT_PATH_MODE='AUTO'
              ):
    """
    Basic write function. The context and options must be already set
    This can be accessed externaly
    eg.
    write( 'c:\\test\\foobar.obj', Blender.Object.GetSelected() ) # Using default options.
    """
    if EXPORT_GLOBAL_MATRIX is None:
        EXPORT_GLOBAL_MATRIX = mathutils.Matrix()

    def veckey3d(vec):
        return round(vec.x, 4), round(vec.y, 4), round(vec.z, 4)

    output_file = lib_wire.open_file(wire_opts, filepath)
    file_write = output_file.write
    lib_wire.write_header(wire_opts, file_write)

    copy_set = set()

    # Get all meshes
    for _i, ob_main in enumerate(objects):
        # ignore dupli children
        if ob_main.parent and ob_main.parent.dupli_type in {'VERTS', 'FACES'}:
            continue

        collected_objects = [(ob_main, ob_main.matrix_world)]
        if ob_main.dupli_type != 'NONE':
            print('creating dupli_list on', ob_main.name)
            ob_main.dupli_list_create(scene)

            collected_objects += [(dob.object, dob.matrix) for dob in ob_main.dupli_list]

            print(ob_main.name, 'has', len(collected_objects) - 1, 'dupli children')

        for obj, obj_mat in collected_objects:
            try:
                convert_settings = 'PREVIEW'
                if EXPORT_APPLY_MODIFIERS_RENDER:
                    convert_settings = 'RENDER'

                mesh = obj.to_mesh(scene,
                                   EXPORT_APPLY_MODIFIERS,
                                   calc_tessface=False,
                                   settings=convert_settings
                                  )
            except RuntimeError:
                mesh = None

            if mesh is None:
                continue

            # _must_ do this before applying transformation,
            # else tessellation may differ
            if wire_opts.triangles:
                # _must_ do this first since it re-allocs arrays
                mesh_triangulate(mesh)

            mesh.transform(EXPORT_GLOBAL_MATRIX * obj_mat)
            # If negative scaling, we have to invert the normals...
            if obj_mat.determinant() < 0.0:
                mesh.flip_normals()

            mesh_verts = mesh.vertices[:]

            # Make our own list so it can be sorted to reduce context switching
            face_index_pairs = [(face, index) for
                                index, face in enumerate(mesh.polygons)]

            # Make sure there is something to write
            if (len(face_index_pairs) + len(mesh.vertices)) <= 0:
                # clean up
                bpy.data.meshes.remove(mesh)
                continue  # dont bother with this mesh.

            if wire_opts.uses_normals() and face_index_pairs:
                mesh.calc_normals_split()
                # No need to call me.free_normals_split later,
                # as this mesh is deleted anyway!

            for face, _f_index in face_index_pairs:
                wire_face = lib_wire.WireFace()

                # Face normal
                wire_face.norm.x = face.normal[0]
                wire_face.norm.y = face.normal[1]
                wire_face.norm.z = face.normal[2]

                # Face vertices
                for vert_idx in face.vertices:
                    wire_vert = lib_wire.WireVertex()
                    wire_face.verts.append(wire_vert)

                    vert_pos = mesh_verts[vert_idx].co
                    wire_vert.pos.x = vert_pos[0]
                    wire_vert.pos.y = vert_pos[1]
                    wire_vert.pos.z = vert_pos[2]
                    vert_norm = mesh_verts[vert_idx].normal
                    wire_vert.norm.x = vert_norm[0]
                    wire_vert.norm.y = vert_norm[1]
                    wire_vert.norm.z = vert_norm[2]

                # Write face
                lib_wire.write_face(wire_opts, file_write, wire_face)

            # clean up
            bpy.data.meshes.remove(mesh)

        if ob_main.dupli_type != 'NONE':
            ob_main.dupli_list_clear()

    # copy all collected files.
    bpy_extras.io_utils.path_reference_copy(copy_set)

    output_file.close()


def _write(context, filepath, wire_opts,
           EXPORT_APPLY_MODIFIERS,  # ok
           EXPORT_APPLY_MODIFIERS_RENDER,  # ok
           EXPORT_SEL_ONLY,  # ok
           EXPORT_GLOBAL_MATRIX,
           EXPORT_PATH_MODE,  # Not used
          ):

    with ProgressReport(context.window_manager) as progress:
        base_name, ext = os.path.splitext(filepath)
        context_name = [base_name, '', '', ext]  # Base name, scene name, frame number, extension

        scene = context.scene

        # Exit edit mode before exporting, so current object states are exported properly.
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        orig_frame = scene.frame_current

        scene_frames = [orig_frame]  # Dont export an animation.

        # Loop through all frames in the scene and export.
        progress.enter_substeps(len(scene_frames))
        for frame in scene_frames:
            scene.frame_set(frame, 0.0)
            if EXPORT_SEL_ONLY:
                objects = context.selected_objects
            else:
                objects = scene.objects

            full_path = ''.join(context_name)

            # erm... bit of a problem here, this can overwrite files when exporting frames.
            # not too bad.
            # EXPORT THE FILE.
            progress.enter_substeps(1)
            write_file(full_path, wire_opts, objects, scene,
                       EXPORT_APPLY_MODIFIERS,
                       EXPORT_APPLY_MODIFIERS_RENDER,
                       EXPORT_GLOBAL_MATRIX,
                       EXPORT_PATH_MODE
                      )
            progress.leave_substeps()

        scene.frame_set(orig_frame, 0.0)
        progress.leave_substeps()


def save(context,
         filepath,
         wire_opts,
         *,
         use_mesh_modifiers=True,
         use_mesh_modifiers_render=False,
         use_selection=True,
         global_matrix=None,
         path_mode='AUTO'
        ):

    _write(context, filepath, wire_opts,
           EXPORT_APPLY_MODIFIERS=use_mesh_modifiers,
           EXPORT_APPLY_MODIFIERS_RENDER=use_mesh_modifiers_render,
           EXPORT_SEL_ONLY=use_selection,
           EXPORT_GLOBAL_MATRIX=global_matrix,
           EXPORT_PATH_MODE=path_mode,
          )

    return {'FINISHED'}
