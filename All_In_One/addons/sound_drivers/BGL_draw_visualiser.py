bl_info = {
    "name": "BGL Visualiser",
    "author": "batFINGER",
    "location": "View3D  Graph Editor  TimeLine",
    "description": "Draw visual representation of sound bakes using BGL",
    "warning": "Still in Testing",
    "wiki_url": "",
    "version": (1, 0),
    "blender": (2, 7, 7),
    "tracker_url": "",
    "icon": 'NONE',
    "support": 'TESTING',
    "category": "Animation",
    }

import bpy
import blf
import bgl
from bgl import *  # TODO fix this laziness
from mathutils import Vector
from bpy.props import (BoolProperty,
                       IntProperty,
                       FloatProperty,
                       IntVectorProperty,
                       StringProperty,
                       FloatVectorProperty,
                       CollectionProperty,
                       PointerProperty)

from sound_drivers.utils import getAction, getSpeaker, interp
from bpy.types import Panel, Operator, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy_extras.view3d_utils import location_3d_to_region_2d

from sound_drivers import debug
from sound_drivers.screen_panels import ScreenLayoutPanel
from math import pi, sin, cos
#from numpy import interp

def draw_sound_widgets(context, wlist):
    speaker = context.scene.speaker
    action = getAction(speaker)
    # action = context.area.sound_action # NEW IDEA REFACTO

    for w in wlist:
        w.draw_action_header_text(speaker, action)

class SupportedAreas():
    screen_areas = ['VIEW_3D', 'NLA_EDITOR', 'GRAPH_EDITOR', 'SEQUENCE_EDITOR', 'TIMELINE']
    pass

