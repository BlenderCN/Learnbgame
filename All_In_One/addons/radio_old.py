bl_info = {
    "name": "Radio Player",
    "author": "nikitron.cc.ua",
    "version": (1, 0, 0),
    "blender": (2, 7, 9),
    "location": "View3D > Tool Shelf > Radio Player",
    "description": "A Little Radio Player for Blender",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import os
import threading
import bpy
import time

class RP_Playlist(bpy.types.PropertyGroup):
    url = bpy.props.StringProperty()
    name = bpy.props.StringProperty()

class Radio(threading.Thread):
    """
    Радио игра
    """
    
    def __init__(self, url, name):
        """Инициализация радио"""
        threading.Thread.__init__(self)
        self.name = name
        self.url = url
    
    def run(self):
        """Запуск"""
        os.system("mplayer %s" % self.url)
        print('radio %s play' % self.name) 

class RP_Play(bpy.types.Operator):
    '''Play a radio'''
    bl_idname = "sound.radioplay"
    bl_label = "Play radio"
    
    url = bpy.props.StringProperty(name="url", default='')
    name = bpy.props.StringProperty(name="name", default='')
    
    @classmethod
    def poll(cls, context):
        try:
            if context.scene.rp_playlist.__len__():
                return 1
            else:
                return 0

    def play(self,url,name):
        """
        Запускаем программу
        """
        if context.window_manager.rp_playing == False:
            context.window_manager.rp_thread.stop()
        bpy.types.WindowManager.rp_thread = Radio(url,name)
        context.window_manager.rp_thread.start()
        context.window_manager.rp_playing = True

    def execute(self, context):
        self.play(self.url,self.name)
        
        self.report({'INFO'}, 'Lets rock...')
        context.window_manager.rp_playing = True
        
        return {'FINISHED'}


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
names = [ '1  Вести',  '2 Амстердам транс',
            '3 Романтика','4 Рекорд электроника', 
            '5 90-е гг','6 Электроскай', 
            '7 1фм лаунж','8 Атмосфера ланж', 
            '9 Сумерьки','10 ЛанжФМ', 
            '11 Ваня','12 Русское Радио', 
            '13 Дача','14 Юмор фм', 
            '15 Транс','16 Маяк', 
            '17 Наше радио','18 Электроника', 
            '19 Энергия','20 Хип Хоп', 
            '21 Классика','22 Шакалад', 
            '23 Классика','24 ДНБ', 
            '25 Кантри','26 Жаз', 
            '27 80-е гг','28 Дабстеп', 
            '29 Прогрессивное','custom link...',
    ]


def dolist(self, urls,names):
    dic={}
    for u,n in zip(urls,names):
        dic[n] = u
        context.scene.rp_playlist.add()
        context.scene.rp_playlist[-1].url = u
        context.scene.rp_playlist[-1].name = n
    print(dic)

class PN_radio(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Radio Player"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'SV'

    def draw(self, context):
        layout = self.layout
        col_over = layout.column()
        row = col_over.row(align=True)

        for i in context.scene.rp_playlist:
            col2 = row.column(align=True)
            col2.scale_x=0.12
            col2.scale_y=1.35
            item = col2.operator("sound.radioplay", text=' ', icon='FILE_SOUND')
            item.url = i.url
            item.name = i.name

def register():
    bpy.types.Scene.rp_playlist = bpy.props.CollectionProperty(type=RP_Playlist)
    dolist(urls,names)
    bpy.types.WindowManager.rp_playing = bpy.props.BoolProperty(name='playing',default=False)
    bpy.utils.register_class(PN_radio)
    bpy.utils.register_class(RP_Play)

if __name__ == "__main__":
    register()
    #threading.Thread(target=radio(url),args=(bpy.context)).start()
    #main(urls[1],names[1])