import bpy
import os
import subprocess

from ..preferences import get_addon_preferences
from ..misc_functions import absolute_path

#playback range cache
class VCachePlaybackRangeCache(bpy.types.Operator):
    bl_idname = "vcache.playback_rangecache"
    bl_label = "Playback range corresponding Cache"
    bl_description = "Playback range corresponding Viewport cached Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        scn=bpy.context.scene
        filelist=[]
        nfilelist=[]
        
        addon_preferences = get_addon_preferences()
        ffmpegPath=absolute_path(addon_preferences.ffmpeg_executable)
        externalplayer=addon_preferences.external_player_executable
        cache_format = addon_preferences.cache_format
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        
        opath=scn.render.filepath
        start=scn.frame_start
        end=scn.frame_end
        
        oformat=scn.render.image_settings.file_format
        
        if bpy.data.is_saved:
            blendname=(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        else:
            blendname='untitled'
        scenename=scn.name
        
        match=blendname + "___" + scenename + "___cache_"
        
        if cache_format=='JPEG':
                ext=".jpg"
        elif cache_format=='PNG':
            ext=".png"
        elif cache_format=='BMP':
            ext=".bmp"
        elif cache_format=='TARGA':
            ext=".tga"
        elif cache_format=='TIFF':
            ext=".tif"
        
        #build lists  
        chk=0
        for f in os.listdir(cachefolder):
            if match in f and ext in f:
                chk=1
                framenumber=int(os.path.splitext((f.split(match)[1]).lstrip("0"))[0])
                filelist.append(framenumber)
                
        if chk==1:
            for n in filelist:
                if n<=end:
                    nfilelist.append(n)
            
            missing=sorted(set(range(start, end + 1)).difference(nfilelist))
            if len(missing)!=0:
                self.report({'WARNING'}, "Missing frames in the sequence : " + str(missing))
                
                #create missing frames
                size=str(100)
                for n in missing:
                    name=match+str(n).zfill(10)+ext
                    outp=os.path.join(cachefolder, name)
                    ffCMD=ffmpegPath+" -f lavfi -i color=c=black:size="+size+"x"+size+" -frames:v 1 "+'"'+outp+'"'
                    subprocess.call(ffCMD)
            else:
                self.report({'INFO'}, "Frame Range Playback launched")
                
            #check player and play            
            if externalplayer=='':
                match2=match+"##########"
                scn.render.filepath = os.path.join(cachefolder, match2)
                scn.render.image_settings.file_format=cache_format
                bpy.ops.render.play_rendered_anim()
                scn.render.filepath = opath
                scn.render.image_settings.file_format=oformat
            else:
                filename=match+str(nfilelist[0]).zfill(10)+ext
                file=os.path.join(cachefolder, filename)
                print(file)
                p = subprocess.Popen([absolute_path(externalplayer), file])
        
        else:
            self.report({'WARNING'}, "No corresponding cache files")
        
        return {'FINISHED'}