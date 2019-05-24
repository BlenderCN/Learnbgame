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

#This is only a test release, expect bugs or other annoyances.

import bpy
import bgl
import blf
from bpy.props import StringProperty, BoolProperty
from math import hypot

bl_info = {
    "name": "Menu Pins",
    "author": "Morshidul Chowdhury (iPLEOMAX)",
    "version": (0, 1),
    "blender": (2, 70, 0),
    "location": "3D View > Display Panel > Show Menu Pins",
    "description": "Pin menus temporarily in 3d View for quick access",
    "wiki_url": "http://blenderartists.org/forum/showthread.php?339859-Addon-Test-Release-Menu-Pinning-for-quick-access",
    "category": "Learnbgame",
}

PinnedMenus = {}

def draw_button(mx, my, x0, y0, width, height):
    color_r = 0.0
    color_g = 0.0
    color_b = 0.0
    color_a = 0.5
    x1 = x0 + width
    y1 = y0 - height/2
    y0 += height/2

    hover = False
    if x0 <= mx <= x1 and y1 <= my <= y0:
        color_r = 0.0
        color_g = 0.5
        color_b = 1.0
        color_a = 0.8
        hover = True

    positions = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]
    settings = [[bgl.GL_QUADS, min(0.0, color_a)], [bgl.GL_LINE_LOOP, min(0.0, color_a)]]
    for mode, box_alpha in settings:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBegin(mode)
        bgl.glColor4f(color_r, color_g, color_b, color_a)
        for v1, v2 in positions:
            bgl.glVertex2f(v1, v2)
        bgl.glEnd()

    return hover

def draw_text(x, y, text):
    blf.position(0, x, y, 0)
    color_r = 1.0
    color_g = 1.0
    color_b = 1.0
    color_a = 1.0
    bgl.glColor4f(color_r, color_g, color_b, color_a)
    blf.draw(0, text)

def get_magnet_xy(x, y):
    menu = None
    dist = 10000.0
    for m in PinnedMenus:
        if PinnedMenus[m]['set']:
            curr = abs(hypot(PinnedMenus[m]['x'] - x, PinnedMenus[m]['y'] - y))
            if curr < 90 and curr < dist:
                dist = curr
                menu = m
    if menu:
        if curr > 50 and not (PinnedMenus[menu]['x'] - 35 < x < PinnedMenus[menu]['x'] + 35):
            y =  PinnedMenus[menu]['y']
            if x < PinnedMenus[menu]['x']:
                x = PinnedMenus[menu]['x'] - 124
            else:
                x = PinnedMenus[menu]['x'] + 124
        else:
            x = PinnedMenus[menu]['x']
            if y < PinnedMenus[menu]['y']:
                y = PinnedMenus[menu]['y'] - 25
            else:
                y = PinnedMenus[menu]['y'] + 25
    return [x, y]

def draw_pins(self, context):
    x = self.x
    y = self.y

    font_id = 0

    ignore_click = False
    self.callmenu = None
    for menu in list(PinnedMenus):
        if not PinnedMenus[menu]['set']:
            ignore_click = True
            mxy = get_magnet_xy(x, y)
            PinnedMenus[menu]['x'] = mxy[0]
            PinnedMenus[menu]['y'] = mxy[1]
            if self.RMB:# or self.LMB:
                PinnedMenus[menu]['set'] = True

        hover = draw_button(x, y, PinnedMenus[menu]['x'] - 60, PinnedMenus[menu]['y'], 120, 22)
        blf.size(font_id, 12, 72)
        draw_text(PinnedMenus[menu]['x'] - 54, PinnedMenus[menu]['y'] - 4, PinnedMenus[menu]['name'])
        if not PinnedMenus[menu]['set']:
            blf.size(font_id, 10, 72)
            draw_text(PinnedMenus[menu]['x'] + 28, PinnedMenus[menu]['y'] - 3, '(move)')

        if hover and not ignore_click:
            if self.RMB:
                PinnedMenus[menu]['set'] = False
            else:
                self.callmenu = menu
            #blf.position(0, 20, 20, 0)
            #blf.draw(0, menu)

