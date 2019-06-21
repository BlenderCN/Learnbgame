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

from .. import helpers
from . import ui_list

def _draw_alert_prop(layout, props, the_prop, cam_type, alert_cam="", min=None, max=None, **kwargs):
    can_alert = not alert_cam or alert_cam == cam_type
    if can_alert:
        value = getattr(props, the_prop)
        if min is not None and value < min:
            layout.alert = True
        if max is not None and value > max:
            layout.alert = True
        layout.prop(props, the_prop, **kwargs)
        layout.alert = False
    else:
        layout.prop(props, the_prop, **kwargs)

def _draw_gated_prop(layout, props, gate_prop, actual_prop):
    row = layout.row(align=True)
    row.prop(props, gate_prop, text="")
    row = row.row(align=True)
    row.active = getattr(props, gate_prop)
    row.prop(props, actual_prop)

def draw_camera_manipulation_props(layout, cam_type, props):
    # Camera Panning
    split = layout.split()
    col = split.column()
    col.label("Limit Panning:")
    col.prop(props, "x_pan_angle")
    col.prop(props, "y_pan_angle")

    # Camera Zoom
    col = split.column()
    col.label("Field of View:")
    col.prop(props, "fov")
    _draw_gated_prop(col, props, "limit_zoom", "zoom_min")
    _draw_gated_prop(col, props, "limit_zoom", "zoom_max")
    _draw_gated_prop(col, props, "limit_zoom", "zoom_rate")

def draw_camera_mode_props(layout, cam_type, props):
    # Point of Attention
    split = layout.split()
    col = split.column()
    col.label("Camera Mode:")
    col = col.column()
    col.alert = cam_type != "fixed" and props.poa_type == "none"
    col.prop(props, "poa_type", text="")
    col.alert = False
    row = col.row()
    row.active = props.poa_type == "object"
    row.prop(props, "poa_object", text="")
    col.separator()
    col.prop(props, "primary_camera")

    # Miscellaneous
    col = split.column()
    col.label("Tracking Settings:")
    col.prop(props, "maintain_los")
    col.prop(props, "fall_vertical")
    col.prop(props, "fast_run")
    col.prop(props, "ignore_subworld")

def draw_camera_poa_props(layout, cam_type, props):
    trans = props.transition

    # PoA Tracking
    split = layout.split()
    col = split.column()
    col.label("Default Tracking Transition:")
    col.prop(trans, "poa_acceleration", text="Acceleration")
    col.prop(trans, "poa_deceleration", text="Deceleration")
    col.prop(trans, "poa_velocity", text="Maximum Velocity")
    col = col.column()
    col.active = cam_type == "follow"
    col.prop(trans, "poa_cut", text="Cut Animation")

    # PoA Offset
    col = split.column()
    col.label("Point of Attention Offset:")
    col.prop(props, "poa_offset", text="")
    col.prop(props, "poa_worldspace")

def draw_camera_pos_props(layout, cam_type, props):
    trans = props.transition

    # Position Tracking (only for follow cams)
    split = layout.split()
    col = split.column()

    # Position Transitions
    col.active = cam_type != "circle"
    col.label("Default Position Transition:")
    _draw_alert_prop(col, trans, "pos_acceleration", cam_type,
                     alert_cam="rail", max=10.0, text="Acceleration")
    _draw_alert_prop(col, trans, "pos_deceleration", cam_type,
                     alert_cam="rail", max=10.0, text="Deceleration")
    _draw_alert_prop(col, trans, "pos_velocity", cam_type,
                     alert_cam="rail", max=10.0, text="Maximum Velocity")
    col = col.column()
    col.active = cam_type == "follow"
    col.prop(trans, "pos_cut", text="Cut Animation")

    # Position Offsets
    col = split.column()
    col.active = cam_type == "follow"
    col.label("Position Offset:")
    col.prop(props, "pos_offset", text="")
    col.prop(props, "pos_worldspace")

