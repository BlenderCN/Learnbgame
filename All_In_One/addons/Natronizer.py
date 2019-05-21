# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

####TODO: Rendering.....

bl_info = {
    "name": "Natronizer",
    "description": "Connect Blender and Natron",
    "author": "Björn Sonnenschein",
    "version": (1, 2),
    "blender": (2, 76, 0),
    "location": "Sequencer > UI panel",
    "warning": "Experimental",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Learnbgame"
}

import bpy, os, glob
from os import listdir
from os.path import isfile, join, expanduser, getmtime
from subprocess import call
import shutil
from bpy.app.handlers import persistent

####Only convert to abspath where needed...

####### Custom Properties
bpy.types.ImageSequence.natronized = bpy.props.BoolProperty(name="Natronized", default=False)
bpy.types.ImageSequence.modifyDate = bpy.props.IntProperty(name="Modify Date", default=0)
bpy.types.ImageSequence.natronProject = bpy.props.StringProperty(name="Natron Project", default="")
bpy.types.ImageSequence.cacheFolder = bpy.props.StringProperty(name="Cache Folder", default="")
bpy.types.Scene.natronPath = bpy.props.StringProperty(name="Natron Path", description="Path to Natron executable", default=expanduser("~") + "/Natron2/Natron", subtype="FILE_PATH")
bpy.types.Scene.natronRendererPath = bpy.props.StringProperty(name="NatronRenderer Path", description="Path to NatronRenderer executable", default= expanduser("~") + "/Natron2/NatronRenderer", subtype="FILE_PATH" )
bpy.types.Scene.customPlugin = bpy.props.StringProperty(name="custom Plugin", description="ID of a Plugin to add to the composition", default="")
bpy.types.Scene.livePreview = bpy.props.BoolProperty(name="live Preview", description="whether the Preview of Natron Projects shall be updated on framechange", default=True)
bpy.types.Scene.livePreview2 = bpy.props.BoolProperty(name="live Preview", description="whether the Preview of Natron Projects shall be updated on framechange", default=False) 

#TODO: Use os.path!

####### Handlers #####
@persistent
def frameChange(scene):
 
    if (bpy.context.scene.livePreview == True):
        current_frame = bpy.context.scene.frame_current
        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == "IMAGE" and i.natronized == True and i.frame_final_start <= current_frame and i.frame_final_end > current_frame and i.mute == False):
                
                date = getmtime(i.natronProject)
                frame =  str(current_frame - i.frame_start + 1)

                if (i.modifyDate < date): ### Check if the project file was modified. If yes, delete cache
                    extension = ".jpg"
                    deleteCache(i, extension)
                    i.modifyDate = date
                    
                framePath = absPath(i.directory + i.elements.items()[int(frame) - 1][1].filename)
                if (os.path.isfile(absPath(framePath)) == False):
                    print ("Rendering Frame")
                    command = absPath(bpy.context.scene.natronRendererPath) + " -w Blender " + frame + "-" + frame + " " +  absPath(i.natronProject)
                    os.system(command)
                    bpy.ops.sequencer.refresh_all()

@persistent
def preRender(scene):
    current_frame = bpy.context.scene.frame_current
    if (current_frame == bpy.context.scene.frame_start):
        if (bpy.context.scene.livePreview == True):
            bpy.context.scene.livePreview == False
            bpy.context.scene.livePreview2 == True

        for i in bpy.context.scene.sequence_editor.sequences:
            if (i.type == "IMAGE" and i.mute == False and i.natronized == True):
                i = setDate(i)
                renderStrip(i)

@persistent
def postRender(scene):
    if (bpy.context.scene.livePreview2 == True):
        bpy.context.scene.livePreview == True
        bpy.context.scene.livePreview2 == False


####### Global Functions #####
def deleteCache(strip, extension):
    print("Cache outdated. Deleting.")
    os.chdir(absPath(strip.cacheFolder))
    filelist = glob.glob("*" + extension)
    for f in filelist:
        os.remove(f)

def absPath(path):
    tempPath = bpy.path.abspath(path)
    absPath = os.path.abspath(tempPath)
    return absPath

def setDate(strip):
    date = getmtime(strip.natronProject)
    strip.modifyDate = date
    return strip