class PinsModal(bpy.types.Operator):
    bl_idname = "pins.toggle"
    bl_label = "Toggle menu pins"
    bl_description = "Show/hide menu pins"

    _handle = None

    @staticmethod
    def handle_add(self, context):
        self.callmenu = None
        self.called = False
        self.LMB = False
        self.RMB = False
        args = (self, context)
        PinsModal._handle = bpy.types.SpaceView3D.draw_handler_add(draw_pins, args, 'WINDOW', 'POST_PIXEL')

    @staticmethod
    def handle_remove(context):
        if PinsModal._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(PinsModal._handle, 'WINDOW')
        PinsModal._handle = None

    def modal(self, context, event):
        context.area.tag_redraw()

        self.LMB = False
        self.RMB = False

        if event.type == 'MOUSEMOVE':
            self.x = event.mouse_region_x
            self.y = event.mouse_region_y
        elif event.type == 'LEFTMOUSE':
            self.LMB = True
            for p in PinnedMenus:
                if not PinnedMenus[p]['set']:
                    return {'RUNNING_MODAL'}
            if self.callmenu:
                bpy.ops.wm.call_menu(name=self.callmenu)
                self.callmenu = None
                return {'RUNNING_MODAL'}
        elif event.type == 'RIGHTMOUSE':
            self.RMB = True
            for p in PinnedMenus:
                if not PinnedMenus[p]['set']:
                    return {'RUNNING_MODAL'}

        if not context.window_manager.pins:
            PinsModal.handle_remove(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.window_manager.pins is False:
                context.window_manager.pins = True
                PinsModal.handle_add(self, context)
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                context.window_manager.pins = False
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "3D View not found, can't run Screencast Keys")
            return {'CANCELLED'}

class PinOperator(bpy.types.Operator):

    bl_idname = "pins.menu"
    bl_label = "Pin this menu"
    bl_description = "Pin this menu here to access it easily"

    menu_id = StringProperty('menu_id')

    def execute(self, context):
        if context.window_manager.pins is False:
            self.report({'WARNING'}, "Enable pins from display options")
            return {'CANCELLED'}
        else:
            menu = self.menu_id
            if not menu in PinnedMenus:
                pindata = {}
                pindata['name'] = getattr(bpy.types, menu).bl_label
                pindata['set'] = False
                pindata['x'] = 0
                pindata['y'] = 0
                pindata['shown'] = False
                PinnedMenus[menu] = pindata
            else:
                del(PinnedMenus[menu])
        return {'FINISHED'}

def pinLayout(self, context):
    self.layout.separator()
    if self.bl_idname in PinnedMenus:
        self.layout.operator(PinOperator.bl_idname, text='Unpin', icon='PINNED').menu_id = self.bl_idname
    else:
        self.layout.operator(PinOperator.bl_idname, text='Pin', icon='UNPINNED').menu_id = self.bl_idname
    #self.layout.separator()

def inject():
    bpy.types.VIEW3D_PT_view3d_display.append(layout)
    bpy.types.WindowManager.pins = BoolProperty(default=False)
    for type in dir(bpy.types):
        if 'INFO_MT' in type or 'VIEW3D_MT' in type:
        #if 'MT' in type:
            attr = getattr(bpy.types, type)
            if hasattr(attr, 'draw'):
                attr.append(pinLayout)

def eject():
    bpy.types.VIEW3D_PT_view3d_display.remove(layout)
    wm = bpy.context.window_manager
    if 'pins' in wm:
        del wm['pins']

    for type in dir(bpy.types):
        if 'INFO_MT' in type or 'VIEW3D_MT' in type:
        #if 'MT' in type:
            attr = getattr(bpy.types, type)
            if hasattr(attr, 'draw'):
                attr.remove(pinLayout)

def layout(self, context):
    if context.window_manager.pins:
        self.layout.operator(PinsModal.bl_idname, 'Hide Menu Pins', icon='X')
    else:
        self.layout.operator(PinsModal.bl_idname, 'Show Menu Pins', icon='MENU_PANEL')

def register():
    bpy.utils.register_module(__name__)
    inject()

def unregister():
    bpy.utils.unregister_module(__name__)
    eject()

if __name__ == "__main__":
    register()