def draw_circle_camera_props(layout, props):
    # Circle Camera Stuff
    layout.prop(props, "circle_center")
    layout.prop(props, "circle_pos")
    layout.prop(props, "circle_velocity")
    row = layout.row(align=True)
    row.active = props.circle_center is None
    row.prop(props, "circle_radius_ui")

class CameraButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (context.camera and context.scene.render.engine == "PLASMA_GAME")


class PlasmaCameraTypePanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = ""
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        camera = context.camera.plasma_camera
        self.layout.prop(camera, "camera_type")


class PlasmaCameraModePanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Camera Tracking"

    def draw(self, context):
        camera = context.camera.plasma_camera
        draw_camera_mode_props(self.layout, camera.camera_type, camera.settings)


class PlasmaCameraAttentionPanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Point of Attention Tracking"

    def draw(self, context):
        camera = context.camera.plasma_camera
        draw_camera_poa_props(self.layout, camera.camera_type, camera.settings)


class PlasmaCameraPositionPanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Position Tracking"

    def draw(self, context):
        camera = context.camera.plasma_camera
        draw_camera_pos_props(self.layout, camera.camera_type, camera.settings)


class PlasmaCameraCirclePanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Circle Camera"

    def draw(self, context):
        camera = context.camera.plasma_camera
        draw_circle_camera_props(self.layout, camera.settings)

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.camera.plasma_camera.camera_type == "circle"


class PlasmaCameraAnimationPanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Camera Animation"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        camera = context.camera.plasma_camera
        props = camera.settings

        split = layout.split()
        col = split.column()
        col.label("Animation:")
        col.active = props.anim_enabled and any(helpers.fetch_fcurves(context.object))
        col.prop(props, "start_on_push")
        col.prop(props, "stop_on_pop")
        col.prop(props, "reset_on_pop")

        col = split.column()
        col.active = camera.camera_type == "rail"
        col.label("Rail:")
        col.prop(props, "rail_pos", text="")

    def draw_header(self, context):
        self.layout.active = any(helpers.fetch_fcurves(context.object))
        self.layout.prop(context.camera.plasma_camera.settings, "anim_enabled", text="")


class PlasmaCameraViewPanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Camera Lens"

    def draw(self, context):
        camera = context.camera.plasma_camera
        draw_camera_manipulation_props(self.layout, camera.camera_type, camera.settings)


class TransitionListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        if item.camera is None:
            layout.label("[Default Transition]")
        else:
            layout.label(item.camera.name, icon="CAMERA_DATA")
        layout.prop(item, "enabled", text="")


class PlasmaCameraTransitionPanel(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Transitions"

    def draw(self, context):
        layout = self.layout
        camera = context.camera.plasma_camera

        ui_list.draw_list(layout, "TransitionListUI", "camera", camera, "transitions",
                          "active_transition_index", rows=3, maxrows=4)

        try:
            item = camera.transitions[camera.active_transition_index]
            trans = item.transition
        except:
            pass
        else:
            layout.separator()
            box = layout.box()
            box.prop(item, "camera", text="Transition From")
            box.prop(item, "mode")

            box.separator()
            split = box.split()
            split.active = item.mode == "manual"

            col = split.column()
            col.label("Tracking Transition:")
            col.prop(trans, "poa_acceleration", text="Acceleration")
            col.prop(trans, "poa_deceleration", text="Deceleration")
            col.prop(trans, "poa_velocity", text="Maximum Velocity")
            col.prop(trans, "poa_cut", text="Cut Transition")

            col = split.column()
            col.label("Position Transition:")
            col.prop(trans, "pos_acceleration", text="Acceleration")
            col.prop(trans, "pos_deceleration", text="Deceleration")
            col.prop(trans, "pos_velocity", text="Maximum Velocity")
            col.prop(trans, "pos_cut", text="Cut Transition")