class BGLWidget(SupportedAreas):

    def __init__(self, op, context, areatype):
        # Calculate scroller width, dpi and pixelsize dependent
        self.pixel_size = context.user_preferences.system.pixel_size
        self.dpi = context.user_preferences.system.dpi
        self.dpi_fac = self.pixel_size * self.dpi / 72
        # A normal widget unit is 20, but the scroller is apparently 16
        self.scroller_width = 16 * self.dpi_fac
        self.region = context.area.regions[-1]
        self.context = context

        self.op = op
        self.areatype = areatype
        speaker = context.scene.speaker
        a = getAction(speaker)
        # a = context.area.sound_action # NEW IDEA REFACTO
        self.handle = self.create_handle(context)
        theme = context.user_preferences.themes[0]
        self.gridcol = [getattr(theme.view_3d.grid, c) for c in 'rgb']
        self.gridcol.append(1.0)
        self.curfc = [getattr(theme.timeline.frame_current, c) for c in 'rgb']
        self.curfc.append(1.0)
        self.theme = theme

    handle = None

    def view3d_find(self, context):
        # returns first 3d view, normally we get from context
        area = context.area
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            for region in area.regions:
                if region.type == 'WINDOW':
                    return self.get_rv3d(context, region)
        return None, None

    def get_rv3d(self, context, region):
        if not context.space_data.region_quadviews:
            return region, context.space_data.region_3d
        else:
            i = -1
            for r in context.area.regions:
                if r.type == 'WINDOW':
                    i += 1
                    if context.region.id == r.id:
                        break

            return r, context.space_data.region_quadviews[i]

    def area_settings(self, context):
        screen = context.screen
        # s = ScreenAreaAction(screen) # REFACTO
        s = context.sound_vis_areas
        area = context.area
        bgl_area = s.get_area(area)
        if bgl_area is None:
            return None
        return getattr(bgl_area, area.type)

    def screen_area_action(self, context):
        screen = context.screen
        # s = ScreenAreaAction(screen) # REFACTO
        s = context.sound_vis_areas
        area = s.get_area_action_details(area)

    def update(self, context):
        '''
        get the details of the region
        '''
        region = context.area.regions[-1]
        w, h = region.width, region.height

        v2 = Vector(region.view2d.region_to_view(w, h))
        v1 = Vector(region.view2d.region_to_view(0, 0))

        v3 = v2 - v1

        self.frame_width = w / v3.x
        self.channel_height = h / v3.y

        self.region_frame_range = Vector((v1.x, v2.x))
        self.region_channel_range = Vector((v1.y, v2.y))

    def draw_region(self, context):
        # check validity
        settings = context.sound_vis_areas.context
        if not getattr(settings, "is_enabled", False):
            return None
        if not getattr(context.window_manager, "bgl_draw_speaker", False):
            self.remove_handle()
            return None

        self.visualise(context)

    def create_handle(self, context):

        # add a handle based on AREA type
        if False:
            print("HOO HA")
        else:
            handle = self.areatype.draw_handler_add(
                self.draw_region,
                (context,),
                'WINDOW',
                'POST_PIXEL')

        return handle

    def remove_handle(self):
        if self.handle:
            self.areatype.draw_handler_remove(self.handle, 'WINDOW')
            self.handle = None

    def draw_action_header_text(self, x, y, speaker, action, margin=4):
        bgl.glPushAttrib(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_ENABLE_BIT)
        font_id = 0
        x = x + margin
        y = y + margin
        # bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        blf.size(font_id, 16, 64)
        blf.position(font_id, x, y, 0.0)
        baking = ""
        if bpy.types.BakeSoundPanel.baking:
            baking = "(BAKING....)"

        s = "[%s] %s %s" % (action["channel_name"], action.name, baking)
        blf.draw(font_id, s)
        blf.size(font_id, 20, 36)
        blf.position(font_id, x + 10 * len(s), y, 0.0)
        blf.draw(font_id, action["wavfile"])
        bgl.glPopAttrib()
        # self.bgl_defaults()

    def draw_bar(self, x, y, amplitude, lw=2.0, color=(0.0, 0.0, 0.0, 0.5)):
        bgl.glEnable(bgl.GL_BLEND)
        #bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
        bgl.glColor4f(*color)

        bgl.glLineWidth(lw)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(x, y)
        bgl.glVertex2f(x, y + amplitude)
        bgl.glEnd()

    def draw_image(self, image, x, y, w, h, color=(0, 0, 0, 0.1)):
        bgl.glColor4f(0.5, 0.0, 0.5, 0.7)

        # draw main line and handles
        # bgl.glBegin(bgl.GL_LINES)
        bgl.glRectf(x, y, x+w, y+h)
        # bgl.glEnd()
        x1 = x
        y1 = y
        x2 = x + w
        y2 = y + h
        color = [0.5, 0.5, 0.5, 1]

        idx = image.gl_load(bgl.GL_NEAREST, bgl.GL_NEAREST)
        print([i for i in image.bindcode])

        bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode[0])
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
        bgl.glEnable(bgl.GL_TEXTURE_2D)
        bgl.glEnable(bgl.GL_BLEND)
        #bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
        bgl.glColor4f(color[0], color[1], color[2], color[3])
        bgl.glBegin(bgl.GL_QUADS)
        bgl.glTexCoord2f(0, 0)
        bgl.glVertex2f(x1, y1)
        bgl.glTexCoord2f(0, 1)
        bgl.glVertex2f(x1, y2)
        bgl.glTexCoord2f(1, 1)
        bgl.glVertex2f(x2, y2)
        bgl.glTexCoord2f(1, 0)
        bgl.glVertex2f(x2, y1)
        bgl.glEnd()
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glDisable(bgl.GL_TEXTURE_2D)

    def draw_box(self, x, y, w, h, color=(0.0, 0.0, 0.0, 1.0)):
        #bgl.glDepthRange (0.1, 1.0)
        bgl.glColor4f(*color)
        bgl.glBegin(bgl.GL_QUADS)

        bgl.glVertex2f(x+w, y+h)
        bgl.glVertex2f(x, y+h)
        bgl.glVertex2f(x, y)
        bgl.glVertex2f(x+w, y)
        bgl.glEnd()

    def point3d_point2d(self, context, pt):
        region, r3dv = self.view3d_find(context)
        if region is not None:
            pt = location_3d_to_region_2d(region, rv3d, pt)
        return pt

    def points3d_points2d(self, context, points):
        '''
        convert 3d points to 2d region pts and draw
        '''
        pts = []
        region, rv3d = self.view3d_find(context)
        if region is not None:
            pts = [location_3d_to_region_2d(region, rv3d, p) for p in points]

        return pts

    def draw_points(self, points, lw=2.0, color=None):
        glLineWidth(lw)
        if color is not None:
            bgl.glColor4f(*color)

        glBegin(GL_LINE_STRIP)

        for f, v in points:
            glVertex2f(f, v)

        glEnd()

    def draw_circle(self, x, y, r, tris=20, color=(0, 0, 0, 0)):
        x, y, r = float(x), float(y), float(r)
        bgl.glColor4f(*color)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)  # // center of circle
        for i in range(tris + 1):
            a = 2 * i * pi / tris
            glVertex2f(x + r * cos(a), y + r * sin(a))
        glEnd()

    def bgl_defaults(self):
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    def draw_midi_keyboard(self, mx, my, w, h, action=None, frame=0):
        '''
        Intented to create a keyboard where key widths are
        accurately in position.

        See http://www.mathpages.com/home/kmath043.htm
        for the math.

        This keyboard has following properties (x=octave width).
        1. All white keys have equal width in front (W=x/7).
        2. All black keys have equal width (B=x/12).
        3. The narrow part of white keys C, D and E is W - B*2/3
        4. The narrow part of white keys F, G, A, and B is W - B*3/4
        '''
        bgl.glEnable(bgl.GL_BLEND)
        octaves = 7
        octave_width = (w - 20) / octaves
        wkw = octave_width / 7
        bkw = octave_width / 12
        cde = wkw - 2 * bkw / 3
        fgab = wkw - 3 * bkw / 4
        wkh = h
        bkh = 0.60 * h

        by = my + wkh - bkh
        x = mx
        y = my
        white = (1.0, 1.0, 1.0, 1.0)
        black = (0.0, 0.0, 0.0, 1.0)
        # draw the white keys
        fc_color = True
        whitenotes = [0, 2, 4, 5, 7, 9, 11]
        blacknotes_1 = [1, 3]
        blacknotes_2 = [6, 8, 10]
        for octave in range(octaves):

            for i in range(7):
                col = white
                if action:
                    #print("XXXXXXXX", '%d"]' % (octave * 12 + whitenotes[i]))
                    fcurves = [fc for fc in action.fcurves if (fc.group.select or fc.select) and fc.data_path.endswith('%d"]' % (octave * 12 + whitenotes[i]))]
                    #fc = action.fcurves.find('["%s%d"]' % (action["channel_name"], octave * 12 + whitenotes[i]))
                    for fc in fcurves:
                        if fc.evaluate(frame) > 0:
                            debug.print("BGL", fc.data_path)
                            r, g, b = fc.color if fc_color else (1, 0, 0)
                            col = (r, g, b, 1.0)
                self.draw_box(x, y, wkw, wkh, color=col)
                x += (wkw + 1)
            # draw the black keys
            x = octave * 7 * (wkw + 1) + cde + mx + 1

            for i in range(2):
                col = black
                if action:
                    fc = action.fcurves.find('["%s%d"]' % (action["channel_name"], octave * 12 + blacknotes_1[i]))
                    if fc:
                        if fc.evaluate(frame) > 0:
                            r, g, b = fc.color if fc_color else (1, 0, 0)
                            col = (r, g, b, 1.0)
                self.draw_box(x, by, bkw, bkh, color=col)
                x += cde + bkw + 1
            x += fgab
            for i in range(3):
                col = black
                if action:
                    fc = action.fcurves.find('["%s%d"]' % (action["channel_name"], octave * 12 + blacknotes_2[i]))
                    if fc:
                        if fc.evaluate(frame) > 0:
                            r, g, b = fc.color if fc_color else (1, 0, 0)
                            col = (r, g, b, 1.0)
                self.draw_box(x, by, bkw, bkh, color=col)
                x += fgab + bkw + 1
            x += 1
        # test call works. TODO
        #self.draw_image(bpy.data.images[0], mx, my, w, h)

    def draw_spectrum(self, context, x, y, speaker, action):

        channels = action["Channels"]
        channel_name = action.get("channel_name")

        #bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

        w = 100
        fw = (context.area.regions[-1].width - (x + 20))
        fh = context.area.regions[-1].height - 50
        lw = max(1, fw / channels)

        screen = context.screen  # SCREENSETTINGS
        area_settings = self.area_settings(context)

        AMP = area_settings.height * fh / 100

        bgl.glEnable(bgl.GL_BLEND)
        self.draw_box(x, y + AMP, channels * (lw + 1), 20, color=self.gridcol)
        bgl.glDisable(bgl.GL_BLEND)
        self.draw_action_header_text(x, y+AMP, speaker, action)

        bgl.glEnable(bgl.GL_BLEND)

        action_fcurve_color = [1, 1, 0, 1.0]
        a_col = baked_fcurve_color = [0.230, 0.40, 0.165, 1.0]

        if len(action.fcurves[0].keyframe_points):
            a_col = action_fcurve_color
        elif len(action.fcurves[0].sampled_points):
            a_col = baked_fcurve_color
        a_col[3] = 0.2

        for i in range(channels):
            col = a_col
            ch = "%s%d" % (channel_name, i)
            amp = self.map_to_action(action, speaker[ch], AMP)
            alpha = 0.2
            col[3] = alpha
            self.draw_box(x, y, lw, AMP, color=col)
            if action.fcurves[i].select:
                col = [c for c in action.fcurves[i].color]
                col.append(1.0)
            else:
                col[3] = 0.8  # change to var
            self.draw_box(x, y, lw, amp, color=col)
            x = x + lw + 1
        #(x, y) = getattr(action.bgl_action_draw, context.area.type).loc   # REFACTO

        self.bgl_defaults()

    def action_range(self, action):
        if action.normalise in {'CHANNEL', 'ACTION'}:
            min, max = action.normalise_range
        else:
            min, max = action['min'], action['max']

        return (min, max)

    def map_to_action(self, action, val, amplitude):
        min, max = self.action_range(action)
        range = abs(max - min)
        '''
        To be refactored to numpy interp
        '''
        if range < 0.0001:
            return 0
        return (abs(val - min) / range) * amplitude


