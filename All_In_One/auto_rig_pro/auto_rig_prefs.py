import bpy



class ARP_MT_arp_addon_preferences(bpy.types.AddonPreferences):
	bl_idname = __package__	

	def draw(self, context):		
		col = self.layout.column(align=True)
		col.prop(context.scene, "arp_debug_mode")
		


#classes = (ARP_MT_arp_addon_preferences)
		
def register():
	from bpy.utils import register_class

	#for cls in classes:
	register_class(ARP_MT_arp_addon_preferences)

	bpy.types.Scene.arp_debug_mode = bpy.props.BoolProperty(name="Debug Mode", default = False, description = "Run the addon in debug mode (should be enabled only for debugging purposes, not recommended for a normal usage)")
	
def unregister():
	from bpy.utils import unregister_class
	
	#for cls in reversed(classes):
	unregister_class(ARP_MT_arp_addon_preferences)	

	del bpy.types.Scene.arp_debug_mode
