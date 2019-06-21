#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "View Straighten",
    "description": "'View Straighten' operator eases view to nearest angle.",
    "author": "Jean Ayer (vrav)", # legal / tracker name: Cody Burrow
    "version": (0, 2, 2),
    "blender": (2, 80, 0),
    "location": "User Preferences > Keymap > add view3d.view_straighten",
    "category": "3D View"
}

# space_view3d_viewstraighten.py

# Activate operator and it eases into the nearest view in 90 degree increments.
# Activating the operator a second time toggles perspective, optionally.
# The length of the view transition is configurable, and can be instant.
# Holding down the operator key allows mouse movement to smoothly
#  shift the view to adjancent sides. Configurable distance.

# Known bugs:
# 2.80 beta complains about the addon's class properties needing annotation.
#   Not sure what to do about that, since using a colon removes them from keymap

from enum import Enum
from mathutils import Quaternion
import bpy
import blf

class state(Enum):
    KeyStart = 0
    Released = 1
    Held = 2
    Snapping = 3
    Head = 4

def draw_callback_px(self, context):
    col = self.textcolor
    font_id = 0
    
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 0, 0.0, 0.0, 0.0, 1.0)
    blf.position(font_id, 64, 24, 0)
    blf.size(font_id, 11, 72)
    
    blf.draw(font_id, self.nearname)
    
    blf.disable(font_id, blf.SHADOW)

