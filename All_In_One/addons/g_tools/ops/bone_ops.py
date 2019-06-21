#importdefs
import bpy
from g_tools.bpy_itfc_funcs import bone_fs
from g_tools.bpy_itfc_funcs import armature_fs

#fdef


#opdef
class select_by_tag_op(bpy.types.Operator):
    """
    Select bones by tag
    名前に付いてるタグに基づいてボーンを選択する
    """
    bl_idname = "armature.select_by_tag"
    bl_label = "Select By Tag"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    

    tag = bpy.props.StringProperty(description = 'Tag',default = "親")


    def execute(self, context):
        bone_fs.select_by_tag()
        return {'FINISHED'}
        
#opdef
class editbone_adjust_op(bpy.types.Operator):
    """Edit underlying bone from pose mode"""
    bl_idname = "armature.editbone_adjust"
    bl_label = "Editbone Adjust"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    
    location = bpy.props.FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )

    offset_head = bpy.props.FloatVectorProperty(
            name="Head offset",
            subtype='TRANSLATION',
            )
            
    offset_tail = bpy.props.FloatVectorProperty(
            name="Tail offset",
            subtype='TRANSLATION',
            )
            
    roll = bpy.props.FloatProperty(description = '',default = 0)
    envelope_distance = bpy.props.FloatProperty(description = '',default = 0)
    envelope_weight = bpy.props.FloatProperty(description = '',default = 1)
    head_radius = bpy.props.FloatProperty(description = '',default = 0)
    tail_radius = bpy.props.FloatProperty(description = '',default = 0)

    target_bone = bpy.props.StringProperty(description = 'Bone name',default = "")

    def execute(self, context):
        
        bone_fs.editbone_adjust(trans = self.location,
                            trans_head = self.offset_head,
                            trans_tail = self.offset_tail,
                            roll = self.roll,
                            envelope_distance = self.envelope_distance, 
                            envelope_weight = self.envelope_weight,
                            head_radius = self.head_radius, 
                            tail_radius = self.tail_radius,
                            target_bone = self.target_bone)
                            
        return {'FINISHED'}
        
class envelope_armature_settings_op(bpy.types.Operator):
    """Set the envelopes and radii of an armature's bones for use in curve/mesh sync."""
    bl_idname = "armature.envelope_armature_settings"
    bl_label = "Envelope Armature Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    


    envelope_distance = bpy.props.FloatProperty(description = 'Envelope distance',default = 0.25)
    envelope_weight = bpy.props.FloatProperty(description = 'Envelope weight',default = 1.0)
    head_radius = bpy.props.FloatProperty(description = 'Head radius',default = 0.0)
    tail_radius = bpy.props.FloatProperty(description = 'Tail radius',default = 0.0)


    def execute(self, context):
        armature_fs.envelope_armature_settings(envelope_distance = self.envelope_distance,envelope_weight = self.envelope_weight,head_radius = self.head_radius,tail_radius = self.tail_radius)
        return {'FINISHED'}
        
class GBonePanel(bpy.types.Panel):
    """Creates a Panel in the 3D View"""
    bl_label = "GBone"    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "G Tools"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        #rowdefs
        row = layout.row()
        row.operator("armature.select_by_tag")
        row = layout.row()
        row.operator("armature.editbone_adjust")
        
        row = layout.row()
        row.operator("armature.envelope_armature_settings")
        
def register():
    #regdef
    bpy.utils.register_class(select_by_tag_op)
    bpy.utils.register_class(editbone_adjust_op)
    bpy.utils.register_class(envelope_armature_settings_op)
    bpy.utils.register_class(GBonePanel)

def unregister():
    #unregdef
    bpy.utils.unregister_class(select_by_tag_op)
    bpy.utils.unregister_class(editbone_adjust_op)
    bpy.utils.unregister_class(envelope_armature_settings_op)
    bpy.utils.unregister_class(GBonePanel)
    
    