import bpy

def hasG2MeshProperties(obj):
    """ Whether a given object has the ghoul 2 mesh-object properties """
    return ("g2_prop_off" in obj) and ("g2_prop_tag" in obj) and ("g2_prop_name" in obj) and ("g2_prop_shader" in obj)

def hasG2ArmatureProperties(obj):
    """ Whether a given object has the ghoul 2 armature properties """
    return "g2_prop_scale" in obj

def initG2Properties():
    """ globally initializes the ghoul 2 custom properties """
    bpy.types.Object.g2_prop_name = bpy.props.StringProperty(name="name", maxlen=64, default="", description="Name (in case it doesn't fit in Blender's Object Name, which is used if this is empty.)")
    bpy.types.Object.g2_prop_shader = bpy.props.StringProperty(name="shader", maxlen=64, default="", description="Shader to use (the one and only way to set this)")
    bpy.types.Object.g2_prop_tag = bpy.props.BoolProperty(name="Tag", default=False, description="Whether this object represents a tag.")
    bpy.types.Object.g2_prop_off = bpy.props.BoolProperty(name="Off", default=False, description="Whether this object should be initially off (can be overridden in skin).")
    bpy.types.Object.g2_prop_scale = bpy.props.FloatProperty(name="Scale", default=100, min=0, subtype='PERCENTAGE', description="Scale of this skeleton.")

class G2PropertiesPanel(bpy.types.Panel):
    bl_label = "Ghoul 2 Properties"
    bl_idname = "OBJECT_PT_g2_props"
    bl_space_type = 'PROPERTIES' # goes in the properties editor
    bl_region_type = 'WINDOW'
    bl_context = "object" # in the objects tab

    @classmethod
    def poll(self, context):
        if context.active_object:
            return context.active_object.type in ['MESH', 'ARMATURE']
    
    def draw(self, context):
        layout = self.layout

        obj = context.active_object
        
        if obj.type == 'MESH':
            if hasG2MeshProperties(obj):
                row = layout.row()
                row.operator("object.remove_g2_properties")
                
                row = layout.row()
                row.prop(obj, "g2_prop_name")
                
                row = layout.row()
                row.prop(obj, "g2_prop_shader")
                
                row = layout.row()
                row.prop(obj, "g2_prop_tag")
                row.prop(obj, "g2_prop_off")
            else:
                row = layout.row()
                row.operator("object.add_g2_properties")
        else:
            assert(obj.type == 'ARMATURE')
            if hasG2ArmatureProperties(obj):
                row = layout.row()
                row.operator("object.remove_g2_properties")
                
                row = layout.row()
                row.prop(obj, "g2_prop_scale")
            else:
                row = layout.row()
                row.operator("object.add_g2_properties")
