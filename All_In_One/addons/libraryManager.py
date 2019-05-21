bl_info = {
    "name": "texture library manager",
    "author": "Antonio Mendoza",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "View3D > Panel Tools > Texture library manager panel (sculpt mode)",
    "warning": "",
    "description": "Load and unload image libraries",
    "category": "Paint",
}


import bpy
import os
import sys

from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, FloatProperty, EnumProperty
from bpy.types import Menu, Panel


def findImage (p_Name):
    
    found = False
    
    for img in bpy.data.textures:
        if img.name == p_Name:
            found = True
            break 
        
    return found
    
def selectImages (p_fileList):
    
    file_list = p_fileList
    img_list = [item for item in file_list if item[-3:] == 'png' or item[-3:] == 'jpg' or item[-4:] == 'jpeg' or item[-3:] == 'tga']    
    return img_list

def image_batchImport(p_dir):

    file_list = sorted(os.listdir(p_dir))
    img_list = selectImages (file_list)
    
    for img in img_list:
        dirImage = os.path.join(p_dir, img)
        tName = os.path.basename(os.path.splitext(img)[0])
        
        if findImage(tName) == False:
            nImage = bpy.data.images.load(dirImage)
            nT = bpy.data.textures.new(name=tName,type='IMAGE')
            bpy.data.textures[tName].image = nImage

def image_batchRemove(p_dir):
    file_list = sorted(os.listdir(p_dir))
    img_list = selectImages (file_list)
    
    for img in img_list:
        dirImage = os.path.join(p_dir, img)
        tName = os.path.basename(os.path.splitext(img)[0])
        
        for tex in bpy.data.textures:
            if tex.name == tName:
                if tex.type == 'IMAGE':
                    image = tex.image
                    tex.image.user_clear()
                    bpy.data.images.remove(image)
                    tex.user_clear()
                    bpy.data.textures.remove(tex)
                
def findUserSysPath():
    
    userPath = ''
    
def readLibraryDir():
        dir = ''
        fileDir = os.path.join(bpy.utils.resource_path('USER'), "scripts\\presets\\texture_library.conf")
        if os.path.isfile(fileDir):
            file = open(fileDir, 'r')
            dir = file.read()
            file.close()
        return dir
                  
class LBM_OP_LibraryUnload(bpy.types.Operator):
    bl_idname = "operator.library_unload"
    bl_label = ""
    
    library = bpy.props.StringProperty()
    
    def execute(self, context):
        dir = os.path.join(context.scene.libmng_string_librarydir,self.library)
        image_batchRemove(dir)
        return {'FINISHED'}
    
class LBM_OP_LibraryLoad(bpy.types.Operator):
    bl_idname = "operator.library_load"
    bl_label = ""
    
    library  = bpy.props.StringProperty()
    
    def execute(self, context):
        dir = context.scene.libmng_string_librarydir + '\\' + self.library
        image_batchImport(dir)
        return {'FINISHED'}

     
class LBM_OP_LoadLibraries(bpy.types.Operator):
    bl_idname = "operator.load_libraries"
    bl_label = "Refresh libraries"
    
    name = bpy.props.StringProperty()
    dir_library = bpy.props.StringProperty()
    libraries = []
    
    @classmethod
    def loadLibraryDir(self):
        dir = ''
        fileDir = os.path.join(bpy.utils.resource_path('USER'), "scripts\\presets\\texture_library.conf")
        if os.path.isfile(fileDir):
            file = open(fileDir, 'r')
            dir = file.read()
            file.close()
            
        self.dir_library = dir
        self.findLibraries(self.dir_library)
        
    def saveLibraryDir(self, p_Dir):
        fileDir = os.path.join(bpy.utils.resource_path('USER'), "scripts\\presets\\texture_library.conf")
        file = open(fileDir, 'w+')
        file.write(p_Dir)
        file.close()
        
    def notInLibraries(self,p_item):
        notFound = True
        
        for item in self.libraries:
            if p_item == item:
                notFound = False
                break 
            
        return notFound
       
    @classmethod
    def findLibraries(self, p_dir):
        dir = p_dir
        
        if os.path.isdir(dir):
            file_list = sorted(os.listdir(dir))
            dir_list = []
            del self.libraries[:]
                  
            for item in file_list:
                lib_dir = os.path.join(dir,item)
                if os.path.isdir(lib_dir):
                    dir_list.append(item)
                
            for lib in dir_list:
                lib_dir = os.path.join(dir,lib)
                if os.path.isdir(lib_dir) and self.notInLibraries(self,lib):
                    self.libraries.append(lib)
     
    def execute(self, context):
        self.saveLibraryDir(context.scene.libmng_string_librarydir)
        self.dir_library =  bpy.context.scene.libmng_string_librarydir
        self.findLibraries(context.scene.libmng_string_librarydir)
        
        return {'FINISHED'}
    


class LBM_PN_LibraryManager(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Library manager"
    bl_category = 'Tools'
    #bl_context = 'sculptmode'
    bl_options = {'DEFAULT_CLOSED'}       
    
    @classmethod
    def poll(cls, context):
        return (context.sculpt_object or context.vertex_paint_object or context.vertex_paint_object or context.image_paint_object)
    
    def draw(self,context):
        
        layout = self.layout
        row = layout.row()
        row.prop(context.scene,'libmng_string_librarydir',text='library dir' )

        row = layout.row()
        op = row.operator(LBM_OP_LoadLibraries.bl_idname)
        box = layout.box()
        i = 0
        
 
        for item in LBM_OP_LoadLibraries.libraries:
            row = box.row(align=True)
            op_name = item
            op = row.label(text=op_name)
            opl = row.operator(LBM_OP_LibraryLoad.bl_idname, icon='ZOOMIN')
            opl.library = op_name
            opul = row.operator(LBM_OP_LibraryUnload.bl_idname, icon='ZOOMOUT')
            opul.library = op_name
    
    

def loadInitData():
    LBM_OP_LoadLibraries.loadLibraryDir()
               
def register():
    
    
    default_library = readLibraryDir()
    bpy.types.Scene.libmng_string_librarydir = bpy.props.StringProperty(name="libraryDir", default=default_library, subtype = 'DIR_PATH')
    
    
    bpy.utils.register_class(LBM_OP_LoadLibraries)
    bpy.utils.register_class(LBM_OP_LibraryLoad)
    bpy.utils.register_class(LBM_OP_LibraryUnload)
    bpy.utils.register_class(LBM_PN_LibraryManager)
    
    loadInitData()
    
 
def unregister():
    
    del bpy.types.Scene.libmng_string_librarydir 
    
    bpy.utils.unregister_class(LBM_OP_LoadLibraries)
    bpy.utils.unregister_class(LBM_OP_LibraryLoad)
    bpy.utils.unregister_class(LBM_OP_LibraryUnload)
    bpy.utils.unregister_class(LBM_PN_LibraryManager)
    
if __name__ == "__main__":
    register()