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

# Blender imports
import bpy
from bpy.types import Operator
from mathutils import Matrix, Vector

# Addon imports
from .setup_phys_drawing import *
from ..functions.common import *
from ..app_handlers import *

class PHYSICS_OT_setup_interactive_sim(Operator, interactive_sim_drawing):
    '''Switch to new scene and set up for rigid body physics simulation'''
    bl_idname = "physics.setup_interactive_sim"
    bl_label = "Setup New Physics Scene for Simulation"
    bl_options = {'REGISTER','UNDO'}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        return len(bpy.context.selected_objects) > 0 and context.scene.name != "Interactive Physics Session"

    def modal(self, context, event):
        try:
            # close sim
            if event.type == "RET":
                # ensure mouse is in 3D_VIEW
                space, i = get_quadview_index(context, event.mouse_x, event.mouse_y)
                if space in (None, "UI" if b280() else "TOOLS"):
                    return {"RUNNING_MODAL"}
                self.close_interactive_sim()
                return {"FINISHED"}
            # cancel sim
            elif event.type == "ESC":
                self.cancel_interactive_sim()
                return {"FINISHED"}
            elif self.replace_end_frame and self.sim_scene.frame_current == 1:
                self.sim_scene.frame_end = 500
                self.replace_end_frame = False
            elif event.type == "Z" and (event.oskey or event.ctrl):
                self.report({"WARNING"}, "Undo not available for interactive simulation. Cancel all changes with the 'ESC' key")
                return {"RUNNING_MODAL"}
            elif b280() and event.type == "A" and event.value == "RELEASE":
                self.sim_scene.frame_end = self.sim_scene.frame_current + 1
                self.replace_end_frame = True
            # block left_click if not in 3D viewport
            elif event.type in ("LEFTMOUSE", "RIGHTMOUSE"):
                space, i = get_quadview_index(context, event.mouse_x, event.mouse_y)
                if space is None:
                    return {"RUNNING_MODAL"}
                elif event.value == "RELEASE":
                    # if event.type == "LEFTMOUSE":
                    self.sim_scene.frame_end = self.sim_scene.frame_current + 1
                    self.replace_end_frame = True
                    # elif event.type == "RIGHTMOUSE":
                    #     bpy.ops.screen.animation_cancel()
                    #     self.sim_scene.frame_set(0)
                    #     bpy.ops.screen.animation_play()
            return {"PASS_THROUGH"}
        except:
            interactive_physics_handle_exception()
            self.close_interactive_sim()
            return {"CANCELLED"}

    def execute(self, context):
        try:
            self.add_to_new_scene()
            self.set_up_physics()
            bpy.ops.screen.animation_play()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        except:
            interactive_physics_handle_exception()
            self.close_interactive_sim()
            return {'CANCELLED'}

    ################################################
    # initialization method

    def __init__(self):
        self.objs = list(bpy.context.selected_objects)
        self.orig_scene = bpy.context.scene
        self.orig_frame = self.orig_scene.frame_current

        self.replace_end_frame = False
        self.matrices = {}
        self.selected_objects = []
        self.sim_scene = None
        for obj in self.objs:
            self.matrices[obj.name] = obj.matrix_world.copy()
        if not b280():
            self.ui_start()

    ###################################################
    # class variables

    #############################################
    # class methods

    def add_to_new_scene(self):
        # add new physics session scene
        self.sim_scene = bpy.data.scenes.new("Interactive Physics Session")
        set_active_scene(self.sim_scene)

        # set new scene properties
        self.sim_scene.phys_use_gravity = False
        self.sim_scene.use_gravity = False
        self.sim_scene.sync_mode = 'NONE'

        # TODO Clear existing objects and any physics cache
        for ob in self.sim_scene.objects:
            bpy.data.objects.remove(ob, do_unlink=True)

        for obj in self.objs:
            link_object(obj, scene=self.sim_scene)
            select(obj, active=True)

        # bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=False)
        bpy.ops.object.visual_transform_apply()

    def set_up_physics(self):
        # add rigid body world to new scene
        bpy.ops.rigidbody.world_add()

        # potentially adjust these values
        rbw = self.sim_scene.rigidbody_world
        rbw.solver_iterations = 15
        rbw.point_cache.frame_start = 1 #more time for sim.
        rbw.point_cache.frame_end = 500 #more time for sim.
        self.sim_scene.frame_start = 1
        self.sim_scene.frame_end = 500
        self.sim_scene.frame_set(0)

        # get group for objects
        obj_coll = bpy_collections().get(collection_name)
        if obj_coll is None:
            obj_coll = bpy_collections().new(collection_name)
        if b280():
            rbw.collection = obj_coll
        else:
            rbw.group = obj_coll
        bpy.ops.rigidbody.objects_add()

        for obj in self.objs:
            obj.lock_rotations_4d = True
            obj.lock_rotation[0] = True
            obj.lock_rotation[1] = True
            obj.lock_rotation[2] = True
            obj.lock_rotation_w = True

            rb = obj.rigid_body
            rb.friction = 0.1
            rb.use_margin = True
            rb.collision_margin = 0
            rb.collision_shape = bpy.context.scene.phys_collision_shape
            rb.restitution = 0
            rb.linear_damping = 1
            rb.angular_damping = 0.9
            rb.mass = 3
            deselect(obj)

        bpy.app.handlers.frame_change_pre.append(handle_edit_session_pre)
        bpy.app.handlers.frame_change_post.append(handle_edit_session_post)

    def close_interactive_sim(self):
        self.ui_end()
        if self.sim_scene is None:
            return
        for obj in self.objs:
            self.matrices[obj.name] = obj.matrix_world.copy()
        bpy.ops.rigidbody.objects_remove()
        bpy.ops.screen.animation_cancel()
        self.sim_scene.frame_set(self.orig_frame)
        set_active_scene(self.orig_scene)
        bpy.data.scenes.remove(self.sim_scene)
        bpy_collections().remove(bpy_collections().get(collection_name))
        for obj in self.objs:
            obj.matrix_world = self.matrices[obj.name]
        self.orig_scene.update()
        for obj in self.objs:
            obj.lock_rotations_4d = False
            obj.lock_rotation = [False]*3
            obj.lock_location = [False]*3
            obj.lock_rotation_w = False
        bpy.app.handlers.frame_change_pre.remove(handle_edit_session_pre)
        bpy.app.handlers.frame_change_post.remove(handle_edit_session_post)

    def cancel_interactive_sim(self):
        for obj in self.objs:
            obj.matrix_world = self.matrices[obj.name]
        self.close_interactive_sim()