class BGL_SoundActionFCurveWidget(BGLWidget):

    def visualise(self, context):
        # Override BGLWidget visualise
        # it's the handle passed to the ScreenArea to draw
        sp = context.scene.speaker
        if sp is None:
            return None
        action = getAction(sp)
        # action = context.area.sound_action # NEW IDEA REFACTO
        if action is None:
            return None

        area_settings = self.area_settings(context)
        if not area_settings:
            return None

        region = context.area.regions[-1]

        self.update(context)

        y = 0
        w = self.frame_width

        x = interp(action.frame_range[0], self.region_frame_range, [0, region.width])
        h = region.height
        #print("XYWH", x,y,w,h)
        frames = action.frame_range.length
        self.draw_sound_action(context, action, x, y, w, h, frames)

    def draw_sound_action(self, context, action, x, y, w, h, frames, color=(1, 1, 1, 1)):
        # from bgl import  #glLineWidth, glBegin, glEnd, glColor4f, glRectf, glEnable, glDisable,glVertex2f, GL_BLEND, GL_LINES
        region = context.region
        #(minf, minh), (maxf, maxh) = region_box
        minf, maxf = self.region_frame_range
        minh, maxh = self.region_channel_range
        a = action
        range = self.action_range(a)

        channel_range = [y + c * h for c in [0.2, 0.8]]
        frame_range = [x, x + frames * w]

        fcurves = [fc for fc in action.fcurves if fc.select]
        for fcurve in fcurves:

            # Strip coords

            cf_x = context.scene.frame_current_final

            #r, g, b, a = color
            col = [c for c in fcurve.color]
            col.append(1.0)

            glColor4f(*color)

            coll = fcurve.keyframe_points if len(fcurve.keyframe_points) else fcurve.sampled_points

            pts = [p for p in coll if minf <= p.co.x <= maxf]
            #pts = fcurve.sampled_points

            points = [(interp(p.co.x, a.frame_range, frame_range),
                        interp(fcurve.evaluate(p.co.x), range, channel_range)) for p in pts if p.co.x < cf_x]

            self.draw_points(points)

            current_frame_loc = interp(cf_x, a.frame_range, frame_range)
            current_channel_loc = interp(fcurve.evaluate(cf_x), range, channel_range)

            self.draw_circle(current_frame_loc, current_channel_loc, 12, color=self.curfc)
            self.draw_circle(current_frame_loc, current_channel_loc, 8, color=(0, 0, 0, 0))
            self.draw_circle(current_frame_loc, current_channel_loc, 3, tris=6, color=col)

            points = [(interp(p.co.x, a.frame_range, frame_range),
                        interp(fcurve.evaluate(p.co.x), range, channel_range)) for p in pts if p.co.x > cf_x]

            self.draw_points(points, lw=1.0)

        glDisable(GL_BLEND)


