import bpy
from bpy import context

# adds an object mode menu 
class QuickObjectTools(bpy.types.Menu):
    bl_label = "Quick Object Tools"
    bl_idname = "object.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.add_subsurf", 'Add Subsurf', icon='MOD_SUBSURF')
        layout.operator("object.apply_subsurf", 'Apply Subsurf')
        
        layout.separator()
        
        layout.menu(SmartModifiers.bl_idname, "Add Smart Modifier", icon='MODIFIER')

        layout.operator_menu_enum("object.modifier_add", "type") 
        layout.operator("object.apply_modifiers")
        layout.operator("object.modifier_remove_all", "Remove All Modifiers")
        
        layout.separator()

        layout.operator("object.mesh_halve", "Halve and Mirror")

        layout.separator() 
                
        layout.operator_menu_enum("object.origin_set", "type")


class SmartModifiers(bpy.types.Menu):
    bl_idname = "object.smart_mod"
    bl_label = "Smart Modifiers"

    def draw (self, context):
        layout = self.layout
        layout.operator("object.empty_add_unactive", "Add Target", icon='CURSOR')

        layout.separator()

        layout.operator("object.add_array", "Array", icon='MOD_ARRAY')
        layout.operator("object.add_boolean", "Boolean", icon='MOD_BOOLEAN')
        layout.operator("object.add_cast", "Cast", icon='MOD_CAST')
        layout.operator("object.add_mirror", "Mirror", icon='MOD_MIRROR')
        layout.operator("object.add_lattice", "Lattice", icon='MOD_LATTICE')
        layout.operator("object.add_screw", "Screw", icon='MOD_SCREW')


class QuickObjectOptions(bpy.types.Menu):
    bl_idname = "object.display_options"
    bl_label = "Quick Object Options"

    def draw(self, context):

        mode = bpy.context.object.mode

        layout = self.layout
        layout.operator("object.double_sided")
        layout.operator("object.all_edges_wire")

        layout.separator()

        if mode == 'OBJECT' or mode == 'SCULPT':
            layout.operator("object.shade_smooth", icon='SOLID')
            layout.operator("object.shade_flat", icon='MESH_UVSPHERE')
        elif mode == 'EDIT':
            layout.operator("mesh.faces_shade_smooth", icon='SOLID')
            layout.operator("mesh.faces_shade_flat", icon='MESH_UVSPHERE')            


class QuickPETObjects(bpy.types.Menu):
    bl_label = "Proportional Editing"
    bl_idname = "object.quick_pet_menu"

    def draw(self, context):
        layout = self.layout
        
        mode = context.mode
        editmodes = ('EDIT_MESH', 'EDIT_CURVE', 'EDIT_LATTICE', 'EDIT_SURFACE', 'EDIT_METABALL')
        pet = context.scene.tool_settings.use_proportional_edit_objects

        if mode == 'OBJECT':
            if pet:
                layout.operator("object.pet", "Disable PET")
            else:
                layout.operator("object.pet", "Enable PET")

        elif mode in editmodes:
            layout.operator("object.pet_edit", "Disable").setting = -1
            layout.operator("object.pet_edit", "Enable").setting = 0
            layout.operator("object.pet_edit", "Connected").setting = 1
            layout.operator("object.pet_edit", "Projected").setting = 2

        layout.separator()

        layout.label("Brush Falloff")
        layout.operator("object.pet_curve_falloff", text="Smooth", icon='SMOOTHCURVE').shape = 'SMOOTH'
        layout.operator("object.pet_curve_falloff", text="Sphere", icon='SPHERECURVE').shape = 'SPHERE'
        layout.operator("object.pet_curve_falloff", text="Root", icon='ROOTCURVE').shape = 'ROOT'
        layout.operator("object.pet_curve_falloff", text="Sharp", icon='SHARPCURVE').shape = 'SHARP'
        layout.operator("object.pet_curve_falloff", text="Linear", icon='LINCURVE').shape = 'LINEAR'
        layout.operator("object.pet_curve_falloff", text="Constant", icon='NOCURVE').shape =  'CONSTANT'
        layout.operator("object.pet_curve_falloff", text="Random", icon='RNDCURVE').shape =  'RANDOM'


def register():
    bpy.utils.register_module(__name__)  

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()   