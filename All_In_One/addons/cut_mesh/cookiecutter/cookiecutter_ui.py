'''
Copyright (C) 2018 CG Cookie

https://github.com/CGCookie/retopoflow

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import math

import bpy
import bgl

from ..common.decorators import blender_version_wrapper
from ..common.debug import debugger
from ..common.drawing import Drawing
from ..common.ui import UI_WindowManager


@blender_version_wrapper('<','2.80')
def set_object_selection(o, sel):
    o.select = sel
@blender_version_wrapper('>=','2.80')
def set_object_selection(o, sel):
    o.select_set('SELECT' if sel else 'DESELECT')

@blender_version_wrapper('<','2.80')
def set_active_object(o):
    bpy.context.scene.objects.active = o
@blender_version_wrapper('>=','2.80')
def set_active_object(o):
    print('unhandled: set_active_object')
    pass

@blender_version_wrapper('<','2.80')
def get_active_object():
    return bpy.context.scene.objects.active
@blender_version_wrapper('>=','2.80')
def get_active_object():
    return bpy.context.active_object


class CookieCutter_UI:
    class Draw:
        def __init__(self, mode):
            assert mode in {'pre3d','post3d','post2d'}
            self.mode = mode
        def __call__(self, fn):
            self.fn = fn
            self.fnname = fn.__name__
            def run(*args, **kwargs):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    print('Caught exception in drawing "%s", calling "%s"' % (self.mode, self.fnname))
                    debugger.print_exception()
                    print(e)
                    return None
            run.fnname = self.fnname
            run.drawmode = self.mode
            return run

    def ui_init(self):
        # self.context = context
        # self.window = self.context.window
        # self.screen = self.context.screen
        # self.area = self.context.area
        # self.space = self.area.spaces[0]
        # self.region_3d = self.space.region_3d
        self._area = self.context.area
        self._space = self.context.space_data
        self._window = self.context.window
        self._screen = self.context.screen
        self.wm = UI_WindowManager()
        self.drawing = Drawing.get_instance()
        fns = {'pre3d':[], 'post3d':[], 'post2d':[]}
        for m,fn in self.find_fns('drawmode'): fns[m].append(fn)
        def draw(fns):
            for fn in fns: fn(self)
        self._draw_pre3d = lambda:draw(fns['pre3d'])
        self._draw_post3d = lambda:draw(fns['post3d'])
        self._draw_post2d = lambda:draw(fns['post2d'])
        self._area.tag_redraw()
        self.window_state_store()

    def ui_start(self):
        def preview():
            self._draw_pre3d()
        def postview():
            self._draw_post3d()
        def postpixel():
            bgl.glEnable(bgl.GL_MULTISAMPLE)
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glEnable(bgl.GL_POINT_SMOOTH)

            self._draw_post2d()

            try:
                self.wm.draw_postpixel(self.context)
            except Exception as e:
                print('Caught exception while trying to draw window UI')
                debugger.print_exception()
                print(e)

        self._handle_preview = self._space.draw_handler_add(preview, tuple(), 'WINDOW', 'PRE_VIEW')
        self._handle_postview = self._space.draw_handler_add(postview, tuple(), 'WINDOW', 'POST_VIEW')
        self._handle_postpixel = self._space.draw_handler_add(postpixel, tuple(), 'WINDOW', 'POST_PIXEL')
        self._area.tag_redraw()

    def ui_update(self):
        self._area.tag_redraw()
        ret = self.wm.modal(self.context, self.event)
        if self.wm.has_focus(): return True
        if ret and 'hover' in ret: return True
        return False

    def ui_end(self):
        self._space.draw_handler_remove(self._handle_preview, 'WINDOW')
        self._space.draw_handler_remove(self._handle_postview, 'WINDOW')
        self._space.draw_handler_remove(self._handle_postpixel, 'WINDOW')
        self._area.tag_redraw()
        self.window_state_restore()

    ####################################################################
    # common Blender UI functions

    def header_text_set(self, s=None):
        if s is None:
            self.context.area.header_text_set()
        else:
            self.context.area.header_text_set(s)

    def cursor_modal_set(self, v):
        self.context.window.cursor_modal_set(v)

    def cursor_modal_restore(self):
        self.context.window.cursor_modal_restore()

    ####################################################################

    def window_state_store(self):
        data = {}
        # 'region overlap': False,    # TODO
        # 'region toolshelf': False,  # TODO
        # 'region properties': False, # TODO

        # remember current mode and set to object mode so we can control
        # how the target mesh is rendered and so we can push new data
        # into target mesh
        data['mode'] = bpy.context.mode
        data['mode translated'] = {
            'OBJECT':        'OBJECT',          # for some reason, we must
            'EDIT_MESH':     'EDIT',            # translate bpy.context.mode
            'SCULPT':        'SCULPT',          # to something that
            'PAINT_VERTEX':  'VERTEX_PAINT',    # bpy.ops.object.mode_set()
            'PAINT_WEIGHT':  'WEIGHT_PAINT',    # accepts...
            'PAINT_TEXTURE': 'TEXTURE_PAINT',
            }[bpy.context.mode]                 # WHY DO YOU DO THIS, BLENDER!?!?!?

        active = get_active_object()
        data['active object'] = active.name if active else None

        data['screen name'] = bpy.context.screen.name

        data['data_wm'] = {}
        for wm in bpy.data.window_managers:
            data_wm = []
            for win in wm.windows:
                data_win = []
                for area in win.screen.areas:
                    data_area = []
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            data_space = {}
                            if space.type == 'VIEW_3D':
                                print(space.show_manipulator)
                                data_space = {
                                    'show_only_render': space.show_only_render,
                                    'show_manipulator': space.show_manipulator,
                                }
                            data_area.append(data_space)
                    data_win.append(data_area)
                data_wm.append(data_win)
            data['data_wm'][wm.name] = data_wm

        # assuming RF is invoked from 3D View context
        rgn_toolshelf = bpy.context.area.regions[1]
        rgn_properties = bpy.context.area.regions[3]
        data['show_toolshelf'] = rgn_toolshelf.width > 1
        data['show_properties'] = rgn_properties.width > 1
        data['region_overlap'] = bpy.context.user_preferences.system.use_region_overlap

        data['selected objects'] = [o.name for o in bpy.data.objects if getattr(o, 'select', False)]
        data['hidden objects'] = [o.name for o in bpy.data.objects if getattr(o, 'hide', False)]

        data['render engine'] = bpy.context.scene.render.engine
        data['viewport_shade'] = bpy.context.space_data.viewport_shade
        data['show_textured_solid'] = bpy.context.space_data.show_textured_solid

        self.window_state = data
        #filepath = options.temp_filepath('state')
        #open(filepath, 'wt').write(json.dumps(data))


    def window_state_restore(self, ignore_panels=False):
        data = self.window_state
        #filepath = options.temp_filepath('state')
        #if not os.path.exists(filepath): return
        #data = json.loads(open(filepath, 'rt').read())

        bpy.context.window.screen = bpy.data.screens[data['screen name']]

        for wm in bpy.data.window_managers:
            data_wm = data['data_wm'][wm.name]
            for win,data_win in zip(wm.windows, data_wm):
                for area,data_area in zip(win.screen.areas, data_win):
                    if area.type != 'VIEW_3D': continue
                    for space,data_space in zip(area.spaces, data_area):
                        if space.type != 'VIEW_3D': continue
                        print(space.show_manipulator, data_space['show_manipulator'])
                        space.show_only_render = data_space['show_only_render']
                        space.show_manipulator = data_space['show_manipulator']

        if data['region_overlap'] and not ignore_panels:
            try:
                # TODO: CONTEXT IS INCORRECT when maximize_area was True????
                ctx = { 'area': self._area, 'space_data': self._space, 'window': self._window, 'screen': self._screen }
                rgn_toolshelf = bpy.context.area.regions[1]
                rgn_properties = bpy.context.area.regions[3]
                if data['show_toolshelf'] and rgn_toolshelf.width <= 1: bpy.ops.view3d.toolshelf(ctx)
                if data['show_properties'] and rgn_properties.width <= 1: bpy.ops.view3d.properties(ctx)
            except Exception as e:
                print(str(e))
                pass
                #self.ui_toggle_maximize_area(use_hide_panels=False)

        Drawing.set_cursor('DEFAULT')

        for o in bpy.data.objects:
            if hasattr(o, 'hide'):
                o.hide = o.name in data['hidden objects']
            if o.name == data['active object']:
                set_object_selection(o, True)
                set_active_object(o)
            if hasattr(o, 'select'):
                set_object_selection(o, o.name in data['selected objects'])

        bpy.ops.object.mode_set(mode=data['mode translated'])

        bpy.context.scene.render.engine = data['render engine']
        bpy.context.space_data.viewport_shade = data['viewport_shade']
        bpy.context.space_data.show_textured_solid = data['show_textured_solid']

    def window_state_overwrite(self, show_only_render=True, hide_manipulator=True):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # overwrite space info by hiding all non-renderable items
        for wm in bpy.data.window_managers:
            for win in wm.windows:
                for area in win.screen.areas:
                    if area.type != 'VIEW_3D': continue
                    for space in area.spaces:
                        if space.type != 'VIEW_3D': continue
                        if show_only_render:
                            space.show_only_render = True
                        if hide_manipulator:
                            space.show_manipulator = False

        # hide tool shelf and properties panel if region overlap is enabled
        rgn_overlap = bpy.context.user_preferences.system.use_region_overlap
        if rgn_overlap and bpy.context.area:
            show_toolshelf = bpy.context.area.regions[1].width > 1
            show_properties = bpy.context.area.regions[3].width > 1
            if show_toolshelf: bpy.ops.view3d.toolshelf()
            if show_properties: bpy.ops.view3d.properties()