class VIEW3D_OT_view_straighten(bpy.types.Operator):
    bl_idname = "view3d.view_straighten"
    bl_label  = "View Straighten"
    # bl_options = {'GRAB_POINTER'}
    
    _timer = None
    
    secondcall = bpy.props.EnumProperty(
        name = "Second Call",
        description = "Calling again can toggle ortho/perspective",
        items = [('IGNORE', 'No effect', ''),
                 ('TOGGLE', 'Toggle Perspective', '')],
        default = 'TOGGLE')
    
    hold = bpy.props.EnumProperty(
        name = "Key Hold",
        description = "Behaviour should the operator key be held",
        items = [('IGNORE', 'No effect', ''),
                 ('SMSNAP', 'Snapping Mode', 'Mouse causes view snapping')],
        default = 'SMSNAP')
    
    text = bpy.props.BoolProperty(
        name = "Show Text",
        description = "Briefly show name of view being moved to",
        default = False)
    
    duration = bpy.props.FloatProperty(
        name = "Time",
        description = "Max time in seconds to ease into view",
        subtype = 'TIME',
        default = 0.12,
        min = 0.0)
    
    movedist = bpy.props.IntProperty(
        name = "Mouse Move Distance",
        description = "Distance mouse must travel when key held to shift view",
        default = 24,
        min = 0)
    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D'
                and not context.scene.view_straighten_is_running)
    
    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        if hasattr(self, '_handle'):
            context.space_data.draw_handler_remove(self._handle, 'WINDOW')
        context.area.tag_redraw()
        context.scene.view_straighten_is_running = False
        return {'FINISHED'}
    
    def modal(self, context, event):
        view3d = context.space_data.region_3d
        self.now = self._timer.time_duration
        
        if event.type == self.hotkey and event.value == 'RELEASE':
            self.state = state.Released
            if self.persptoggle:
                view3d.view_perspective = 'PERSP' if not view3d.is_perspective else 'ORTHO'
                view3d.update()
        
        if self.state == state.Held or self.state == state.Head:
            # late key-held operations...
            # wait for key 'PRESS' pulse and and watch mouse move.
            # if mouse moves a certain distance, shift to neighbor view.
            if event.type in {'ESC', 'MIDDLEMOUSE'}:
                self.state = state.Released
                self.interrupt = True
            elif event.type == self.hotkey:
                # received press pulse
                
                if self.state == state.Held:
                    self.state = state.Snapping
                
                self.persptoggle = False # no persp toggling if key held!
                self.start = self.now
                self.startangle = view3d.view_rotation
                
                # 2.8 HACK: mouse_x and mouse_y bug out and get odd values
                # getting mouse_prev_x and mouse_prev_y seems more reliable
                mpos_cur = [event.mouse_prev_x, event.mouse_prev_y]
                xdiff = mpos_cur[0] - self.mpos_start[0]
                ydiff = mpos_cur[1] - self.mpos_start[1]
                
                # mpos_prev = [event.mouse_prev_x, event.mouse_prev_y]
                # mdelta = [mpos_cur[0] - mpos_prev[0], mpos_cur[1] - mpos_prev[1]]
                # print("start", self.mpos_start)
                # print("curre", mpos_cur)
                # print("x", xdiff, "y", ydiff)
                # print("delta", mdelta)
                # if abs(ydiff > self.movedist) or abs(xdiff > self.movedist):
                #     print("rotating!!!!!")
                
                # after puzzling for a while, for now I have
                #  opted to simply hardcode rotation changes
                if ydiff > self.movedist:
                    # mouse moving north, model showing relative bottom
                    self.state = state.Snapping
                    rotval = self.rotation if self.rotation & 1 else ((self.rotation + 2) % 4)
                    
                    if self.rotation == 0:
                        if self.nearname == 'Left':
                            self.rotation = 1
                        elif self.nearname == 'Right':
                            self.rotation = 3
                        elif self.nearname == 'Back':
                            self.rotation = 2
                        elif self.nearname == 'Bottom':
                            self.rotation = 2
                        elif self.nearname == 'Top':
                            pass
                    elif self.rotation == 1:
                        if self.nearname == 'Bottom':
                            self.rotation = 2
                        elif self.nearname == 'Top':
                            self.rotation = 0
                    elif self.rotation == 2:
                        if self.nearname == 'Left':
                            self.rotation = 1
                        elif self.nearname == 'Right':
                            self.rotation = 3
                        elif self.nearname == 'Back':
                            self.rotation = 0
                        elif self.nearname == 'Bottom':
                            pass
                        elif self.nearname == 'Top':
                            self.rotation = 0
                    elif self.rotation == 3:
                        if self.nearname == 'Bottom':
                            self.rotation = 2
                        elif self.nearname == 'Top':
                            self.rotation = 0
                    
                    self.nearname = self.neighbors[self.nearname][rotval]
                
                elif xdiff > self.movedist:
                    # mouse moving east, model showing relative left
                    self.state = state.Snapping
                    rotval = ((self.rotation + 3) % 4) if not self.rotation & 1 else ((self.rotation + 1) % 4)
                    
                    if self.rotation == 0:
                        if self.nearname == 'Bottom':
                            self.rotation = 3
                        elif self.nearname == 'Top':
                            self.rotation = 1
                    elif self.rotation == 1:
                        if self.nearname == 'Left':
                            self.rotation = 2
                        elif self.nearname == 'Right':
                            self.rotation = 0
                        elif self.nearname == 'Back':
                            self.rotation = 3
                        elif self.nearname == 'Bottom':
                            self.rotation = 3
                        elif self.nearname == 'Top':
                            pass
                    elif self.rotation == 2:
                        if self.nearname == 'Bottom':
                            self.rotation = 3
                        elif self.nearname == 'Top':
                            self.rotation = 1
                    elif self.rotation == 3:
                        if self.nearname == 'Left':
                            self.rotation = 2
                        elif self.nearname == 'Right':
                            self.rotation = 0
                        elif self.nearname == 'Back':
                            self.rotation = 1
                        elif self.nearname == 'Top':
                            self.rotation = 1
                        elif self.nearname == 'Bottom':
                            pass
                    
                    self.nearname = self.neighbors[self.nearname][rotval]
                
                elif ydiff < -self.movedist:
                    # mouse moving south, model showing relative top
                    self.state = state.Snapping
                    rotval = self.rotation if not self.rotation & 1 else ((self.rotation + 2) % 4)
                    
                    if self.rotation == 0:
                        if self.nearname == 'Left':
                            self.rotation = 3
                        elif self.nearname == 'Right':
                            self.rotation = 1
                        elif self.nearname == 'Back':
                            self.rotation = 2
                        elif self.nearname == 'Bottom':
                            pass
                        elif self.nearname == 'Top':
                            self.rotation = 2
                    elif self.rotation == 1:
                        if self.nearname == 'Bottom':
                            self.rotation = 0
                        elif self.nearname == 'Top':
                            self.rotation = 2
                    elif self.rotation == 2:
                        if self.nearname == 'Left':
                            self.rotation = 3
                        elif self.nearname == 'Right':
                            self.rotation = 1
                        elif self.nearname == 'Back':
                            self.rotation = 0
                        elif self.nearname == 'Bottom':
                            self.rotation = 0
                        elif self.nearname == 'Top':
                            pass
                    elif self.rotation == 3:
                        if self.nearname == 'Bottom':
                            self.rotation = 0
                        elif self.nearname == 'Top':
                            self.rotation = 2
                    
                    self.nearname = self.neighbors[self.nearname][rotval]
                
                elif xdiff < -self.movedist:
                    # mouse moving west, model showing relative right
                    self.state = state.Snapping
                    rotval = ((self.rotation + 3) % 4) if self.rotation & 1 else ((self.rotation + 1) % 4)
                    
                    if self.rotation == 0:
                        if self.nearname == 'Bottom':
                            self.rotation = 1
                        elif self.nearname == 'Top':
                            self.rotation = 3
                    elif self.rotation == 1:
                        if self.nearname == 'Left':
                            self.rotation = 0
                        elif self.nearname == 'Right':
                            self.rotation = 2
                        elif self.nearname == 'Back':
                            self.rotation = 3
                        elif self.nearname == 'Bottom':
                            pass
                        elif self.nearname == 'Top':
                            self.rotation = 3
                    elif self.rotation == 2:
                        if self.nearname == 'Bottom':
                            self.rotation = 1
                        elif self.nearname == 'Top':
                            self.rotation = 3
                    elif self.rotation == 3:
                        if self.nearname == 'Left':
                            self.rotation = 0
                        elif self.nearname == 'Right':
                            self.rotation = 2
                        elif self.nearname == 'Back':
                            self.rotation = 1
                        elif self.nearname == 'Top':
                            pass
                        elif self.nearname == 'Bottom':
                            self.rotation = 1
                    
                    self.nearname = self.neighbors[self.nearname][rotval]
                
                self.near = self.directions[self.nearname][self.rotation]
        
        if self.interrupt:
            return self.cancel(context)
        elif view3d.view_rotation.dot(self.near) > 0.99997:
            view3d.view_rotation = self.near
            view3d.update()
            if self.state != state.Released and self.hold != 'IGNORE':
                if self.state == state.Snapping:
                    self.mpos_start = [event.mouse_prev_x, event.mouse_prev_y]
                    # print("updated start")
                    self.state = state.Head
                elif self.state == state.KeyStart:
                    self.state = state.Held
            else:
                return self.cancel(context)
        elif event.type in {'ESC', 'MIDDLEMOUSE'}:
            # rather than cancel here, allow another PASS_THROUGH
            # this lets the middle mouse event grab the view, for some reason
            self.interrupt = True
        elif event.type == 'TIMER' and not self.interrupt:
            self.factor = (self.now - self.start) / self.duration if self.duration > 0.0 else 1.0
            self.factor = 1.0 if self.factor > 1.0 else self.factor
            view3d.view_rotation = self.startangle.slerp(self.near, self.factor)
            view3d.update()
        
        # when watching mouse, hit this a lot
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        context.scene.view_straighten_is_running = True
        
        # state 0 allows hold, 1 key released, 2 held, 3 snapping, 4 at head
        badkeys = {'NONE', 'LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE'}
        self.hotkey = event.type if event.type not in badkeys else ''
        self.state = state.KeyStart if self.hotkey != '' else state.Released
        self.interrupt = False
        self.persptoggle = False
        
        self.mpos_start = [event.mouse_x, event.mouse_y]
        # self.mpos_cur = self.mpos_start
        
        self.now = 0.0
        self.start = 0.0
        self.factor = 0.0
        self.near = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.nearname = ''
        
        self.directions = {
            "Front":(
                Quaternion(( 0.7071, 0.7071, 0.0000, 0.0000)),
                Quaternion(( 0.5000, 0.5000,-0.5000, 0.5000)),
                Quaternion(( 0.0000, 0.0000,-0.7071, 0.7071)),
                Quaternion((-0.5000,-0.5000,-0.5000, 0.5000))),
            "Right":(
                Quaternion(( 0.5000, 0.5000, 0.5000, 0.5000)),
                Quaternion(( 0.0000, 0.7071, 0.0000, 0.7071)),
                Quaternion((-0.5000, 0.5000,-0.5000, 0.5000)),
                Quaternion((-0.7071, 0.0000,-0.7071, 0.0000))),
            "Back":(
                Quaternion(( 0.0000, 0.0000, 0.7071, 0.7071)),
                Quaternion((-0.5000, 0.5000, 0.5000, 0.5000)),
                Quaternion((-0.7071, 0.7071, 0.0000, 0.0000)),
                Quaternion((-0.5000, 0.5000,-0.5000,-0.5000))),
            "Left":(
                Quaternion(( 0.5000, 0.5000,-0.5000,-0.5000)),
                Quaternion(( 0.7071, 0.0000,-0.7071, 0.0000)),
                Quaternion(( 0.5000,-0.5000,-0.5000, 0.5000)),
                Quaternion(( 0.0000,-0.7071, 0.0000, 0.7071))),
            "Top":(
                Quaternion(( 1.0000, 0.0000, 0.0000, 0.0000)),
                Quaternion(( 0.7071, 0.0000, 0.0000, 0.7071)),
                Quaternion(( 0.0000, 0.0000, 0.0000, 1.0000)),
                Quaternion((-0.7071, 0.0000, 0.0000, 0.7071))),
            "Bottom":(
                Quaternion(( 0.0000, 1.0000, 0.0000, 0.0000)),
                Quaternion(( 0.0000, 0.7071,-0.7071, 0.0000)),
                Quaternion(( 0.0000, 0.0000,-1.0000, 0.0000)),
                Quaternion(( 0.0000,-0.7071,-0.7071, 0.0000)))
        }
        
        view3d = context.space_data.region_3d
        self.startangle = view3d.view_rotation
        self.rotation = 0
        neardot = 0.0
        for side in self.directions:
            i = 0
            for angle in self.directions[side]:
                dot = abs(angle.dot(view3d.view_rotation))
                if dot > neardot:
                    neardot = dot
                    self.nearname = side
                    self.near = angle
                    self.rotation = i
                i = i + 1 if i < 3 else 0
        
        if neardot >= 0.99997 and self.secondcall == 'TOGGLE':
            if self.hold != 'IGNORE':
                self.persptoggle = True
                self.state = state.Held
            else:
                view3d.view_perspective = 'PERSP' if not view3d.is_perspective else 'ORTHO'
                view3d.update()
                context.scene.view_straighten_is_running = False
                return {'CANCELLED'}
        
        if self.text:
            current_theme = context.preferences.themes.items()[0][0]
            self.textcolor = context.preferences.themes[current_theme].view_3d.space.text_hi
            self._handle = context.space_data.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
        
        if self.hold != 'IGNORE':
            # neighbors are ordered NESW
            self.neighbors = {
                "Front":("Top", "Right", "Bottom", "Left"),
                "Right":("Top", "Back", "Bottom", "Front"),
                "Back":("Top", "Left", "Bottom", "Right"),
                "Left":("Top", "Front", "Bottom", "Back"),
                "Top":("Back", "Right", "Front", "Left"),
                "Bottom":("Front", "Right", "Back", "Left")
            }
        
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(VIEW3D_OT_view_straighten)
    bpy.types.Scene.view_straighten_is_running = bpy.props.BoolProperty(
        name = '',
        description = '',
        default = False,
        options = {'HIDDEN'})

def unregister():
    del bpy.types.Scene.view_straighten_is_running
    bpy.utils.unregister_class(VIEW3D_OT_view_straighten)
