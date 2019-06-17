__reload_order_index__ = 2

import bpy
from .operators import GROUP_OT_add_lod, GROUP_OT_remove_lod, OBJECT_OT_lod_copy, OBJECT_OT_lod_update
from .utils.enums import bl_space_type, bl_region_type, bl_context, bl_icon


class LODPanel:
    bl_label = "LOD"
    bl_space_type = bl_space_type.VIEW_3D
    bl_region_type = bl_region_type.TOOLS
    bl_context = bl_context.OBJECTMODE
    bl_category = "Level Of Detail"


class OBJECT_PT_lod(LODPanel, bpy.types.Panel):
    """"""
    bl_label = "LOD"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        # Add copy operator.
        layout.operator(OBJECT_OT_lod_copy.bl_idname, icon=bl_icon.COPYDOWN)

        # Add update operator.
        layout.operator(OBJECT_OT_lod_update.bl_idname, icon=bl_icon.FILE_REFRESH)

        layout.label("Read the included documentation for help.", icon=bl_icon.QUESTION)


class OBJECT_PT_lod_group(LODPanel, bpy.types.Panel):
    """"""
    bl_label = "LOD Group"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Active group.
        layout.prop_search(scene, 'lod_group', bpy.data, 'groups', text='Group Settings')

        # If the group exists.
        if scene.lod_group in bpy.data.groups:
            group = bpy.data.groups[scene.lod_group]

            # Number of objects in group.
            layout.label(str(len([obj for obj in group.objects if obj.type == 'MESH'])) + ' objects with mesh in group')

            # Display each level.
            for index, obj in enumerate(group.lod):
                # Object of this level.
                level_obj = group.objects.get(obj.object, None)

                box = layout.box()
                row = box.row(align=True)

                # Object selection.
                row.prop_search(obj, 'object', group, 'objects', text='Level ' + str(index + 1))
                # Distance.
                row.prop(obj, 'distance', text='Distance')

                # If the object exists.
                if level_obj is not None:
                    row = box.row(align=True)
                    # Number of polygons.
                    row.label(str(len(level_obj.data.polygons)) + ' polygons')
                    # Number of modifiers.
                    row.label(str(len(level_obj.modifiers)) + ' modifiers')
                    # Number of constraints.
                    row.label(str(len(level_obj.constraints)) + ' constraints')

                # Remove level operator.
                op = box.operator(GROUP_OT_remove_lod.bl_idname, icon=bl_icon.X)
                # Operator parameter.
                op.index = index

            layout.separator()

            # Add level operator.
            layout.operator(GROUP_OT_add_lod.bl_idname, icon=bl_icon.PLUS)


class OBJECT_PT_lod_object(LODPanel, bpy.types.Panel):
    """"""
    bl_label = "LOD Object"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        lod = obj.lod
        if lod.use_active_camera:
            offset_obj = bpy.context.scene.camera
        else:
            offset_obj = bpy.data.objects.get(lod.offset, None)

        # LOD group of this object.
        layout.prop_search(lod, 'group', bpy.data, 'groups')
        layout.prop(lod, 'use_active_camera')
        if not lod.use_active_camera:
            # Offset object of this object.
            layout.prop_search(lod, 'offset', scene, 'objects')

        if offset_obj is not None:
            # Distance from object to offset object.
            layout.label("Current Distance: " + str(round((obj.location - offset_obj.location).length, 2)))

        layout.prop(lod, 'use_mesh')
        layout.prop(lod, 'use_modifiers')
        layout.prop(lod, 'use_constraints')

        split = layout.split(percentage=0.5)
        col = split.column()
        col.prop(lod, 'use_frustum')
        col = split.column()
        col.enabled = lod.use_frustum
        col.prop(lod, 'frustum_level')
        col.prop(lod, 'frustum_radius')

        split = layout.split(percentage=0.5)
        col = split.column()
        col.prop(lod, 'render_active')
        col = split.column()
        col.enabled = not lod.render_active
        col.prop(lod, 'render_level')

        split = layout.split(percentage=0.5)
        col = split.column()
        col.prop(lod, 'viewport_active')
        col = split.column()
        col.enabled = not lod.viewport_active
        col.prop(lod, 'viewport_level')


def register():
    pass


def unregister():
    pass
