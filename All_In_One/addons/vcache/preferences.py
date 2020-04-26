import bpy
import os

addon_name = os.path.basename(os.path.dirname(__file__))

class VCacheAddonPrefs(bpy.types.AddonPreferences):
    bl_idname = addon_name
    
    prefs_folderpath = bpy.props.StringProperty(
            name="Preferences Folder Path",
            default=os.path.join(bpy.utils.user_resource('CONFIG'), "viewport_cache_files"),
            description="Folder where Cache Files will be stored",
            subtype="DIR_PATH",
            )
            
    ffmpeg_executable = bpy.props.StringProperty(
            name="Path to FFMPEG executable",
            default='',
            description="Points to external executable file of FFMPEG for cubemap stitch functions (ffmpeg release folder\bin\executable file)",
            subtype="FILE_PATH"
            )
    
    external_player_executable = bpy.props.StringProperty(
            name="Path to External Player executable",
            default='',
            description="Points to external executable file of Player for playback functions",
            subtype="FILE_PATH"
            )
    
    vrplayer_executable = bpy.props.StringProperty(
            name="Path to VR Player executable",
            default='',
            description="Points to external executable file of VR Player for cubemap playback functions",
            subtype="FILE_PATH"
            )
    
    cache_format = bpy.props.EnumProperty(items = (('PNG', "PNG", "Portable Network Graphics"),
                 ('TARGA', "TARGA", "Targa"),
                 ('BMP', "BMP", "Bitmap"),
                 ('JPEG', "JPEG", "Joint Photographic Experts Group"),
                 ('TIFF', "TIFF", "Tagged Image File Format")
                 ),
                 default = 'JPEG',
                 name = 'Cache Format'
                 )
    
    cache_format_depth = bpy.props.EnumProperty(items = (('8', "8", ""),
                 ('16', "16", "")
                 ),
                 default = '8',
                 name = 'Color Depth'
                 )
                 
    cache_format_channel = bpy.props.EnumProperty(items = (('RGB', "RGB", ""),
                 ('RGBA', "RGBA", "")
                 ),
                 default = 'RGB',
                 name = 'Channels'
                 )
                 
    cache_tiff_compression = bpy.props.EnumProperty(items = (('NONE', "None", ""),
                 ('DEFLATE', "Deflate", ""),
                 ('LZW', "LZW", ""),
                 ('PACKBITS', "Pack Bits", ""),
                 ),
                 default = 'DEFLATE',
                 name = 'Tiff Compression'
                 )
    
    cache_format_compression = bpy.props.IntProperty(
            name="Cache Images Compression",
            default=10,
            min=0,
            max=100
            )
    
    cache_format_quality = bpy.props.IntProperty(
            name="Cache Images Quality",
            default=90,
            min=0,
            max=100
            )
            
    cache_dimension_coef = bpy.props.IntProperty(
            name="Cache Images Resulotion Multiplier",
            default=1,
            min=1,
            max=10
            )
            
    cache_real_viewport_size = bpy.props.BoolProperty(
            name="Cache Viewport real size",
            description="Cached Images will have the viewport size without taking toolshelf and properties panels size into account",
            default=False
            )
    
    vcache_play_after_caching = bpy.props.BoolProperty(
            name="Play after Caching",
            description="Cached Images will be played instantly after caching",
            default=True
            )
    
    cache_vr_video_format = bpy.props.EnumProperty(items = (('mp4', "Mp4", "Mpeg 4"),
                 ('mov', "Mov", "Quicktime"),
                 ('avi', "Avi", "Audio Video Interleave"),
                 ),
                 default = 'mp4',
                 name = 'VR Video Format'
                 )        

    pref_general = bpy.props.BoolProperty(
            name="General Settings",
            default=False
            )
            
    pref_format = bpy.props.BoolProperty(
            name="Format Settings",
            default=False
            )
            
    pref_infos = bpy.props.BoolProperty(
            name="Informations",
            default=False
            )
                
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        box=col.box()
        row=box.row()
        if self.pref_general==False:
            row.prop(self, 'pref_general', icon='TRIA_RIGHT', text='', emboss=False)
        else:
            row.prop(self, 'pref_general', icon='TRIA_DOWN', text='', emboss=False)
        row.label('General Settings', icon='SCRIPTWIN')
        if self.pref_general==True:
            row=box.row()
            row.prop(self, 'vcache_play_after_caching')
            row=box.row()
            row.prop(self, 'prefs_folderpath', text='External Cache Folder Path')
            row=box.row()
            row.prop(self, 'ffmpeg_executable', text='External FFMPEG executable')
            row=box.row()
            row.prop(self, 'external_player_executable', text='External Player executable')
#            row=box.row()
#            row.prop(self, 'vrplayer_executable', text='External VR Player executable')
        
        box=col.box()
        row=box.row()
        if self.pref_format==False:
            row.prop(self, 'pref_format', icon='TRIA_RIGHT', text='', emboss=False)
        else:
            row.prop(self, 'pref_format', icon='TRIA_DOWN', text='', emboss=False)
        row.label('Cache Format Settings', icon='IMAGE_DATA')
        if self.pref_format==True:
            row=box.row()
            row.prop(self, "cache_real_viewport_size", text='Real Viewport Size')
            row.prop(self, 'cache_dimension_coef', text='Resolution Multiplier')
            row=box.row()
            row.prop(self, "cache_format", expand=False, text="Cache Format")
            if self.cache_format=='JPEG':
                row.prop(self, 'cache_format_quality', text='Quality')
            elif self.cache_format =='PNG':
                row.prop(self, 'cache_format_compression', text='Compression')
                row.prop(self, "cache_format_depth", expand=False, text="Depth")
                row.prop(self, 'cache_format_channel', expand=False, text='')
            elif self.cache_format == 'TIFF':
                row.prop(self, 'cache_tiff_compression', expand=False, text='Compression')
                row.prop(self, "cache_format_depth", expand=False, text="Depth")
                row.prop(self, 'cache_format_channel', expand=False, text='')
#            row=box.row()
#            row.prop(self, "cache_vr_video_format", expand=False)
                
        box=col.box()
        row=box.row()
        if self.pref_infos==False:
            row.prop(self, 'pref_infos', icon='TRIA_RIGHT', text='', emboss=False)
        else:
            row.prop(self, 'pref_infos', icon='TRIA_DOWN', text='', emboss=False)
        row.label('Utils', icon='QUESTION')
        if self.pref_infos==True:
            row=box.row()
            row.operator("vcache.open_cache", icon='FILE_FOLDER')
            row=box.row()
            row.label('Default Shortcuts', icon='SORTALPHA')
            split=box.split()
            col=split.column(align=True)
            col.label('Pie Menu')
            col.label('Cache')
            col.label('Playback')
            col.label('Scene Settings')
            col=split.column(align=True)
            col.label('ctrl + alt + Y')
            col.label('alt + Y')
            col.label('ctrl + Y')
            col.label('shift + Y')
        

# get addon preferences
def get_addon_preferences():
    addon = bpy.context.user_preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)