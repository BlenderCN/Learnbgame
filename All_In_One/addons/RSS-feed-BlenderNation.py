# nikitron.cc.ua ordered for this. Much thanks to Nikolay Fomichev https://vk.com/pythal
bl_info = {
    "name": "RSS",
    "version": (0, 2, 0),
    "blender": (2, 8, 0), 
    "category": "Learnbgame",
    "author": "Nikolay Fomichev",
    "location": "World",
    "description": "makes RSS appears in world properties",
    "warning": "",
    "wiki_url": "",          
    "tracker_url": "",  
}

import bpy
import urllib.error as err
import urllib.request as req
from xml.etree import ElementTree as ET
import re
import pprint

bpy.types.WindowManager.RSSadress = bpy.props.StringProperty(name='', default='http://feeds.feedburner.com/BlenderNation')

def getRss(adress):
    try:
        page = req.urlopen(adress).read().decode('utf8')
    except err.URLError:
        page = None
       
    tree = ET.XML(page) if page else None
    
    return tree    

class RssPanel(bpy.types.Panel):
    ''' Read feed '''
    bl_label = "RSS"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'world'
    bl_options = {'DEFAULT_CLOSED'}
    
    
    #adress = bpy.context.window_manager.RSSadress[1]['default']
    tree = getRss(bpy.context.window_manager.RSSadress)
    def init(self, context):
        pass
        
    def draw(self, context):
        width1=100
        for i in context.screen.areas:
            if i.type == 'PROPERTIES':
                width1 = (i.width-70)//4.5
        layout = self.layout
        row = layout.row()
        row.scale_y=2
        row.prop(context.window_manager, "RSSadress")
        row.operator('world.reloadrss', text='Reload')
        def RSS_read():
            for el in self.tree.getchildren():
                for i in el.findall('item'):
                    box = layout.box()
                    title = i.find('title')
                    link = i.find('link')
                    description = i.find('description')
                    dtext___ = re.split('<img', description.text)[:-1]
                    dtext__ = re.split('<p>',str(dtext___))[1]
                    dtext_ = re.split('</p>',dtext__)[0]
                    col = box.column()
                    col.scale_y=1.5
                    col.operator('wm.url_open', text=title.text).url = link.text
                    dtext = pprint.pformat(dtext_, width=width1)
                    col = box.column()
                    col.scale_y=0.6
                    for a in dtext.splitlines():
                        col.label(a[1:-1])
        if self.tree:
            if bpy.context.window_manager.RSSadress == \
                    'http://feeds.feedburner.com/BlenderNation':
                RSS_read()
        else:
            layout.label('No connection to Internet!')

          
class reloadRSS(bpy.types.Operator):
    bl_label = "Reload operator"
    bl_idname = "world.reloadrss"
    bl_description = "Reload"
 
    def invoke(self, context, event):
        bpy.types.RssPanel.tree = getRss(context.window_manager.RSSadress)      
        return{"FINISHED"}
              
# registering and menu integration
def register():
    bpy.utils.register_class(RssPanel)
    bpy.utils.register_class(reloadRSS)
 
# unregistering and removing menus
def unregister():
    bpy.utils.unregister_class(RssPanel)
    bpy.utils.unregister_class(reloadRSS)
 
if __name__ == "__main__":
    register()

