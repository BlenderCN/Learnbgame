
bl_info = {
    "name": "Petgame Mesh Export",
    "description": "petgame mesh exporter",
    "author": "Joe Harding",
    "version": (1, 0),
    "blender": (2, 69, 0),
    "location": "File > Export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
import bmesh
import io
import os
import pprint
import mathutils

from bpy_extras.io_utils import ExportHelper


class ExportMesh(bpy.types.Operator, ExportHelper):

    filename_ext = ".xml"

    # unique identifier for buttons and menu items to reference.
    bl_idname = "io.export_petgame_mesh"

    # display name in the interface.
    bl_label = "Petgame Mesh Export"

    # enable undo for the operator.
    bl_options = {'REGISTER', 'UNDO'}

    export_scene_label = 'export_scene'
    
    working_scene_label = 'working_scene'

    # b/c we extend operator, execute is called by blender when running the operator
    def execute(self, context):
        print("### Petgame Mesh Export Script Start ###")

        # start off my checking if we have the required 'working_scene' set
        if not self.working_scene_label in bpy.data.scenes:
            print("ERROR: you must have scene '{n}' set in your project".format(n=self.working_scene_label))
            # TODO - find some way of exiting the script gracefully and alerting the user

        # start off by deselecting everything
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = None

        # clean up any already existing export scenes
        self.clean_export_scene()
 
        # copy all the objects in our working scene that have a data type of MESH
        self.clone_into_export_scene()

        # merge all the export scene objects together
        for obj in bpy.data.scenes[self.export_scene_label].objects:
            obj.data.name = "new"
            obj.select = True
            bpy.context.scene.objects.active = obj

        bpy.ops.object.join()

        # setting the name of an object
        bpy.context.object.name = 'export_object'

        # setting the name of the data of an object
        bpy.context.object.data.name = 'export_data'

        # convert quads to tris for each mesh
        for obj in bpy.context.scene.objects.data.objects:
            if obj.type == 'MESH':
                print("selecting mesh: {name} for export...".format(name=obj.name))
                obj.select = True
                bpy.context.scene.objects.active = obj
                verts = bpy.context.scene.objects.active.data.vertices

                for vert in verts:
                    vert.select = True

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.quads_convert_to_tris()
                bpy.ops.object.mode_set(mode='OBJECT')


        group_lookup = {g.index: g.name for g in bpy.context.object.vertex_groups}
        group_name_to_verts = {name: [] for name in group_lookup.values()}

        mesh = bpy.context.object.data

        loop_uv = []
        loop_position = []

        # get the world matrix so we can use it to convert local coords to global coords
        world_matrix = bpy.context.active_object.matrix_world

        for uv_loop in mesh.uv_layers.active.data:
            loop_uv.append(self.get_flipped_uv(uv_loop.uv))

        for triangle in mesh.polygons:
            for loop_index in triangle.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index

                raw_vertex = mesh.vertices[vertex_index]
                for g in raw_vertex.groups:
                    group_name_to_verts[group_lookup[g.group]].append(loop_index)

                loop_position.append(world_matrix * mesh.vertices[vertex_index].co)
 
        # make the working scene active again
        bpy.context.screen.scene = bpy.data.scenes[self.working_scene_label]

        self.print_xml(loop_position, loop_uv, group_name_to_verts)

        print("### PetGame Mesh Export Script End ###")
        # this lets blender know the operator finished successfully. 
        return {'FINISHED'}


    def clone_into_export_scene(self):
        # start in working scene where we copy out objects
        bpy.context.screen.scene = bpy.data.scenes[self.working_scene_label]
        bpy.context.scene.update()

        copy_list = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                data_copy = obj.data.copy()
                obj_copy = obj.copy()
                obj_copy.data = data_copy
                copy_list.append(obj_copy)

        print("copying objects from current scene...")
        print(copy_list)

        # create export scene and link objects copied previously
        bpy.ops.scene.new()
        bpy.context.scene.name = self.export_scene_label

        for copy in copy_list:
            bpy.data.scenes[self.export_scene_label].objects.link(copy)


    def clean_export_scene(self):
        if self.export_scene_label in bpy.data.scenes:
            for obj in bpy.data.scenes[self.export_scene_label].objects:
                obj.select = True

            bpy.ops.object.delete()

            print("removing already existing '{n}'...".format(n=self.export_scene_label))
            bpy.context.screen.scene = bpy.data.scenes[self.export_scene_label]
            bpy.ops.scene.delete()

        if 'export_object' in bpy.data.objects:
            print("cleaning up already existing 'export_object' object")
            bpy.data.objects['export_object'].data = None
            bpy.data.objects.remove(bpy.data.objects['export_object'])

        if 'export_data' in bpy.data.meshes:
            print("cleaning up already existing 'export_data' mesh")
            if bpy.data.meshes['export_data'].users != 0:
                print("ERROR: previous export data still exists")
            else:
                bpy.data.meshes.remove(bpy.data.meshes['export_data'])



    # ttby one here on the 'V' to flip image correct way up for petgame rendering
    def get_flipped_uv(self, uv):
        return (uv[0], 1 - uv[1])

    # print out the mesh data to petgame xml
    def print_xml(self, position_coords, uv_coords, group_name_to_verts_data):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        print("Exporting to XML file \"%s\"..." % filepath)

        file = open(filepath, "w")
        fw = file.write
        fw('<!-- petgame mesh {v} -->\n'.format(v=bl_info["version"]))
        fw('<mesh>\n')

        fw('<vertexGroups>\n')
        for group_name in group_name_to_verts_data:
            xml_string = '<group name="{group_name}">\n'
            fw(xml_string.format(group_name=group_name))

            for vertex_index in group_name_to_verts_data[group_name]:
                xml_string = '<index>{vertex_index}</index>\n'
                fw(xml_string.format(vertex_index=vertex_index))

            fw('</group>\n')

        fw('</vertexGroups>\n')

        for index, position_coord in enumerate(position_coords):
            # using the z axis for our y axis and the negative y axis for our z axis
            fw('<vertex refIndex="{index}" x="{x}" y="{y}" z="{z}" />\n'.format(index=index, x=position_coord[0], y=position_coord[2], z=-position_coord[1]))

        for index, uv_coord in enumerate(uv_coords):
            fw('<uv refIndex="{index}" u="{u}" v="{v}" />\n'.format(index=index, u=uv_coord[0], v=uv_coord[1]))
    
        fw('</mesh>\n')

        file.close()

    def invoke(self, context, event):
        wm = context.window_manager

        if True:
            # File selector
            wm.fileselect_add(self) # will run self.execute()
            return {'RUNNING_MODAL'}
        elif True:
            # search the enum
            wm.invoke_search_popup(self)
            return {'RUNNING_MODAL'}
        elif False:
            # Redo popup
            return wm.invoke_props_popup(self, event)
        elif False:
            return self.execute(context)


def menu_func_export(self, context):
    self.layout.operator(ExportMesh.bl_idname, text="Petgame Mesh (.xml)")


def register():
    bpy.utils.register_class(ExportMesh)

    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportMesh)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == '__main__':
    register()
