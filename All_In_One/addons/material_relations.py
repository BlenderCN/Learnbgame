# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Display material relationship",
    "author": "Antonio Vazquez (antonioya)",
    "version": (0, 1, 1),
    "blender": (2, 68, 0),
    "location": "Material Panel",
    "description": "Display the objects that use the selected material.",
    "category": "Learnbgame"
}


import bpy
#------------------------------------------------------
# Action class
#------------------------------------------------------
class RunAction(bpy.types.Operator):
    bl_idname = "object.select_material"
    bl_label = "Select"
    bl_description = "Select objects with current material"

    #------------------------------
    # Execute
    #------------------------------
    def execute(self, context):
        # Get current material
        currentMaterial = bpy.context.object.active_material
        # Loop material list
        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                if slot.material == currentMaterial:
                    obj.select = True
        
        return {'FINISHED'}
#------------------------------------------------------
# UI Class
#------------------------------------------------------
class PanelUI(bpy.types.Panel):
    bl_label = "Material relationship"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"    
    
    #------------------------------
    # Draw UI
    #------------------------------
    def draw(self, context):
        layout = self.layout
        if (bpy.context.object.active_material is not None):
            # Button
            row = layout.row(align=False)
            row.operator("object.select_material", icon='BORDER_RECT')
            row.label(" ")
            # info
            row = layout.row()
            # Get current material
            currentMaterial = bpy.context.object.active_material
            # Loop material list
            objList = []
            for obj in bpy.data.objects:
                for slot in obj.material_slots:
                    if slot.material == currentMaterial:
                        objList.append(obj)  
            # Display result
            row.label(currentMaterial.name + "  (" + str(len(objList)) + " relationship)", icon='MATERIAL_DATA')

            
            box = layout.box()
            for obj in bpy.data.objects:
                for slot in obj.material_slots:
                    if slot.material == currentMaterial:
                        objList.append(obj)  
                        row = box.row()
                        buf = obj.name
                        if (len(obj.material_slots) > 1):
                            buf = buf + "  (" + str(len(obj.material_slots)) + " materials)"
                        
                        row.label(buf, icon='OBJECT_DATAMODE')          
            

        else:
            buf = "** No selected material **"
            layout.label(buf, icon='MATERIAL_DATA')
                
        
#------------------------------------------------------
# Registration
#------------------------------------------------------
def register():
    bpy.utils.register_class(RunAction)
    bpy.utils.register_class(PanelUI)
    

def unregister():
    bpy.utils.unregister_class(RunAction)
    bpy.utils.unregister_class(PanelUI)


if __name__ == "__main__":
    register()
