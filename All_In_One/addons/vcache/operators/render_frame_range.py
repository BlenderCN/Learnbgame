import bpy
import os

from ..preferences import get_addon_preferences
from ..misc_functions import absolute_path, create_cache_folder, suppress_files_pattern

#open gl render frame range
class VCacheOpenGLRange(bpy.types.Operator):
    bl_idname = "vcache.opengl_range"
    bl_label = "Cache Frame Range"
    bl_description = "Cache Frame Range"
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        scn=bpy.context.scene
        
        cache=addon_preferences.prefs_folderpath
        cachefolder = absolute_path(cache)
        format = addon_preferences.cache_format
        depth = addon_preferences.cache_format_depth
        quality = addon_preferences.cache_format_quality
        compression = addon_preferences.cache_format_compression
        tiffcompression = addon_preferences.cache_tiff_compression
        channel= addon_preferences.cache_format_channel
        mult = addon_preferences.cache_dimension_coef
        realsize = scn.vcache_real_size
        draft = scn.vcache_draft
        only_render = scn.vcache_only_render
        cam = scn.vcache_camera
        
        opath=scn.render.filepath
        oframe=scn.frame_current
        oformat=scn.render.image_settings.file_format
        odepth=scn.render.image_settings.color_depth
        oquality=scn.render.image_settings.quality
        ocompression=scn.render.image_settings.compression
        otiffcompression=scn.render.image_settings.tiff_codec
        ocolor=scn.render.image_settings.color_mode
        oxsize=scn.render.resolution_x
        oysize=scn.render.resolution_y
        opct=scn.render.resolution_percentage
        ochannel=scn.render.image_settings.color_mode
        oalpha=scn.render.alpha_mode
        oaa=scn.render.use_antialiasing
        osamples=scn.render.antialiasing_samples
        ocam=context.scene.camera
        oonlyrender=bpy.context.space_data.show_only_render
        start=scn.frame_start
        end=scn.frame_end
        
        create_cache_folder()
        
        #find 3d view area
        garea=''
        if bpy.context.area.type=="VIEW_3D":
            garea=bpy.context.area
        else:
            for area in bpy.context.window.screen.areas:
                if area.type=="VIEW_3D":
                    garea=area
        
        if garea!='':
            #define size of the render
            for i in garea.regions:
                if i.type=='HEADER':
                    if i.height!=1:
                        h1=i.height
                    else:
                        h1=0
                elif i.type=='TOOLS' and realsize==False:
                    if i.width!=1:
                        w1=i.width
                    else:
                        w1=0
                elif i.type=='UI' and realsize==False:
                    if i.width!=1:
                        w2=i.width
                    else:
                        w2=0
            if realsize==False:
                nxsize=garea.width-(w1+w2)
                nysize=garea.height-h1
            else:
                nxsize=garea.width
                nysize=garea.height-h1
            
            if bpy.data.is_saved:
                blendname=(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
            else:
                blendname='untitled'
            scenename=scn.name
            pattern=blendname + "___" + scenename + "___cache_"
            fname=pattern + "##########"
            scn.render.filepath = os.path.join(cachefolder, fname)
            
            suppress_files_pattern(cachefolder, pattern)
            
            scn.render.image_settings.file_format = format
            scn.render.image_settings.color_mode = 'RGB'
            scn.render.resolution_x=nxsize
            scn.render.resolution_y=nysize

            if format=='JPEG':
                scn.render.image_settings.quality = quality
            elif format=='PNG':
                scn.render.image_settings.color_depth = depth
                scn.render.image_settings.compression = compression
                scn.render.image_settings.color_mode = channel
                if channel=='RGBA':
                    scn.render.alpha_mode = 'TRANSPARENT'
            elif format=='TIFF':
                scn.render.image_settings.color_depth = depth
                scn.render.image_settings.compression = compression
                scn.render.image_settings.tiff_codec = tiffcompression
                scn.render.image_settings.color_mode = channel
                if channel=='RGBA':
                    scn.render.alpha_mode = 'TRANSPARENT'
            if draft==True:
                scn.render.use_antialiasing = False
                scn.render.resolution_percentage=50
            else:
                scn.render.use_antialiasing = True
                scn.render.antialiasing_samples = '16'
                scn.render.resolution_percentage=100*mult
            if only_render==True:
                bpy.context.space_data.show_only_render=True
            if cam!='':
                chk=0
                for n in bpy.context.scene.objects:
                    if n.name==cam:
                        chk=1
                        scn.render.resolution_x = oxsize
                        scn.render.resolution_y = oysize
                        scn.render.resolution_percentage = opct
                        
                        bpy.context.scene.camera=n
                        bpy.ops.render.opengl(animation=True, write_still=True, view_context=False)
                if chk==0:
                    self.report({'WARNING'}, cam+" missing - Clear it to Cache")
            else:
                bpy.ops.render.opengl(animation=True, write_still=True, view_context=True)
            
            if addon_preferences.vcache_play_after_caching==True:
                bpy.ops.vcache.playback_rangecache()
            
            #reset the renders settings
            scn.render.filepath = opath
            scn.render.image_settings.file_format = oformat
            scn.render.image_settings.color_depth = odepth
            scn.render.image_settings.quality = oquality
            scn.render.image_settings.compression = ocompression
            scn.render.image_settings.tiff_codec = otiffcompression
            scn.render.image_settings.color_mode = ocolor
            scn.render.resolution_x = oxsize
            scn.render.resolution_y = oysize
            scn.render.resolution_percentage = opct
            scn.render.image_settings.color_mode = ochannel
            scn.render.alpha_mode = oalpha
            scn.render.use_antialiasing=oaa
            scn.render.antialiasing_samples=osamples
            bpy.context.space_data.show_only_render=oonlyrender
            bpy.context.scene.camera=ocam

        return {'FINISHED'}