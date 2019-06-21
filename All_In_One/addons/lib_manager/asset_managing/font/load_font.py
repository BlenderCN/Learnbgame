import bpy

def load_font(self,ThumbnailList,item_info,link=True):
    font = bpy.data.fonts.load(item_info['path'],True)
