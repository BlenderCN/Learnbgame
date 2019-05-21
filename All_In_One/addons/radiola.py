bl_info = {
    "name": "Radiola",
    "author": "nikitron.cc.ua",
    "version": (0, 0, 1),
    "blender": (2, 7, 9),
    "location": "View3D > Tool Shelf > SV > Radiola",
    "description": "Play the radio",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import os
import signal
#import threading
import bpy
import time
import subprocess as sp

class OP_radiola(bpy.types.Operator):
    '''Radiola'''
    bl_idname = "sound.radiola"
    bl_label = "play radio"

    make = bpy.props.BoolProperty(name='make',default=False)
    clear = bpy.props.BoolProperty(name='clear',default=False)
    play = bpy.props.BoolProperty(name='play',default=True)
    item_play = bpy.props.IntProperty(name='composition',default=0)

    def execute(self, context):

        if self.clear:
            context.scene.rp_playlist.clear()
            context.window_manager.radiola_clear = True
            self.clear = False
            return {'FINISHED'} 
        if self.make:
            self.dolist(urls,names)
            context.window_manager.radiola_clear = False
            self.make = False
            return {'FINISHED'} 

        if not len(context.scene.rp_playlist):
            self.dolist(urls,names)
        url = context.scene.rp_playlist[self.item_play].url

        if self.play:
            music = sp.Popen(['/usr/bin/mplayer', url])
            context.window_manager.radiola_ind = self.item_play
            context.window_manager.radiola = music.pid
        else:
            os.kill(context.window_manager.radiola, signal.SIGTERM)
            #music.terminate()
        return {'FINISHED'} 

    def dolist(self,urls,names):
        for u,n in zip(urls,names):
            bpy.context.scene.rp_playlist.add()
            bpy.context.scene.rp_playlist[-1].url = u
            bpy.context.scene.rp_playlist[-1].name = n


class OP_radiola_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Radiola"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'SV'

    def draw(self, context):
        ''' \
        Radiola \
        '''
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1
        if context.window_manager.radiola_clear:
            col.operator('sound.radiola',text='Make').make = True
        else:
            col.operator('sound.radiola',text='Clear').clear = True
        col = layout.column(align=True)
        col.scale_y = 3
        b = col.operator('sound.radiola',text='Stop')
        b.play=False
        playlist_print = [a.name for a in context.scene.rp_playlist]
        i=0
        col = layout.column(align=True)
        col.scale_y = 1
        for p in playlist_print:
            i+=1
            if i == (context.window_manager.radiola_ind+1):
                a = col.operator('sound.radiola', text='> '+str(i)+' | '+str(p))
                a.item_play=i-1
                a.play=True
            else:
                a = col.operator("sound.radiola", text='    '+str(i)+' | '+str(p))
                a.item_play=i-1
                a.play=True

class RP_Playlist(bpy.types.PropertyGroup):
    url = bpy.props.StringProperty()
    name = bpy.props.StringProperty()

urls = [    'http://icecast.vgtrk.cdnvideo.ru/vestifm_mp3_192kbps',
            'http://strm112.1.fm/atr_mobile_mp3',
            'http://ic2.101.ru:8000/v4_1',
            'http://online.radiorecord.ru:8101/rr_320',
            'http://air.radiorecord.ru:8102/sd90_320',
            'http://46.105.180.202:8040/sr_128',
            'http://strm112.1.fm/chilloutlounge_mobile_mp3',
            'http://185.53.169.128:8000/192',
            'http://sumerki.su:8000/Sumerki',
            'http://myradio.ua:8000/loungefm128.mp3',
            'http://icecast.piktv.cdnvideo.ru/vanya',  #:8108/shanson128.mp3
            'http://icecast.rmg.cdnvideo.ru/rr.mp3',  #:8000/russianradio128.mp3
            'http://81.30.54.74:8000/radio4',
            'http://ic2.101.ru:8000/v5_1',
            'http://radio.globaltranceinvasion.com:8000/radiohi',
            'http://icecast.vgtrk.cdnvideo.ru/mayakfm_mp3_192kbps',
            'http://nashe1.hostingradio.ru/nashe-128.mp3',
            'http://icecast.radiodfm.cdnvideo.ru/dfm.mp3',
            'http://ic2.101.ru:8000/v1_1',
            'http://listen1.myradio24.com:9000/4455',
            'http://174.36.206.197:8000/;stream.nsv',
            'http://choco.hostingradio.ru:10010/fm', #http://pianosolo.streamguys.net:80/live
            'http://sc1c-sjc.1.fm:7070/?type=.flv',
            'http://source.dnbradio.com:10128/128k.mp3',
            'http://sc3b-sjc.1.fm:7802/?type=.flv',
            'http://quarrel.str3am.com:7990/;stream.nsv&type=mp3',
            'http://s7.radioheart.ru:8003/live',
            'http://stream.dubstep.fm/stream/1/',
            'http://176.104.22.115:8000/192.mp3',
    ]
names = [   'Вести',       'Амстердам транс',
            'Романтика',   'Рекорд электроника', 
            '90-е гг',     'Электроскай', 
            '1фм лаунж',   'Атмосфера ланж', 
            'Сумерьки',    'ЛанжФМ', 
            'Ваня',        'Русское Радио', 
            'Дача',        'Юмор фм', 
            'Транс',       'Маяк', 
            'Наше радио',  'Электроника', 
            'Энергия',     'Хип Хоп', 
            'Классика',    'Шакалад', 
            'Классика',    'ДНБ', 
            'Кантри',      'Жаз', 
            '80-е гг',     'Дабстеп', 
            'Прогрессивное','custom link...',
    ]

def dolist(urls,names):
    dic={}
    for u,n in zip(urls,names):
        #dic[n] = u
        bpy.context.scene.rp_playlist.add()
        bpy.context.scene.rp_playlist[-1].url = u
        bpy.context.scene.rp_playlist[-1].name = n
    #print(dic)

def register():
    try:
        if 'rp_playlist' in bpy.context.scene:
            bpy.context.scene.rp_playlist.clear()
    except:
        pass
    bpy.utils.register_class(RP_Playlist)
    bpy.types.Scene.rp_playlist = bpy.props.CollectionProperty(type=RP_Playlist)
    bpy.types.WindowManager.radiola_clear=bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.radiola=bpy.props.IntProperty()
    bpy.types.WindowManager.radiola_ind=bpy.props.IntProperty()
    bpy.utils.register_class(OP_radiola)
    bpy.utils.register_class(OP_radiola_panel)

def unregister():
    bpy.utils.unregister_class(OP_radiola_panel)
    bpy.utils.unregister_class(OP_radiola)
    del bpy.types.WindowManager.radiola_ind
    del bpy.types.WindowManager.radiola
    del bpy.types.WindowManager.radiola_clear
    del bpy.types.Scene.rp_playlist


if __name__ == '__main__':
    register()