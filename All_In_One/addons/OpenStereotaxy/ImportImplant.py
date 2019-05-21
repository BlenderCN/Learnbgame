
# SurgeryPlannerTool.py
# 

import bpy
import os
import math
from bpy.types import Panel, Operator

Scene                                   = bpy.data.scenes['Scene']
Scene.unit_settings.system              = 'METRIC'
Scene.unit_settings.system_rotation     = 'DEGREES'


# Custom move operator

        
class ImportAnatomy(Operator):
    bl_idname   = 'ImportAnatomy'
    bl_label    = 'Import anatomy'    
        
   
    



# Class for the add-on panel
class OpenSterotaxyPanel(bpy.types.Panel):
    """Stereotaxic surgical planning tool add-on"""
    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'
    bl_label        = 'Electrode'         
    bl_context      = 'objectmode'
    bl_category     = 'OPenStereotaxy'
    

    chamber_items   = bpy.props.EnumProperty(items= (('0', 'Crist 19mm', 'Standard 19mm diameter chamber for acute recordings'),    
                             ('1', 'Ide-McMahon chronic', 'Chamber for chronic implant with microdive (McMahon et al. 2014)'),    
                             ('2', 'Murphy chronic', 'Chamber with integrated connector housing (2018)'),    
                             ('3', 'Swimming pool', 'Large rectangular chamber for acute recordings and micro-injections')),
                             name = "Chamber type")   
    

    def execute(self, context):
        print("Chamber type", self.chamber_items)
        return {"FINISHED"}

    # Add UI elements here
    def draw(self, context):
        layout  = self.layout 
        scene   = context.scene
         
        box = layout.box()
        col = box.column()
        obj = bpy.data.objects['Electrode_1']
   
        #===== Button for inserting electrode
        row = col.row()    
        row.label(text="Chamber type:")   
        row = col.row()  
        row.operator('AddElectrode', text='Add chamber', icon='MESH_CYLINDER') 
        #row.operator('my.move', text='Select chamber')
        #print("Chamber type", self.chamber_items)
        #layout.operator('mesh.primitive_cylinder_add', text='Add chamber', icon='MESH_CYLINDER')
        
     
        #===== Electrode size controls
        row = col.row()                             
        row.label(text="Electrode dimensions:")  
        row = col.row()
        #row = layout.row(align=True)
        row.prop(obj, 'dimensions',index=0, text='Radius:')
        row = col.row()
        row.prop(obj, 'dimensions',index=2, text='Length:')                  
        
        #===== Electrode positioning controls
        row = col.row()                             
        row.label(text="Electrode trajectory")
        row = col.row()  
        split = row.split()                         # Create two columns, by using a split layout.
        col = split.column(align=True)              # First column   
        col.label(text="Target location")
        col.prop(obj, 'location', index=0, text='X:')
        col.prop(obj, 'location', index=1, text='Y:')
        col.prop(obj, 'location', index=2, text='Z:')
        col = split.column(align=True)              # Second column, aligned
        col.label(text="Electrode angle")
        col.prop(obj, 'rotation_euler', index=0, text='X:')
        col.prop(obj, 'rotation_euler', index=1, text='Y:')
        col.prop(obj, 'rotation_euler', index=2, text='Z:')

        #===== Electrode positioning buttons
        # button    = 'Tip to cursor'
        # button2 = 'End to cursor'

        #===== New label         
        box = layout.box()
        col = box.column()
        row = col.row()    
        row.label(text="Modify chamber:")   



# Register
def register():
    bpy.utils.register_class(OpenSterotaxyPanel)
    bpy.utils.register_class(ImportAnatomy)
    
# Unregister
def unregister():
    bpy.utils.unregister_class(OpenSterotaxyPanel)
    bpy.utils.unregister_class(ImportAnatomy)
    
# Needed to run script in Text Editor
if __name__ == '__main__':
    register()
    
# Add electrode object to scene
def AddElectrode(Length=60, Radius=0.5, Angle=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=Radius, depth=Length)        # Add a cylinder
    cyl                 = bpy.context.object                                # get cylinder object handle
    cyl.name            = 'Electrode_1'                                     # Rename cylinder
    for v in cyl.data.vertices:                                             # For each vertex
        v.co.z += cyl.dimensions.z/2                                        # Move origin to base of cylinder
    cyl.location        = bpy.context.scene.cursor_location                 # Move cylinder base to 3D cursor location
    cyl.rotation_euler  = (math.radians(Angle[0]),0,0)                      # Adjust electrode angle
    return cyl

    
# Import chamber meshes
def ImportChamber(ChamberFiles):
    for ChamberPart in ChamberFiles:
        Import  = bpy.ops.import_scene.stl(filepath=ChamberPart,axis_up='Z')    # Import chamber part geometry from '.stl' file
        ChamberObj  = bpy.context.selected_objects[0]                           # Get object handle