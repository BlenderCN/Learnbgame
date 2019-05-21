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
    "name": "Mouselook Navigation",
    "description": "Alternative 3D view navigation",
    "author": "dairin0d, moth3r",
    "version": (1, 0, 8),
    "blender": (2, 7, 0),
    "location": "View3D > orbit/pan/dolly/zoom/fly/walk",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/MouselookNavigation",
    "tracker_url": "https://github.com/dairin0d/mouselook-navigation/issues",
    "category": "Learnbgame"
}
#============================================================================#

if "dairin0d" in locals():
    import imp
    imp.reload(dairin0d)
    imp.reload(utils_navigation)

import bpy
import bgl
import bmesh

from mathutils import Color, Vector, Matrix, Quaternion, Euler

import math
import time
import os
import json

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_view3d import SmartView3D, RaycastResult
from {0}dairin0d.utils_userinput import InputKeyMonitor, ModeStack, KeyMapUtils
from {0}dairin0d.utils_gl import cgl
from {0}dairin0d.utils_ui import NestedLayout, calc_region_rect
from {0}dairin0d.bpy_inspect import prop, BlRna
from {0}dairin0d.utils_addon import AddonManager
""".format(dairin0d_location))

from .utils_navigation import trackball, apply_collisions, calc_selection_center, calc_zbrush_border

addon = AddonManager()

"""
Note: due to the use of timer, operator consumes more resources than Blender's default
ISSUES:
* correct & stable collision detection?
* Blender's trackball
* ortho-grid/quadview-clip/projection-name display is not updated (do the issues disappear in 2.73 / Gooseberry branch?)
* Blender doesn't provide information about current selection center (try to use snap-cursor for this?), last paint/sculpt stroke
* zoom/rotate around last paint/sculpt stroke? (impossible: sculpt/paint is modal, and Blender provides mouse coordinates only for invoke/modal operator callbacks)

In the wiki:
* explain the rules for key setup (how the text is interpreted)
* explain fly/walk modes (e.g. what the scrollwheel does)
* other peculiarities of the algorithms I use?
* put a warning that if "emulate 3 mouse button" is enabled, the Alt key pan won't work in ZBrush preset (in this case, Alt+LMB will emulate middle mouse button)
* put a warning that User Preferences make the addon slow

Config/Presets:
* Load/Save/Import/Export config (+move almost everything from preferences to config)
* Load/Save/Import/Export presets

Keymaps:
* Generic solution for keymap registration
* remove default keymap behavior and use a default preset instead?
    * the default keymap behavior is actually a special case, since it takes the shortcut from the default navigation operator
    * incorporate this feature into the generic key-registration mechanism?
* implement key combinations in InputKeyMonitor? (e.g. Ctrl+Shift+LeftMouse and the like)

* In Blender 2.73, Grease Pencil can be edited (and points can be selected)

* Option to create an undo record when navigating from a camera?
* Add optional shortcuts to move focus to certain locations? (current orbit point, active element, selection center, cursor, world origin)
* Navigation history?
* Create camera here?



GENERIC KEYMAP REGISTRATION:
* Addon may have several operators with auto-registrable shortcuts. For each of them, a separate list of keymaps must be displayed (or: use tabbed interface?)
    * For a specific operator, there is a list of keymaps (generic mechanism), followed by invocation options UI (the draw function must be supplied by the implementation)
    * List of keymap setups: each of the items is associated with (or includes?) its own operator invocation options, but it's also possible to use universal operator invocation options
        * Keymaps (to which the shortcuts will be inserted): by default, all possible keymaps are available, but the implementation may specify some restricted set.
            * Should be displayed as a list of toggles, but an enum property won't have enough bits for all keymaps. Use collection and custom-drawn menu with operators?
        * Event value and event type (string): this form allows to specify several alternative shortcuts, though for convenience we may provide a special UI with full_event properties
        * Modifiers: any/shift/ctrl/alt/oskey/other key
        * Insert after, Insert before: the generic default is ("*", ""), which simply appends to the end. However, the implementation mught supply its own default.
        * (not shown directly in the UI): is_current, index: index is the only thing that needs to be specified as an /actual/ operator invocation parameter; when the operator is invoked, it can easily find the appropriate configuration by index.
        * Included operator invocation options (if implemented as an include and not as a reference by index)
    * Invocation options are likely to include shortcuts/modes/transitions that work within the corresponding modal operator
* As a general rule, addon should clean up its keymaps on disabling, but it shouldn't erase the keymaps manually added by the user (is this actually possible?)
* When addon is enabled, there are 3 cases:
    * Addon is enabled for the first time: should execute default keymap auto-registration behavior
    * Addon is enabled on Blender startup: the autro-registration setup is verified by user and saved with user preferences, so default behavior shouldn't happen
    * Addon is enabled after being disabled: all user changes from preferences are lost, BUT: if there is a config saved in a file, the addon might try to recover at least some user configuration
    * Or maybe just always use config file and force user to manually save it?
* Presets (in general case, addon may have independent lists of presets for each separate feature, and each feature might include 1 or more operators)
    * in general case, presets can affect key setup, the properties with which the operator(s) will be invoked, and some global settings
    * Save (to presets directory), Load (from presets directory), Delete (from presets directory), Import (from user-specified location), Export (to user-specified location)
    * in some cases, the presets might want to use the same shortcuts as some built-in operators (the default shortcuts should still be provided in case the built-in operator was not found in keymaps)
    * should presets contain the difference from some default control scheme, or there shouldn't be any default other than some specially-matked preset?
    * Maybe it's better to make presets work for the whole addon, not just key setup? (this would make them a complete config setup)
    * Is is possible to generalize preset/config loading, or it has to be an implementation-specific callback?
    * Built-in presets may also be hard-coded (e.g. useful in case of single-file addons)

