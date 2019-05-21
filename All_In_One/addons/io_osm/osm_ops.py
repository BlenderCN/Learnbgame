import bpy

class MATERIAL_OT_add_osm_tag(bpy.types.Operator):
    bl_label = 'Add tag'
    bl_idname = 'material.add_osm_tag'
    bl_description = 'Add an OSM tag'

    def execute(self,context):
        mat = context.material
        mat.osm.tags.add()
        return {'FINISHED'}


class MATERIAL_OT_remove_osm_tag(bpy.types.Operator):
    bl_label = 'Remove tag'
    bl_idname = 'material.remove_osm_tag'
    bl_description = 'Remove the OSM tag'

    index = bpy.props.IntProperty()

    def execute(self,context):
        mat = context.material
        mat.osm.tags.remove(self.index)
        return {'FINISHED'}


class GROUP_OT_add_osm_tag(bpy.types.Operator):
    bl_label = 'Add tag'
    bl_idname = 'group.add_osm_tag'
    bl_description = 'Add an OSM tag'

    group = bpy.props.StringProperty()

    def execute(self,context):
        group = bpy.data.groups[self.group]
        group.osm.tags.add()
        return {'FINISHED'}


class GROUP_OT_remove_osm_tag(bpy.types.Operator):
    bl_label = 'Remove tag'
    bl_idname = 'group.remove_osm_tag'
    bl_description = 'Remove the OSM tag'

    index = bpy.props.IntProperty()
    group = bpy.props.StringProperty()

    def execute(self,context):
        group = bpy.data.groups[self.group]
        group.osm.tags.remove(self.index)
        return {'FINISHED'}


class SCENE_OT_rebuild_osm(bpy.types.Operator):
    bl_label = 'Rebuild'
    bl_idname = 'scene.rebuild_osm'
    bl_description = 'Rereads OSM file and rebuilds existing OSM objects.'

    def execute(self,context):
        from os import path
        from io_osm.import_osm import rebuild_osm

        filepath = context.scene.osm.file

        if filepath!='' and path.exists(filepath):
            rebuild_osm(filepath,context)
        return {'FINISHED'}

class SCENE_OT_remove_osm(bpy.types.Operator):
    bl_label = 'Remove'
    bl_idname = 'scene.remove_osm'
    bl_description = 'Removes all OSM objects in the scene.'

    def execute(self,context):
        from os import path
        from io_osm.import_osm import remove_osm

        remove_osm(context)
        return {'FINISHED'}


def register_ops():
    bpy.utils.register_class(MATERIAL_OT_add_osm_tag)
    bpy.utils.register_class(MATERIAL_OT_remove_osm_tag)
    bpy.utils.register_class(GROUP_OT_add_osm_tag)
    bpy.utils.register_class(GROUP_OT_remove_osm_tag)
    bpy.utils.register_class(SCENE_OT_rebuild_osm)
    bpy.utils.register_class(SCENE_OT_remove_osm)

def unregister_ops():
    bpy.utils.unregister_class(MATERIAL_OT_add_osm_tag)
    bpy.utils.unregister_class(MATERIAL_OT_remove_osm_tag)
    bpy.utils.unregister_class(GROUP_OT_add_osm_tag)
    bpy.utils.unregister_class(GROUP_OT_remove_osm_tag)
    bpy.utils.unregister_class(SCENE_OT_rebuild_osm)
    bpy.utils.unregister_class(SCENE_OT_remove_osm)
