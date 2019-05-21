#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import *
import math

from .. import idprops

camera_types = [("circle", "Circle Camera", "The camera circles a fixed point"),
                ("follow", "Follow Camera", "The camera follows an object"),
                ("fixed", "Fixed Camera", "The camera is fixed in one location"),
                ("rail", "Rail Camera", "The camera follows an object by moving along a line")]

class PlasmaTransition(bpy.types.PropertyGroup):
    poa_acceleration = FloatProperty(name="PoA Acceleration",
                                     description="Rate the camera's Point of Attention tracking velocity increases in feet per second squared",
                                     min=-100.0, max=100.0, precision=0, default=60.0,
                                     unit="ACCELERATION", options=set())
    poa_deceleration = FloatProperty(name="PoA Deceleration",
                                     description="Rate the camera's Point of Attention tracking velocity decreases in feet per second squared",
                                     min=-100.0, max=100.0, precision=0, default=60.0,
                                     unit="ACCELERATION", options=set())
    poa_velocity = FloatProperty(name="PoA Velocity",
                                 description="Maximum velocity of the camera's Point of Attention tracking",
                                 min=-100.0, max=100.0, precision=0, default=60.0,
                                 unit="VELOCITY", options=set())
    poa_cut = BoolProperty(name="Cut",
                           description="The camera immediately begins tracking the Point of Attention",
                           options=set())

    pos_acceleration = FloatProperty(name="Position Acceleration",
                                     description="Rate the camera's positional velocity increases in feet per second squared",
                                     min=-100.0, max=100.0, precision=0, default=60.0,
                                     unit="ACCELERATION", options=set())
    pos_deceleration = FloatProperty(name="Position Deceleration",
                                     description="Rate the camera's positional velocity decreases in feet per second squared",
                                     min=-100.0, max=100.0, precision=0, default=60.0,
                                     unit="ACCELERATION", options=set())
    pos_velocity = FloatProperty(name="Position Max Velocity",
                                 description="Maximum positional velocity of the camera",
                                 min=-100.0, max=100.0, precision=0, default=60.0,
                                 unit="VELOCITY", options=set())
    pos_cut = BoolProperty(name="Cut",
                           description="The camera immediately moves to its new position",
                           options=set())


class PlasmaManualTransition(bpy.types.PropertyGroup):
    camera = PointerProperty(name="Camera",
                             description="The camera from which this transition is intended",
                             type=bpy.types.Object,
                             poll=idprops.poll_camera_objects,
                             options=set())
    transition = PointerProperty(type=PlasmaTransition, options=set())
    mode = EnumProperty(name="Transition Mode",
                        description="Type of transition that should occur between the two cameras",
                        items=[("ignore", "Ignore Camera", "Ignore this camera and do not transition"),
                               ("auto", "Auto", "Auto transition as defined by the two cameras' properies"),
                               ("manual", "Manual", "Manually defined transition")],
                        default="auto",
                        options=set())
    enabled = BoolProperty(name="Enabled",
                           description="Export this transition",
                           default=True,
                           options=set())