class BGL_SoundStripWidget(BGL_SoundActionFCurveWidget):

    def visualise(self, context):
        '''
        Override BGLWidget visualise
        it's the handle passed to the ScreenArea to draw
        '''
        sp = context.scene.speaker
        if sp is None:
            return None
        action = getAction(sp)
        # action = context.area.sound_action # NEW IDEA REFACTO
        if action is None:
            return None
        area_settings = self.area_settings(context)
        if not area_settings:
            debug.print("No Area Settings")
            return None
        self.draw_strips(action, context)

    def draw_strips(self, action, context):

        if not context.scene.sequence_editor:
            return

        curx = 1
        region = context.area.regions[-1]
        self.update(context)
        w = self.frame_width

        h = self.channel_height

        for strip in context.scene.sequence_editor.sequences:
            if strip.type == 'SOUND':

                # Get corners (x1, y1), (x2, y2) of the strip rectangle in px region coords
                x, y = self.get_strip_rectf(region, strip)

                '''
                #check if any of the coordinates are out of bounds
                if strip_coords[0] > xwin2 or strip_coords[2] < xwin1 or strip_coords[1] > ywin2 or strip_coords[3] < ywin1:
                    continue

                '''
                # Draw

                color = [1.0, 1.0, 1.0, 0.3]
                frames = strip.frame_final_duration
                region_box = (0, 0), (100, 100)
                self.draw_sound_action(context, action, x, y, w, h, frames)

    def get_strip_rectf(self, region, strip):
         # Get x and y in terms of the grid's frames and channels

        x, y = region.view2d.view_to_region(strip.frame_final_start, strip.channel, clip=False)

        return (x, y)

