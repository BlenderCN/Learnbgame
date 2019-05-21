# ##### BEGIN GPL LICENSE BLOCK #####
#
#  node_colorramp_dropper.py
#  Drop multiple mouse-picked colors to colorramp node
#  Copyright (C) 2016 Quentin Wenger
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



bl_info = {"name": "Node ColorRamp Dropper",
           "description": "Drop multiple mouse-picked colors to colorramp node",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 2),
           "blender": (2, 75, 0),
           "location": "Node Editor > Properties > ColorRamp Dropper",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "Node"
           }



import bgl
import bpy
import blf

import itertools


# Blender's limit of ColorRamp keys amount
PTS_LIMIT = 32


NO_HANDLE = 0
NEED_REDRAW = 1
TOO_MANY = 2
OK = 3

def sgn(x):
    return 1 if x >= 0 else -1

def ncs(xs):
    # https://en.wikipedia.org/w/index.php?title=Spline_%28mathematics%29
    # &oldid=288288033#Algorithm_for_computing_natural_cubic_splines
    # we use constant 'distances' for the parametrization
    # (unlike
    #  http://www.giref.ulaval.ca/~afortin/mat17442/documents/splines.pdf,
    #  as we then want predefined subintervals)
    n = len(xs)
    as_ = xs
    bs = [None]*(n - 1)
    cs = [None]*n
    ds = [None]*(n - 1)
    ls = [None]*n
    ms = [None]*n
    zs = [None]*n
    hs = [1.0]*(n - 1)
    hit = iter(hs)
    hit2 = iter(hs)
    next(hit2)
    ait = iter(as_)
    ait2 = iter(as_)
    next(ait2)
    ait3 = iter(as_)
    next(ait3)
    next(ait3)
    alpha = [3.0/h2*(a3 - a2) - 3.0/h*(a2 - a)
        for a, a2, a3, h, h2 in zip(ait, ait2, ait3, hit, hit2)]
    ls[0] = 1.0
    ls[n - 1] = 1.0
    ms[0] = 0.0
    zs[0] = 0.0
    zs[n - 1] = 0.0
    cs[n - 1] = 0.0
    for i in range(1, n - 1):
        l = 4.0 - hs[i - 1]*ms[i - 1]
        ls[i] = l
        ms[i] = hs[i]/l
        zs[i] = (alpha[i - 1] - hs[i - 1]*zs[i - 1])/l
    for j in range(n - 2, -1, -1):
        cs[j] = zs[j] - ms[j]*cs[j + 1]
        bs[j] = (
            as_[j + 1] - as_[j])/hs[j] - (hs[j]*(cs[j + 1] + 2.0*cs[j]))/3.0
        ds[j] = (cs[j + 1] - cs[j])/(3.0 * hs[j])
    return as_[:-1], bs, cs[:-1], ds