class PlasmaCameraProperties(bpy.types.PropertyGroup):
    # Point of Attention
    poa_type = EnumProperty(name="Point of Attention",
                            description="The point of attention that this camera tracks",
                            items=[("avatar", "Track Local Player", "Camera tracks the player's avatar"),
                                   ("object", "Track Object", "Camera tracks an object in the scene"),
                                   ("none", "Don't Track", "Camera does not track anything")],
                            options=set())
    poa_object = PointerProperty(name="PoA Object",
                                 description="Object the camera should track as its Point of Attention",
                                 type=bpy.types.Object,
                                 options=set())
    poa_offset = FloatVectorProperty(name="PoA Offset",
                                     description="Offset from the point of attention's origin to track",
                                     soft_min=-50.0, soft_max=50.0,
                                     size=3, default=(0.0, 0.0, 3.0),
                                     options=set())
    poa_worldspace = BoolProperty(name="Worldspace Offset",
                                  description="Point of Attention Offset is in worldspace coordinates",
                                  options=set())

    # Position Offset
    pos_offset = FloatVectorProperty(name="Position Offset",
                                     description="Offset the camera's position",
                                     soft_min=-50.0, soft_max=50.0,
                                     size=3, default=(0.0, 10.0, 3.0),
                                     options=set())
    pos_worldspace = BoolProperty(name="Worldspace Offset",
                                  description="Position offset is in worldspace coordinates",
                                  options=set())

    # Default Transition
    transition = PointerProperty(type=PlasmaTransition, options=set())

    # Limit Panning
    x_pan_angle = FloatProperty(name="X Degrees",
                                description="Maximum camera pan angle in the X direction",
                                min=0.0, max=math.radians(180.0), precision=0, default=math.radians(90.0),
                                subtype="ANGLE", options=set())
    y_pan_angle = FloatProperty(name="Y Degrees",
                                description="Maximum camera pan angle in the Y direction",
                                min=0.0, max=math.radians(180.0), precision=0, default=math.radians(90.0),
                                subtype="ANGLE", options=set())
    pan_rate = FloatProperty(name="Pan Velocity",
                             description="",
                             min=0.0, precision=1, default=50.0,
                             unit="VELOCITY", options=set())

    # Zooming
    fov = FloatProperty(name="Default FOV",
                        description="Horizontal Field of View angle",
                        min=0.0, max=math.radians(180.0), precision=0, default=math.radians(70.0),
                        subtype="ANGLE")
    limit_zoom = BoolProperty(name="Limit Zoom",
                              description="The camera allows zooming per artist limitations",
                              options=set())
    zoom_max = FloatProperty(name="Max FOV",
                             description="Maximum camera FOV when zooming",
                             min=0.0, max=math.radians(180.0), precision=0, default=math.radians(120.0),
                             subtype="ANGLE", options=set())
    zoom_min = FloatProperty(name="Min FOV",
                             description="Minimum camera FOV when zooming",
                             min=0.0, max=math.radians(180.0), precision=0, default=math.radians(35.0),
                             subtype="ANGLE", options=set())
    zoom_rate = FloatProperty(name="Zoom Velocity",
                              description="Velocity of the camera's zoom in degrees per second",
                              min=0.0, max=180.0, precision=0, default=90.0,
                              unit="VELOCITY", options=set())

    # Miscellaneous Movement Props
    maintain_los = BoolProperty(name="Maintain LOS",
                                description="The camera should maintain line-of-sight with the object it's tracking",
                                options=set())
    fall_vertical = BoolProperty(name="Fall Camera",
                                 description="The camera will orient itself vertically when the local player begins falling",
                                 options=set())
    fast_run = BoolProperty(name="Faster When Falling",
                            description="The camera's velocity will have a floor when the local player is falling",
                            options=set())
    ignore_subworld = BoolProperty(name="Ignore Subworld Movement",
                                   description="The camera will not be parented to any subworlds",
                                   options=set())

    # Core Type Properties
    primary_camera = BoolProperty(name="Primary Camera",
                                  description="The camera should be considered the Age's primary camera.",
                                  options=set())

    # Cricle Camera
    def _get_circle_radius(self):
        # This is coming from the UI, so we need to get the active object from
        # Blender's context and pass that on to the actual getter.
        return self.get_circle_radius(bpy.context.object)
    def _set_circle_radius(self, value):
        # Don't really care about error checking...
        self.circle_radius_value = value

    circle_center = PointerProperty(name="Center",
                                    description="Center of the circle camera's orbit",
                                    type=bpy.types.Object,
                                    options=set())
    circle_pos = EnumProperty(name="Position on Circle",
                              description="The point on the circle the camera moves to",
                              items=[("closest", "Closest Point", "The camera moves to the point on the circle closest to the Point of Attention"),
                                     ("farthest", "Farthest Point", "The camera moves to the point on the circle farthest from the Point of Attention")],
                              options=set())
    circle_velocity = FloatProperty(name="Velocity",
                                    description="Velocity of the circle camera in degrees per second",
                                    min=0.0, max=math.radians(360.0), precision=0, default=math.radians(36.0),
                                    subtype="ANGLE", options=set())
    circle_radius_ui = FloatProperty(name="Radius",
                                     description="Radius at which the circle camera should orbit the Point of Attention",
                                     min=0.0, get=_get_circle_radius, set=_set_circle_radius, options=set())
    circle_radius_value = FloatProperty(name="INTERNAL: Radius",
                                        description="Radius at which the circle camera should orbit the Point of Attention",
                                        min=0.0, default=8.5, options={"HIDDEN"})

    # Animation
    anim_enabled = BoolProperty(name="Animation Enabled",
                                description="Export the camera's animation",
                                default=True,
                                options=set())
    start_on_push = BoolProperty(name="Start on Push",
                                 description="Start playing the camera's animation when the camera is activated",
                                 default=True,
                                 options=set())
    stop_on_pop = BoolProperty(name="Pause on Pop",
                               description="Pauses the camera's animation when the camera is no longer activated",
                               default=True,
                               options=set())
    reset_on_pop = BoolProperty(name="Reset on Pop",
                                description="Reset the camera's animation to the beginning when the camera is no longer activated",
                                options=set())

    # Rail
    rail_pos = EnumProperty(name="Position on Rail",
                            description="The point on the rail the camera moves to",
                            items=[("closest", "Closest Point", "The camera moves to the point on the rail closest to the Point of Attention"),
                                   ("farthest", "Farthest Point", "The camera moves to the point on the rail farthest from the Point of Attention")],
                            options=set())

    def get_circle_radius(self, bo):
        """Gets the circle camera radius for this camera when it is attached to the given Object"""
        assert bo is not None
        if self.circle_center is not None:
            vec = bo.location - self.circle_center.location
            return vec.magnitude
        return self.circle_radius_value

    def harvest_actors(self):
        if self.poa_type == "object":
            return set((self.poa_object.name),)
        return set()


class PlasmaCamera(bpy.types.PropertyGroup):
    camera_type = EnumProperty(name="Camera Type",
                               description="",
                               items=camera_types,
                               options=set())
    settings = PointerProperty(type=PlasmaCameraProperties, options=set())
    transitions = CollectionProperty(type=PlasmaManualTransition,
                                     name="Transitions",
                                     description="",
                                     options=set())
    active_transition_index = IntProperty(options={"HIDDEN"})
