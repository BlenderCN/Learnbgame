bl_info = {
    "name": "Music Player",
    "author": "edddy <edddy74@live.fr> + nikitron.cc.ua a little",
    "version": (0, 2, 2),
    "blender": (2, 7, 5),
    "location": "View3D > Tool Shelf > Music Player",
    "description": "A Little Music Player for Blender",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

from bpy_extras.io_utils import ImportHelper
from bpy.props import *
import bpy, aud, time, threading
import re
import urllib.request as req # for future playlists
import os
import random

#itemdefault = req.urlopen('http://mp3vega.com/down-v1/4770v4/7a374117a2fd/u52089946/audios/testovaya_muzyka_melodiya_super_-_angel_skoro_budet_moya_1_pesnyaot_k_angel%20MP3VEGA.COM.mp3').read()
#bpy.context.scene.mp_playlist.append(itemdefault)
bpy.types.WindowManager.mp_show_names = bpy.props.BoolProperty(default=False,
            name='show_names', description='show playlist')

phrase=['This is it...','That it...','Next...','You good...','She is well...',
        'То что надо...','They did it...','Push...','Alloha...','Na-na-na...',
        'Bam-bam-bam...','Boom...','Jazz...','Wow...','Do it...','Make it...',
        'Keep it on...','Carramba...','Oh yeah...','Bambina...','Muchacha...',
        'Me gustos...','Круто...','Ещё...','Да...','Это оно...','Расслабон...',
        'Да, детка...',]

class MP_Playlist(bpy.types.PropertyGroup):
    playlist = bpy.props.StringProperty()

def volume_up(self, context):
    try:
        context.window_manager.mp_playsound.volume = context.scene.mp_volume
    except:
        pass

def soundIsOn(context):
    try:
        while context.window_manager.mp_playsound.status:
            time.sleep(0.001)
        if context.window_manager.mp_index+1 < context.scene.mp_playlist.__len__():
            context.window_manager.mp_index += 1
            bpy.ops.sound.play()
        elif context.window_manager.mp_cycled:
            context.window_manager.mp_index = 0
            bpy.ops.sound.play()
        else:
            context.window_manager.mp_index = 0
    except:
        pass

def playlistprint():
    pl = [a.playlist for a in bpy.context.scene.mp_playlist]
    print ('Playlist: \n')
    for i, p in enumerate(pl):
        print (str(i+1)+ '.', p)
    return

class MP_writePL(bpy.types.Operator):
    '''Write default playlist'''
    bl_idname = "sound.writeplaylist"
    bl_label = "Write playlist"

    @classmethod
    def poll(cls, context):
        return (context.scene.mp_playlist.__len__())

    def execute(self, context):
        path = os.path.join(os.path.dirname(__file__),'MP_playlist')
        file=open(path, 'w+', encoding='utf-8')
        for t in context.scene.mp_playlist:
            file.write(t.playlist)
        file.close()
        return {'FINISHED'}

class MP_openPL(bpy.types.Operator):
    '''Open default playlist'''
    bl_idname = "sound.openplaylist"
    bl_label = "Open playlist"

    @classmethod
    def poll(cls, context):
        return context.scene.mp_playlist.__len__()

    def execute(self, context):
        path = os.path.join(os.path.dirname(__file__),'MP_playlist')
        file=open(path, 'r+', encoding='utf-8')
        text=file.read()
        file.close()
        for t in text:
            context.scene.mp_playlist.add()
            context.scene.mp_playlist[-1].playlist = t
        return {'FINISHED'}

class MP_Shuffle(bpy.types.Operator):
    '''shuffle'''
    bl_idname = "sound.shuffle"
    bl_label = "Shuffle"

    @classmethod
    def poll(cls, context):
        if context.scene.mp_playlist.__len__():
            return 1
        else:
            return 0

    def execute(self, context):
        #storing
        comp_store = []
        comp_store_names = []
        
        item = context.window_manager.mp_index
        it_adress = context.scene.mp_playlist[item].playlist
        for comp, compn in zip(context.scene.mp_playlist, \
                context.scene.mp_playlist_names):
            comp_store.append(comp.playlist)
            comp_store_names.append(compn.playlist)
        #clearing
        context.scene.mp_playlist.clear()
        context.scene.mp_playlist_names.clear()
        #shuffling
        u = random.randint(0,len(comp_store)-1)
        random.shuffle(comp_store, random=random.seed(u))
        random.shuffle(comp_store_names, random=random.seed(u))
        #rewriting
        k = 0
        for comp, compn in zip(comp_store, comp_store_names):
            context.scene.mp_playlist.add()
            context.scene.mp_playlist_names.add()
            context.scene.mp_playlist[-1].playlist = comp
            context.scene.mp_playlist_names[-1].playlist = compn
            if it_adress == comp:
                context.window_manager.mp_index = k
            k += 1
        
        return {'FINISHED'}
    

class MP_DelComposition(bpy.types.Operator):
    '''delete composition'''
    bl_idname = "sound.delcompos"
    bl_label = "Delete composition"
    
    item_delete = bpy.props.IntProperty(name="item", default=0)
    
    @classmethod
    def poll(cls, context):
        if context.scene.mp_playlist.__len__():
            return 1
        else:
            return 0

    def execute(self, context):
        context.scene.mp_playlist.remove(self.item_delete)
        context.scene.mp_playlist_names.remove(self.item_delete)
        if context.window_manager.mp_index > 0 and \
                self.item_delete < context.window_manager.mp_index:
            context.window_manager.mp_index -= 1
        elif self.item_delete == context.window_manager.mp_index and \
                context.window_manager.mp_playsound.status:
            bpy.ops.sound.stop()
        return {'FINISHED'}

class MP_PlaySIC(bpy.types.Operator):
    '''Play a sound File'''
    bl_idname = "sound.play"
    bl_label = "Play sound"
    
    item_play = bpy.props.StringProperty(name="item", default='[False, 0]')
    
    @classmethod
    def poll(cls, context):
        try:
            if context.window_manager.mp_playsound.status or not context.scene.mp_playlist.__len__():
                return 0
            else:
                return 1
        except:
            if context.scene.mp_playlist.__len__():
                return 1
            else:
                return 0

    def execute(self, context):
        check = eval(self.item_play)
        if check[0]:
            bpy.context.window_manager.mp_index = check[1]
            check[0] = False
        bpy.types.WindowManager.mp_f = aud.Factory(context.scene.mp_playlist[context.window_manager.mp_index].playlist)
        bpy.types.WindowManager.mp_playsound = context.window_manager.mp_d.play(context.window_manager.mp_f.fadein(0,3))
        context.window_manager.mp_pause=False
        context.window_manager.mp_playsound.volume=context.scene.mp_volume
        threading.Thread(target=soundIsOn, args=(context,)).start()
        self.report({'INFO'}, 'Lets rock...')
        context.window_manager.mp_playing = True
        
        if bpy.context.scene.mp_playlist_names.__len__():
            pl = [a.playlist for a in bpy.context.scene.mp_playlist_names]
        else:
            pl = [a.playlist for a in bpy.context.scene.mp_playlist]
        print ("||| %s of %s ||| %s" % (str(context.window_manager.mp_index+1), str(len(context.scene.mp_playlist)), str(pl[context.window_manager.mp_index])))
        return {'FINISHED'}
    
    #could be used for shuffle button or some button to show operators dinamically
    #def invoke(self, context, event):
        #wm = context.window_manager
        #wm.invoke_props_dialog(self, 250)
        #return {'RUNNING_MODAL'}

class MP_ImportSIC(bpy.types.Operator):
    '''Load a sound File'''
    bl_idname = "sound.import"
    bl_label = "Import sound"

    filename_ext = ".mp3"
    filter_glob = StringProperty(default="*.mp3;*.ogg;*.wav;*.avi;*.mp4;*.wma", options={'HIDDEN'})
    filepath = StringProperty(subtype="FILE_PATH")
    filename = StringProperty()
    files = CollectionProperty(name="File Path",type=bpy.types.OperatorFileListElement)
    directory = StringProperty(subtype='DIR_PATH')

    
    def execute(self, context):
        print(self.filename)
        if self.files :
            for sfile in self.files:
                context.scene.mp_playlist.add()
                context.scene.mp_playlist[-1].playlist = os.path.join(self.directory + sfile.name)
                context.scene.mp_playlist_names.add()
                context.scene.mp_playlist_names[-1].playlist = sfile.name
            playlistprint()
        else:
            context.scene.mp_playlist.add()
            context.scene.mp_playlist[-1].playlist = self.filepath
        self.report({'INFO'}, 'Do it again...')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MP_ImportM3U(bpy.types.Operator, ImportHelper):
    '''Load a M3U File'''
    bl_idname = "sound.import_m3u"
    bl_label = "Import m3u"
    
    filename_ext = ".m3u"
    filter_glob = StringProperty(default="*.m3u;*.M3U", options={'HIDDEN'})
    
    def execute(self, context):
        f = open(self.filepath)
        for l in f :
            if not l[0]=='#':
                context.scene.mp_playlist.add()
                context.scene.mp_playlist[-1].playlist = l[0:-1]
        f.close()
        del f
        playlistprint()
        return {'FINISHED'}

class MP_StopSIC(bpy.types.Operator):
    '''stop sound load'''
    bl_idname = "sound.stop"
    bl_label = "stop sound"

    cicle_off = BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        try:
            return (context.window_manager.mp_playsound.status)
        except:
            return 0

    def execute(self, context):
        context.window_manager.mp_playsound.stop()
        context.window_manager.mp_index = context.scene.mp_playlist.__len__()
        self.report({'INFO'}, 'Break...')
        context.window_manager.mp_playing = False
        
        if self.cicle_off:
            context.window_manager.mp_cycled = False
            self.cicle_off = False
        return {'FINISHED'}

class MP_DelList(bpy.types.Operator):
    '''Delet play list'''
    bl_idname = "sound.delplaylist"
    bl_label = "Del play list"

    @classmethod
    def poll(cls, context):
        return (context.scene.mp_playlist.__len__())

    def execute(self, context):
        context.scene.mp_playlist.clear()
        context.scene.mp_playlist_names.clear()
        self.report({'INFO'}, 'Fresh...')
        
        return {'FINISHED'}

class MP_NextSIC(bpy.types.Operator):
    '''Next sound'''
    bl_idname = "sound.next"
    bl_label = "next sound"

    @classmethod
    def poll(cls, context):
        try:
            return (context.window_manager.mp_playsound.status and \
                context.window_manager.mp_index+1 < context.scene.mp_playlist.__len__())
        except:
            return 0

    def execute(self, context):
        global phrase
        context.window_manager.mp_index+=0.5
        # sorry for 0.5 but i don't understand why it jump on x2 item FF...
        context.window_manager.mp_playsound.stop()
        self.report({'INFO'}, str(random.choice(phrase)))
        return {'FINISHED'}

class MP_PrevSIC(bpy.types.Operator):
    '''Previus sound load'''
    bl_idname = "sound.prev"
    bl_label = "previus sound"

    @classmethod
    def poll(cls, context):
        if context.scene.mp_playlist.__len__():
            return (context.window_manager.mp_index)
        else:
            return 0

    def execute(self, context):
        global phrase
        context.window_manager.mp_index-=2
        context.window_manager.mp_playsound.stop()
        self.report({'INFO'}, str(random.choice(phrase)))
        return {'FINISHED'}

class MP_PauseSIC(bpy.types.Operator):
    '''pause sound load'''
    bl_idname = "sound.pause"
    bl_label = "pause sound"

    @classmethod
    def poll(cls, context):
        try:
            return (context.window_manager.mp_playsound.status)
        except:
            return 0

    def execute(self, context):
        
        context.window_manager.mp_playsound.pause()
        context.window_manager.mp_pause=True
        self.report({'INFO'}, 'Wait...')
        return {'FINISHED'}       
 
class MP_ResumeSIC(bpy.types.Operator):
    '''resume sound load'''
    bl_idname = "sound.resume"
    bl_label = "resume sound"

    def execute(self, context):
        
        context.window_manager.mp_playsound.resume()
        context.window_manager.mp_pause=False
        self.report({'INFO'}, 'Again...')
        return {'FINISHED'} 
    
class MP_SetPosSIC(bpy.types.Operator):
    '''set position of song in seconds'''
    bl_idname = "sound.setpos"
    bl_label = "set position"

    @classmethod
    def poll(cls, context):
        try:
            return (context.window_manager.mp_playsound.status)
        except:
            return 0

    def execute(self, context):
        context.window_manager.mp_playsound.position = context.window_manager.mp_MusHandle
        return {'FINISHED'} 

# not working
class MP_PrintPlaylist(bpy.types.Operator):
    '''Print playlist'''
    bl_idname = "sound.printplaylist"
    bl_label = "print playlist"

    def execute(self, context):
        pl = [a.playlist for a in context.scene.mp_playlist]
        print ('Playlist: \n')
        for i, p in enumerate(pl):
            print (str(i+1)+ '.', p)
        return {'FINISHED'} 


class VIEW3D_PT_Musicplayer(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Music Player"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'SV'
    
    def draw(self, context):
        layout = self.layout
        col_over = layout.column()
        row = col_over.row(align=True)
        
        ############# left column
        col2 = row.column(align=True)
        col2.scale_x=0.12
        col2.scale_y=1.35
        #col2.operator("sound.openplaylist", text="Open playlist", icon='ZOOMIN')
        col2.operator("sound.import", text=' ', icon='FILE_SOUND')
        col2.operator("sound.prev", text=" ", icon='REW')
        if context.window_manager.mp_pause:
            col2.operator("sound.resume", text=" ", icon='PLAY')
        else:
            col2.operator("sound.pause", text=" ", icon='PAUSE')
        col2.prop(bpy.context.window_manager, 'mp_cycled', text='', icon='RECOVER_LAST')
        
        ############# central column
        col = row.column(align=False)
        row_butt = col.row()
        row_butt.scale_y=2.5
        if not context.window_manager.mp_playing:
            row_butt.operator("sound.play", text="PLAY ", icon='PLAY')
        else:
            sto = row_butt.operator("sound.stop", text="STOP ", icon='FULLSCREEN')
            sto.cicle_off = True
        if bpy.context.scene.mp_playlist_names.__len__():
            
            # line - item and time
            plaingindex = 'Song: '+str(context.window_manager.mp_index+1)+'/'+str(len(context.scene.mp_playlist))
            row2 = col.row(align=False)
            row2.scale_y=0.75
            row2.label(text=plaingindex)
            columna=row2.column()
            if context.window_manager.mp_playing:
                posa = str(round(context.window_manager.mp_playsound.position))
            else:
                posa = 0
            columna.label(text = str(posa)+' s')
            
            # line - name of song
            row_pos = col.row(align=False)
            row_pos.scale_y=0.75
            if hasattr(bpy.types.WindowManager, 'mp_playsound'):
                if hasattr(context.window_manager.mp_playsound, 'position') and \
                        context.window_manager.mp_index < \
                        context.scene.mp_playlist_names.__len__():
                    row_pos.label(text=bpy.context.scene.mp_playlist_names[ \
                            context.window_manager.mp_index].playlist)
        else:
            row_nomus = col.row(align=False)
            row_nomus.scale_y=1.5
            row_nomus.label(text='Load music, please')
        row_vol = col.row(align=False)
        row_vol.scale_y=1
        row_vol.prop(context.scene, "mp_volume", slider=True)
        
        ############# right column
        col3 = row.column(align=True)
        col3.scale_x=0.12
        col3.scale_y=1.35
        #col2.operator("sound.import_m3u", text="Import m3u", icon='ZOOMIN')
        #col2.operator("sound.writeplaylist", text="Save playlist", icon='ZOOMIN')
        col3.operator("sound.delplaylist", text=" ", icon='X')
        col3.operator("sound.next", text=" ", icon='FF')
        if bpy.context.window_manager.mp_show_names:
            ico = 'FILE'
        else:
            ico = 'TEXT'#'RESTRICT_VIEW_ON'
        col3.prop(bpy.context.window_manager, 'mp_show_names',icon=ico, icon_only=True)
        col3.operator('sound.shuffle', text='', icon='RNDCURVE')
        
        
        #col.operator("sound.printplaylist", text="Print playlist", icon='TEXT')
        row = col_over.row(align=True)
        row.prop(context.window_manager, 'mp_MusHandle', slider=True, text='Second')
        row.operator('sound.setpos', text='Set Position')
        #row = layout.row(align=False)

        if bpy.context.scene.mp_playlist_names.__len__():
            playlist_print = [a.playlist for a in context.scene.mp_playlist_names]
            if bpy.context.window_manager.mp_show_names:
                col = layout.column(align=True)
                i=0
                for p in playlist_print:
                    i+=1
                    row = col.row(align=True)
                    if i == (context.window_manager.mp_index+1):
                        row.operator("sound.play", text='> '+str(i)+' | '+str(p)).item_play=str([True, i-1])
                    else:
                        row.operator("sound.play", text='    '+str(i)+' | '+str(p)).item_play=str([True, i-1])
                    delco = row.operator('sound.delcompos', text='', icon='X')
                    delco.item_delete = i-1
            #a = context.window_manager
            #a.progress_begin(0,1)
            #a.progress_update(0.5)
            #a.progress_end()


# define classes for registration
classes = [MP_PlaySIC,
            MP_SetPosSIC,
            MP_ImportSIC,
            MP_ImportM3U,
            MP_StopSIC,
            MP_DelList,
            MP_NextSIC,
            MP_PrevSIC,
            MP_PauseSIC,
            MP_ResumeSIC,
            VIEW3D_PT_Musicplayer,
            MP_PrintPlaylist,
            MP_openPL,
            MP_writePL,
            MP_Playlist,
            MP_DelComposition,
            MP_Shuffle]


# registering 
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.mp_index=bpy.props.IntProperty()
    bpy.types.WindowManager.mp_cycled = bpy.props.BoolProperty( \
        description='start first if last is played',default=False)
    bpy.types.WindowManager.mp_pause = bpy.props.BoolProperty(False)
    bpy.types.WindowManager.mp_playing = bpy.props.BoolProperty(False)
    bpy.types.Scene.mp_volume = bpy.props.FloatProperty(name="Volume",default=1.0, min=0.0, max=1.0, update=volume_up)
    bpy.types.WindowManager.mp_d = aud.device()
    bpy.types.WindowManager.mp_MusHandle = bpy.props.FloatProperty(name="MusHandle",default=0.0, min=0.0, max=600)
    bpy.types.Scene.mp_playlist = bpy.props.CollectionProperty(type=MP_Playlist)
    bpy.types.Scene.mp_playlist_names = bpy.props.CollectionProperty(type=MP_Playlist)


# unregistering 
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        del bpy.types.WindowManager.mp_index
        del bpy.types.Scene.mp_playlist
        del bpy.types.Scene.mp_playlist_names
        del bpy.types.WindowManager.mp_pause
        del bpy.types.Scene.mp_volume
        del bpy.types.WindowManager.mp_d
    except:
        pass
    try:
        del bpy.types.WindowManager.mp_f
        del bpy.types.WindowManager.mp_playsound
        del bpy.types.WindowManager.mp_show_names
        del bpy.types.WindowManager.mp_MusHandle
    except:
        pass

if __name__ == "__main__": 
    #unregister()
    register()
    

