"""

@addon.PropertyGroup
class MouselookNavigation_InputSettings:
    modes = ['ORBIT', 'PAN', 'DOLLY', 'ZOOM', 'FLY', 'FPS']
    transitions = ['NONE:ORBIT', 'NONE:PAN', 'NONE:DOLLY', 'NONE:ZOOM', 'NONE:FLY', 'NONE:FPS', 'ORBIT:PAN', 'ORBIT:DOLLY', 'ORBIT:ZOOM', 'ORBIT:FLY', 'ORBIT:FPS', 'PAN:DOLLY', 'PAN:ZOOM', 'DOLLY:ZOOM', 'FLY:FPS']
    
    default_mode = 'ORBIT' | prop("Default mode", name="Default mode", items=modes)
    allowed_transitions = set(transitions) | prop("Allowed transitions between modes", name="Transitions", items=transitions)
    
    ortho_unrotate = True | prop("In Ortho mode, rotation is abandoned if another mode is selected", name="Ortho unrotate")
    
    independent_modes = False | prop("When switching to a different mode, use the mode's last position/rotation/zoom", name="Independent modes")
    
    zbrush_mode = False | prop("The operator would be invoked only if mouse is over empty space or close to region border", name="ZBrush mode")
    
    def _keyprop(name, default_keys):
        return default_keys | prop(name, name)
    keys_confirm = _keyprop("Confirm", "Ret, Numpad Enter, Left Mouse: Press")
    keys_cancel = _keyprop("Cancel", "Esc, Right Mouse: Press")
    keys_rotmode_switch = _keyprop("Trackball on/off", "Space: Press")
    keys_origin_mouse = _keyprop("Origin: Mouse", "")
    keys_origin_selection = _keyprop("Origin: Selection", "")
    keys_orbit = _keyprop("Orbit", "") # main operator key (MMB) by default
    keys_orbit_snap = _keyprop("Orbit Snap", "Alt")
    keys_pan = _keyprop("Pan", "Shift")
    keys_dolly = _keyprop("Dolly", "")
    keys_zoom = _keyprop("Zoom", "Ctrl")
    keys_fly = _keyprop("Fly", "{Invoke key}: Double click")
    keys_fps = _keyprop("Walk", "Tab: Press")
    keys_FPS_forward = _keyprop("FPS forward", "W, Up Arrow")
    keys_FPS_back = _keyprop("FPS back", "S, Down Arrow")
    keys_FPS_left = _keyprop("FPS left", "A, Left Arrow")
    keys_FPS_right = _keyprop("FPS right", "D, Right Arrow")
    keys_FPS_up = _keyprop("FPS up", "E, R, Page Up")
    keys_FPS_down = _keyprop("FPS down", "Q, F, Page Down")
    keys_fps_acceleration = _keyprop("FPS fast", "Shift")
    keys_fps_slowdown = _keyprop("FPS slow", "Ctrl")
    keys_fps_crouch = _keyprop("FPS crouch", "Ctrl")
    keys_fps_jump = _keyprop("FPS jump", "Space")
    keys_fps_teleport = _keyprop("FPS teleport", "{Invoke key}, V")
    
    def draw(self, layout):
        with layout.split(0.15):
            with layout.column():
                layout.prop(self, "allowed_transitions")
            with layout.row():
                with layout.column():
                    layout.prop(self, "default_mode")
                    layout.prop(self, "ortho_unrotate", toggle=True)
                    layout.prop(self, "independent_modes", toggle=True)
                    layout.prop(self, "zbrush_mode", toggle=True)
                    #layout.label() # just an empty line
                    layout.prop(self, "keys_rotmode_switch")
                    layout.prop(self, "keys_origin_mouse")
                    layout.prop(self, "keys_origin_selection")
                    layout.prop(self, "keys_orbit")
                    layout.prop(self, "keys_orbit_snap")
                    layout.prop(self, "keys_pan")
                    layout.prop(self, "keys_dolly")
                    layout.prop(self, "keys_zoom")
                    layout.prop(self, "keys_fly")
                    layout.prop(self, "keys_fps")
                with layout.column():
                    layout.prop(self, "keys_confirm")
                    layout.prop(self, "keys_cancel")
                    layout.label() # just an empty line
                    layout.prop(self, "keys_FPS_forward")
                    layout.prop(self, "keys_FPS_back")
                    layout.prop(self, "keys_FPS_left")
                    layout.prop(self, "keys_FPS_right")
                    layout.prop(self, "keys_FPS_up")
                    layout.prop(self, "keys_FPS_down")
                    layout.prop(self, "keys_fps_acceleration")
                    layout.prop(self, "keys_fps_slowdown")
                    layout.prop(self, "keys_fps_crouch")
                    layout.prop(self, "keys_fps_jump")
                    layout.prop(self, "keys_fps_teleport")

@addon.Operator(idname="view3d.mouselook_navigation", label="Mouselook navigation", description="Mouselook navigation", options={'GRAB_POINTER', 'BLOCKING'})
class MouselookNavigation:
    input_settings_id = 0 | prop("Input Settings ID", "Input Settings ID", min=0)
    
    def copy_input_settings(self, inp_set):
        self.default_mode = inp_set.default_mode
        self.allowed_transitions = inp_set.allowed_transitions
        self.ortho_unrotate = inp_set.ortho_unrotate
        self.independent_modes = inp_set.independent_modes
        self.zbrush_mode = inp_set.zbrush_mode
    
    def create_keycheckers(self, event, inp_set):
        self.keys_invoke = self.km.keychecker(event.type)
        if event.value in {'RELEASE', 'CLICK'}:
            self.keys_invoke_confirm = self.km.keychecker(event.type+":PRESS")
        else:
            self.keys_invoke_confirm = self.km.keychecker(event.type+":RELEASE")
        self.keys_confirm = self.km.keychecker(inp_set.keys_confirm)
        self.keys_cancel = self.km.keychecker(inp_set.keys_cancel)
        self.keys_rotmode_switch = self.km.keychecker(inp_set.keys_rotmode_switch)
        self.keys_origin_mouse = self.km.keychecker(inp_set.keys_origin_mouse)
        self.keys_origin_selection = self.km.keychecker(inp_set.keys_origin_selection)
        self.keys_orbit = self.km.keychecker(inp_set.keys_orbit)
        self.keys_orbit_snap = self.km.keychecker(inp_set.keys_orbit_snap)
        self.keys_pan = self.km.keychecker(inp_set.keys_pan)
        self.keys_dolly = self.km.keychecker(inp_set.keys_dolly)
        self.keys_zoom = self.km.keychecker(inp_set.keys_zoom)
        self.keys_fly = self.km.keychecker(inp_set.keys_fly)
        self.keys_fps = self.km.keychecker(inp_set.keys_fps)
        self.keys_FPS_forward = self.km.keychecker(inp_set.keys_FPS_forward)
        self.keys_FPS_back = self.km.keychecker(inp_set.keys_FPS_back)
        self.keys_FPS_left = self.km.keychecker(inp_set.keys_FPS_left)
        self.keys_FPS_right = self.km.keychecker(inp_set.keys_FPS_right)
        self.keys_FPS_up = self.km.keychecker(inp_set.keys_FPS_up)
        self.keys_FPS_down = self.km.keychecker(inp_set.keys_FPS_down)
        self.keys_fps_acceleration = self.km.keychecker(inp_set.keys_fps_acceleration)
        self.keys_fps_slowdown = self.km.keychecker(inp_set.keys_fps_slowdown)
        self.keys_fps_crouch = self.km.keychecker(inp_set.keys_fps_crouch)
        self.keys_fps_jump = self.km.keychecker(inp_set.keys_fps_jump)
        self.keys_fps_teleport = self.km.keychecker(inp_set.keys_fps_teleport)
    
    @classmethod
    def poll(cls, context):
        if not addon.preferences.is_enabled: return False
        return (context.space_data.type == 'VIEW_3D')
    
    def modal(self, context, event):
        try:
            return self.modal_main(context, event)
        except:
            # If anything fails, at least dispose the resources
            self.cleanup(context)
            raise
    
    def modal_main(self, context, event):
        region = context.region
        v3d = context.space_data
        rv3d = context.region_data
        
        region_pos, region_size = self.sv.region_rect()
        
        userprefs = context.user_preferences
        drag_threshold = userprefs.inputs.drag_threshold
        tweak_threshold = userprefs.inputs.tweak_threshold
        mouse_double_click_time = userprefs.inputs.mouse_double_click_time / 1000.0
        rotate_method = userprefs.inputs.view_rotate_method
        invert_mouse_zoom = userprefs.inputs.invert_mouse_zoom
        invert_wheel_zoom = userprefs.inputs.invert_zoom_wheel
        use_zoom_to_mouse = userprefs.view.use_zoom_to_mouse
        use_auto_perspective = userprefs.view.use_auto_perspective
        
        addon_prefs = addon.preferences
        flips = addon_prefs.flips
        
        use_zoom_to_mouse |= self.force_origin_mouse
        use_auto_perspective &= self.rotation_snap_autoperspective
        
        use_zoom_to_mouse |= (self.use_origin_selection and self.zoom_to_selection)
        
        walk_prefs = userprefs.inputs.walk_navigation
        teleport_time = walk_prefs.teleport_time
        walk_speed_factor = walk_prefs.walk_speed_factor
        use_gravity = walk_prefs.use_gravity
        view_height = walk_prefs.view_height
        jump_height = walk_prefs.jump_height
        
        self.km.update(event)
        
        prev_mode = self.mode_stack.mode
        self.mode_stack.update()
        mode = self.mode_stack.mode
        
        mouse_prev = Vector((event.mouse_prev_x, event.mouse_prev_y))
        mouse = Vector((event.mouse_x, event.mouse_y))
        mouse_offset = mouse - self.mouse0
        mouse_delta = mouse - mouse_prev
        mouse_region = mouse - region_pos
        
        if self.independent_modes and (mode != prev_mode) and (mode not in {'FLY', 'FPS'}):
            mode_state = self.modes_state[mode]
            self.sv.is_perspective = mode_state[0]
            self.sv.distance = mode_state[1]
            self.pos = mode_state[2].copy()
            self.sv.focus = self.pos
            self.rot = mode_state[3].copy()
            self.euler = mode_state[4].copy()
            if rotate_method == 'TURNTABLE':
                self.sv.turntable_euler = self.euler # for turntable
            else:
                self.sv.rotation = self.rot # for trackball
        
        if (prev_mode in {'FLY', 'FPS'}) and (mode not in {'FLY', 'FPS'}):
            focus_proj = self.sv.focus_projected + region_pos
            context.window.cursor_warp(focus_proj.x, focus_proj.y)
        
        # Attempt to match Blender's default speeds
        ZOOM_SPEED_COEF = -0.77
        ZOOM_WHEEL_COEF = -0.25
        TRACKBALL_SPEED_COEF = 0.35
        TURNTABLE_SPEED_COEF = 0.62
        
        clock = time.clock()
        dt = 0.01
        speed_move = 2.5 * self.sv.distance# * dt # use realtime dt
        speed_zoom = Vector((1, 1)) * ZOOM_SPEED_COEF * dt
        speed_zoom_wheel = ZOOM_WHEEL_COEF
        speed_rot = TRACKBALL_SPEED_COEF * dt
        speed_euler = Vector((-1, 1)) * TURNTABLE_SPEED_COEF * dt
        speed_autolevel = 1 * dt
        
        if invert_mouse_zoom:
            speed_zoom *= -1
        if invert_wheel_zoom:
            speed_zoom_wheel *= -1
        
        if flips.orbit_x:
            speed_euler.x *= -1
        if flips.orbit_y:
            speed_euler.y *= -1
        if flips.zoom_x:
            speed_zoom.x *= -1
        if flips.zoom_y:
            speed_zoom.y *= -1
        if flips.zoom_wheel:
            speed_zoom_wheel *= -1
        
        speed_move *= self.fps_speed_modifier
        speed_zoom *= self.zoom_speed_modifier
        speed_zoom_wheel *= self.zoom_speed_modifier
        speed_rot *= self.rotation_speed_modifier
        speed_euler *= self.rotation_speed_modifier
        speed_autolevel *= self.autolevel_speed_modifier
        
        confirm = self.keys_confirm()
        cancel = self.keys_cancel()
        
        wheel_up = int(event.type == 'WHEELUPMOUSE')
        wheel_down = int(event.type == 'WHEELDOWNMOUSE')
        wheel_delta = wheel_up - wheel_down
        
        is_orbit_snap = False
        trackball_mode = self.trackball_mode
        
        if self.explicit_orbit_origin is not None:
            m_ofs = self.sv.matrix
            m_ofs.translation = self.explicit_orbit_origin
            m_ofs_inv = m_ofs.inverted()
        
        if (mode == 'FLY') or (mode == 'FPS'):
            if self.sv.is_region_3d or not self.sv.quadview_lock:
                self.explicit_orbit_origin = None
                self.sv.is_perspective = True
                self.sv.lock_cursor = False
                self.sv.lock_object = None
                self.sv.use_viewpoint = True
                self.sv.bypass_camera_lock = True
                trackball_mode = 'CENTER'
                
                mode = 'ORBIT'
                
                move_vector = self.FPS_move_vector()
                
                if self.mode_stack.mode == 'FPS':
                    if move_vector.z != 0: # turn off gravity if manual up/down is used
                        use_gravity = False
                        walk_prefs.use_gravity = use_gravity
                    elif self.keys_fps_jump():
                        use_gravity = True
                        walk_prefs.use_gravity = use_gravity
                    
                    rotate_method = 'TURNTABLE'
                    min_speed_autolevel = 30 * dt
                    speed_autolevel = max(speed_autolevel, min_speed_autolevel)
                    
                    self.update_fly_speed(wheel_delta, True)
                    
                    if not self.keys_fps_teleport():
                        self.teleport_allowed = True
                    
                    if self.teleport_allowed and self.keys_fps_teleport():
                        #ray_data = self.sv.ray(self.sv.project(self.sv.focus))
                        raycast_result = self.sv.ray_cast(self.sv.project(self.sv.focus))
                        if raycast_result.success:
                            normal = raycast_result.normal
                            ray_data = self.sv.ray(self.sv.project(self.sv.focus))
                            if normal.dot(ray_data[1] - ray_data[0]) > 0: normal = -normal
                            self.teleport_time_start = clock
                            self.teleport_pos = raycast_result.location + normal * view_height
                            self.teleport_pos_start = self.sv.viewpoint
                    
                    if move_vector.magnitude > 0:
                        self.teleport_pos = None
                else:
                    use_gravity = False
                    
                    self.update_fly_speed(wheel_delta, (move_vector.magnitude > 0))
                    
                    if (not self.keys_invoke.is_event) and self.keys_invoke():
                        self.fly_speed = Vector()
                        mode = 'PAN'
                
                self.rotate_method = rotate_method # used for FPS horizontal
                
                if (event.type == 'MOUSEMOVE') or (event.type == 'INBETWEEN_MOUSEMOVE'):
                    if mode == 'ORBIT':
                        if rotate_method == 'TURNTABLE':
                            self.change_euler(mouse_delta.y * speed_euler.y, mouse_delta.x * speed_euler.x, 0)
                        else: # 'TRACKBALL'
                            if flips.orbit_x:
                                mouse_delta.x *= -1
                            if flips.orbit_y:
                                mouse_delta.y *= -1
                            self.change_rot_mouse(mouse_delta, mouse, speed_rot, trackball_mode)
                    elif mode == 'PAN':
                        self.change_pos_mouse(mouse_delta, False)
                
                mode = self.mode_stack.mode # for display in header
                
                self.pos = self.sv.focus
        else:
            self.sv.use_viewpoint = False
            self.sv.bypass_camera_lock = False
            use_gravity = False
            self.teleport_pos = None
            self.teleport_allowed = False
            
            confirm |= self.keys_invoke_confirm()
            
            if self.sv.can_move:
                if self.keys_rotmode_switch():
                    if rotate_method == 'TURNTABLE':
                        rotate_method = 'TRACKBALL'
                    else:
                        rotate_method = 'TURNTABLE'
                    userprefs.inputs.view_rotate_method = rotate_method
                self.rotate_method = rotate_method # used for FPS horizontal
                
                is_orbit_snap = self.keys_orbit_snap()
                delta_orbit_snap = int(is_orbit_snap) - int(self.prev_orbit_snap)
                self.prev_orbit_snap = is_orbit_snap
                if delta_orbit_snap < 0:
                    self.euler = self.sv.turntable_euler
                    self.rot = self.sv.rotation
                
                if not self.sv.is_perspective:
                    if mode == 'DOLLY':
                        mode = 'ZOOM'
                    
                    # The goal is to make it easy to pan view without accidentally rotating it
                    if self.ortho_unrotate:
                        if mode in ('PAN', 'DOLLY', 'ZOOM'):
                            # forbid transitions back to orbit
                            self.mode_stack.remove_transitions({'ORBIT:PAN', 'ORBIT:DOLLY', 'ORBIT:ZOOM'})
                            self.reset_rotation(rotate_method, use_auto_perspective)
                
                if (event.type == 'MOUSEMOVE') or (event.type == 'INBETWEEN_MOUSEMOVE'):
                    if mode == 'ORBIT':
                        # snapping trackball rotation is problematic (I don't know how to do it)
                        if (rotate_method == 'TURNTABLE') or is_orbit_snap:
                            self.change_euler(mouse_delta.y * speed_euler.y, mouse_delta.x * speed_euler.x, 0)
                        else: # 'TRACKBALL'
                            if flips.orbit_x:
                                mouse_delta.x *= -1
                            if flips.orbit_y:
                                mouse_delta.y *= -1
                            self.change_rot_mouse(mouse_delta, mouse, speed_rot, trackball_mode)
                        
                        if use_auto_perspective:
                            self.sv.is_perspective = not is_orbit_snap
                        
                        if is_orbit_snap:
                            self.snap_rotation(self.rotation_snap_subdivs)
                    elif mode == 'PAN':
                        self.change_pos_mouse(mouse_delta, False)
                    elif mode == 'DOLLY':
                        if flips.dolly_y:
                            mouse_delta.y *= -1
                        self.change_pos_mouse(Vector((0.0, mouse_delta.y)), True)
                    elif mode == 'ZOOM':
                        self.change_distance((mouse_delta.y*speed_zoom.y + mouse_delta.x*speed_zoom.x), use_zoom_to_mouse)
                
                if wheel_delta != 0:
                    self.change_distance(wheel_delta * speed_zoom_wheel, use_zoom_to_mouse)
            else:
                if (event.type == 'MOUSEMOVE') or (event.type == 'INBETWEEN_MOUSEMOVE'):
                    if mode == 'PAN':
                        self.sv.camera_offset_pixels -= mouse_delta
                    elif mode == 'ZOOM':
                        self.sv.camera_zoom += (mouse_delta.y*speed_zoom.y + mouse_delta.x*speed_zoom.x) * -10
        
        if event.type.startswith('TIMER'):
            if self.sv.can_move:
                dt = clock - self.clock
                self.clock = clock
                
                if speed_autolevel > 0:
                    if (not is_orbit_snap) or (mode != 'ORBIT'):
                        if rotate_method == 'TURNTABLE':
                            self.change_euler(0, 0, speed_autolevel, False)
                        elif self.autolevel_trackball:
                            speed_autolevel *= 1.0 - abs(self.sv.forward.z)
                            self.change_euler(0, 0, speed_autolevel, self.autolevel_trackball_up)
                
                if self.teleport_pos is None:
                    abs_speed = self.calc_abs_speed(walk_speed_factor, speed_zoom, use_zoom_to_mouse, speed_move, use_gravity, dt, jump_height, view_height)
                else:
                    abs_speed = self.calc_abs_speed_teleport(clock, dt, teleport_time)
                
                if abs_speed.magnitude > 0:
                    self.change_pos(abs_speed)
            
            context.area.tag_redraw()
        
        if self.explicit_orbit_origin is not None:
            pre_rotate_focus = m_ofs_inv * self.pos
            m_ofs = self.sv.matrix
            m_ofs.translation = self.explicit_orbit_origin
            self.pos = m_ofs * pre_rotate_focus
            self.sv.focus = self.pos
        
        self.modes_state[mode] = (self.sv.is_perspective, self.sv.distance, self.pos.copy(), self.rot.copy(), self.euler.copy())
        
        self.update_cursor_icon(context)
        txt = "{} (zoom={:.3f})".format(mode, self.sv.distance)
        context.area.header_text_set(txt)
        
        if confirm:
            self.cleanup(context)
            return {'FINISHED'}
        elif cancel:
            self.revert_changes()
            self.cleanup(context)
            return {'CANCELLED'}
        
        if addon_prefs.pass_through:
            # Arguably more useful? Allows to more easily combine navigation with other operations,
            # e.g. using mouse & NDOF device simultaneously or sculpt-rotate-sculpt-rotate without releasing the MMB
            return {'PASS_THROUGH'}
        else:
            return {'RUNNING_MODAL'}
    
    def calc_abs_speed(self, walk_speed_factor, speed_zoom, use_zoom_to_mouse, speed_move, use_gravity, dt, jump_height, view_height):
        abs_speed = Vector()
        
        fps_speed = self.calc_FPS_speed(walk_speed_factor)
        if fps_speed.magnitude > 0:
            if not self.sv.is_perspective:
                self.change_distance((fps_speed.y * speed_zoom.y) * (-4), use_zoom_to_mouse)
                fps_speed.y = 0
            speed_move *= dt
            abs_speed = self.abs_fps_speed(fps_speed.x, fps_speed.y, fps_speed.z, speed_move, use_gravity)
        
        if use_gravity:
            gravity = -9.91
            self.velocity.z *= 0.999 # dampen
            self.velocity.z += gravity * dt
            is_jump = self.keys_fps_jump()
            if is_jump:
                if self.velocity.z < 0:
                    self.velocity.z *= 0.9
                if not self.prev_jump:
                    self.velocity.z += jump_height
                self.velocity.z += (abs(gravity) + jump_height) * dt
            self.prev_jump = is_jump
            
            is_crouching = self.keys_fps_crouch()
            
            pos0 = self.sv.viewpoint
            pos = pos0.copy()
            
            v0 = abs_speed
            v = abs_speed
            #v, collided = apply_collisions(context.scene, pos, v0, view_height, is_crouching, False, 1)
            pos += v
            
            v0 = self.velocity * dt
            v, collided = apply_collisions(bpy.context.scene, pos, v0, view_height, is_crouching, True, 0)
            if collided:
                self.velocity = Vector()
            pos += v
            
            abs_speed = pos - pos0
        else:
            self.velocity = Vector()
        
        return abs_speed
    
    def calc_abs_speed_teleport(self, clock, dt, teleport_time):
        p0 = self.sv.viewpoint
        t = (clock - self.teleport_time_start) + dt # +dt to move immediately
        if t >= teleport_time:
            p1 = self.teleport_pos
            self.teleport_pos = None
        else:
            t = t / teleport_time
            p1 = self.teleport_pos * t + self.teleport_pos_start * (1.0 - t)
        abs_speed = p1 - p0
        return abs_speed
    
    def update_fly_speed(self, wheel_delta, dont_fly=False):
        if dont_fly:
            self.fly_speed = Vector() # stop (FPS overrides flight)
            self.change_distance(wheel_delta*0.5)
        else:
            fwd_speed = self.fly_speed.y
            if (wheel_delta * fwd_speed < 0) and (abs(fwd_speed) >= 2):
                wheel_delta *= 2 # quick direction reversal
            fwd_speed = min(max(fwd_speed + wheel_delta, -9), 9)
            fwd_speed = round(fwd_speed) # avoid accumulation errors
            self.fly_speed.y = fwd_speed
    
    def FPS_move_vector(self):
        move_forward = self.keys_FPS_forward()
        move_back = self.keys_FPS_back()
        move_left = self.keys_FPS_left()
        move_right = self.keys_FPS_right()
        move_up = self.keys_FPS_up()
        move_down = self.keys_FPS_down()
        
        move_x = int(move_right) - int(move_left)
        move_y = int(move_forward) - int(move_back)
        move_z = int(move_up) - int(move_down)
        
        return Vector((move_x, move_y, move_z))
    
    def calc_FPS_speed(self, walk_speed_factor=5):
        move_vector = self.FPS_move_vector()
        
        movement_accelerate = self.keys_fps_acceleration()
        movement_slowdown = self.keys_fps_slowdown()
        move_speedup = int(movement_accelerate) - int(movement_slowdown)
        if self.mode_stack.mode in {'PAN', 'DOLLY', 'ZOOM'}:
            move_speedup = 0
        
        fps_speed = move_vector * (walk_speed_factor ** move_speedup)
        
        if fps_speed.magnitude == 0:
            fps_speed = self.fly_speed.copy()
            fps_speed.x = self.calc_fly_speed(fps_speed.x)
            fps_speed.y = self.calc_fly_speed(fps_speed.y)
            fps_speed.z = self.calc_fly_speed(fps_speed.z)
        
        return fps_speed
    
    def calc_fly_speed(self, v, k=2):
        if round(v) == 0:
            return 0
        return math.copysign(2 ** (abs(v) - k), v)
    
    def change_distance(self, delta, to_explicit_origin=False):
        log_zoom = math.log(max(self.sv.distance, self.min_distance), 2)
        self.sv.distance = math.pow(2, log_zoom + delta)
        if to_explicit_origin and (self.explicit_orbit_origin is not None):
            dst = self.explicit_orbit_origin
            offset = self.pos - dst
            log_zoom = math.log(max(offset.magnitude, self.min_distance), 2)
            offset = offset.normalized() * math.pow(2, log_zoom + delta)
            self.pos = dst + offset
            self.sv.focus = self.pos
    
    def abs_fps_speed(self, dx, dy, dz, speed=1.0, use_gravity=False):
        xdir, ydir, zdir = self.sv.right, self.sv.forward, self.sv.up
        fps_horizontal = (self.fps_horizontal or use_gravity) and self.sv.is_perspective
        if (self.rotate_method == 'TURNTABLE') and fps_horizontal:
            ysign = (-1.0 if zdir.z < 0 else 1.0)
            zdir = Vector((0, 0, 1))
            ydir = Quaternion(zdir, self.euler.z) * Vector((0, 1, 0))
            xdir = ydir.cross(zdir)
            ydir *= ysign
        return (xdir*dx + ydir*dy + zdir*dz) * speed
    
    def change_pos(self, abs_speed):
        self.pos += abs_speed
        self.sv.focus = self.pos
    
    def change_pos_mouse(self, mouse_delta, is_dolly=False):
        self.pos += self.mouse_delta_movement(mouse_delta, is_dolly)
        self.sv.focus = self.pos
    
    def mouse_delta_movement(self, mouse_delta, is_dolly=False):
        region = self.sv.region
        region_center = Vector((region.width*0.5, region.height*0.5))
        p0 = self.sv.unproject(region_center)
        p1 = self.sv.unproject(region_center - mouse_delta)
        pd = p1 - p0
        if is_dolly:
            pd_x = pd.dot(self.sv.right)
            pd_y = pd.dot(self.sv.up)
            pd = (self.sv.right * pd_x) + (self.sv.forward * pd_y)
        return pd
    
    def reset_rotation(self, rotate_method, use_auto_perspective):
        self.rot = self.rot0.copy()
        self.euler = self.euler0.copy()
        if rotate_method == 'TURNTABLE':
            self.sv.turntable_euler = self.euler # for turntable
        else:
            self.sv.rotation = self.rot # for trackball
        
        if use_auto_perspective:
            self.sv.is_perspective = self._perspective0
    
    numpad_orientations = [
        ('LEFT', Quaternion((0, 0, -1), math.pi/2.0)),
        ('RIGHT', Quaternion((0, 0, 1), math.pi/2.0)),
        ('BOTTOM', Quaternion((1, 0, 0), math.pi/2.0)),
        ('TOP', Quaternion((-1, 0, 0), math.pi/2.0)),
        ('FRONT', Quaternion((1, 0, 0, 0))),
        ('BACK', Quaternion((0, 0, 0, 1))),
        ('BACK', Quaternion((0, 0, 0, -1))),
    ]
    def detect_numpad_orientation(self, q):
        for name, nq in self.numpad_orientations:
            if abs(q.rotation_difference(nq).angle) < 1e-6: return name
    def snap_rotation(self, n=1):
        grid = math.pi*0.5 / n
        euler = self.euler.copy()
        euler.x = round(euler.x / grid) * grid
        euler.y = round(euler.y / grid) * grid
        euler.z = round(euler.z / grid) * grid
        self.sv.turntable_euler = euler
        self.rot = self.sv.rotation
        numpad_orientation = self.detect_numpad_orientation(self.rot)
        if numpad_orientation:
            bpy.ops.view3d.viewnumpad(type=numpad_orientation, align_active=False)
        else:
            bpy.ops.view3d.view_orbit(angle=0.0, type='ORBITUP')
    
    def change_euler(self, ex, ey, ez, always_up=False):
        self.euler.x += ex
        self.euler.z += ey
        if always_up and (self.sv.up.z < 0) or (abs(self.euler.y) > math.pi*0.5):
            _pi = math.copysign(math.pi, self.euler.y)
            self.euler.y = _pi - (_pi - self.euler.y) * math.pow(2, -abs(ez))
        else:
            self.euler.y *= math.pow(2, -abs(ez))
        self.sv.turntable_euler = self.euler
        self.rot = self.sv.rotation # update other representation
    
    def change_rot_mouse(self, mouse_delta, mouse, speed_rot, trackball_mode):
        if trackball_mode == 'CENTER':
            mouse_delta *= speed_rot
            spin = -((self.sv.right * mouse_delta.x) + (self.sv.up * mouse_delta.y)).normalized()
            axis = spin.cross(self.sv.forward)
            self.rot = Quaternion(axis, mouse_delta.magnitude) * self.rot
        elif trackball_mode == 'WRAPPED':
            mouse_delta *= speed_rot
            cdir = Vector((0, -1, 0))
            tv, x_neg, y_neg = self.trackball_vector(mouse)
            r = cdir.rotation_difference(tv)
            spin = r * Vector((mouse_delta.x, 0, mouse_delta.y))
            axis = spin.cross(tv)
            axis = self.sv.matrix.to_3x3() * axis
            self.rot = Quaternion(axis, mouse_delta.magnitude) * self.rot
        else:
            # Glitchy/buggy. Consult with Dalai Felinto?
            region = self.sv.region
            mouse -= Vector((region.x, region.y))
            halfsize = Vector((region.width, region.height))*0.5
            p1 = (mouse - mouse_delta) - halfsize
            p2 = (mouse) - halfsize
            p1 = Vector((p1.x/halfsize.x, p1.y/halfsize.y))
            p2 = Vector((p2.x/halfsize.x, p2.y/halfsize.y))
            q = trackball(p1.x, p1.y, p2.x, p2.y, 1.1)
            axis, angle = q.to_axis_angle()
            axis = self.sv.matrix.to_3x3() * axis
            q = Quaternion(axis, angle * speed_rot*200)
            self.rot = q * self.rot
        self.rot.normalize()
        self.sv.rotation = self.rot # update other representation
        self.euler = self.sv.turntable_euler # update other representation
    
    def _wrap_xy(self, xy, m=1):
        region = self.sv.region
        x = xy.x % (region.width*m)
        y = xy.y % (region.height*m)
        return Vector((x, y))
    def trackball_vector(self, xy):
        region = self.sv.region
        region_halfsize = Vector((region.width*0.5, region.height*0.5))
        radius = region_halfsize.magnitude * 1.1
        xy -= Vector((region.x, region.y)) # convert to region coords
        xy = self._wrap_xy(xy, 2)
        x_neg = (xy.x >= region.width)
        y_neg = (xy.y >= region.height)
        xy = self._wrap_xy(xy)
        xy -= region_halfsize # make relative to center
        xy *= (1.0/radius) # normalize
        z = math.sqrt(1.0 - xy.length_squared)
        return Vector((xy.x, -z, xy.y)).normalized(), x_neg, y_neg
    
    def update_cursor_icon(self, context):
        # DEFAULT, NONE, WAIT, CROSSHAIR, MOVE_X, MOVE_Y, KNIFE, TEXT, PAINT_BRUSH, HAND, SCROLL_X, SCROLL_Y, SCROLL_XY, EYEDROPPER
        if self.mode_stack.mode in {'FLY', 'FPS'}:
            context.window.cursor_modal_set('NONE')
        else:
            context.window.cursor_modal_set('SCROLL_XY')
    
    def invoke(self, context, event):
        wm = context.window_manager
        userprefs = context.user_preferences
        addon_prefs = addon.preferences
        region = context.region
        v3d = context.space_data
        rv3d = context.region_data
        
        if event.value == 'RELEASE':
            # 'ANY' is useful for click+doubleclick, but release is not intended
            # IMPORTANT: self.bl_idname is NOT the same as class.bl_idname!
            for kc, km, kmi in KeyMapUtils.search(MouselookNavigation.bl_idname):
                if (kmi.type == event.type) and (kmi.value == 'ANY'):
                    return {'CANCELLED'}
        
        if addon_prefs.use_universal_input_settings:
            inp_set = addon_prefs.universal_input_settings
        else:
            input_settings_id = min(self.input_settings_id, len(addon_prefs.autoreg_keymaps)-1)
            autoreg_keymap = addon_prefs.autoreg_keymaps[input_settings_id]
            inp_set = autoreg_keymap.input_settings
        
        self.copy_input_settings(inp_set)
        
        self.sv = SmartView3D(context)
        
        region_pos, region_size = self.sv.region_rect()
        clickable_region_pos, clickable_region_size = self.sv.region_rect(False)
        
        self.zbrush_border = calc_zbrush_border(self.sv.area, self.sv.region)
        
        self.km = InputKeyMonitor(event)
        self.create_keycheckers(event, inp_set)
        mouse_prev = Vector((event.mouse_prev_x, event.mouse_prev_y))
        mouse = Vector((event.mouse_x, event.mouse_y))
        mouse_delta = mouse - mouse_prev
        mouse_region = mouse - region_pos
        mouse_clickable_region = mouse - clickable_region_pos
        
        depthcast_radius = addon_prefs.zbrush_radius
        raycast_radius = min(addon_prefs.zbrush_radius, 16)
        
        if addon_prefs.zbrush_method == 'ZBUFFER':
            cast_result = self.sv.depth_cast(mouse_region, depthcast_radius)
        elif addon_prefs.zbrush_method == 'RAYCAST':
            cast_result = self.sv.ray_cast(mouse_region, raycast_radius)
        else: # SELECTION
            cast_result = RaycastResult() # Auto Depth is useless with ZBrush mode anyway
        
        self.zoom_to_selection = addon_prefs.zoom_to_selection
        self.force_origin_mouse = self.keys_origin_mouse()
        self.force_origin_selection = self.keys_origin_selection()
        self.use_origin_mouse = userprefs.view.use_mouse_depth_navigate
        self.use_origin_selection = userprefs.view.use_rotate_around_active
        if self.force_origin_selection:
            self.use_origin_selection = True
            self.use_origin_mouse = False
        elif self.force_origin_mouse:
            self.use_origin_selection = False
            self.use_origin_mouse = True
        
        self.explicit_orbit_origin = None
        if self.use_origin_selection:
            self.explicit_orbit_origin = calc_selection_center(context, True)
        elif self.use_origin_mouse:
            if cast_result.success:
                self.explicit_orbit_origin = cast_result.location
                if self.sv.is_perspective:
                    # Blender adjusts distance so that focus and z-point lie in the same plane
                    viewpoint = self.sv.viewpoint
                    self.sv.distance = self.sv.z_distance(self.explicit_orbit_origin)
                    self.sv.viewpoint = viewpoint
            else:
                self.explicit_orbit_origin = self.sv.unproject(mouse_region)
        
        mode_keys = {'ORBIT':self.keys_orbit, 'PAN':self.keys_pan, 'DOLLY':self.keys_dolly, 'ZOOM':self.keys_zoom, 'FLY':self.keys_fly, 'FPS':self.keys_fps}
        self.mode_stack = ModeStack(mode_keys, self.allowed_transitions, self.default_mode, 'NONE')
        self.mode_stack.update()
        if self.mode_stack.mode == 'NONE':
            if self.zbrush_mode:
                mouse_region_11 = clickable_region_size - mouse_clickable_region
                wrk_x = min(mouse_clickable_region.x, mouse_region_11.x)
                wrk_y = min(mouse_clickable_region.y, mouse_region_11.y)
                wrk_pos = min(wrk_x, wrk_y)
                if wrk_pos > self.zbrush_border:
                    if addon_prefs.zbrush_method == 'SELECTION':
                        cast_result = self.sv.select(mouse_region)
                    if cast_result.success: return {'PASS_THROUGH'}
            self.mode_stack.mode = self.default_mode
        self.update_cursor_icon(context)
        
        self.color_crosshair_visible = addon_prefs.get_color("color_crosshair_visible")
        self.color_crosshair_obscured = addon_prefs.get_color("color_crosshair_obscured")
        self.color_zbrush_border = addon_prefs.get_color("color_zbrush_border")
        self.show_crosshair = addon_prefs.show_crosshair
        self.show_focus = addon_prefs.show_focus
        self.show_zbrush_border = addon_prefs.show_zbrush_border
        
        settings = addon_prefs
        self.fps_horizontal = settings.fps_horizontal
        self.trackball_mode = settings.trackball_mode
        self.fps_speed_modifier = settings.fps_speed_modifier
        self.zoom_speed_modifier = settings.zoom_speed_modifier
        self.rotation_snap_subdivs = settings.rotation_snap_subdivs
        self.rotation_snap_autoperspective = settings.rotation_snap_autoperspective
        self.rotation_speed_modifier = settings.rotation_speed_modifier
        self.autolevel_trackball = settings.autolevel_trackball
        self.autolevel_trackball_up = settings.autolevel_trackball_up
        self.autolevel_speed_modifier = settings.autolevel_speed_modifier
        
        self.prev_orbit_snap = False
        self.min_distance = 2 ** -10
        
        self.fly_speed = Vector()
        
        self._clock0 = time.clock()
        self._continuous0 = userprefs.inputs.use_mouse_continuous
        self._mouse0 = Vector((event.mouse_x, event.mouse_y))
        self._perspective0 = self.sv.is_perspective
        self._distance0 = self.sv.distance
        self._pos0 = self.sv.focus
        self._rot0 = self.sv.rotation
        self._euler0 = self.sv.turntable_euler
        self._smooth_view0 = userprefs.view.smooth_view
        
        self.mouse0 = self._mouse0.copy()
        self.clock0 = self._clock0
        self.pos = self._pos0.copy()
        self.rot0 = self._rot0.copy()
        self.rot = self.rot0.copy()
        self.euler0 = self._euler0.copy()
        self.euler = self.euler0.copy()
        
        self.modes_state = {}
        for mode in MouselookNavigation_InputSettings.modes:
            self.modes_state[mode] = (self.sv.is_perspective, self.sv.distance, self.pos.copy(), self.rot.copy(), self.euler.copy())
        
        self.clock = self.clock0
        self.velocity = Vector()
        self.prev_jump = False
        self.teleport_pos = None
        self.teleport_pos_start = None
        self.teleport_time_start = -1
        self.teleport_allowed = False
        
        self.sculpt_levels0 = None
        if (context.mode == 'SCULPT') and context.tool_settings.sculpt.show_low_resolution:
            for modifier in context.object.modifiers:
                if modifier.type == 'MULTIRES':
                    self.sculpt_levels0 = modifier.sculpt_levels
                    modifier.sculpt_levels = min(modifier.sculpt_levels, 1)
                    break
        
        userprefs.inputs.use_mouse_continuous = True
        userprefs.view.smooth_view = 0
        
        self.register_handlers(context)
        
        context.area.header_text_set()
        
        # We need the view to redraw so that crosshair would appear
        # immediately after user presses MMB
        context.area.tag_redraw()
        
        return {'RUNNING_MODAL'}
    
    def revert_changes(self):
        self.sv.bypass_camera_lock = True
        self.sv.use_viewpoint = False
        self.sv.rotation = self._rot0
        self.sv.distance = self._distance0
        self.sv.focus = self._pos0
        self.sv.is_perspective = self._perspective0
        self.mode_stack.mode = None # used for setting mouse position
    
    def cleanup(self, context):
        if self.mode_stack.mode is None:
            context.window.cursor_warp(self.mouse0.x, self.mouse0.y)
        elif self.mode_stack.mode in {'FLY', 'FPS'}:
            focus_proj = self.sv.focus_projected + self.sv.region_rect()[0]
            context.window.cursor_warp(focus_proj.x, focus_proj.y)
        
        if (context.mode == 'SCULPT') and context.tool_settings.sculpt.show_low_resolution:
            for modifier in context.object.modifiers:
                if modifier.type == 'MULTIRES':
                    modifier.sculpt_levels = self.sculpt_levels0
                    break
        
        userprefs = context.user_preferences
        userprefs.inputs.use_mouse_continuous = self._continuous0
        userprefs.view.smooth_view = self._smooth_view0
        
        self.unregister_handlers(context)
        
        context.area.header_text_set()
        context.window.cursor_modal_restore()
        
        # We need the view to redraw so that crosshair would disappear
        # immediately after user releases MMB
        context.area.tag_redraw()
    
    def register_handlers(self, context):
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = addon.timer_add(0.01, context.window)
        self._handle_view = addon.draw_handler_add(bpy.types.SpaceView3D, draw_callback_view, (self, context), 'WINDOW', 'POST_VIEW')
    
    def unregister_handlers(self, context):
        addon.remove(self._timer)
        addon.remove(self._handle_view)


def draw_crosshair(self, context, use_focus):
    if not self.sv.can_move:
        return # if camera can't be manipulated, crosshair is meaningless
    
    focus_proj = None
    if use_focus:
        if self.explicit_orbit_origin and not self.show_focus:
            return
        alpha = (0.4 if self.explicit_orbit_origin else 1.0)
        focus_proj = self.sv.focus_projected
        z_ref = self.sv.z_distance(self.sv.focus, 0.01)
    elif self.explicit_orbit_origin:
        alpha = 1.0
        focus_proj = self.sv.project(self.explicit_orbit_origin)
        z_ref = self.explicit_orbit_origin
    
    if focus_proj is None:
        return
    
    l0, l1 = 16, 25
    lines = [(Vector((0, l0)), Vector((0, l1))), (Vector((0, -l0)), Vector((0, -l1))),
             (Vector((l0, 0)), Vector((l1, 0))), (Vector((-l0, 0)), Vector((-l1, 0)))]
    lines = [(self.sv.unproject(p0 + focus_proj, z_ref, True),
              self.sv.unproject(p1 + focus_proj, z_ref, True)) for p0, p1 in lines]
    
    color = self.color_crosshair_visible
    color_visible = (color[0], color[1], color[2], 1.0*alpha)
    color = self.color_crosshair_obscured
    color_obscured = (color[0], color[1], color[2], 0.35*alpha)
    
    with cgl('DepthFunc', 'LineWidth', DEPTH_TEST=True, DEPTH_WRITEMASK=False, BLEND=True, LINE_STIPPLE=False):
        for c, df, lw in ((color_visible, 'LEQUAL', 1), (color_obscured, 'GREATER', 3)):
            cgl.Color = c
            cgl.DepthFunc = df
            cgl.LineWidth = lw
            with cgl.batch('LINES') as batch:
                for p0, p1 in lines:
                    batch.vertex(*p0)
                    batch.vertex(*p1)

def draw_callback_view(self, context):
    if self.sv.region_data != context.region_data:
        return
    
    if self.show_crosshair:
        draw_crosshair(self, context, False)
        draw_crosshair(self, context, True)

def draw_callback_px(self, context):
    context = bpy.context # we need most up-to-date context
    userprefs = context.user_preferences
    addon_prefs = addon.preferences
    
    if addon_prefs.show_zbrush_border and addon_prefs.zbrush_mode:
        area = context.area
        region = context.region
        
        full_rect = calc_region_rect(area, region)
        clickable_rect = calc_region_rect(area, region, False)
        border = calc_zbrush_border(area, region)
        color = addon_prefs.get_color("color_zbrush_border")
        
        x, y = clickable_rect[0] - full_rect[0]
        w, h = clickable_rect[1]
        
        with cgl(BLEND=True):
            cgl.Color = (color[0], color[1], color[2], 0.5)
            with cgl.batch('LINE_LOOP') as batch:
                batch.vertex(x + border, y + border)
                batch.vertex(x + w-border, y + border)
                batch.vertex(x + w-border, y + h-border)
                batch.vertex(x + border, y + h-border)


@addon.Operator(idname="wm.mouselook_navigation_autoreg_keymaps_update", label="Update Autoreg Keymaps", description="Update auto-registered keymaps")
def update_keymaps(activate=True):
    idname = MouselookNavigation.bl_idname
    
    KeyMapUtils.remove(idname)
    
    if activate:
        # Attention: userprefs.addons[__name__] may not exist during unregistration
        context = bpy.context
        wm = context.window_manager
        userprefs = context.user_preferences
        addon_prefs = addon.preferences
        
        key_monitor = InputKeyMonitor()
        #keymaps = wm.keyconfigs.addon.keymaps
        
        # For a specific operator, the same (exact clones) keymap items may need to be
        # inserted into keymaps of several modes (depending on what conflicts may arise).
        # Since we need mouselook operator to have higher priority than default navigation,
        # but lower priority than 3D manipulator, we have to put it into the user keymaps
        # (because only user keymaps actually store user modifications).
        # User may still want to have several mouselook shortcuts in one mode, e.g. if (s)he
        # wants standard Blender control scheme (mouse to orbit/pan/zoom, Shift+F to fly/walk)
        keymaps = wm.keyconfigs.user.keymaps
        
        if len(addon_prefs.autoreg_keymaps) == 0 and addon_prefs.use_default_keymap:
            kmi = next(KeyMapUtils.search("view3d.rotate"), (None, None, None))[2]
            if kmi:
                ark = addon_prefs.autoreg_keymaps.add()
                ark.keymaps = {'3D View'}
                ark.value_type = kmi.type+":"+"ANY" #kmi.value
                ark.any = True #kmi.any
                ark.shift = False #kmi.shift
                ark.ctrl = False #kmi.ctrl
                ark.alt = False #kmi.alt
                ark.oskey = False #kmi.oskey
                ark.key_modifier = "" #kmi.key_modifier
        
        kmi_to_insert = {}
        
        for ark_id, ark in enumerate(addon_prefs.autoreg_keymaps):
            insert_before = set(v.strip() for v in ark.insert_before.split(","))
            insert_before.discard("")
            insert_after = set(v.strip() for v in ark.insert_after.split(","))
            insert_after.discard("")
            
            for mode_name in ark.keymaps:
                kmi_datas = kmi_to_insert.setdefault(mode_name, [])
                
                value_type = ark.value_type
                if ":" not in value_type:
                    value_type += ": Press"
                keys = key_monitor.parse_keys(value_type)
                keys_modifier = key_monitor.parse_keys(ark.key_modifier)
                
                any = ark.any
                shift = ark.shift
                ctrl = ark.ctrl
                alt = ark.alt
                oskey = ark.oskey
                key_modifier = 'NONE'
                if keys_modifier and (not keys_modifier[0].startswith("!")):
                    key_modifier = keys_modifier[0].split(":")[0]
                
                for key in keys:
                    if not key.startswith("!"):
                        key_type, key_value = key.split(":")
                        kmi_data = dict(idname=idname, type=key_type, value=key_value,
                            any=any, shift=shift, ctrl=ctrl, alt=alt, oskey=oskey, key_modifier=key_modifier,
                            properties=dict(input_settings_id=ark_id))
                        kmi_datas.append((insert_after, kmi_data, insert_before))
        
        for keymap_name, kmi_datas in kmi_to_insert.items():
            try:
                km = keymaps[keymap_name] # expected to exist in user keymaps
            except:
                continue
            KeyMapUtils.insert(km, kmi_datas)

@addon.PropertyGroup
class AutoRegKeymapInfo:
    mode_names = ['3D View', 'Object Mode', 'Mesh', 'Curve', 'Armature', 'Metaball', 'Lattice', 'Font', 'Pose', 'Vertex Paint', 'Weight Paint', 'Image Paint', 'Sculpt', 'Particle']
    keymaps = {'3D View'} | prop("Keymaps", name="Keymaps", items=mode_names)
    value_type = "" | prop("Type of event", name="Type of event")
    any = False | prop("Any modifier", name="Any")
    shift = False | prop("Shift", name="Shift")
    ctrl = False | prop("Ctrl", name="Ctrl")
    alt = False | prop("Alt", name="Alt")
    oskey = False | prop("Cmd (OS key)", name="Cmd")
    key_modifier = "" | prop("Regular key pressed as a modifier", name="")
    insert_after = "view3d.manipulator" | prop("Insert after the specified operators", name="Insert after")
    insert_before = "*" | prop("Insert before the specified operators", name="Insert before")
    input_settings = MouselookNavigation_InputSettings | prop()
    
    def get_is_current(self):
        userprefs = bpy.context.user_preferences
        addon_prefs = addon.preferences
        return (addon_prefs.autoreg_keymap_id == self.index) and (not addon_prefs.use_universal_input_settings)
    def set_is_current(self, values):
        userprefs = bpy.context.user_preferences
        addon_prefs = addon.preferences
        if values:
            addon_prefs.autoreg_keymap_id = self.index
            addon_prefs.use_universal_input_settings = False
        else:
            addon_prefs.use_universal_input_settings = True
    is_current = False | prop(get=get_is_current, set=set_is_current)
    index = 0 | prop()

@addon.Operator(idname="wm.mouselook_navigation_autoreg_keymap_add", label="Add Autoreg Keymap")
def add_autoreg_keymap(self, context):
    """Add auto-registered keymap"""
    wm = context.window_manager
    userprefs = context.user_preferences
    addon_prefs = addon.preferences
    addon_prefs.use_default_keymap = False
    ark = addon_prefs.autoreg_keymaps.add()
    ark.index = len(addon_prefs.autoreg_keymaps)-1
    addon_prefs.autoreg_keymap_id = ark.index

@addon.Operator(idname="wm.mouselook_navigation_autoreg_keymap_remove", label="Remove Autoreg Keymap")
def remove_autoreg_keymap(self, context, index=0):
    """Remove auto-registered keymap"""
    wm = context.window_manager
    userprefs = context.user_preferences
    addon_prefs = addon.preferences
    addon_prefs.use_default_keymap = False
    addon_prefs.autoreg_keymaps.remove(self.index)
    if addon_prefs.autoreg_keymap_id >= len(addon_prefs.autoreg_keymaps):
        addon_prefs.autoreg_keymap_id = len(addon_prefs.autoreg_keymaps)-1
    for i, ark in enumerate(addon_prefs.autoreg_keymaps):
        ark.index = i

class PresetManager:
    presets = {}
    sorted_names = []
    
    @classmethod
    def load(cls):
        cls.presets = {}
        cls.sorted_names = []
        
        dirpath = os.path.join(addon.path, "presets")
        if not os.path.isdir(dirpath):
            return
        
        for dirpath, dirnames, filenames in os.walk(dirpath):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                with open(filepath, "r") as file:
                    data = json.loads(file.read())
                filename = os.path.splitext(filename)[0]
                cls.presets[filename] = data
        
        cls.sorted_names = sorted(cls.presets.keys())
    
    @staticmethod
    def enum_items(self, context):
        # WARNING: There is a known bug with using a callback, Python must keep a reference to the strings returned or Blender will crash.
        enum_items = []
        for preset_name in PresetManager.sorted_names:
            enum_items.append((preset_name, preset_name, preset_name))
        return enum_items

@addon.Operator(idname="wm.mouselook_navigation_autoreg_keymaps_preset_load", label="Load Autoreg Keymaps Preset")
def autoreg_keymaps_preset_load(self, context, preset_id = '' | prop("Preset ID", name="Preset ID", items=PresetManager.enum_items)):
    """Load Autoreg Keymaps Preset"""
    wm = context.window_manager
    userprefs = context.user_preferences
    addon_prefs = addon.preferences
    
    addon_prefs.use_default_keymap = False
    
    preset = PresetManager.presets[self.preset_id]
    
    flips = preset.get("flips", ())
    addon_prefs.flips.orbit_x = "orbit_x" in flips
    addon_prefs.flips.orbit_y = "orbit_y" in flips
    addon_prefs.flips.dolly = "dolly" in flips
    addon_prefs.flips.zoom_x = "zoom_x" in flips
    addon_prefs.flips.zoom_y = "zoom_y" in flips
    addon_prefs.flips.zoom_wheel = "zoom_wheel" in flips
    
    addon_prefs.use_universal_input_settings = preset.get("universal", True)
    BlRna.reset(addon_prefs.universal_input_settings)
    BlRna.deserialize(addon_prefs.universal_input_settings, preset.get("settings"))
    
    while addon_prefs.autoreg_keymaps:
        addon_prefs.autoreg_keymaps.remove(0)
    
    for ark_data in preset.get("keymaps", tuple()):
        ark = addon_prefs.autoreg_keymaps.add()
        BlRna.deserialize(ark, ark_data)
        ark.index = len(addon_prefs.autoreg_keymaps)-1
    addon_prefs.autoreg_keymap_id = len(addon_prefs.autoreg_keymaps)-1
    
    update_keymaps()

@addon.Panel(idname="VIEW3D_PT_mouselook_navigation", space_type='VIEW_3D', region_type='UI', label="Mouselook Nav.")
class VIEW3D_PT_mouselook_navigation:
    def draw_header(self, context):
        self.layout.prop(addon.preferences, "is_enabled", text="")
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        
        addon_prefs = addon.preferences
        settings = addon_prefs
        
        with layout.row(True):
            layout.label("Show/hide:")
            layout.prop(settings, "show_crosshair", text="", icon='ZOOMIN')
            with layout.row(True)(active=settings.show_crosshair):
                layout.prop(settings, "show_focus", text="", icon='LAMP_HEMI')
            layout.prop(settings, "show_zbrush_border", text="", icon='BORDER_RECT')
        
        with layout.column(True):
            layout.prop(settings, "zoom_speed_modifier")
            layout.prop(settings, "rotation_speed_modifier")
            layout.prop(settings, "fps_speed_modifier")
        
        layout.prop(settings, "fps_horizontal")
        layout.prop(settings, "zoom_to_selection")
        
        with layout.box():
            with layout.row():
                layout.label(text="Orbit snap")
                layout.prop(settings, "rotation_snap_autoperspective", text="To Ortho", toggle=True)
            layout.prop(settings, "rotation_snap_subdivs", text="Subdivs")
        
        with layout.box():
            with layout.row():
                layout.label(text="Trackball")
                layout.prop(settings, "trackball_mode", text="")
            with layout.row(True):
                layout.prop(settings, "autolevel_trackball", text="Autolevel", toggle=True)
                with layout.row(True)(active=settings.autolevel_trackball):
                    layout.prop(settings, "autolevel_trackball_up", text="Up", toggle=True)
        
        layout.prop(settings, "autolevel_speed_modifier")

@addon.PropertyGroup
class NavigationDirectionFlip:
    orbit_x = False | prop()
    orbit_y = False | prop()
    dolly = False | prop()
    zoom_x = False | prop()
    zoom_y = False | prop()
    zoom_wheel = False | prop()
    
    def draw(self, layout):
        layout.label("Invert:")
        layout.prop(self, "orbit_x", toggle=True)
        layout.prop(self, "orbit_y", toggle=True)
        layout.prop(self, "dolly", toggle=True)
        layout.prop(self, "zoom_x", toggle=True)
        layout.prop(self, "zoom_y", toggle=True)
        layout.prop(self, "zoom_wheel", toggle=True)

@addon.Preferences.Include
class ThisAddonPreferences:
    show_crosshair = True | prop("Crosshair visibility", name="Show Crosshair")
    show_focus = True | prop("Orbit Center visibility", name="Show Orbit Center")
    show_zbrush_border = True | prop("ZBrush border visibility", name="Show ZBrush border")
    use_blender_colors = True | prop("Use Blender's colors", name="Use Blender's colors")
    color_crosshair_visible = Color() | prop("Crosshair (visible) color", name="Crosshair (visible)")
    color_crosshair_obscured = Color() | prop("Crosshair (obscured) color", name="Crosshair (obscured)")
    color_zbrush_border = Color() | prop("ZBrush border color", name="ZBrush border")
    
    def get_color(self, attr_name):
        if self.use_blender_colors:
            try:
                return userprefs.themes[0].view_3d.view_overlay
            except:
                return Color((0,0,0))
        else:
            return getattr(self, attr_name)
    
    def calc_zbrush_mode(self):
        if self.use_universal_input_settings:
            return self.universal_input_settings.zbrush_mode
        return any(ark.input_settings.zbrush_mode for ark in self.autoreg_keymaps)
    zbrush_mode = False | prop(get=calc_zbrush_mode)
    
    use_default_keymap = True | prop(name="Use default keymap", options={'HIDDEN'})
    autoreg_keymaps = [AutoRegKeymapInfo] | prop("Auto-registered keymaps", name="Auto-registered keymaps")
    autoreg_keymap_id = 0 | prop("Keymap ID", name="Keymap ID", min=0)
    use_universal_input_settings = True | prop("Use same settings for each keymap", name="Universal")
    universal_input_settings = MouselookNavigation_InputSettings | prop()
    
    zbrush_radius = 20 | prop("In ZBrush mode, allow navigation only when distance (in pixels) to the nearest geometry is greater than this value", name="ZBrush radius", min=0, max=64)
    zbrush_method = 'ZBUFFER' | prop("Which method to use to determine if mouse is over empty space", name="ZBrush method", items=[('RAYCAST', "Raycast"), ('ZBUFFER', "Z-buffer"), ('SELECTION', "Selection")])
    
    is_enabled = True | prop("Enable/disable Mouselook Navigation", name="Enabled")
    
    def use_zbuffer_update(self, context):
        addon.use_zbuffer = addon.preferences.use_zbuffer
    use_zbuffer = True | prop("Preemptively grab Z-buffer (WARNING: CAN BE SLOW!)", name="Record Z-buffer", update=use_zbuffer_update)
    
    pass_through = False | prop("Other operators can be used while navigating", name="Non-blocking")
    
    flips = NavigationDirectionFlip | prop()
    
    zoom_speed_modifier = 1.0 | prop("Zooming speed", name="Zoom speed")
    rotation_speed_modifier = 1.0 | prop("Rotation speed", name="Rotation speed")
    fps_speed_modifier = 1.0 | prop("FPS movement speed", name="FPS speed")
    fps_horizontal = False | prop("Force forward/backward to be in horizontal plane, and up/down to be vertical", name="FPS horizontal")
    zoom_to_selection = True | prop("Zoom to selection when Rotate Around Selection is enabled", name="Zoom to selection")
    trackball_mode = 'WRAPPED' | prop("Rotation algorithm used in trackball mode", name="Trackball mode", items=[('BLENDER', 'Blender', 'Blender (buggy!)', 'ERROR'), ('WRAPPED', 'Wrapped'), ('CENTER', 'Center')])
    rotation_snap_subdivs = 2 | prop("Intermediate angles used when snapping (1: 90°, 2: 45°, 3: 30°, etc.)", name="Orbit snap subdivs", min=1)
    rotation_snap_autoperspective = True | prop("If Auto Perspective is enabled, rotation snapping will automatically switch the view to Ortho", name="Orbit snap->ortho")
    autolevel_trackball = False | prop("Autolevel in Trackball mode", name="Trackball Autolevel")
    autolevel_trackball_up = False | prop("Try to autolevel 'upright' in Trackball mode", name="Trackball Autolevel up")
    autolevel_speed_modifier = 0.0 | prop("Autoleveling speed", name="Autolevel speed", min=0.0)
    
    def draw(self, context):
        layout = NestedLayout(self.layout)
        
        use_universal_input_settings = (self.use_universal_input_settings or len(self.autoreg_keymaps) == 0)
        
        with layout.row()(alignment='LEFT'):
            layout.prop(self, "use_zbuffer")
            layout.prop(self, "pass_through")
        
        with layout.row():
            with layout.column():
                layout.prop(self, "zbrush_radius")
                layout.prop(self, "show_zbrush_border")
                layout.prop(self, "show_crosshair")
                layout.prop(self, "show_focus")
            with layout.column():
                with layout.row():
                    layout.prop_menu_enum(self, "zbrush_method")
                    layout.prop(self, "use_blender_colors")
                with layout.column()(active=not self.use_blender_colors):
                    layout.row().prop(self, "color_zbrush_border")
                    layout.row().prop(self, "color_crosshair_visible")
                    layout.row().prop(self, "color_crosshair_obscured")
        
        with layout.row(True):
            self.flips.draw(layout)
        
        with layout.box():
            with layout.row():
                layout.label("Auto-registered keymaps:")
                layout.operator("wm.mouselook_navigation_autoreg_keymap_add", text="Add", icon='ZOOMIN')
                layout.operator("wm.mouselook_navigation_autoreg_keymaps_update", text="Update", icon='FILE_REFRESH')
                layout.operator_menu_enum("wm.mouselook_navigation_autoreg_keymaps_preset_load", "preset_id", text="Load Preset", icon='FILESEL')
            
            autoreg_keymaps = self.autoreg_keymaps
            for i, ark in enumerate(autoreg_keymaps):
                with layout.box():
                    with layout.row():
                        icon = (('PROP_CON' if ark.is_current else 'PROP_ON') if not use_universal_input_settings else 'PROP_OFF')
                        layout.prop(ark, "is_current", text="", icon=icon, icon_only=True, toggle=True, emboss=False)
                        with layout.split(0.6):
                            with layout.row():
                                layout.prop_menu_enum(ark, "keymaps", text="Keymaps")
                                layout.prop(ark, "value_type", text="")
                            with layout.split(0.7, True):
                                with layout.row(True):
                                    not_any = not ark.any
                                    layout.prop(ark, "any", toggle=True)
                                    layout.row(True)(active=not_any).prop(ark, "shift", toggle=True)
                                    layout.row(True)(active=not_any).prop(ark, "ctrl", toggle=True)
                                    layout.row(True)(active=not_any).prop(ark, "alt", toggle=True)
                                    layout.row(True)(active=not_any).prop(ark, "oskey", toggle=True)
                                layout.prop(ark, "key_modifier", text="")
                        layout.operator("wm.mouselook_navigation_autoreg_keymap_remove", text="", icon='X').index = i
                    with layout.row():
                        layout.prop(ark, "insert_after", text="")
                        layout.label(icon='ARROW_LEFTRIGHT')
                        layout.prop(ark, "insert_before", text="")
        
        with layout.box():
            if use_universal_input_settings:
                inp_set = self.universal_input_settings
            else:
                autoreg_keymap_id = min(self.autoreg_keymap_id, len(self.autoreg_keymaps)-1)
                inp_set = self.autoreg_keymaps[autoreg_keymap_id].input_settings
            inp_set.draw(layout)

def register():
    addon.register()
    addon.use_zbuffer = addon.preferences.use_zbuffer
    
    addon.draw_handler_add(bpy.types.SpaceView3D, draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')
    
    PresetManager.load()
    
    if (not KeyMapUtils.exists(MouselookNavigation.bl_idname)):
        # Strange bug:
        # If there was no interaction with 3D view since Blender was launched,
        # then addon reloading (F8) will cause blender to crash, if the next line
        # is not commented. If there WAS some interaction with 3D view,
        # then addon reloading would work fine.
        update_keymaps(True)

def unregister():
    update_keymaps(False)
    
    addon.unregister()

if __name__ == "__main__":
    register()
