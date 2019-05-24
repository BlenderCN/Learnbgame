'''
Copyright (C) 2015 Pistiwique

Created by Pistiwique

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Auto matcap setup",
    "author": "Pistiwique, Matpi",
    "version": (0, 1, 0),
    "blender": (2, 74, 0),
    "description": "Setup matcap",
    "wiki_url": "https://www.youtube.com/watch?v=-uxy9irGr80",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=26&t=1064",
    "category": "Learnbgame",
}
    
    
import bpy, os.path
from bpy.props import *
import pickle

bpy.types.Scene.my_dirpath = bpy.props.StringProperty(name="", maxlen=1024, subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'})


#####################################
#####   User preferences panel  #####
#####################################

class AutoMatcapPrefs(bpy.types.AddonPreferences):
    """Creates the tools in a Panel, in the scene context of the properties editor"""
    bl_idname = __name__

    bpy.types.Scene.Enable_Tab_01 = bpy.props.BoolProperty(default=False)
    
    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "Enable_Tab_01", text="Info", icon="QUESTION")
        if context.scene.Enable_Tab_01:
            row = layout.row()
            row.label(text="Matcap directory path")
            row.prop(context.scene, "my_dirpath")
            
######################################################################            
    
def SaveCurrentSetup():

    myfilepath = bpy.path.abspath('//')
    mydirectory = os.path.dirname(myfilepath)+"/"
    
    my_dict = {}
    key = "materials"
      
    my_dict["render_engine"] = bpy.context.scene.render.engine 
    my_dict["material_mode"] = bpy.context.scene.game_settings.material_mode
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    myViewport_shade = space.viewport_shade
    my_dict["viewport_shade"] = myViewport_shade
    if bpy.context.active_object.active_material:        
        for mat in bpy.context.active_object.material_slots:
            list_mat = mat.name
            my_dict.setdefault(key, [])
            my_dict[key].append(list_mat)
            
    else:        
        my_dict["materials"] = "No material"
            
    output = open(mydirectory + "backup_setup", "wb")
    pickle.dump(my_dict, output)
    output.close()            

def SetupScene():
    # Configure the scene
    bpy.context.scene.render.engine = 'BLENDER_RENDER'
    bpy.context.scene.game_settings.material_mode = 'GLSL'
    bpy.context.space_data.viewport_shade = 'TEXTURED'
                    
class AutoMatcapPanel(bpy.types.Panel):
    bl_idname = "matcapPanel"
    bl_label = "Auto Matcap setup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        
        ob = context.object

        myfilepath = bpy.path.abspath('//')
        mydirectory = os.path.dirname(myfilepath)+"/"
               
        if bpy.context.object and bpy.context.object.type == 'MESH':
            if not bpy.data.filepath:
                layout.label(icon="CANCEL", text="Need to save blend first")
                layout.operator("wm.save_mainfile", text="Save As", icon="FILE_TICK")
            else:
                if not bpy.data.materials or 'Matcap' not in bpy.data.materials:
                   layout.operator("object.new_matcap", text="Create Matcap", icon='MATCAP_07')
                elif 'Matcap' in bpy.data.materials and not os.path.isfile(mydirectory + "backup_setup"):
                    layout.operator("object.setup_matcap", text="Setup Matcap", icon='MATCAP_07')
                else:
                    layout.operator("object.new_matcap", text="New Matcap texture", icon='MATCAP_07')
                if ob.active_material and ob.active_material.name == 'Matcap':
                    layout.label(text=ob.active_material.active_texture.image.name)
                    layout.template_ID_preview(ob.active_material, "active_texture", new="texture.new", rows=3, cols=8)
                    if os.path.isfile(mydirectory + "backup_setup"):
                        layout.operator("object.previous_setup", icon="LOOP_BACK")
         
        else:
            layout.label(icon="ERROR", text="No mesh in the scene")
      
class  NewMatcap(bpy.types.Operator):
    bl_idname = "object.new_matcap"
    bl_label = "Create new Matcap"
    bl_options = {'REGISTER'}
    
    filepath = StringProperty(subtype='FILE_PATH')

    directory = StringProperty(subtype='DIR_PATH')
        
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.select
    
    def execute(self, context):

        myfilepath = bpy.path.abspath('//')
        mydirectory = os.path.dirname(myfilepath)+"/"
     
        if bpy.data.materials:
           
            # get list of image before loadind the next
            img_listA = []

            for imgA in bpy.data.images:
                img_listA.append(imgA.name)

            try:
                img = bpy.data.images.load(self.filepath)
            except:
                raise NameError("Cannot load image %s" % self.filepath)

            # get list of image after loading
            img_listB = []

            for imgB in bpy.data.images:
                img_listB.append(imgB.name) 

            # comparison of 2 lists      
            last_img = [item for item in img_listB if item not in img_listA]

            # convert result list in string
            img_Name = ''.join(last_img)
                               
            if 'Matcap' in bpy.data.materials and os.path.isfile(mydirectory + "backup_setup"):
                # Define Matcap material as active   
                bpy.context.active_object.active_material = bpy.data.materials['Matcap']
             
                # Create image texture from image
                matTex = bpy.data.textures.new(img_Name, type = 'IMAGE')
                matTex.image = img 
                
                bpy.data.materials['Matcap'].active_texture = bpy.data.textures[img_Name]
                
                return {'FINISHED'}
               
            elif not 'Matcap' in bpy.data.materials and not os.path.isfile(mydirectory + "backup_setup"): 
                
                SaveCurrentSetup()
                
                SetupScene()
                
                if bpy.context.active_object.material_slots:   
                    for mat in context.active_object.material_slots:
                        bpy.ops.object.material_slot_remove()
                                
                # create new material        
                mat = bpy.data.materials.new("Matcap")
                mat.diffuse_color = (0.8, 0.8, 0.8)
                mat.use_shadeless = True
                
                # Create image texture from image
                matTex = bpy.data.textures.new(img_Name, type = 'IMAGE')
                matTex.image = img 
                
                # Add texture slot for color texture
                mtex = mat.texture_slots.add()
                mtex.texture = matTex
                mtex.texture_coords = 'NORMAL'
                mtex.use_map_color_diffuse = True 
                mtex.mapping = 'FLAT'
                
                # assign material
                ob = bpy.context.active_object
                me = ob.data
                me.materials.append(mat)
                
                return {'FINISHED'}
            
            elif not 'Matcap' in bpy.data.materials and os.path.isfile(mydirectory + "backup_setup"): 
                
                if bpy.context.active_object.material_slots:   
                    for mat in context.active_object.material_slots:
                        bpy.ops.object.material_slot_remove()
                                
                # create new material        
                mat = bpy.data.materials.new("Matcap")
                mat.diffuse_color = (0.8, 0.8, 0.8)
                mat.use_shadeless = True
                
                # Create image texture from image
                matTex = bpy.data.textures.new(img_Name, type = 'IMAGE')
                matTex.image = img 
                
                # Add texture slot for color texture
                mtex = mat.texture_slots.add()
                mtex.texture = matTex
                mtex.texture_coords = 'NORMAL'
                mtex.use_map_color_diffuse = True 
                mtex.mapping = 'FLAT'
                
                # assign material
                ob = bpy.context.active_object
                me = ob.data
                me.materials.append(mat)
                
                return {'FINISHED'}
               
        else: # no material
            
            SaveCurrentSetup()
            
            SetupScene()

            img_listA = []
            
            for imgA in bpy.data.images:
                img_listA.append(imgA.name)

            try:
                img = bpy.data.images.load(self.filepath)
            except:
                raise NameError("Cannot load image %s" % self.filepath)

            img_listB = []
            
            for imgB in bpy.data.images:
                img_listB.append(imgB.name) 
   
            last_img = [item for item in img_listB if item not in img_listA]

            img_Name = ''.join(last_img)
            
            # create new material        
            mat = bpy.data.materials.new("Matcap")
            mat.diffuse_color = (0.8, 0.8, 0.8)
            mat.use_shadeless = True
            
            # Create image texture from image
            matTex = bpy.data.textures.new(img_Name, type = 'IMAGE')
            matTex.image = img 
            
            # Add texture slot for color texture
            mtex = mat.texture_slots.add()
            mtex.texture = matTex
            mtex.texture_coords = 'NORMAL'
            mtex.use_map_color_diffuse = True 
            mtex.mapping = 'FLAT'
            
            # assign material
            ob = bpy.context.active_object
            me = ob.data
            me.materials.append(mat)
            
            return {'FINISHED'}
   
    def invoke(self, context, event):
        scn = context.scene
        self.directory = scn.my_dirpath
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class  SetupMatcap(bpy.types.Operator):
    bl_idname = "object.setup_matcap"
    bl_label = "Setup Matcap"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
               
        SaveCurrentSetup()
        
        SetupScene()
        
        if context.active_object.material_slots:
            for mat in context.active_object.material_slots:
                bpy.ops.object.material_slot_remove()
      
        # Define Matcap material as active   
        bpy.context.active_object.active_material = bpy.data.materials['Matcap']

        return {'FINISHED'} 
    
class BackBackupSetup(bpy.types.Operator):
    ''' Back to setup before created Matcap'''
    bl_idname = "object.previous_setup"
    bl_label = "Previous setup"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        
        myfilepath = bpy.path.abspath('//')
        mydirectory = os.path.dirname(myfilepath)+"/"
        # read python dict back from the file
        pkl_file = open(mydirectory + "backup_setup", "rb")
        my_dict = pickle.load(pkl_file) 
        
        bpy.context.scene.render.engine = my_dict["render_engine"]
        bpy.context.scene.game_settings.material_mode = my_dict["material_mode"]
        bpy.context.space_data.viewport_shade = my_dict["viewport_shade"]  
        if my_dict["materials"] == "No material":
            for mat in context.active_object.material_slots:
                bpy.ops.object.material_slot_remove()
        else:
            for mat in context.active_object.material_slots:
                bpy.ops.object.material_slot_remove()
            ob = bpy.context.active_object
            me = ob.data
            my_mat = my_dict["materials"]
            for mat in my_mat:
                mat_list = bpy.data.materials[mat]
                me.materials.append(mat_list)                   
        pkl_file.close()
        os.remove(mydirectory + "backup_setup")
        
        return {'FINISHED'}
   
def register():
   bpy.utils.register_module(__name__)

 
def unregister():
    bpy.utils.unregister_module(__name__)

 
if __name__ == "__main__":
    register()