class BGL_SoundActionWidget(BGLWidget):

    def visualise(self, context):
        area = context.area
        speaker = context.scene.speaker
        action = getAction(speaker)
        scene = context.scene
        frame = scene.frame_current
        '''
        print("MHHM")
        action = context.screen.sound_driver_areas["VIEW_3D_4"].action
        print("THIS WORKING", action)
        #action = context.area.sound_action # NEW IDEA REFACTO
        '''
        if action is None:
            return None

        area_settings = self.area_settings(context)
        if area_settings is None:
            return None
        (x, y) = area_settings.loc
        fw = (context.area.regions[-1].width - (x + 20))
        fh = context.area.regions[-1].height - 50
        area_settings = self.area_settings(context)

        AMP = area_settings.height * fh / 100
        if action.get("MIDI"):

            bgl.glEnable(bgl.GL_BLEND)
            self.draw_box(x, y + AMP, 3 * fw, 20, color=self.gridcol)
            bgl.glDisable(bgl.GL_BLEND)
            self.draw_action_header_text(x, y+AMP, speaker, action)
            self.draw_midi_keyboard(x, y, fw, AMP, action=action, frame=frame)
        else:
            self.draw_spectrum(context, x, y, speaker, action)

class SD_NLATrackListWidget(BGL_SoundActionWidget):

    def visualise(self, context):
        area = context.area
        speaker = context.scene.speaker

        area_settings = self.area_settings(context)

        if area_settings is None:
            return None

        region = area.regions[-1]
        (x, y) = area_settings.loc
        x += 0.5 * region.width
        fw = 0.5 * (area.regions[-1].width - (x + 20))
        area_settings = self.area_settings(context)
        tracks = [t for t in speaker.animation_data.nla_tracks]

        fh = (area.regions[-1].height - 50) / 4  # len(tracks)

        for track in tracks:

            for strip in track.strips:
                if strip.select:
                    a = strip.action
                    self.draw_spectrum(context, x, y, speaker, a)
                    #y += fh
                    x += 3

                    y += 3