def renderStrip(strip):
    command = absPath(bpy.context.scene.natronRendererPath) + " -w Blender " +  absPath(strip.natronProject)
    os.system(command)
    bpy.ops.sequencer.refresh_all()


####### Panels #####  
class MovieManagerPanel(bpy.types.Panel):    
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Natronize"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout
        
        row = layout.row()
        col = row.column() 
        col.prop( scn, "natronPath" ) 
        row = layout.row()
        col = row.column() 
        col.prop( scn, "natronRendererPath" ) 
        
        row = layout.row()
        col = row.column() 
        col.prop( scn, "customPlugin" ) 
        
        row = layout.row()
        col = row.column() 
        col.operator( "natron.natronize" ) 

        col = row.column() 
        col.operator( "natron.edit" ) 
            
        row = layout.row()
        col = row.column() 
        col.operator( "natron.preview" ) 
        col = row.column() 
        col.prop( scn, "livePreview" ) 


####### Operators #####
class Natronize_Operator(bpy.types.Operator): 
     
    bl_idname = "natron.natronize"
    bl_label = "Natronize"
            
    def invoke(self, context, event ):  
        
        for i in bpy.context.selected_sequences:
            if i.type == "MOVIE":
                extension = ".jpg"
                channelIncrease = 1
                self.executeScripts(i, extension)
                self.createNewStrip(i, channelIncrease,extension)

        return {'FINISHED'}    
    
    def executeScripts (self, strip, extension):
        projectPath = bpy.data.filepath
        stripPath = strip.filepath
        stripName = strip.name
        duration = strip.frame_final_duration + strip.frame_offset_start + strip.frame_offset_end 
        
        renderDir = projectPath + stripName + "/"
        shutil.rmtree(renderDir, ignore_errors=True)
        os.mkdir(absPath(renderDir)) #####Ordner erstellen
        
        scriptPath = renderDir + stripName + ".py"
        script2Path = renderDir + stripName + "modif.py"
        natronProjectPath = renderDir + str(stripName) + ".ntp"
        renderPath = renderDir + "/rendered######"  + extension
        natronPath = bpy.context.scene.natronPath
        customPlugin = bpy.context.scene.customPlugin
        
        scriptFile = open(scriptPath, "w")
        scriptFile.write("app1.resetProject() \n" + \
            "app1.getProjectParam('frameRange').set(1," + str(duration) + ") \n" + \
            "app.saveProjectAs('" + absPath(natronProjectPath) + "') \n" + \
            "app1.closeProject()")
        scriptFile.close()
        
        scriptFile2 = open(script2Path, "w")
        if (customPlugin == ""):
            scriptFile2.write( \
                "n = app1.createNode('fr.inria.openfx.ReadFFmpeg') \n" + \
                "myWriter = app1.createNode('fr.inria.openfx.WriteOIIO') \n" + \
                "v = app1.createNode('fr.inria.built-in.Viewer') \n" + \
                "d = app1.createNode('fr.inria.built-in.Dot') \n" + \
                "n.getParam('filename').set('" + absPath(stripPath) + "') \n" + \
                "n.getParam('ocioInputSpaceIndex').set('" + strip.colorspace_settings.name + "') \n" + \
                "myWriter.getParam('filename').set('" + absPath(renderPath) + "') \n" + \
                "myWriter.setScriptName('Blender') \n" + \
                "myWriter.getParam('frameRange').set('Project frame range') \n" + \
                "myWriter.connectInput(0, d) \n" + \
                "v.connectInput(0, d) \n" + \
                "d.connectInput(0, n) \n" + \
                "d.setPosition(1000,250) \n" + \
                "v.setPosition(950,350) \n" + \
                "myWriter.setPosition(950,150) \n" + \
                "n.setPosition(0,200) \n" + \
                "app1.saveProject('" + absPath(natronProjectPath) + "') \n" + \
                "app1.closeProject()")
                
        else:
            scriptFile2.write( \
                "n = app1.createNode('fr.inria.openfx.ReadFFmpeg') \n" + \
                "myWriter = app1.createNode('fr.inria.openfx.WriteOIIO') \n" + \
                "v = app1.createNode('fr.inria.built-in.Viewer') \n" + \
                "d = app1.createNode('fr.inria.built-in.Dot') \n" + \
                "c = app1.createNode('" + customPlugin + "') \n" + \
                "n.getParam('filename').set('" + absPath(stripPath) + "') \n" + \
                "n.getParam('ocioInputSpaceIndex').set('" + strip.colorspace_settings.name + "') \n" + \
                "myWriter.getParam('filename').set('" + absPath(renderPath) + "') \n" + \
                "myWriter.setScriptName('Blender') \n" + \
                "myWriter.getParam('frameRange').set('Project frame range') \n" + \
                "myWriter.connectInput(0, d) \n" + \
                "v.connectInput(0, d) \n" + \
                "d.connectInput(0, c) \n" + \
                "c.connectInput(0, n) \n" + \
                "d.setPosition(1000,250) \n" + \
                "v.setPosition(950,350) \n" + \
                "myWriter.setPosition(950,150) \n" + \
                "n.setPosition(0,200) \n" + \
                "c.setPosition(400,200) \n" + \
                "app1.saveProject('" + absPath(natronProjectPath) + "') \n" + \
                "app1.closeProject()")
        scriptFile2.close()
        
        command = absPath(natronPath) + " -l " + script2Path + " " +  absPath(natronProjectPath)
       
        call([absPath(natronPath), absPath(scriptPath),  "-b"])
        os.system(command)
        os.remove(absPath(scriptPath))
        os.remove(absPath(script2Path)) 
        
    def createNewStrip (self, strip, channelIncrease, extension):
        projectPath = bpy.data.filepath
        stripName = strip.name
        duration = strip.frame_final_duration + strip.frame_offset_start + strip.frame_offset_end 
        
        renderDir = projectPath + stripName + "/"
        natronProjectPath = renderDir + str(stripName) + ".ntp"
        
        
        file = []
        for j in range(1, duration + 1):
            frame = {"name":"rendered" + str(j).zfill(6) + extension}
            file.append(frame)
        
        bpy.ops.sequencer.select_all(action='DESELECT')
        #i.select = True
        newStrip = bpy.ops.sequencer.image_strip_add(
            directory = renderDir,
            frame_start=strip.frame_start, 
            channel = strip.channel + channelIncrease,
            files = file,
            replace_sel = True)
            
        newStrip = bpy.context.scene.sequence_editor.active_strip
        newStrip.natronProject = natronProjectPath
        newStrip.cacheFolder = renderDir
        newStrip.natronized = True
        newStrip.frame_final_start = strip.frame_final_start
        newStrip.frame_final_end = strip.frame_final_end

            
