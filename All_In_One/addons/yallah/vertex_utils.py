import bpy


class LoadVertexGroups(bpy.types.Operator):
    """Operator to load the vertex groups from a JSON file."""

    bl_idname = "object.load_vertex_groups"
    bl_label = "Load and create a vertex group from a JSON dictionary file."

    vertex_groups_filename = bpy.props.StringProperty(name="VertexGroupdFile",
                                                      description="The json file with the description of the vertex groups to load",
                                                      subtype="FILE_PATH")

    replace_existing = bpy.props.BoolProperty(name="Replace Existing",
                                              default=False,
                                              description="If True, existing vertex groups with the same name will be overridden by the loaded ones. Otherwise an error will be thrown.")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'MESH':
                if context.mode == 'OBJECT':
                    return True

        return False

    def execute(self, context):

        import json

        obj = context.active_object  # type: bpy.types.Object

        if not obj.type == 'MESH':
            raise Exception("Object {} is not a MESH. Found {}".format(obj.name, obj.type))

        try:
            print("Loading groups info from '{}'".format(self.vertex_groups_filename))
            with open(self.vertex_groups_filename, "r") as in_file:
                in_dict = json.load(fp=in_file)
        except Exception as e:
            self.report({'ERROR'}, "Exception loading JON file: {}.".format(e))
            return {'CANCELLED'}

        for groupName in in_dict.keys():

            # If the group already exist, remove it
            if groupName in obj.vertex_groups:

                if self.replace_existing:
                    obj.vertex_groups.remove(obj.vertex_groups[groupName])
                else:
                    self.report({'ERROR'}, "A group named '{}' already exists.".format(groupName))
                    return {'CANCELLED'}

            # print("Creating group '{}'".format(groupName))
            vg = obj.vertex_groups.new(groupName)
            group_vertices = in_dict[groupName]
            assert isinstance(group_vertices, list)
            vg.add(group_vertices, weight=1.0, type='REPLACE')

        return {'FINISHED'}


class SaveVertexGroups(bpy.types.Operator):
    """Save the indices of the active vertex group onto a JSON file."""

    bl_idname = "object.save_vertex_group"
    bl_label = "Save the indices of the active vertex group onto a JSON file."

    vertex_group_filename = bpy.props.StringProperty(name="VertexGroupFile",
                                                      description="The json file that will be written.",
                                                      subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'MESH':
                if context.mode == 'OBJECT':
                    return True

        return False

    def execute(self, context):

        import json

        #
        # Solution found here:
        # https://blender.stackexchange.com/questions/75223/python-finding-vertices-in-a-vertex-group
        obj = context.active_object  # type: bpy.types.Object
        mesh = obj.data  # type: bpy.types.Mesh
        vg_idx = obj.vertex_groups.active_index
        vs = [v.index for v in mesh.vertices if vg_idx in [vg.group for vg in v.groups]]

        vg_name = obj.vertex_groups[vg_idx].name
        out_dict = {vg_name: vs}

        try:
            with open(self.vertex_group_filename, "w") as out_file:
                json.dump(obj=out_dict, fp=out_file)

        except Exception as e:
            self.report({'ERROR'}, "Exception saving the JON file: {}.".format(e))
            return {'CANCELLED'}

        return {'FINISHED'}


def register():
    bpy.utils.register_class(LoadVertexGroups)
    bpy.utils.register_class(SaveVertexGroups)


def unregister():
    bpy.utils.unregister_class(LoadVertexGroups)
    bpy.utils.unregister_class(SaveVertexGroups)
