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

bl_info = {
    "name"        : "Interactive Physics Editor",
    "author"      : "Christopher Gearhart <chris@bblanimation.com> & Patrick Moore <patrick@d3tool.com>",
    "version"     : (1, 1, 2),
    "blender"     : (2, 80, 0),
    "description" : "Simplifies the process of positioning multiple objects in 3D space with collision handling",
    "location"    : "View 3D > Tools > Physics > Interactive Physics Editor",
    "warning"     : "",  # used for warning icon and text in addons panel
    "wiki_url"    : "https://www.blendermarket.com/products/interactive-physics-editor",
    "tracker_url" : "https://github.com/bblanimation/interactive-physics-editor/issues",
    "category"    : "3D View"}

# Blender imports
import bpy
from bpy.types import Scene

# Addon imports
from .lib.classesToRegister import *
from .functions.common import *
from . import addon_updater_ops

# property update functions
def update_lock_loc(scene, context):
    for obj in scene.objects:
        obj.lock_location = (scene.phys_lock_loc_x, scene.phys_lock_loc_y, scene.phys_lock_loc_z)
def update_lock_rot(scene, context):
    for obj in scene.objects:
        obj.lock_rotation = (scene.phys_lock_rot_x, scene.phys_lock_rot_y, scene.phys_lock_rot_z)
def update_collision_margin(scene, context):
    for obj in scene.objects:
        obj.rigid_body.collision_margin = scene.phys_collision_margin
def update_collision_shape(scene, context):
    for obj in scene.objects:
        obj.rigid_body.collision_shape = scene.phys_collision_shape
def update_enable_gravity(scene, context):
    scene.use_gravity = scene.phys_use_gravity

def register():
    # register classes
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)
    # register properties
    Scene.phys_lock_loc_x = BoolProperty(name="Lock X", default=False, update=update_lock_loc)
    Scene.phys_lock_loc_y = BoolProperty(name="Lock Y", default=False, update=update_lock_loc)
    Scene.phys_lock_loc_z = BoolProperty(name="Lock Z", default=False, update=update_lock_loc)
    Scene.phys_lock_rot_x = BoolProperty(name="Lock X", default=True, update=update_lock_rot)
    Scene.phys_lock_rot_y = BoolProperty(name="Lock Y", default=True, update=update_lock_rot)
    Scene.phys_lock_rot_z = BoolProperty(name="Lock Z", default=True, update=update_lock_rot)
    Scene.phys_collision_margin = FloatProperty(name="Collision Margin", default=0.0, min=-1, max=1, step=1, update=update_collision_margin)
    Scene.phys_collision_shape = EnumProperty(name="Collision Shape", items=(("CONVEX_HULL", "Convex (fast)", "Objects collide with other objects using a convex collision shape"), ("MESH", "Concave", "Objects collide with other objects using a concave collision shape (best for hollow objects)")), default="CONVEX_HULL", update=update_collision_shape)
    Scene.phys_use_gravity = BoolProperty(name="Use Gravity", default=False, update=update_enable_gravity)
    # addon updater code and configurations
    addon_updater_ops.register(bl_info)

def unregister():
    # unregister addon updater
    addon_updater_ops.unregister()
    # unregister properties
    del Scene.phys_use_gravity
    del Scene.phys_collision_shape
    del Scene.phys_collision_margin
    del Scene.phys_lock_rot_z
    del Scene.phys_lock_rot_y
    del Scene.phys_lock_rot_x
    del Scene.phys_lock_loc_z
    del Scene.phys_lock_loc_y
    del Scene.phys_lock_loc_x
    # unregister classes
    for cls in classes:
        bpy.utils.unregister_class(cls)
