
import bpy


class WarCraft3PanelArmature(bpy.types.Panel):
    bl_label = 'WarCraft 3'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return context.armature

    def draw(self, context):
        warcraft3data = context.armature.warcraft_3
        layout = self.layout
        layout.label('Animations:')
        row = layout.row()
        row.template_list(
            listtype_name='UI_UL_list',
            list_id='name',
            dataptr=warcraft3data,
            propname='sequencesList',
            active_dataptr=warcraft3data,
            active_propname='sequencesListIndex',
            rows=2
            )
        col = row.column(align=True)
        col.operator('warcraft_3.add_sequence_to_armature', icon='ZOOMIN', text='')
        col.operator('warcraft_3.remove_sequence_to_armature', icon='ZOOMOUT', text='')


class WarCraft3PanelBone(bpy.types.Panel):
    bl_label = 'WarCraft 3'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return context.bone

    def draw(self, context):
        bone = context.bone
        warcraft3data = bone.warcraft_3
        layout = self.layout
        layout.prop(warcraft3data, 'nodeType')
        if context.object.mode == 'POSE':
            layout.operator(
                'warcraft_3.update_bone_settings',
                text='Update All Nodes'
                )
