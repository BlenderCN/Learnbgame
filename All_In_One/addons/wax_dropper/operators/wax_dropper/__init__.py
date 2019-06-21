# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import time

# Blender imports
import bgl
import bpy
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_line_line
from bpy_extras import view3d_utils

# Addon imports
from .wax_drop_datastructure import *
from .wax_drop_ui_init import *
from .wax_drop_ui_tools import *
from .wax_drop_ui_draw import *
from .wax_drop_states import *
from ...functions import *
from ...addon_common.cookiecutter.cookiecutter import CookieCutter
from ...addon_common.common import ui
from ...addon_common.common.bmesh_utils import BMeshSelectState, BMeshHideState
from ...addon_common.common.maths import Point, Point2D, XForm
from ...addon_common.common.decorators import PersistentOptions

@PersistentOptions()
class WaxDropperOptions:
    defaults = {
        "action": "add",
        "blob_size": 1.0,
        "paint_radius":2.0,
        "depth_offset":0.0,
        "position": 9,
        "resolution":0.4,
        "surface_target": "object",  #object, object_wax
    }


class OBJECT_OT_wax_dropper(WaxDrop_UI_Init, WaxDrop_UI_Draw, WaxDrop_UI_Tools, WaxDrop_States, CookieCutter):
    """ Paint and sketch on target object with metaballs """
    operator_id    = "object.wax_dropper"
    bl_idname      = "object.wax_dropper"
    bl_label       = "Wax Dropper"
    bl_description = "Paint and sketch on target object with metaballs"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"

    ################################################
    # CookieCutter Operator methods

    @classmethod
    def can_start(cls, context):
        """ Start only if editing a mesh """
        ob = context.active_object
        return ob is not None and ob.type == "MESH"

    def start(self):
        """ initialization function """
        bpy.ops.ed.undo_push()  # push current state to undo

        # initialize vars
        scn = bpy.context.scene

        self.header_text_set("Wax Dropper")
        self.cursor_modal_set("CROSSHAIR")
        self.manipulator_hide()

        # get target object and apply modifiers
        self.source = bpy.context.object
        if len(self.source.modifiers) > 0: apply_modifiers(self.source)
        # hide other objects
        self.unhidden_objects = [obj for obj in scn.objects if obj != self.source and not obj.hide]
        [hide(obj) for obj in self.unhidden_objects]

        # get options for UI box
        self.wax_opts = WaxDropperOptions()

        # make wax and meta objects
        self.wax_obj, self.meta_obj = self.make_wax_base()

        destructive = "DESTRUCTIVE" # or "NON-DESTRUCTIVE"
        self.last_updated_resolution = self.wax_opts["resolution"]
        self.net_ui_context = NetworkUIContext(self.context, bpy.context.object, geometry_mode=destructive)
        self.net_ui_context_wax = NetworkUIContext(self.context, self.wax_obj, geometry_mode=destructive)
        self.hint_bad = False   # draw obnoxious things over the bad segments
        self.input_net = InputNetwork(self.net_ui_context)
        self.spline_net = SplineNetwork(self.net_ui_context)
        self.network_cutter = NetworkCutter(self.input_net, self.net_ui_context)
        self.sketcher = self.SketchManager(self.input_net, self.spline_net, self.net_ui_context, self.network_cutter)

        self.brush = None

        def fn_get_pos_wrap(v):
            if type(v) is int: return v
            return Point2D(v)
        def fn_set_pos_wrap(v):
            if type(v) is int: return v
            return tuple(v)
        fn_pos = self.wax_opts.gettersetter("position", fn_get_wrap=fn_get_pos_wrap, fn_set_wrap=fn_set_pos_wrap)
        self.ui_setup()
        self.ui_setup_post()
        self.start_post()

    def end_commit(self):
        """ Commit changes to mesh! """
        self.remove_meta_wax()
        if self.wax_opts["action"] != "none":
            # add/subtract wax object to/from source
            jmod = self.source.modifiers.new('Join Wax', type='BOOLEAN')
            jmod.operation = 'UNION' if self.wax_opts["action"] == 'add' else 'DIFFERENCE'
            jmod.object = self.wax_obj
            apply_modifiers(self.source)
            self.remove_wax_blobs()
        self.end_commit_post()

    def end_cancel(self):
        """ Cancel changes """
        bpy.ops.ed.undo()

    def end(self):
        """ Restore everything, because we're done """
        [unhide(obj) for obj in self.unhidden_objects]
        self.manipulator_restore()
        self.header_text_restore()
        self.cursor_modal_restore()

    # def update(self):
    #     """ Check if we need to update any internal data structures """
    #     if not self.is_dirty: return

    ###################################################
    # class variables

    # NONE!

    #############################################
    # class methods

    def make_wax_base(self):
        scn = bpy.context.scene
        if 'Meta Wax' in bpy.data.objects:
            meta_obj = bpy.data.objects.get('Meta Wax')
            meta_data = meta_obj.data
        else:
            meta_data = bpy.data.metaballs.new('Meta Wax')
            meta_obj = bpy.data.objects.new('Meta Wax', meta_data)
            meta_data.resolution = self.wax_opts['resolution']
            meta_data.render_resolution = 1
            scn.objects.link(meta_obj)
        if 'Wax Blobs' not in bpy.data.objects:
            wax_me = bpy.data.meshes.new('Wax Blobs')
            wax_obj = bpy.data.objects.new('Wax Blobs', wax_me)
            scn.objects.link(wax_obj)
            smod = wax_obj.modifiers.new('Smooth', type = 'SMOOTH')
            smod.iterations = 10
        else:
            wax_obj = bpy.data.objects.get('Wax Blobs')
            wax_me = wax_obj.data

        meta_obj.hide = True
        meta_obj.matrix_world = self.source.matrix_world
        wax_obj.matrix_world = self.source.matrix_world

        return wax_obj, meta_obj

    def perform_wax_action(self, delete_wax:bool):
        scn = bpy.context.scene
        coord = self.event.mouse_region_x, self.event.mouse_region_y

        region = bpy.context.region
        rv3d = bpy.context.region_data
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_target = ray_origin + (view_vector * 1000)

        imx = self.meta_obj.matrix_world.inverted()
        # NOTE: cannot use wax_obj ray cast as first test, as this may register a hit through the source mesh
        # result, loc = self.wax_obj.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)[:2]
        result, loc, _, _, obj = scn.ray_cast(ray_origin, ray_target - ray_origin)[:5]

        if result:
            if delete_wax:
                if obj != self.wax_obj:
                    return
                to_remove = []
                for mb in self.meta_obj.data.elements:
                    if (mb.co - loc).length < 1.5 * self.wax_opts["blob_size"]:
                        to_remove.append(mb)
                # closest_mb = min(self.meta_obj.data.elements, key = lambda x: (x.co - loc).length)
                # self.meta_obj.data.elements.remove(closest_mb)
                for mb in to_remove:
                    self.meta_obj.data.elements.remove(mb)
                self.push_meta_to_wax()
            else:
                self.draw_wax(loc * self.meta_obj.matrix_world)
                self.push_meta_to_wax()

    def draw_wax(self, loc, radius=None):
        # NOTE: wax must be pushed to meta_obj with 'self.push_meta_to_wax()'
        mb = self.meta_obj.data.elements.new(type='BALL')
        mb.co = loc
        mb.radius = radius or self.wax_opts["blob_size"]

    def brush_density(self):
        density = 1/(.5 * self.wax_opts["blob_size"])**2
        nps = self.brush.calc_npoints(density)
        self.brush.generate_spiral_points(nps)

    def remove_meta_wax(self):
        # remove meta wax object
        meta_obj = bpy.data.objects.get('Meta Wax')
        if meta_obj is not None:
            md = meta_obj.data
            bpy.data.objects.remove(meta_obj)
            bpy.data.metaballs.remove(md)

    def remove_wax_blobs(self):
        # remove wax blobs object
        wax_obj = bpy.data.objects.get('Wax Blobs')
        if wax_obj is not None:
            wd = wax_obj.data
            bpy.data.objects.remove(wax_obj)
            bpy.data.meshes.remove(wd)

    def push_meta_to_wax(self):
        scn = bpy.context.scene
        scn.update()
        old_data = self.wax_obj.data
        self.wax_obj.data = self.meta_obj.to_mesh(scn, apply_modifiers=True, settings='PREVIEW')
        bpy.data.meshes.remove(old_data)

    def shift_along_normal(self, loc:Vector, norm:Vector):
        return loc + vec_mult(Vector([self.wax_opts["blob_size"]*0.75]*3), norm) * self.wax_opts["depth_offset"]

    def fuse_and_continue(self):
        """ apply currently drawn wax to source object """
        self.end_commit()
        self.wax_obj, self.meta_obj = self.make_wax_base()
        self.net_ui_context.update_bme()
        self.net_ui_context.update_bvh()

    #############################################
    # Subclassing functions

    def ui_setup_post(self):
        pass

    def start_post(self):
        pass

    def end_commit_post(self):
        pass

    #############################################