class DropperWorker(object):
    def __init__(self, initial_context):
        super(DropperWorker, self).__init__()

        self.node_tree = initial_context.space_data.node_tree
        self.node = self.node_tree.nodes.active

        self.initial_area = initial_context.area
        
        self.main_points = []
        self.points = [] # [x, y, region_x, region_y, is_main, rgb]
        self.current_mouse_main_point = []
        self.current_mouse_points = []

        self.handle = None
        self.space = None
        self.area = None
        self.viewport = None

        # we can assume same window manager as later
        wm = initial_context.window_manager

        a = 0.0
        b = 1.0
        if wm.crd_use_interval:
            a = wm.crd_interval_min
            b = wm.crd_interval_max

        if wm.crd_use_active and self.node and self.node.type == 'VALTORGB':
            cr = self.node.color_ramp
            if wm.crd_erase_keys:
                if wm.crd_use_interval:
                    if wm.crd_erase_keys_interval == 'ALL':
                        self.remaining = 0
                    elif wm.crd_erase_keys_interval == 'INTERVAL':
                        self.remaining = 0
                        for key in cr.elements:
                            if key.position < a or b < key.position:
                                self.remaining += 1
                else:
                    self.remaining = 0
            else:
                self.remaining = len(cr.elements)
        else:
            if wm.crd_erase_keys:
                if wm.crd_use_interval:
                    if wm.crd_erase_keys_interval == 'ALL':
                        self.remaining = 0
                    elif wm.crd_erase_keys_interval == 'INTERVAL':
                        # Blender's default: one at 0.0, one at 1.0
                        a = wm.crd_interval_min
                        b = wm.crd_interval_max
                        self.remaining = int(0.0 < a) + int(b < 1.0)
                else:
                    self.remaining = 0
            else:
                # Blender's default: 2 keys
                self.remaining = 2

    @staticmethod
    def convertFromSRGB(value):            
        if value <= 0.04045:
            return value/12.92
        else:
            a = 0.055
            return ((value + a)/(1.0 + a))**2.4

    @staticmethod
    def convertFromRec709(value):
        if value < 0.081:
            return value/4.5
        else:
            a = 0.099
            return ((value + a)/(1.0 + a))**(1.0/0.45)

    @staticmethod
    def convertFromXYZ(color):
        x, y, z = color
        return [
            0.41847*x - 0.15866*y - 0.082835*z,
            -0.91169*x + 0.25243*y + 0.015708*z,
            0.0009209*x - 0.0025498*y + 0.1786*z]

    def convertColorspace(self, context, color):
        # transformations: see Wikipedia
        dev = context.scene.display_settings.display_device
        if dev == "sRGB":
            return list(map(self.convertFromSRGB, color))
        elif dev == "Rec709":
            return list(map(self.convertFromRec709, color))
        elif dev == "XYZ":
            return self.convertFromXYZ(color)
        
        return color

    @staticmethod
    def drawPoint(x, y, main=True):
        r = 6 if main else 3

        bgl.glBegin(bgl.GL_LINES)
        bgl.glColor3f(1.0, 1.0, 1.0)
        bgl.glVertex2i(x - r, y)
        bgl.glVertex2i(x - r, y + r)
        bgl.glVertex2i(x - r, y + r)
        bgl.glVertex2i(x, y + r)
        
        bgl.glVertex2i(x + r, y)
        bgl.glVertex2i(x + r, y - r)
        bgl.glVertex2i(x + r, y - r)
        bgl.glVertex2i(x, y - r)
        
        bgl.glColor3f(0.0, 0.0, 0.0)
        bgl.glVertex2i(x, y + r)
        bgl.glVertex2i(x + r, y + r)
        bgl.glVertex2i(x + r, y + r)
        bgl.glVertex2i(x + r, y)
        
        bgl.glVertex2i(x, y - r)
        bgl.glVertex2i(x - r, y - r)
        bgl.glVertex2i(x - r, y - r)
        bgl.glVertex2i(x - r, y)
        bgl.glEnd()

    @staticmethod
    def drawSegment(x1, y1, x2, y2, future=False, limit=False):
        dx = x2 - x1
        dy = y2 - y1
        if max(abs(dx), abs(dy)) < 20:
            return
        
        if future:
            alpha = 0.2
        else:
            alpha = 0.5

        if abs(dx) >= abs(dy):
            xa = x1 + sgn(dx)*10
            xb = x2 - sgn(dx)*10
            ratio = dy/abs(dx)
            ya = y1 + 10*ratio
            yb = y2 - 10*ratio
        else:
            ya = y1 + sgn(dy)*10
            yb = y2 - sgn(dy)*10
            ratio = dx/abs(dy)
            xa = x1 + 10*ratio
            xb = x2 - 10*ratio
        
        #bgl.glLineWidth(2)
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
        bgl.glEnable(bgl.GL_BLEND)
        
        if limit:
            bgl.glColor4f(1.0, 0.0, 0.0, alpha)
        else:
            bgl.glColor4f(0.0, 0.0, 0.0, alpha)

        bgl.glLineStipple(1, 0x00FF)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(xa, ya)
        bgl.glVertex2f(xb, yb)
        bgl.glEnd()
        
        bgl.glColor4f(1.0, 1.0, 1.0, alpha)

        bgl.glLineStipple(1, 0xFF00)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(xa, ya)
        bgl.glVertex2f(xb, yb)
        bgl.glEnd()

        bgl.glLineStipple(1, 0xFFFF)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        #bgl.glLineWidth(1)
        
    def drawCallback(self, context):
        # use ImageTexture.evaluate / get Image.pixels in case of View2D?

        # seems unnecessary to restore afterwards.
        bgl.glViewport(*self.viewport)
        bgl.glScissor(*self.viewport)

        b = bgl.Buffer(bgl.GL_FLOAT, 3)
        for p in itertools.chain(self.points, self.current_mouse_points):
            bgl.glReadPixels(p[0], p[1], 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, b)
            p[-1] = self.convertColorspace(context, b.to_list())

        points_drawn = 0
        max_points_to_draw = PTS_LIMIT - self.remaining
        last_point_drawn = None
        for p in self.points:
            if points_drawn == max_points_to_draw:
                break
            self.drawPoint(*p[2:5])
            last_point_drawn = p
            points_drawn += 1

        # under cursor -> probably not wanted
        for p in self.current_mouse_points[:-1]:
            if points_drawn == max_points_to_draw:
                break
            self.drawPoint(*p[2:5])
            last_point_drawn = p
            points_drawn += 1

        segments_drawn = 0
        if len(self.points) > 1:
            ps = iter(self.points)
            next(ps)
            for p1, p2 in zip(self.points, ps):
                if segments_drawn == max_points_to_draw - 1:
                    break
                self.drawSegment(p1[2], p1[3], p2[2], p2[3], False)
                segments_drawn += 1

        if self.current_mouse_points:
            p1 = self.points[-1]
            p2 = self.current_mouse_points[0]
            if segments_drawn < max_points_to_draw - 1:
                self.drawSegment(p1[2], p1[3], p2[2], p2[3], True)
                segments_drawn += 1
                if len(self.current_mouse_points) > 1:
                    ps = iter(self.current_mouse_points)
                    next(ps)
                    for p1, p2 in zip(self.current_mouse_points, ps):
                        if segments_drawn == max_points_to_draw - 1:
                            break
                        self.drawSegment(p1[2], p1[3], p2[2], p2[3], True)
                        segments_drawn += 1

        if points_drawn == max_points_to_draw:
            # this means even the point under the cursor _is_ already
            # surnumerary, thus we have to draw the last segment in red
            if self.current_mouse_points:
                p1 = last_point_drawn
                p2 = self.current_mouse_points[-1]
                self.drawSegment(p1[2], p1[3], p2[2], p2[3], True, True)

        if context.window_manager.crd_show_values:
            for p, i in zip(
                itertools.chain(self.points, self.current_mouse_points),
                range(points_drawn)):
                blf.position(0, p[2] + 10, p[3] - 10, 0)
                bgl.glColor4f(0.8, 0.8, 0.8, 1.0)
                blf.size(0, 10, context.user_preferences.system.dpi)
                blf.draw(0, "(%.3f, %.3f, %.3f)" % tuple(p[-1]))
            if points_drawn <= max_points_to_draw:
                # we want to draw the current color anyways
                if self.current_mouse_points:
                    p = self.current_mouse_points[-1]
                    blf.position(0, p[2] + 10, p[3] - 10, 0)
                    bgl.glColor4f(0.8, 0.8, 0.8, 1.0)
                    blf.size(0, 10, context.user_preferences.system.dpi)
                    blf.draw(0, "(%.3f, %.3f, %.3f)" % tuple(p[-1]))
                

        bgl.glColor4f(0.8, 0.8, 0.8, 1.0)
        blf.size(0, 20, context.user_preferences.system.dpi)
        if context.window_manager.crd_use_intermediate:
            blf.position(0, 10, 60, 0)
            blf.draw(0, "Oversamples:")
            blf.position(0, 160, 60, 0)
            blf.draw(0, str(context.window_manager.crd_intermediate_amount))
        blf.position(0, 10, 30, 0)
        blf.draw(0, "Path Type:")
        blf.position(0, 160, 30, 0)
        blf.draw(
            0,
            {'POLYLINE':"Polyline", 'CUBIC_SPLINE':"Cubic Spline"}[
                context.window_manager.crd_path_type])

    def updatePoints(self, context):
        if self.handle is None:
            return
        
        # better reuse of previously created arrays?
        
        self.points = []
        self.current_mouse_points = []

        wm = context.window_manager
        am = wm.crd_intermediate_amount

        if not wm.crd_keep_memory:
            max_pts_to_draw = PTS_LIMIT - self.remaining
            sub = wm.crd_intermediate_amount if wm.crd_use_intermediate else 0
            if len(self.main_points)*(1 + sub) - 1 > max_pts_to_draw:
                self.main_points = self.main_points[
                    :(max_pts_to_draw + 1)//(1 + sub) + 1]

        if self.current_mouse_main_point == self.main_points[-1]:
            main_points = [] + self.main_points # quite hacky...
        else:
            main_points = self.main_points + [self.current_mouse_main_point]

        if len(main_points) == 1:
            self.points = [main_points[0] + [True, None]]        
        elif not wm.crd_use_intermediate or am == 0:
            self.points = [p + [True, None] for p in main_points]
        elif wm.crd_path_type == 'POLYLINE':
            self.points.append(main_points[0] + [True, None])
            pts = iter(main_points)
            next(pts)
            for pt, pt2 in zip(main_points, pts):
                dx = (pt2[0] - pt[0])/(am + 1.0)
                dy = (pt2[1] - pt[1])/(am + 1.0)
                for i in range(1, am + 1):
                    self.points.append([
                        int(pt[0] + dx*i),
                        int(pt[1] + dy*i),
                        int(pt[2] + dx*i),
                        int(pt[3] + dy*i),
                        False, None])
                self.points.append(pt2 + [True, None])
        elif wm.crd_path_type == 'CUBIC_SPLINE':
            self.points.append(main_points[0] + [True, None])
            xs = [p[0] for p in main_points]
            ys = [p[1] for p in main_points]
            asx, bsx, csx, dsx = ncs(xs)
            asy, bsy, csy, dsy = ncs(ys)
            gtrx = main_points[0][2] - main_points[0][0] # global to region
            gtry = main_points[0][3] - main_points[0][1]
            pts = iter(main_points)
            next(pts)
            for ax, bx, cx, dx, ay, by, cy, dy, pt in zip(
                asx, bsx, csx, dsx, asy, bsy, csy, dsy, pts):
                for i in range(1, am + 1):
                    dt = i/(am + 1.0)
                    x = int(ax + bx*dt + cx*dt**2 + dx*dt**3)
                    y = int(ay + by*dt + cy*dt**2 + dy*dt**3)
                    self.points.append([x, y, x + gtrx, y + gtry, False, None])
                self.points.append(pt + [True, None])

        # a bit hacky, but seems like the simplest way
        if self.current_mouse_main_point != self.main_points[-1]:
            if not wm.crd_use_intermediate:
                am = 0
            self.current_mouse_points = self.points[-(am + 1):]
            self.points = self.points[:-(am + 1)]

        self.area.tag_redraw()

    def removeHandle(self, context):
        type(self.space).draw_handler_remove(self.handle, 'WINDOW')
        self.handle = None
        self.area.tag_redraw()

    def updateMousePosition(self, context, event):
        if self.handle is None:
            return

        self.current_mouse_main_point = [
            # hack around spaces and coords...
            event.mouse_x, event.mouse_y,
            event.mouse_x - self.viewport[0], event.mouse_y - self.viewport[1]]
            #event.mouse_region_x, event.mouse_region_y]
        self.updatePoints(context)

    def update(self, context):
        # this ensures the redraw
        self.initial_area.tag_redraw()
        self.updatePoints(context)

    def setScreenElements(self, context, event):
        # context.space_data remains NODE_EDITOR-typed even if the event
        # (e.g. the first left click) was performed on another area
        # thus we hack here and select the relevant area/region/space
        x = event.mouse_x
        y = event.mouse_y
        for area in context.window_manager.windows[0].screen.areas:
            if (
                (area.x <= x <= area.x + area.width) and
                (area.y <= y <= area.y + area.height)):
                self.area = area
                break
        else:
            raise RuntimeError #temp?

        # any other choice?
        self.space = self.area.spaces[0]

        for region in self.area.regions:
            if region.type == 'WINDOW':
                self.viewport = [
                    region.x, region.y, region.width, region.height]
                break
        else:
            raise RuntimeError

    def addPoint(self, context, event):
        if self.handle is None:
            self.setScreenElements(context, event)
            self.handle = type(self.space).draw_handler_add(
                self.drawCallback, (context,), 'WINDOW', 'POST_PIXEL')

        if (context.window_manager.crd_keep_memory or
            (len(self.points) < PTS_LIMIT - self.remaining)):
            self.current_mouse_main_point = [
                event.mouse_x, event.mouse_y,
                event.mouse_x - self.viewport[0],
                event.mouse_y - self.viewport[1]]
                #event.mouse_region_x, event.mouse_region_y]
            self.main_points.append(self.current_mouse_main_point)
            self.updatePoints(context)

    def removePoint(self, context):
        if self.handle is None or not self.main_points:
            return False

        if len(self.main_points) > 1:
            self.main_points.pop()
            self.updatePoints(context)
            return True
        else:
            self.main_points = []
            self.removeHandle(context)
            return False
        
    def finalize(self, context):
        if self.handle is None:
            return NO_HANDLE

        for p in self.points:
            if p[-1] is None:
                return NEED_REDRAW

        wm = context.window_manager
        
        a = 0.0
        b = 1.0
        if wm.crd_use_interval:
            a = wm.crd_interval_min
            b = wm.crd_interval_max
        
        if wm.crd_use_active and self.node and self.node.type == 'VALTORGB':
            cr = self.node.color_ramp
        else:
            if self.node_tree.type == 'COMPOSITING':
                idname = 'CompositorNodeValToRGB'
            elif self.node_tree.type == 'TEXTURE':
                idname = 'TextureNodeValToRGB'
            elif self.node_tree.type == 'SHADER':
                idname = 'ShaderNodeValToRGB'
            nd = self.node_tree.nodes.new(idname)
            self.node_tree.nodes.active = nd
            cr = nd.color_ramp

        pts_to_draw = PTS_LIMIT - self.remaining
        if not pts_to_draw:
            self.removeHandle(context)
            return TOO_MANY

        if self.remaining == 0:
            # we have to avoid removing all elements (forbidden)
            # thus we keep one and transform it into something usable
            while len(cr.elements) > 1:
                cr.elements.remove(cr.elements[0])
            cr.elements[0].position = a
            cr.elements[0].color = self.points[0][-1] + [wm.crd_keys_alpha]
        else:
            if wm.crd_erase_keys:
                # if we get here: interval removal only
                while True:
                    for element in cr.elements:
                        if a <= element.position <= b:
                            cr.elements.remove(element)
                            break
                    else:
                        break
            key = cr.elements.new(a)
            key.color = self.points[0][-1] + [wm.crd_keys_alpha]

        if len(self.points) > 1:
            if wm.crd_use_segments_length:
                ps = iter(self.points)
                next(ps)
                lengths = []
                for p1, p2, _ in zip(self.points, ps, range(pts_to_draw - 1)):
                    lengths.append(
                        ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5)
                total_length = sum(lengths)
                ratio = (b - a)/total_length
                
                ps = iter(self.points)
                next(ps)
                for p, l in zip(ps, itertools.accumulate(lengths)):
                    key = cr.elements.new(a + l*ratio)
                    key.color = p[-1] + [wm.crd_keys_alpha]
                # last -> precision
                key.position = b
            else:
                ratio = (b - a)/(min(len(self.points), pts_to_draw) - 1)
                ps = iter(self.points)
                next(ps)
                for p, i, _ in zip(
                    ps, itertools.count(a + ratio, ratio),
                    range(pts_to_draw - 1)):
                    key = cr.elements.new(i)
                    key.color = p[-1] + [wm.crd_keys_alpha]
                key.position = b
        
        self.removeHandle(context)
        if len(self.points) > pts_to_draw:
            return TOO_MANY
        return OK

    def cancel(self, context):
        if self.handle is None:
            return
        
        self.removeHandle(context)

    def isActive(self):
        return self.handle is not None
        

class NodeColorRampDropperDraw(bpy.types.Operator):
    bl_idname = "wm.crd_draw"
    bl_label = "Draw ColorRamp Dropper Path"

    # in some cases we have to delay a bit (until redraw)
    # to be sure we get the values
    require_redraw = False

    @classmethod
    def poll(cls, context):
        return (
            context.space_data.type == 'NODE_EDITOR' and
            context.space_data.node_tree is not None)

    def modal(self, context, event):
        if self.require_redraw:
            done = self._dropper_worker.finalize(context)
            if done == NO_HANDLE:
                self.require_redraw = False
                return {'CANCELLED'}
            elif done == OK:
                self.require_redraw = False
                context.window.cursor_modal_restore()
                return {'FINISHED'}
            elif done == TOO_MANY:
                self.require_redraw = False
                context.window.cursor_modal_restore()
                self.report(
                    {'INFO'},
                    "Too many points (limit: %s), truncated" % PTS_LIMIT)
                return {'CANCELLED'}
            elif done == NEED_REDRAW:
                pass
        elif event.type == 'MOUSEMOVE':
            if context.window_manager.crd_free_hand:
                if self._dropper_worker.isActive():
                    self._dropper_worker.addPoint(context, event)
            # in case of crd_free_hand we will have to updatePoints...
            # is not dramatic.
            self._dropper_worker.updateMousePosition(context, event)
        elif event.type == 'LEFTMOUSE':
            if context.window_manager.crd_free_hand:
                if event.value == 'PRESS':
                    self._dropper_worker.addPoint(context, event)
                elif event.value == 'RELEASE':
                    self.require_redraw = True
            else:
                if event.value == 'PRESS':
                    self._dropper_worker.addPoint(context, event)
        elif event.type == 'RIGHTMOUSE':
            if context.window_manager.crd_free_hand:
                context.window.cursor_modal_restore()
                self._dropper_worker.cancel(context)
                return {'CANCELLED'}
            else:
                if event.value == 'PRESS':
                    done = self._dropper_worker.removePoint(context)
                    if not done:
                        context.window.cursor_modal_restore()
                        return {'CANCELLED'}
        elif event.type == 'RET':
            if context.window_manager.crd_free_hand:
                self.require_redraw = True
            else:
                done = self._dropper_worker.finalize(context)
                if done == NO_HANDLE:
                    return {'CANCELLED'}
                elif done == OK:
                    context.window.cursor_modal_restore()
                    return {'FINISHED'}
                elif done == TOO_MANY:
                    context.window.cursor_modal_restore()
                    self.report(
                        {'INFO'},
                        "Too many points (limit: %s), truncated" % PTS_LIMIT)
                    return {'CANCELLED'}
                elif done == NEED_REDRAW:
                    self.require_redraw = True
        elif event.type == 'ESC':
            context.window.cursor_modal_restore()
            self._dropper_worker.cancel(context)
            return {'CANCELLED'}
        elif event.type == 'MIDDLEMOUSE':
            if event.value == 'PRESS':
                # make this customizable for more items
                tps = ('POLYLINE', 'CUBIC_SPLINE')
                for i, tp in enumerate(tps):
                    if context.window_manager.crd_path_type == tp:
                        context.window_manager.crd_path_type = tps[i - 1]
                        break
                self._dropper_worker.update(context)
        elif event.type == 'WHEELUPMOUSE':
            context.window_manager.crd_use_intermediate = True
            context.window_manager.crd_intermediate_amount += 1
            self._dropper_worker.update(context)
        elif event.type == 'WHEELDOWNMOUSE':
            context.window_manager.crd_intermediate_amount = max(
                0, context.window_manager.crd_intermediate_amount - 1)
            context.window_manager.crd_use_intermediate = (
                context.window_manager.crd_intermediate_amount != 0)
            self._dropper_worker.update(context)
        
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self._dropper_worker = DropperWorker(context)
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('EYEDROPPER')
        return {'RUNNING_MODAL'}


class NodeColorRampDropperPanel(bpy.types.Panel):
    bl_label = "ColorRamp Dropper"
    bl_idname = "NODE_PT_node_colorramp_dropper"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree is not None

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        
        layout.prop(wm, "crd_use_active")

        if wm.crd_use_interval:
            split = layout.split(percentage=0.33)
            split.prop(wm, "crd_use_interval")
            row = split.row(align=True)
            row.prop(wm, "crd_interval_min")
            row.prop(wm, "crd_interval_max")
            split = layout.split(percentage=0.33)
            split.prop(wm, "crd_erase_keys")
            row = split.row()
            row.prop(wm, "crd_erase_keys_interval", expand=True)
            row.enabled = wm.crd_erase_keys
        else:
            layout.prop(wm, "crd_use_interval")
            layout.prop(wm, "crd_erase_keys")
        
        split = layout.split(percentage=0.33)
        split.label("Path Type:")
        row = split.row()
        row.prop(wm, "crd_path_type", expand=True)
        
        if wm.crd_use_intermediate:
            split = layout.split(percentage=0.33)
            split.prop(wm, "crd_use_intermediate")
            split.prop(wm, "crd_intermediate_amount")
        else:
            layout.prop(wm, "crd_use_intermediate")

        layout.prop(wm, "crd_free_hand")
        layout.prop(wm, "crd_use_segments_length")
        layout.prop(wm, "crd_keep_memory")
        layout.prop(wm, "crd_keys_alpha", slider=True)
        layout.prop(wm, "crd_show_values")

        layout.operator(NodeColorRampDropperDraw.bl_idname)


def checkIntervalValues_min(self, context):
    if self.crd_interval_max < self.crd_interval_min:
        self.crd_interval_max = self.crd_interval_min

def checkIntervalValues_max(self, context):
    if self.crd_interval_min > self.crd_interval_max:
        self.crd_interval_min = self.crd_interval_max

def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.WindowManager.crd_use_active = bpy.props.BoolProperty(
        name="Use Active Node",
        description="Drop the values into the active node, "
            "if possible (else, a new ColorRamp node is created)",
        default=True)
    bpy.types.WindowManager.crd_use_interval = bpy.props.BoolProperty(
        name="Use Interval",
        description="Distribute the values in a custom subinterval "
            "of the colorramp",
        default=False)
    bpy.types.WindowManager.crd_interval_min = bpy.props.FloatProperty(
        name="Minimum",
        description="Lower bound of the custom interval",
        precision=3,
        min=0.0,
        max=1.0,
        default=0.0,
        update=checkIntervalValues_min)
    bpy.types.WindowManager.crd_interval_max = bpy.props.FloatProperty(
        name="Maximum",
        description="Upper bound of the custom interval",
        precision=3,
        min=0.0,
        max=1.0,
        default=1.0,
        update=checkIntervalValues_max)
    bpy.types.WindowManager.crd_erase_keys = bpy.props.BoolProperty(
        name="Erase Existing Keys",
        description="Remove already existing keys from the colorramp "
            "before dropping the new ones into it",
        default=True)
    bpy.types.WindowManager.crd_erase_keys_interval = bpy.props.EnumProperty(
        items=[
            ('ALL', "All", "Remove all keys"),
            ('INTERVAL', "Interval",
             "Remove keys within the given (closed) interval only")],
        name="Erase existing Keys",
        description="Remove already existing keys from the colorramp "
            "before dropping the new ones",
        default='ALL')
    bpy.types.WindowManager.crd_use_segments_length = bpy.props.BoolProperty(
        name="Use Segments Length",
        description="Take the lengths of the drawn segments in account for "
            "placing the new keys in the colorramp",
        default=True)
    bpy.types.WindowManager.crd_path_type = bpy.props.EnumProperty(
        items=[
            ('POLYLINE', "Polyline",
             "Connect selected points with straight lines"),
            ('CUBIC_SPLINE', "Cubic Spline",
             "Connect selected points with a natural cubic spline")],
        name="Type of Path",
        description="Type of the path to be used for selecting colors",
        default='POLYLINE')
    bpy.types.WindowManager.crd_show_values = bpy.props.BoolProperty(
        name="Show Values",
        description="Display color values at selected points",
        default=False)
    bpy.types.WindowManager.crd_use_intermediate = bpy.props.BoolProperty(
        name="Use Intermediate Points",
        description="Select intermediate points additionally",
        default=False)
    bpy.types.WindowManager.crd_intermediate_amount = bpy.props.IntProperty(
        name="Amount",
        description="Number of additional intermediate points per original "
            "segment",
        min=0,
        default=3)
    bpy.types.WindowManager.crd_free_hand = bpy.props.BoolProperty(
        name="Free-Hand Drawing",
        description="Draw the complete path in a single PRESS-MOVE-RELEASE "
            "cycle",
        default=False)
    bpy.types.WindowManager.crd_keys_alpha = bpy.props.FloatProperty(
        name="Keys Alpha",
        description="Alpha value of the added keys",
        precision=3,
        min=0.0,
        max=1.0,
        default=1.0)
    bpy.types.WindowManager.crd_keep_memory = bpy.props.BoolProperty(
        name="Keep Memory",
        description="Keep points above the allowed amount limit in memory "
            "while drawing",
        default=False)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.WindowManager.crd_use_active
    del bpy.types.WindowManager.crd_use_interval
    del bpy.types.WindowManager.crd_interval_min
    del bpy.types.WindowManager.crd_interval_max
    del bpy.types.WindowManager.crd_erase_keys
    del bpy.types.WindowManager.crd_erase_keys_interval
    del bpy.types.WindowManager.crd_use_segments_length
    del bpy.types.WindowManager.crd_path_type
    del bpy.types.WindowManager.crd_show_values
    del bpy.types.WindowManager.crd_use_intermediate
    del bpy.types.WindowManager.crd_intermediate_amount
    del bpy.types.WindowManager.crd_free_hand
    del bpy.types.WindowManager.crd_keys_alpha
    del bpy.types.WindowManager.crd_keep_memory


if __name__ == "__main__":
    register()
