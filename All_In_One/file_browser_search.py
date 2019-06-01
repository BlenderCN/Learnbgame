# file_brower_search.py Copyright (C) 2012, Jakub Zolcik
#
# Relaxes selected vertices while retaining the shape as much as possible
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "File Browser Search",
    "author": "Jakub Zolcik",
    "version": (0,1,1),
    "blender": (2, 6, 1),
    "api": 35622,
    "location": "File Browser",
    "description": "Searches through files in File Browser",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

"""
Usage:

Launches in File Browser

"""

import bpy
import os
import re

 
class FilteredFileItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="File name", default="")
    dname = bpy.props.StringProperty(name="Display name", default="")
    
def fileSearch(self, context):

    filter = context.window_manager.filtered_search_prop
    directory = context.window_manager.last_directory_prop
    
    filecol = context.window_manager.filtered_files_prop
    
    for fname in filecol:
        filecol.remove(0)

    if filter=="":
        return None
    
    pattern = ""
    if(len(filter) < 3):
        pattern = (filter.lower() + r".*\..*")
    else:
        pattern = (r".*" + filter.lower() + r".*\..*")
    prog = re.compile(pattern)    


    maxf = 100
    cf = 0
    dlen = len(directory)

    if context.window_manager.file_searchtree:
        for path, dirs, files in os.walk(directory):
            for filename in files:
                filename = (os.path.join(path, filename))[dlen:]
                #rfilename = (os.path.join(path, filename))[dlen:]
                if prog.match(filename.lower()) != None:
                    p = context.window_manager.filtered_files_prop.add()
                    #p.name = rfilename
                    p.name = filename
                    if context.window_manager.file_hideextensions:
                        ind = filename.rfind(".")
                        if ind > -1:
                            filename = filename[0:ind]
                    p.dname = filename
                    cf+=1
                if(cf>=maxf):
                    break
            if(cf>=maxf):
                break;
            
    else:
        filesList=os.listdir(directory)
        for filename in filesList:
            if prog.match(filename.lower()) != None:
                p = context.window_manager.filtered_files_prop.add()
                p.name = filename
                if context.window_manager.file_hideextensions:
                    ind = filename.rfind(".")
                    if ind > -1:
                        filename = filename[0:ind]
                p.dname = filename
    
    return None    

def blendDataFromFile(file, part):
    with bpy.data.libraries.load(file) as (data_from, data_to):
        if part == "Brush":
            return data_from.brushes
        elif part == "Camera":
            return data_from.cameras
        elif part == "Lamp":        
            return data_from.lamps
        elif part == "Material":
            return data_from.materials
        elif part == "Mesh":
            return data_from.meshes
        elif part == "MovieClip":
            return data_from.movieclips
        elif part == "Object":
            return data_from.objects
        elif part == "Scene":
            return data_from.scenes
        elif part == "Text":
            return data_from.texts
        elif part == "Texture":
            return data_from.textures
        elif part == "World":
            return data_from.worlds
        else:
            return None

def notFileSearch(self, context):

    filter = context.window_manager.filtered_search_prop
    directory = context.window_manager.last_directory_prop
    
    filecol = context.window_manager.filtered_files_prop
    
    for fname in filecol:
        filecol.remove(0)

    if filter=="":
        return None

    ind_e = directory.find(".blend")

    if(ind_e == -1):
        return None

    ind_e = ind_e + 6
    
    file = directory[0:ind_e]

    part = directory[ind_e+1:-1]

    if (part == ""):
        return None

    data = None

    data = blendDataFromFile(file, part)
    
    pattern = ""
    if(len(filter) < 3):
        pattern = (filter.lower() + r".*")
    else:
        pattern = (r".*" + filter.lower() + r".*")
    prog = re.compile(pattern)


    for name in data:
        if prog.match(name.lower()) != None:
            p = context.window_manager.filtered_files_prop.add()
            p.name = name
            p.dname = name

    return None   


def filteredSearchFunc(self, context):

    if(context.active_operator.bl_idname=="WM_OT_link_append"):
        return notFileSearch(self, context)
    else:
        return fileSearch(self, context)



class FilteredFileSelectOperator(bpy.types.Operator):
    bl_idname = "file.filtered_file_select"
    bl_label = "Select File"

    fname = bpy.props.StringProperty()

    def execute(self, context):
        context.space_data.params.filename = self.fname
        if context.window_manager.file_autoexecute:
            bpy.ops.file.execute('INVOKE_DEFAULT')
        return {'FINISHED'}


 

class FilteredSearchPanel(bpy.types.Panel):

    bl_idname = "FILE_PT_filteredsearch"

    bl_label = "Search:"

    bl_space_type = 'FILE_BROWSER'

    bl_region_type = 'CHANNELS'


    @classmethod
    def poll(cls, context):
        return (context.space_data.params is not None)

    def draw(self, context):

        layout = self.layout
        
        directory = context.space_data.params.directory
        
        if context.window_manager.last_directory_prop != directory:
            context.window_manager.last_directory_prop = directory
            filteredSearchFunc(self, context)
        

        layout.prop(context.window_manager, "filtered_search_prop")
        box = layout.box()
        length = len(context.window_manager.filtered_files_prop)
        incolumn = int(length / context.window_manager.file_columnsnumber)
        r = length % context.window_manager.file_columnsnumber
        row = box.row()
        col = row.column()
        it = 0
        tr = 0

        for f in context.window_manager.filtered_files_prop:
            col.operator("file.filtered_file_select", text = f.dname, emboss=False).fname = f.name
            it+=1
            if tr < r:
                if it % (incolumn + 1) == 0:
                    tr+=1
                    if(it<length):
                        col = row.column()
            else:
                if (it - tr) % incolumn == 0:
                    if(it<length):
                        col = row.column()
        
        layout.prop(context.window_manager, "file_autoexecute")
        layout.prop(context.window_manager, "file_searchtree")
        layout.prop(context.window_manager, "file_hideextensions")
        layout.prop(context.window_manager, "file_columnsnumber")



def register():

    bpy.utils.register_module(__name__)

    bpy.types.WindowManager.filtered_search_prop = bpy.props.StringProperty(update=filteredSearchFunc)
    bpy.types.WindowManager.last_directory_prop = bpy.props.StringProperty()
    bpy.types.WindowManager.file_autoexecute = bpy.props.BoolProperty(name="Open Automatically")
    bpy.types.WindowManager.file_hideextensions = bpy.props.BoolProperty(name="Hide Extensions", update=filteredSearchFunc)
    bpy.types.WindowManager.file_searchtree = bpy.props.BoolProperty(name="Search Subdirectories", update=filteredSearchFunc)
    bpy.types.WindowManager.file_columnsnumber = bpy.props.IntProperty(name="Number of Columns", default=1, min=1, max=15, update=filteredSearchFunc)
    bpy.types.WindowManager.filtered_files_prop = bpy.props.CollectionProperty(type=FilteredFileItem)
    

def unregister():
    
    del bpy.types.WindowManager.filtered_search_prop
    del bpy.types.WindowManager.last_directory_prop
    del bpy.types.WindowManager.file_autoexecute
    del bpy.types.WindowManager.filtered_files_prop
    del bpy.types.WindowManager.file_searchtree
    del bpy.types.WindowManager.file_hideextensions
    del bpy.types.WindowManager.file_columnsnumber

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
