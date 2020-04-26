import bpy

class BoneMatchPanel(bpy.types.Panel):
    bl_label = "Bone Match"
    bl_category = "RIG Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    # bl_context = "posemode"

    def draw(self, context):
        settings = context.scene.BoneMatch
        layout = self.layout
        row = layout.row(align= True)
        row.prop(settings, 'metarig',text='Metarig')
        row = layout.row(align= True)
        row.operator("bonematch.bind_bones",icon="ARMATURE_DATA",text ='Bind' )
        row.operator("bonematch.match_bones",icon="MOD_ARMATURE",text = 'Match')
        layout.separator()
        row = layout.row(align= True)
        row.prop(settings, 'autorig',text='Autorig')
        row = layout.row(align= True)
        row.operator("bonematch.update_rig",icon="FILE_REFRESH",text = 'Update')