class SelectScreenAreaOperator(SupportedAreas, Operator):
    """Display Sound Action in View"""
    bl_idname = "sounddrivers.select_area"
    bl_label = "Display SoundAction"
    type = StringProperty(options={'SKIP_SAVE'})
    area_index = IntProperty(default=-1, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        screen_areas = self.screen_areas
        if len(self.type):
            screen_areas = [self.type]
        if self.area_index > -1:
            area = context.screen.areas[self.area_index]
            # s = ScreenAreaAction(context.screen) # REFACTO
            s = context.sound_vis_areas
            s.set_action_to_area(area, None)
            # toggle through the supported areas
            if area.type in screen_areas:
                i = screen_areas.index(area.type)

            if i >= len(screen_areas):
                i = 0

            area.type = self.screen_areas[i]
            return {'FINISHED'}
        return {'CANCELLED'}

class ScreenActionOperator(Operator):
    """Display Sound Action in View"""
    bl_idname = "sounddrivers.view_action"
    bl_label = "Display SoundAction"
    action = StringProperty(options={'SKIP_SAVE'})
    area_index = IntProperty(default=-1, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        action = bpy.data.actions.get(self.action)
        if action is None:
            action = getAction(context.scene.speaker)
        if self.area_index > -1:
            area = context.screen.areas[self.area_index]
            # s = ScreenAreaAction(context.screen) # REFACTO
            s = context.sound_vis_areas
            s.set_action_to_area(area, action)
            area.type = 'VIEW_3D'
            return {'FINISHED'}

        return {'FINISHED'}


class BGLDrawSpeaker(Operator):
    """Draw the Context Speaker Action"""
    bl_idname = "wm.draw_speaker_vis"
    bl_label = "BGL DRAW SPEAKER"

    timer = None
    handle = None
    callbacks = []

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not context.scene.bgl_draw_speaker:

                return self.cancel(context)

            # change theme color, silly!
            pass

        return {'PASS_THROUGH'}

    def execute(self, context):
        self.callbacks.append(BGL_SoundActionWidget(self, context, bpy.types.SpaceView3D))
        self.callbacks.append(BGL_SoundActionWidget(self, context, bpy.types.SpaceGraphEditor))
        self.callbacks.append(SD_NLATrackListWidget(self, context, bpy.types.SpaceNLA))
        self.callbacks.append(BGL_SoundStripWidget(self, context, bpy.types.SpaceSequenceEditor))
        self.callbacks.append(BGL_SoundActionFCurveWidget(self, context, bpy.types.SpaceTimeline))

        return {'FINISHED'}

    def cancel(self, context):
        wm = context.window_manager

        for cb in self.callbacks:
            cb.remove_handle()
            del(cb)

        wm.event_timer_remove(self.timer)
        self.callbacks.clear()

        for area in context.screen.areas:
            area.tag_redraw()
        return {'CANCELLED'}


class BGL_Draw_VisualiserPanel(SupportedAreas, ScreenLayoutPanel, Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_label = "BGL Visualiser"

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)
        screen_areas = [a.type for a in context.screen.areas if a.type in cls.screen_areas]
        return speaker is not None and len(screen_areas) and 'VISUAL' in speaker.vismode

    def draw_header(self, context):
        layout = self.layout
        dm = context.driver_manager
        scene = context.scene
        wm = context.window_manager
        layout.prop(wm, "bgl_draw_speaker", text="")

    def draw_area_operator(self, context, layout, index):

        op = layout.operator("sounddrivers.select_area", text="BGL")
        layout.enabled = context.screen.areas[index].type in self.screen_areas
        op.area_index = index

    def draw(self, context):
        layout = self.layout
        self.draw_area_buttons(context)
        return
        dm = context.driver_manager
        # s = ScreenAreaAction(context.screen) # REFACTO
        s = context.sound_vis_areas
        for i, a in enumerate(context.screen.areas):
            if a.type in self.screen_areas:
                row = layout.row()
                row.label(str(i))
                row.label(a.type)

                op = row.operator("sounddrivers.view_action")
                op.area_index = i
                area = s.get_area(a)
                if area is not None:
                    row = layout.row()
                    row.label(str(area.action))
                    x = getattr(area, a.type)
                    if x is not None:
                        row = layout.row()
                        row.prop(x, "height")
        '''
        speaker = getSpeaker(context)
        action = getAction(speaker)
        #action = context.area.sound_action # NEW IDEA REFACTO
        if action is None:
            return None
        screen_areas = [a.type for a in context.screen.areas]
        for t in self.screen_areas:
            if t not in screen_areas:
                continue
            action_bgl = getattr(action.bgl_action_draw, t, None)
            if action_bgl is None:
                debug.print("No action.bgl_action_draw for ", t)
                continue
            row = layout.row()
            text = bpy.types.Space.bl_rna.properties['type'].enum_items[t].name
            row.prop(action.bgl_action_draw, "use_%s" % t, text=text)
            box = layout.box()
            box.prop(action_bgl, "loc")
            box.prop(action_bgl, "color")
            box.prop(action_bgl, "height")
        '''

class SoundVisAreaPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "SoundVis"
    bl_category = "SoundVIS"

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        sva = context.sound_vis_areas.context
        return wm.bgl_draw_speaker and sva is not None

    def draw_header(self, context):
        layout = self.layout
        sva = context.sound_vis_areas.context
        layout.prop(sva, "is_enabled", text="")

    def draw(self, context):
        screen = context.screen
        sva = context.sound_vis_areas.context
        layout = self.layout
        layout.prop(sva, "loc")
        layout.prop(sva, "height")

class ScreenAreaAction():

    def __init__(self, context):
        self.screen = context.screen
        #self.context = self.get_area(context.area)
        if getattr(context, "area", None):
            self.context = getattr(self.get_area(context.area), context.area.type, None)
        else:
            self.context = None

    def create_area(self, key, index, area):
        a = self.screen.sound_driver_areas.add()
        a.name = key
        a.type = area.type
        a.index = index
        return a

    def key(self, area):
        areas = [a for a in self.screen.areas]
        index = areas.index(area)
        key = "%s_%d" % (area.type, index)
        return index, key

    def get_area(self, area):
        if area is None:
            return None
        if not hasattr(self.screen, "sound_driver_areas"):
            return None
        # look up
        index, key = self.key(area)
        return self.screen.sound_driver_areas.get(key)

    def set_action_to_area(self, area, action):
        if area is None:
            return None

        index, key = self.key(area)
        store = self.screen.sound_driver_areas.get(key)
        if store is None:
            store = self.create_area(key, index, area)
        if action is None:
            return

        store.action_name = action.name
        store.action_channel_name = action.get("channel_name", "")

def get_action(self):
    if self.use_active_action:
        return getAction(bpy.context.scene.speaker)
    else:
        return bpy.data.actions.get(self.action_name)

def set_action(self, action):
    if action is not None:
        self.action_name = action.name
    else:
        self.action_name = ""

def start(self, context):
    if hasattr(bpy.types, "SoundActionViewBGL"):
        pass
    if self.bgl_draw_speaker:
        bpy.ops.wm.draw_speaker_vis()
    else:
        scene = context.scene
        for area in context.screen.areas:
            area.tag_redraw()
            for region in area.regions:
                region.tag_redraw()

def update_graph(self, context):
    #print("UPDG", self.height)
    if context.area.type == 'PROPERTIES':
        bpy.ops.graph.view_all_with_bgl_graph()
    return None

def reg_screen_action_bgl():
    def index(self):
        sp = self.name.split("_")
        return int(sp[-1])

    def area(self):
        return self.id_data.areas[self.area_index]

    prop_dic = {"loc": IntVectorProperty(size=2, default=(0, 24), min=0),
                "color": FloatVectorProperty(subtype='COLOR_GAMMA', size=4),
                "height": IntProperty(default=20, min=10, max=100, step=1, subtype='PERCENTAGE', description="Height (Percent of View)", update=update_graph),
                "use_fcurve_colors": BoolProperty(default=True),
                "is_enabled": BoolProperty(default=True, description="Enable SoundVis for this Area"),
                }

    action_bgl_props = type("ActionBGL", (PropertyGroup,), prop_dic)
    register_class(action_bgl_props)
    #sa = SupportedAreas()

    propdic = {"area_index": property(index),
               "area": property(area),
               "area_type": StringProperty(default='VIEW3D'),  # change to ENUM
               "action_name": StringProperty(default=""),
               "use_active_action": BoolProperty(default=True),
               "channel_name": StringProperty(),
               "action": property(get_action, set_action),
               "VIEW_3D": PointerProperty(type=action_bgl_props),
               "GRAPH_EDITOR": PointerProperty(type=action_bgl_props),
               "NLA_EDITOR": PointerProperty(type=action_bgl_props),
               "SEQUENCE_EDITOR": PointerProperty(type=action_bgl_props),
               #"CONSOLE": PointerProperty(type=action_bgl_props), # for testing UI
               "TIMELINE": PointerProperty(type=action_bgl_props),
               }

    def get_sda_current(self):
        return ScreenAreaAction(self)

    SD_AreaSettings = type("SD_AreaSettings", (bpy.types.PropertyGroup,), propdic)
    bpy.utils.register_class(SD_AreaSettings)
    bpy.types.Screen.sound_driver_areas = CollectionProperty(type=SD_AreaSettings)
    bpy.types.Context.sound_vis_areas = property(get_sda_current)

settings_panels = []

def register():
    bpy.types.WindowManager.bgl_draw_speaker = BoolProperty(update=start,
                                                             name="Draw Details",
                                                             default=False,
                                                             description="Show BGL Visualiser")
    register_class(BGLDrawSpeaker)
    register_class(BGL_Draw_VisualiserPanel)
    reg_screen_action_bgl()
    register_class(ScreenActionOperator)
    register_class(SelectScreenAreaOperator)

    for t in ['GRAPH_EDITOR', 'VIEW_3D', 'SEQUENCE_EDITOR', 'NLA_EDITOR']:
        propdic = {"bl_space_type": t}
        SettingsPanel = type("SD_SoundVis_PT_%s" % t, (SoundVisAreaPanel,), propdic)
        settings_panels.append(SettingsPanel)
        register_class(SettingsPanel)

def unregister():
    # unregister_module(__name__)
    unregister_class(BGLDrawSpeaker)
    unregister_class(BGL_Draw_VisualiserPanel)
    unregister_class(ScreenActionOperator)
    unregister_class(SelectScreenAreaOperator)
    for t in ['GRAPH_EDITOR', 'VIEW_3D', 'SEQUENCE_EDITOR', 'NLA_EDITOR']:
        SettingsPanel = getattr(bpy.types, "SD_SoundVis_PT_%s" % t, None)
        if SettingsPanel:
            unregister_class(SettingsPanel)
    bpy.context.window_manager.bgl_draw_speaker = False
    # del(bpy.types.WindowManager.bgl_draw_speaker)
