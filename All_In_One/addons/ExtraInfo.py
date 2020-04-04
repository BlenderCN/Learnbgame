import bgl
import blf
import bpy

'''

    Copyright (c) 2019

    Jorge Hernández - Meléndez Saiz
    zebus3dream@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.


'''

bl_info = {
    "name": "ExtraInfo",
    "description": "Show Extra Information in Viewport",
    "author": "zebus3d",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "wiki_url": "",
    "category": "Learnbgame",
}


font_info = {
    "font_id": 0,
    "handler": None,
}



def draw_callback_px(self, context):
    # esto se calcula cada pasada de dibujado del viewport:

    display = []

    font_id = font_info["font_id"]
    
    x = 19
    toolbarWidth = bpy.context.area.regions[1].width

    offsetTextInTop = 86
    yOffset = bpy.context.area.height - offsetTextInTop

    fontSize = 11
    blf.size(font_id, fontSize, 72)
    
    # sombra:
    # el level tiene que ser 3, 5 o 0
    level = 5
    r = 0.0
    g = 0.0
    b = 0.0
    a = 0.9
    
    blf.enable(font_id , blf.SHADOW )
    blf.shadow(font_id, level, r, g, b, a)
    blf.shadow_offset(font_id, 1, -1)
    
    engines = {
        'BLENDER_EEVEE' : 'Eevee',
        'BLENDER_WORKBENCH' : 'Workbench',
        'CYCLES' : 'Cycles'
    }

    re = 'Engine: ' + engines.get(bpy.context.scene.render.engine)
    display.append(re)

    view_layer = bpy.context.view_layer
    stats = bpy.context.scene.statistics(view_layer).split("|")

    if bpy.context.mode == 'OBJECT':
        ss = stats[2:5]
        ss.append(stats[-2])
        stats = ss
    elif bpy.context.mode == 'EDIT_MESH':
        ss = stats[1:6]
        stats = ss
    elif bpy.context.mode == 'SCULPT':
        ss = stats[1:4]
        ss.append(stats[-2])
        stats = ss
    else:
        stats = []

    if len(stats) > 0:
        display = display + stats

    if engines.get(bpy.context.scene.render.engine) == 'Cycles':
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        if space.shading.type == 'RENDERED': 
            rendered = 20
        else:
            rendered = 0
    else:
        rendered = 0

    if bpy.context.space_data.overlay.show_overlays:
        if bpy.context.space_data.overlay.show_text:
            for counter, value in enumerate(display):
                # print(value)
                value = value.replace(" ","")
                value = value.replace(":",": ")
                # print(value)
                increment = (20*counter)
                blf.position(font_id, x+toolbarWidth, yOffset-increment-rendered, 0)
                blf.draw(font_id, value)



def init():
    font_info["font_id"] = 0
    # run every frame
    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')


def register():
    init()

def unregister():
    pass

if __name__ == "__main__":
    register()