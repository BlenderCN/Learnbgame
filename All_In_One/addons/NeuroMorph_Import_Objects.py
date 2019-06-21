#    NeuroMorph_import_obj_batch.py (C) 2014,  Diego Marcos, Corrado Cali, Biagio Nigro, Anne Jorstad
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/

bl_info = {  
    "name": "NeuroMorph Import Objects (.obj)",
    "author": "Diego Marcos, Corrado Cali, Biagio Nigro, Anne Jorstad",
    "version": (1, 2, 3),
    "blender": (2, 7, 0),
    "location": "Scene > Wavefront (.obj) Batch Import",
    "description": "Imports .obj files in batch, with option of applying a Remesh modifier",  
    "warning": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Learnbgame",
}  

import bpy
import os


# Highlight either use_size_rescaling or use_microns_per_pix_rescaling, but not both
def _gen_order_update(name1, name2):
        def _u(self, ctxt):
            if (getattr(self, name1)):
                setattr(self, name2, False)
            elif (getattr(self, name1) == False and getattr(self, name2) == False):
                setattr(self, name1, True)
        return _u


# Define the import panel within the Scene panel
class ImportWavefrontPanel(bpy.types.Panel):
    bl_label = "Import Objects"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene , "remesh_when_importing")
        row.prop(context.scene , "apply_remesh")         
        
        row = self.layout.row()
        row.prop(context.scene , "use_smooth_shade")

        row = self.layout.row()
        row.prop(context.scene , "remesh_octree_depth")

        row = self.layout.row()
        row.prop(context.scene , "pix_scale")
       
        row = self.layout.row()
        row.operator("import.obj", text='Import Object(s)', icon='MESH_ICOSPHERE')
              
        
class ObjImportButton(bpy.types.Operator):
    """Objects will be resized by the scale provided"""
    bl_idname = "import.obj"
    bl_label = "Import (might take several minutes)"
 
    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    files = bpy.props.CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
    
    def execute(self, context):
        #print(self.directory)
        #files = os.listdir(self.directory)
        #ObjBatchImport(self.directory,files)

        items = [file.name for file in self.files]
        ObjBatchImport(self.directory,items)

        return {'FINISHED'} 
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}         


def ObjBatchImport(dir,files):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    old_objects = bpy.data.objects[:]
    
    for f in files:
        if f[-4:] == '.obj':
            bpy.ops.import_scene.obj(filepath=dir + f)    

    s = bpy.context.scene.pix_scale

    for ob in bpy.data.objects[:]:
         
         if ob not in old_objects:
             
             bpy.context.scene.objects.active = ob
             bpy.data.objects.get(ob.name).select = True
             ob.scale = [s, s, s]  # anisotropic image stacks should be handled by the user
             ob.rotation_euler = [-0, 0, 0]
             bpy.ops.object.transform_apply(scale=True)
             if bpy.context.scene.remesh_when_importing == True:
                
                ob.modifiers.new("import_remesh", type='REMESH')
                ob.modifiers['import_remesh'].octree_depth = bpy.context.scene.remesh_octree_depth
                ob.modifiers['import_remesh'].mode = 'SMOOTH'
                ob.modifiers['import_remesh'].use_smooth_shade = bpy.context.scene.use_smooth_shade
                ob.modifiers['import_remesh'].use_remove_disconnected = False
                if bpy.context.scene.apply_remesh == True:
                   bpy.context.scene.objects.active = ob
                   bpy.ops.object.modifier_apply(modifier='import_remesh')

    #bpy.ops.object.transform_apply(scale=True)
               

def register():
    bpy.utils.register_module(__name__)

    # Define import properties
    bpy.types.Scene.remesh_when_importing = bpy.props.BoolProperty \
        (
        name = "Use Remesh",
        description = "Add 'Remesh' modifier to imported meshes in smooth mode",
        default = True
        )
    bpy.types.Scene.apply_remesh = bpy.props.BoolProperty \
        (
        name = "Finalize Remesh",
        description = "Apply 'Remesh' modifier without editable preview; original meshes will be deleted",
        default = False
        )
    bpy.types.Scene.use_smooth_shade = bpy.props.BoolProperty \
        (
        name = "Smooth Shading",
        description = "Smooth the output faces (recommended)",
        default = True
        )
    bpy.types.Scene.remesh_octree_depth = bpy.props.IntProperty \
        (
        name = "Remesh Resolution",
        description = "Octree resolution: higher values result in finer details",
        default = 7
        )
    bpy.types.Scene.pix_scale = bpy.props.FloatProperty \
        (
        name = "Scale (microns per pixel)",
        description = "Scale used to resize object during in import (number of microns per pixel in the image stack)",
        default = 1.0,
        min = 1e-100,
        precision=4
        )

    bpy.types.Scene.source =  bpy.props.StringProperty(subtype="FILE_PATH")

    pass
    
def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.source
    del bpy.types.Scene.pix_scale
    del bpy.types.Scene.remesh_octree_depth
    del bpy.types.Scene.use_smooth_shade
    del bpy.types.Scene.apply_remesh
    del bpy.types.Scene.remesh_when_importing

    pass
    
if __name__ == "__main__":
    register()  
