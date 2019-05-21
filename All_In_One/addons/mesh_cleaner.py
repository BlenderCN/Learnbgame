'''
 * ------------------------------------------------------------
 * "THE BEERWARE LICENSE" (Revision 42):
 * Greenbaburu wrote this code. As long as you retain this 
 * notice, you can do whatever you want with this stuff. If we
 * meet someday, and you think this stuff is worth it, you can
 * buy me a beer in return.
 * ------------------------------------------------------------
'''

bl_info = {
    "name": "mesh_cleaner",
    "author": "Greenbaburu",
    "version": (0, 2, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tools > Mesh Cleaner",
    "description": "Clean the mesh",
    "category": "Mesh Tool",
    }

import bpy

objects_list = []

# remove doubles and dissolve limit
def redis():
    bpy.ops.mesh.select_all(action='SELECT')           
    bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
    bpy.ops.mesh.dissolve_limited(angle_limit=0.0872665, use_dissolve_boundaries=False, delimit={'NORMAL'})
    bpy.ops.mesh.normals_make_consistent(inside=False)

class AllMeshCleanerOperator(bpy.types.Operator):
    """Clean all the meshes"""
    bl_idname = "mesh.mesh_clean_all_operator"
    bl_label = "Mesh Cleaner Operator"
    
    name = bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        name = self.name
        scene = context.scene

        print(objects_list)        
           
        for obj in objects_list:
            
            object = scene.objects[obj.name]
            bpy.context.scene.objects.active = object
            
            try: # from Edit Mode
                redis()
            except: # from Object Mode 
                bpy.ops.object.editmode_toggle()
                redis()
                bpy.ops.object.editmode_toggle()        
        
        return {'FINISHED'}
       

class MeshCleanerOperator(bpy.types.Operator):
    """Clean mesh"""
    bl_idname = "mesh.mesh_clean_operator"
    bl_label = "Mesh Cleaner Operator"
    
    name = bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        name = self.name
        scene = context.scene
        object = scene.objects[name]
        bpy.context.scene.objects.active = object
        
        try: # from Edit Mode
            redis()
        except: # from Object Mode 
            bpy.ops.object.editmode_toggle()
            redis()
            bpy.ops.object.editmode_toggle()        
        
        return {'FINISHED'}

class Mesh_cleaner_panel(bpy.types.Panel):
    """Mesh Cleaner"""
    bl_label = "Mesh Cleaner"
    bl_idname = "OBJECT_PT_select"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Mesh Cleaner"
    
    def draw(self, context):
        layout = self.layout
        
        row_1 = layout.row()
        row_1.label(text="Selected Objects:") 
                
        row_cleanAll = layout.row()
        row_cleanAll.operator("mesh.mesh_clean_all_operator", text="Clean all the meshes", icon="PARTICLEMODE").name # = obj.name
        
        objects = bpy.context.scene.objects
    
        for obj in objects:            
            if obj.select == True and obj.type == 'MESH':                    
                    
                    if obj not in objects_list: objects_list.append(obj)
                    
                    row_2 = layout.row()                
                    row_2.prop(obj, "name", text="")
                    row_2.prop(obj, "hide", text="")
                    row_2.operator("mesh.mesh_clean_operator", text="", icon="PARTICLEMODE").name = obj.name
        
def register():
    bpy.utils.register_class(Mesh_cleaner_panel)
    bpy.utils.register_class(MeshCleanerOperator)
    bpy.utils.register_class(AllMeshCleanerOperator)

def unregister():
    bpy.utils.unregister_class(Mesh_cleaner_panel)
    bpy.utils.unregister_class(MeshCleanerOperator)
    bpy.utils.unregister_class(AllMeshCleanerOperator)

if __name__ == "__main__":
    register()