class Edit_Operator(bpy.types.Operator): 
     
    bl_idname = "natron.edit"
    bl_label = "Edit"
    
    def invoke(self, context, event ):  
        strip=bpy.context.scene.sequence_editor.active_strip
        
        if (strip.natronized == True):
            command = absPath(bpy.context.scene.natronPath) + " " +  absPath(strip.natronProject) + " &"
            os.system(command)
        return {'FINISHED'} 

    
class Preview_Operator(bpy.types.Operator): 
     
    bl_idname = "natron.preview"
    bl_label = "Render Preview"
    
    def invoke(self, context, event ):  
        for i in bpy.context.selected_sequences:
            if (i.type == "IMAGE"):
                if (i.natronized == True):
                    i = setDate(i)
                    renderStrip(i)
        return {'FINISHED'} 

    
def register():
    bpy.utils.register_class( MovieManagerPanel ) 
    bpy.utils.register_class( Natronize_Operator ) 
    bpy.utils.register_class( Edit_Operator ) 
    bpy.utils.register_class( Preview_Operator ) 
    bpy.app.handlers.frame_change_pre.append(frameChange)
    bpy.app.handlers.render_pre.append(preRender)
    bpy.app.handlers.render_post.append(postRender)
def unregister():
    bpy.utils.unregister_class( MovieManagerPanel ) 
    bpy.utils.unregister_class( Natronize_Operator ) 
    bpy.utils.unregister_class( Edit_Operator ) 
    bpy.utils.unregister_class( Preview_Operator ) 
    bpy.app.handlers.frame_change_pre.remove(frameChange)
    bpy.app.handlers.render_pre.remove(preRender)
    bpy.app.handlers.render_post.remove(postRender)
if __name__ == "__main__":
    register()