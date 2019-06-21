# Copyright (C) 2019 Christopher Gearhart
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
# NONE!

# Blender imports
import bpy
from addon_utils import check, paths, enable
from bpy.types import Panel
from bpy.props import *
props = bpy.props

# Addon imports
from .cmlist_attrs import *
from .cmlist_actions import *
from .app_handlers import *
from .timers import *
from .matlist_window import *
from .matlist_actions import *
from ..lib.bricksDict import *
from ..lib.Brick.test_brick_generators import *
from ..lib.caches import cacheExists
from ..buttons.revertSettings import *
from ..buttons.brickify import *
from ..buttons.customize.tools.bricksculpt import *
from ..functions import *
from .. import addon_updater_ops
if b280():
    from .other_property_groups import *


def settingsCanBeDrawn():
    scn = bpy.context.scene
    if scn.cmlist_index == -1:
        return False
    if bversion() < '002.079':
        return False
    if not bpy.props.bricker_initialized:
        return False
    return True


class BRICKER_MT_specials(bpy.types.Menu):
    bl_idname      = "BRICKER_MT_specials"
    bl_label       = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("cmlist.copy_settings_to_others", icon="COPY_ID", text="Copy Settings to Others")
        layout.operator("cmlist.copy_settings", icon="COPYDOWN", text="Copy Settings")
        layout.operator("cmlist.paste_settings", icon="PASTEDOWN", text="Paste Settings")
        layout.operator("cmlist.select_bricks", icon="RESTRICT_SELECT_OFF", text="Select Bricks").deselect = False
        layout.operator("cmlist.select_bricks", icon="RESTRICT_SELECT_ON", text="Deselect Bricks").deselect = True


class VIEW3D_PT_bricker_brick_models(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Brick Models"
    bl_idname      = "VIEW3D_PT_bricker_brick_models"
    bl_context     = "objectmode"

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # Call to check for update in background
        # Internally also checks to see if auto-check enabled
        # and if the time interval has passed
        addon_updater_ops.check_for_update_background()
        # draw auto-updater update box
        addon_updater_ops.update_notice_box_ui(self, context)

        # if blender version is before 2.79, ask user to upgrade Blender
        if bversion() < '002.079':
            col = layout.column(align=True)
            col.label(text="ERROR: upgrade needed", icon='ERROR')
            col.label(text="Bricker requires Blender 2.79+")
            return

        # draw UI list and list actions
        rows = 2 if len(scn.cmlist) < 2 else 4
        row = layout.row()
        row.template_list("CMLIST_UL_items", "", scn, "cmlist", scn, "cmlist_index", rows=rows)

        col = row.column(align=True)
        col.operator("cmlist.list_action" if bpy.props.bricker_initialized else "bricker.initialize", text="", icon="ADD" if b280() else "ZOOMIN").action = 'ADD'
        col.operator("cmlist.list_action", icon='REMOVE' if b280() else 'ZOOMOUT', text="").action = 'REMOVE'
        col.menu("BRICKER_MT_specials", icon='DOWNARROW_HLT', text="")
        if len(scn.cmlist) > 1:
            col.separator()
            col.operator("cmlist.list_action", icon='TRIA_UP', text="").action = 'UP'
            col.operator("cmlist.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        # draw menu options below UI list
        if scn.cmlist_index == -1:
            layout.operator("cmlist.list_action" if bpy.props.bricker_initialized else "bricker.initialize", text="New Brick Model", icon="ADD" if b280() else "ZOOMIN").action = 'ADD'
        else:
            cm, n = getActiveContextInfo()[1:]
            if not createdWithNewerVersion(cm):
                # first, draw source object text
                source_name = " %(n)s" % locals() if cm.animated or cm.modelCreated else ""
                col1 = layout.column(align=True)
                col1.label(text="Source Object:%(source_name)s" % locals())
                if not (cm.animated or cm.modelCreated):
                    col2 = layout.column(align=True)
                    col2.prop_search(cm, "source_obj", scn, "objects", text='')

            # initialize variables
            obj = cm.source_obj
            v_str = cm.version[:3]

            # if model created with newer version, disable
            if createdWithNewerVersion(cm):
                col = layout.column(align=True)
                col.scale_y = 0.7
                col.label(text="Model was created with")
                col.label(text="Bricker v%(v_str)s. Please" % locals())
                col.label(text="update Bricker in your")
                col.label(text="addon preferences to edit")
                col.label(text="this model.")
            # if undo stack not initialized, draw initialize button
            elif not bpy.props.bricker_initialized:
                row = col1.row(align=True)
                row.operator("bricker.initialize", text="Initialize Bricker", icon="MODIFIER")
                # draw test brick generator button (for testing purposes only)
                if BRICKER_OT_test_brick_generators.drawUIButton():
                    col = layout.column(align=True)
                    col.operator("bricker.test_brick_generators", text="Test Brick Generators", icon="OUTLINER_OB_MESH")
            # if use animation is selected, draw animation options
            elif cm.useAnimation:
                if cm.animated:
                    row = col1.row(align=True)
                    row.operator("bricker.delete_model", text="Delete Brick Animation", icon="CANCEL")
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    if cm.brickifyingInBackground and cm.framesToAnimate > 0:
                        col.scale_y = 0.75
                        row.label(text="Animating...")
                        row.operator("bricker.stop_brickifying_in_background", text="Stop", icon="PAUSE")
                        row = col.row(align=True)
                        percentage = round(cm.numAnimatedFrames * 100 / cm.framesToAnimate, 2)
                        row.label(text=str(percentage) + "% completed")
                    else:
                        row.active = brickifyShouldRun(cm)
                        row.operator("bricker.brickify", text="Update Animation", icon="FILE_REFRESH")
                    if createdWithUnsupportedVersion(cm):
                        v_str = cm.version[:3]
                        col = layout.column(align=True)
                        col.scale_y = 0.7
                        col.label(text="Model was created with")
                        col.label(text="Bricker v%(v_str)s. Please" % locals())
                        col.label(text="run 'Update Model' so")
                        col.label(text="it is compatible with")
                        col.label(text="your current version.")
                else:
                    row = col1.row(align=True)
                    row.active = obj is not None and obj.type == 'MESH' and (obj.rigid_body is None or obj.rigid_body.type == "PASSIVE")
                    row.operator("bricker.brickify", text="Brickify Animation", icon="MOD_REMESH")
                    if obj and obj.rigid_body is not None:
                        col = layout.column(align=True)
                        col.scale_y = 0.7
                        if obj.rigid_body.type == "ACTIVE":
                            col.label(text="Bake rigid body transforms")
                            col.label(text="to keyframes (SPACEBAR >")
                            col.label(text="Bake To Keyframes).")
                        else:
                            col.label(text="Rigid body settings will")
                            col.label(text="be lost.")
            # if use animation is not selected, draw modeling options
            else:
                if not cm.animated and not cm.modelCreated:
                    row = col1.row(align=True)
                    row.active = obj is not None and obj.type == 'MESH' and (obj.rigid_body is None or obj.rigid_body.type == "PASSIVE")
                    row.operator("bricker.brickify", text="Brickify Object", icon="MOD_REMESH")
                    if obj and obj.rigid_body is not None:
                        col = layout.column(align=True)
                        col.scale_y = 0.7
                        if obj.rigid_body.type == "ACTIVE":
                            col.label(text="Bake rigid body transforms")
                            col.label(text="to keyframes (SPACEBAR >")
                            col.label(text="Bake To Keyframes).")
                        else:
                            col.label(text="Rigid body settings will")
                            col.label(text="be lost.")
                else:
                    row = col1.row(align=True)
                    row.operator("bricker.delete_model", text="Delete Brickified Model", icon="CANCEL")
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    if cm.brickifyingInBackground:
                        row.label(text="Brickifying...")
                        row.operator("bricker.stop_brickifying_in_background", text="Stop", icon="PAUSE")
                        # row = col.row(align=True)
                        # percentage = round(cm.numAnimatedFrames * 100 / cm.framesToAnimate, 2)
                        # row.label(text=str(percentage) + "% completed")
                    else:
                        row.active = brickifyShouldRun(cm)
                        row.operator("bricker.brickify", text="Update Animation", icon="FILE_REFRESH")
                    if createdWithUnsupportedVersion(cm):
                        col = layout.column(align=True)
                        col.scale_y = 0.7
                        col.label(text="Model was created with")
                        col.label(text="Bricker v%(v_str)s. Please" % locals())
                        col.label(text="run 'Update Model' so")
                        col.label(text="it is compatible with")
                        col.label(text="your current version.")
                    elif matrixReallyIsDirty(cm, include_lost_matrix=False) and cm.customized:
                        row = col.row(align=True)
                        row.label(text="Customizations will be lost")
                        row = col.row(align=True)
                        row.operator("bricker.revert_matrix_settings", text="Revert Settings", icon="LOOP_BACK")

            col = layout.column(align=True)
            row = col.row(align=True)

        if bpy.data.texts.find('Bricker log') >= 0:
            split = layout_split(layout, factor=0.9)
            col = split.column(align=True)
            row = col.row(align=True)
            row.operator("bricker.report_error", text="Report Error", icon="URL")
            col = split.column(align=True)
            row = col.row(align=True)
            row.operator("bricker.close_report_error", text="", icon="PANEL_CLOSE")


def is_baked(mod):
    return mod.point_cache.is_baked is not False


class VIEW3D_PT_bricker_animation(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Animation"
    bl_idname      = "VIEW3D_PT_bricker_animation"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        scn, cm, n = getActiveContextInfo()
        if cm.modelCreated:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        if not cm.animated:
            col = layout.column(align=True)
            col.prop(cm, "useAnimation")
        if cm.useAnimation:
            col1 = layout.column(align=True)
            col1.active = cm.animated or cm.useAnimation
            col1.scale_y = 0.85
            row = col1.row(align=True)
            split = layout_split(row, factor=0.5)
            col = split.column(align=True)
            col.prop(cm, "startFrame")
            col = split.column(align=True)
            col.prop(cm, "stopFrame")
            source = cm.source_obj
            self.appliedMods = False
            if source:
                for mod in source.modifiers:
                    if mod.type in ("CLOTH", "SOFT_BODY") and mod.show_viewport:
                        self.appliedMods = True
                        t = mod.type
                        if mod.point_cache.frame_end < cm.stopFrame:
                            s = str(max([mod.point_cache.frame_end+1, cm.startFrame]))
                            e = str(cm.stopFrame)
                        elif mod.point_cache.frame_start > cm.startFrame:
                            s = str(cm.startFrame)
                            e = str(min([mod.point_cache.frame_start-1, cm.stopFrame]))
                        else:
                            s = "0"
                            e = "-1"
                        totalSkipped = int(e) - int(s) + 1
                        if totalSkipped > 0:
                            row = col1.row(align=True)
                            row.label(text="Frames %(s)s-%(e)s outside of %(t)s simulation" % locals())
            if get_addon_preferences().brickifyInBackground != "OFF":
                col = layout.column(align=True)
                row = col.row(align=True)
                row.label(text="Background Processing:")
                row = col.row(align=True)
                row.prop(cm, "maxWorkers")
                row = col.row(align=True)
                row.prop(cm, "backProcTimeout")


class VIEW3D_PT_bricker_model_transform(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Model Transform"
    bl_idname      = "VIEW3D_PT_bricker_model_transform"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        scn, cm, _ = getActiveContextInfo()
        if cm.modelCreated or cm.animated:
            return True
        return False

    def draw(self, context):
        layout = self.layout
        scn, cm, n = getActiveContextInfo()

        col = layout.column(align=True)
        row = col.row(align=True)

        if not (cm.animated or cm.lastSplitModel):
            col.scale_y = 0.7
            row.label(text="Use Blender's built-in")
            row = col.row(align=True)
            row.label(text="transformation manipulators")
            col = layout.column(align=True)
            return

        row.prop(cm, "applyToSourceObject")
        if cm.animated or (cm.lastSplitModel and cm.modelCreated):
            row = col.row(align=True)
            row.prop(cm, "exposeParent")
        row = col.row(align=True)
        parent = bpy.data.objects['Bricker_%(n)s_parent' % locals()]
        row = layout.row()
        row.column().prop(parent, "location")
        if parent.rotation_mode == 'QUATERNION':
            row.column().prop(parent, "rotation_quaternion", text="Rotation")
        elif parent.rotation_mode == 'AXIS_ANGLE':
            row.column().prop(parent, "rotation_axis_angle", text="Rotation")
        else:
            row.column().prop(parent, "rotation_euler", text="Rotation")
        # row.column().prop(parent, "scale")
        layout.prop(parent, "rotation_mode")
        layout.prop(cm, "transformScale")


class VIEW3D_PT_bricker_model_settings(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Model Settings"
    bl_idname      = "VIEW3D_PT_bricker_model_settings"
    bl_context     = "objectmode"

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        if not settingsCanBeDrawn():
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()
        source = cm.source_obj

        col = layout.column(align=True)
        # draw Brick Model dimensions to UI
        if source:
            r = BRICKER_OT_brickify.getModelResolution(source, cm)
            if cm.brickType == "CUSTOM" and r is None:
                col.label(text="[Custom object not found]")
            else:
                split = layout_split(col, factor=0.5)
                col1 = split.column(align=True)
                col1.label(text="Dimensions:")
                col2 = split.column(align=True)
                col2.alignment = "RIGHT"
                col2.label(text="{}x{}x{}".format(int(r.x), int(r.y), int(r.z)))
        row = col.row(align=True)
        row.prop(cm, "brickHeight")
        row = col.row(align=True)
        row.prop(cm, "gap")

        row = col.row(align=True)
        row.label(text="Randomize:")
        row = col.row(align=True)
        split = layout_split(row, factor=0.5)
        col1 = split.column(align=True)
        col1.prop(cm, "randomLoc", text="Loc")
        col2 = split.column(align=True)
        col2.prop(cm, "randomRot", text="Rot")

        col = layout.column(align=True)
        row = col.row(align=True)
        if not cm.useAnimation:
            row = col.row(align=True)
            row.prop(cm, "splitModel")

        row = col.row(align=True)
        row.label(text="Brick Shell:")
        row = col.row(align=True)
        row.prop(cm, "brickShell", text="")
        if cm.brickShell != "INSIDE":
            row = col.row(align=True)
            row.prop(cm, "calculationAxes", text="")
        row = col.row(align=True)
        row.prop(cm, "shellThickness", text="Thickness")
        obj = cm.source_obj
        # if obj and not cm.isWaterTight:
        #     row = col.row(align=True)
        #     # row.scale_y = 0.7
        #     row.label(text="(Source is NOT single closed mesh)")
        #     # row = col.row(align=True)
        #     # row.operator("scene.make_closed_mesh", text="Make Single Closed Mesh")


class VIEW3D_PT_bricker_customize(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Customize Model"
    bl_idname      = "VIEW3D_PT_bricker_customize"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        scn, cm, _ = getActiveContextInfo()
        if createdWithUnsupportedVersion(cm):
            return False
        if not (cm.modelCreated or cm.animated):
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        if matrixReallyIsDirty(cm):
            layout.label(text="Matrix is dirty!")
            col = layout.column(align=True)
            col.label(text="Model must be updated to customize:")
            col.operator("bricker.brickify", text="Update Model", icon="FILE_REFRESH")
            if cm.customized and not cm.matrixLost:
                row = col.row(align=True)
                row.label(text="Prior customizations will be lost")
                row = col.row(align=True)
                row.operator("bricker.revert_matrix_settings", text="Revert Settings", icon="LOOP_BACK")
            return
        if cm.animated:
            layout.label(text="Not available for animations")
            return
        if not cm.lastSplitModel:
            col = layout.column(align=True)
            col.label(text="Model must be split to customize:")
            col.operator("bricker.brickify", text="Split & Update Model", icon="FILE_REFRESH").splitBeforeUpdate = True
            return
        if cm.buildIsDirty:
            col = layout.column(align=True)
            col.label(text="Model must be updated to customize:")
            col.operator("bricker.brickify", text="Update Model", icon="FILE_REFRESH")
            return
        if cm.brickifyingInBackground:
            col = layout.column(align=True)
            col.label(text="Model is brickifying...")
            return
        elif not cacheExists(cm):
            layout.label(text="Matrix not cached!")
            col = layout.column(align=True)
            col.label(text="Model must be updated to customize:")
            col.operator("bricker.brickify", text="Update Model", icon="FILE_REFRESH")
            if cm.customized:
                row = col.row(align=True)
                row.label(text="Customizations will be lost")
                row = col.row(align=True)
                row.operator("bricker.revert_matrix_settings", text="Revert Settings", icon="LOOP_BACK")
            return
        # if not bpy.props.bricker_initialized:
        #     layout.operator("bricker.initialize", icon="MODIFIER")
        #     return

        # # display BrickSculpt tools
        # col = layout.column(align=True)
        # row = col.row(align=True)
        # # brickSculptInstalled = hasattr(bpy.props, "bricksculpt_module_name")
        # # row.active = brickSculptInstalled
        # col.active = False
        # row.label(text="BrickSculpt Tools:")
        # row = col.row(align=True)
        # row.operator("bricker.bricksculpt", text="Draw/Cut Tool", icon="MOD_DYNAMICPAINT").mode = "DRAW"
        # row = col.row(align=True)
        # row.operator("bricker.bricksculpt", text="Merge/Split Tool", icon="MOD_DYNAMICPAINT").mode = "MERGE/SPLIT"
        # row = col.row(align=True)
        # row.operator("bricker.bricksculpt", text="Paintbrush Tool", icon="MOD_DYNAMICPAINT").mode = "PAINT"
        # row.prop_search(cm, "paintbrushMat", bpy.data, "materials", text="")
        # if not BRICKER_OT_bricksculpt.BrickSculptInstalled:
        #     row = col.row(align=True)
        #     row.scale_y = 0.7
        #     row.label(text="BrickSculpt available for purchase")
        #     row = col.row(align=True)
        #     row.scale_y = 0.7
        #     row.label(text="at the Blender Market:")
        #     col = layout.column(align=True)
        #     row = col.row(align=True)
        #     row.operator("wm.url_open", text="View Website", icon="WORLD").url = "http://www.blendermarket.com/products/bricksculpt"
        #     layout.split()
        #     layout.split()

        col1 = layout.column(align=True)
        col1.label(text="Selection:")
        split = layout_split(col1, factor=0.5)
        # set top exposed
        col = split.column(align=True)
        col.operator("bricker.select_bricks_by_type", text="By Type")
        # set bottom exposed
        col = split.column(align=True)
        col.operator("bricker.select_bricks_by_size", text="By Size")

        col1 = layout.column(align=True)
        col1.label(text="Toggle Exposure:")
        split = layout_split(col1, factor=0.5)
        # set top exposed
        col = split.column(align=True)
        col.operator("bricker.set_exposure", text="Top").side = "TOP"
        # set bottom exposed
        col = split.column(align=True)
        col.operator("bricker.set_exposure", text="Bottom").side = "BOTTOM"

        col1 = layout.column(align=True)
        col1.label(text="Brick Operations:")
        split = layout_split(col1, factor=0.5)
        # split brick into 1x1s
        col = split.column(align=True)
        col.operator("bricker.split_bricks", text="Split")
        # merge selected bricks
        col = split.column(align=True)
        col.operator("bricker.merge_bricks", text="Merge")
        # Add identical brick on +/- x/y/z
        row = col1.row(align=True)
        row.operator("bricker.draw_adjacent", text="Draw Adjacent Bricks")
        # change brick type
        row = col1.row(align=True)
        row.operator("bricker.change_brick_type", text="Change Type")
        # change material type
        row = col1.row(align=True)
        row.operator("bricker.change_brick_material", text="Change Material")
        # additional controls
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(cm, "autoUpdateOnDelete")
        # row = col.row(align=True)
        # row.operator("bricker.redraw_bricks")


class VIEW3D_PT_bricker_smoke_settings(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Smoke Settings"
    bl_idname      = "VIEW3D_PT_bricker_smoke_settings"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        if not settingsCanBeDrawn():
            return False
        scn = bpy.context.scene
        if scn.cmlist_index == -1:
            return False
        cm = scn.cmlist[scn.cmlist_index]
        source = cm.source_obj
        if source is None:
            return False
        return is_smoke(source)

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()
        source = cm.source_obj

        col = layout.column(align=True)
        if is_smoke(source):
            row = col.row(align=True)
            row.prop(cm, "smokeDensity", text="Density")
            row = col.row(align=True)
            row.prop(cm, "smokeQuality", text="Quality")

        if is_smoke(source):
            col = layout.column(align=True)
            row = col.row(align=True)
            row.label(text="Smoke Color:")
            row = col.row(align=True)
            row.prop(cm, "smokeBrightness", text="Brightness")
            row = col.row(align=True)
            row.prop(cm, "smokeSaturation", text="Saturation")
            row = col.row(align=True)
            row.label(text="Flame Color:")
            row = col.row(align=True)
            row.prop(cm, "flameColor", text="")
            row = col.row(align=True)
            row.prop(cm, "flameIntensity", text="Intensity")


class VIEW3D_PT_bricker_brick_types(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Brick Types"
    bl_idname      = "VIEW3D_PT_bricker_brick_types"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(cm, "brickType", text="")

        if mergableBrickType(cm.brickType):
            col = layout.column(align=True)
            col.label(text="Max Brick Size:")
            row = col.row(align=True)
            row.prop(cm, "maxWidth", text="Width")
            row.prop(cm, "maxDepth", text="Depth")
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(cm, "legalBricksOnly")

        if cm.brickType == "CUSTOM":
            col = layout.column(align=True)
            col.label(text="Brick Type Object:")
        elif cm.lastSplitModel:
            col.label(text="Custom Brick Objects:")
        if cm.brickType == "CUSTOM" or cm.lastSplitModel:
            for prop in ("customObject1", "customObject2", "customObject3"):
                if prop[-1] == "2" and cm.brickType == "CUSTOM":
                    col.label(text="Distance Offset:")
                    row = col.row(align=True)
                    row.prop(cm, "distOffset", text="")
                    col = layout.column(align=True)
                    col.label(text="Other Objects:")
                split = layout_split(col, factor=0.825)
                col1 = split.column(align=True)
                col1.prop_search(cm, prop, scn, "objects", text="")
                col1 = split.column(align=True)
                col1.operator("bricker.redraw_custom_bricks", icon="FILE_REFRESH", text="").target_prop = prop


class VIEW3D_PT_bricker_merge_settings(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Merge Settings"
    bl_idname      = "VIEW3D_PT_bricker_merge_settings"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        scn = bpy.context.scene
        if scn.cmlist_index == -1:
            return False
        cm = scn.cmlist[scn.cmlist_index]
        return mergableBrickType(cm.brickType)

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(cm, "mergeType", text="")
        if cm.mergeType == "RANDOM":
            row = col.row(align=True)
            row.prop(cm, "mergeSeed")
            row = col.row(align=True)
            row.prop(cm, "connectThresh")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(cm, "mergeInternals")
        if cm.brickType == "BRICKS AND PLATES":
            row = col.row(align=True)
            row.prop(cm, "alignBricks")
            if cm.alignBricks:
                row = col.row(align=True)
                row.prop(cm, "offsetBrickLayers")


class VIEW3D_PT_bricker_materials(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Materials"
    bl_idname      = "VIEW3D_PT_bricker_materials"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}
    # COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        if not settingsCanBeDrawn():
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()
        obj = cm.source_obj

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(cm, "materialType", text="")

        if cm.materialType == "CUSTOM":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(cm, "customMat", text="")
            if brick_materials_installed() and not brick_materials_loaded():
                row = col.row(align=True)
                row.operator("abs.append_materials", text="Import Brick Materials", icon="IMPORT")
            if cm.modelCreated or cm.animated:
                col = layout.column(align=True)
                row = col.row(align=True)
                row.operator("bricker.apply_material", icon="FILE_TICK")
        elif cm.materialType == "RANDOM":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(cm, "randomMatSeed")
            if cm.modelCreated or cm.animated:
                if cm.materialIsDirty and not cm.lastSplitModel:
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.label(text="Run 'Update Model' to apply changes")
                elif cm.lastMaterialType == cm.materialType or (not cm.useAnimation and cm.lastSplitModel):
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.operator("bricker.apply_material", icon="FILE_TICK")
            col = layout.column(align=True)
        elif cm.materialType == "SOURCE" and obj:
            col = layout.column(align=True)
            col.active = len(obj.data.uv_layers) > 0
            row = col.row(align=True)
            row.prop(cm, "useUVMap", text="Use UV Map")
            if cm.useUVMap:
                split = layout_split(row, factor=0.75)
                split.prop(cm, "uvImage", text="")
                split.operator("image.open", icon="FILEBROWSER" if b280() else "FILESEL", text="")
            if len(obj.data.vertex_colors) > 0:
                col = layout.column(align=True)
                col.scale_y = 0.7
                col.label(text="(Vertex colors not supported)")
            if cm.shellThickness > 1 or cm.internalSupports != "NONE":
                if len(obj.data.uv_layers) <= 0 or len(obj.data.vertex_colors) > 0:
                    col = layout.column(align=True)
                row = col.row(align=True)
                row.label(text="Internal Material:")
                row = col.row(align=True)
                row.prop(cm, "internalMat", text="")
                row = col.row(align=True)
                row.prop(cm, "matShellDepth")
                if cm.modelCreated:
                    row = col.row(align=True)
                    if cm.matShellDepth <= cm.lastMatShellDepth:
                        row.operator("bricker.apply_material", icon="FILE_TICK")
                    else:
                        row.label(text="Run 'Update Model' to apply changes")

            col = layout.column(align=True)
            row = col.row(align=True)
            row.label(text="Color Snapping:")
            row = col.row(align=True)
            row.prop(cm, "colorSnap", text="")
            if cm.colorSnap == "RGB":
                row = col.row(align=True)
                row.prop(cm, "colorSnapAmount")
            if cm.colorSnap == "ABS":
                row = col.row(align=True)
                row.prop(cm, "transparentWeight", text="Transparent Weight")

        if cm.materialType == "RANDOM" or (cm.materialType == "SOURCE" and cm.colorSnap == "ABS"):
            matObj = getMatObject(cm.id, typ="RANDOM" if cm.materialType == "RANDOM" else "ABS")
            if matObj is None:
                createNewMatObjs(cm.id)
            else:
                if not brick_materials_installed():
                    col.label(text="'ABS Plastic Materials' not installed")
                elif scn.render.engine not in ('CYCLES', 'BLENDER_EEVEE'):
                    col.label(text="Switch to 'Cycles' or 'Eevee' for Brick Materials")
                else:
                    # draw materials UI list and list actions
                    numMats = len(matObj.data.materials)
                    rows = 5 if numMats > 5 else (numMats if numMats > 2 else 2)
                    split = layout_split(col, factor=0.85)
                    col1 = split.column(align=True)
                    col1.template_list("MATERIAL_UL_matslots", "", matObj, "material_slots", matObj, "active_material_index", rows=rows)
                    col1 = split.column(align=True)
                    col1.operator("bricker.mat_list_action", icon='REMOVE' if b280() else 'ZOOMOUT', text="").action = 'REMOVE'
                    col1.scale_y = 1 + rows
                    if not brick_materials_loaded():
                        col.operator("abs.append_materials", text="Import Brick Materials", icon="IMPORT")
                    else:
                        col.operator("bricker.add_abs_plastic_materials", text="Add ABS Plastic Materials", icon="ADD" if b280() else "ZOOMIN")
                    # settings for adding materials
                    if hasattr(bpy.props, "abs_mats_common"):  # checks that ABS plastic mats are at least v2.1
                        col = layout.column(align=True)
                        row = col.row(align=True)
                        row.prop(scn, "include_transparent")
                        row = col.row(align=True)
                        row.prop(scn, "include_uncommon")

                    col = layout.column(align=True)
                    split = layout_split(col, factor=0.25)
                    col = split.column(align=True)
                    col.label(text="Add:")
                    col = split.column(align=True)
                    col.prop_search(cm, "targetMaterial", bpy.data, "materials", text="")

        if cm.materialType == "SOURCE" and obj:
            noUV = scn.render.engine in ("CYCLES", "BLENDER_EEVEE") and cm.colorSnap != "NONE" and (not cm.useUVMap or len(obj.data.uv_layers) == 0)
            if noUV:
                col = layout.column(align=True)
                col.scale_y = 0.5
                col.label(text="Based on RGB value of first")
                col.separator()
                if scn.render.engine == "octane":
                    nodeNamesStr = "'Octane Diffuse' node"
                elif scn.render.engine == "LUXCORE":
                    nodeNamesStr = "'Matte Material' node"
                else:
                    nodeNamesStr = "'Diffuse' or 'Principled' node"
                col.label(text=nodeNamesStr)
            if cm.colorSnap == "RGB" or (cm.useUVMap and len(obj.data.uv_layers) > 0 and cm.colorSnap == "NONE"):
                if scn.render.engine in ("CYCLES", "BLENDER_EEVEE", "octane"):
                    col = layout.column(align=True)
                    col.label(text="Material Properties:")
                    row = col.row(align=True)
                    row.prop(cm, "colorSnapSpecular")
                    row = col.row(align=True)
                    row.prop(cm, "colorSnapRoughness")
                    row = col.row(align=True)
                    row.prop(cm, "colorSnapIOR")
                if scn.render.engine in ("CYCLES", "BLENDER_EEVEE"):
                    row = col.row(align=True)
                    row.prop(cm, "colorSnapSubsurface")
                    row = col.row(align=True)
                    row.prop(cm, "colorSnapSubsurfaceSaturation")
                    row = col.row(align=True)
                    row.prop(cm, "colorSnapTransmission")
                if scn.render.engine in ("CYCLES", "BLENDER_EEVEE", "octane"):
                    row = col.row(align=True)
                    row.prop(cm, "includeTransparency")
                col = layout.column(align=False)
                col.scale_y = 0.5
                col.separator()
            elif noUV:
                col.separator()



class VIEW3D_PT_bricker_detailing(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Detailing"
    bl_idname      = "VIEW3D_PT_bricker_detailing"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        if cm.brickType == "CUSTOM":
            col = layout.column(align=True)
            col.scale_y = 0.7
            row = col.row(align=True)
            row.label(text="(not applied to custom")
            row = col.row(align=True)
            row.label(text="brick types)")
            layout.separator()
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Studs:")
        row = col.row(align=True)
        row.prop(cm, "studDetail", text="")
        row = col.row(align=True)
        row.label(text="Logo:")
        row = col.row(align=True)
        row.prop(cm, "logoType", text="")
        if cm.logoType != "NONE":
            if cm.logoType == "LEGO":
                row = col.row(align=True)
                row.prop(cm, "logoResolution", text="Resolution")
                row.prop(cm, "logoDecimate", text="Decimate")
                row = col.row(align=True)
            else:
                row = col.row(align=True)
                row.prop_search(cm, "logoObject", scn, "objects", text="")
                row = col.row(align=True)
                row.prop(cm, "logoScale", text="Scale")
            row.prop(cm, "logoInset", text="Inset")
            col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Underside:")
        row = col.row(align=True)
        row.prop(cm, "hiddenUndersideDetail", text="")
        row.prop(cm, "exposedUndersideDetail", text="")
        row = col.row(align=True)
        row.label(text="Cylinders:")
        row = col.row(align=True)
        row.prop(cm, "circleVerts")
        row = col.row(align=True)
        row.prop(cm, "loopCut")
        row.active = not (cm.studDetail == "NONE" and cm.exposedUndersideDetail == "FLAT" and cm.hiddenUndersideDetail == "FLAT")

        row = col.row(align=True)
        split = layout_split(row, factor=0.5)
        col1 = split.column(align=True)
        col1.label(text="Bevel:")
        if not (cm.modelCreated or cm.animated):
            row = col.row(align=True)
            row.prop(cm, "bevelAdded", text="Bevel Bricks")
            return
        try:
            testBrick = getBricks()[0]
            bevel = testBrick.modifiers[testBrick.name + '_bvl']
            col2 = split.column(align=True)
            row = col2.row(align=True)
            row.prop(cm, "bevelShowRender", icon="RESTRICT_RENDER_OFF", toggle=True)
            row.prop(cm, "bevelShowViewport", icon="RESTRICT_VIEW_OFF", toggle=True)
            row.prop(cm, "bevelShowEditmode", icon="EDITMODE_HLT", toggle=True)
            row = col.row(align=True)
            row.prop(cm, "bevelWidth", text="Width")
            row = col.row(align=True)
            row.prop(cm, "bevelSegments", text="Segments")
            row = col.row(align=True)
            row.prop(cm, "bevelProfile", text="Profile")
            row = col.row(align=True)
            row.operator("bricker.bevel", text="Remove Bevel", icon="CANCEL")
        except (IndexError, KeyError):
            row = col.row(align=True)
            row.operator("bricker.bevel", text="Bevel bricks", icon="MOD_BEVEL")


class VIEW3D_PT_bricker_supports(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Supports"
    bl_idname      = "VIEW3D_PT_bricker_supports"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(cm, "internalSupports", text="")
        col = layout.column(align=True)
        row = col.row(align=True)
        if cm.internalSupports == "LATTICE":
            row.prop(cm, "latticeStep")
            row = col.row(align=True)
            row.active == cm.latticeStep > 1
            row.prop(cm, "latticeHeight")
            row = col.row(align=True)
            row.prop(cm, "alternateXY")
        elif cm.internalSupports == "COLUMNS":
            row.prop(cm, "colThickness")
            row = col.row(align=True)
            row.prop(cm, "colStep")
        obj = cm.source_obj
        # if obj and not cm.isWaterTight:
        #     row = col.row(align=True)
        #     # row.scale_y = 0.7
        #     row.label(text="(Source is NOT single closed mesh)")


class VIEW3D_PT_bricker_advanced(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Advanced"
    bl_idname      = "VIEW3D_PT_bricker_advanced"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, n = getActiveContextInfo()

        # Alert user that update is available
        if addon_updater_ops.updater.update_ready:
            col = layout.column(align=True)
            col.scale_y = 0.7
            col.label(text="Bricker update available!", icon="INFO")
            col.label(text="Install from Bricker addon prefs")
            layout.separator()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("bricker.clear_cache", text="Clear Cache")
        row = col.row(align=True)
        row.label(text="Insideness:")
        row = col.row(align=True)
        row.prop(cm, "insidenessRayCastDir", text="")
        row = col.row(align=True)
        row.prop(cm, "castDoubleCheckRays")
        row = col.row(align=True)
        row.prop(cm, "useNormals")
        row = col.row(align=True)
        row.prop(cm, "verifyExposure")
        row = col.row(align=True)
        row.label(text="Meshes:")
        row = col.row(align=True)
        row.prop(cm, "instanceBricks")
        if not cm.useAnimation and not (cm.modelCreated or cm.animated):
            row = col.row(align=True)
            row.label(text="Model Orientation:")
            row = col.row(align=True)
            row.prop(cm, "useLocalOrient", text="Use Source Local")
        # draw test brick generator button (for testing purposes only)
        if BRICKER_OT_test_brick_generators.drawUIButton():
            col = layout.column(align=True)
            col.operator("bricker.test_brick_generators", text="Test Brick Generators", icon="OUTLINER_OB_MESH")


class VIEW3D_PT_bricker_matrix_details(Panel):
    """ Display Matrix details for specified brick location """
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Brick Details"
    bl_idname      = "VIEW3D_PT_bricker_matrix_details"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if bpy.props.Bricker_developer_mode == 0:
            return False
        if not settingsCanBeDrawn():
            return False
        scn, cm, _ = getActiveContextInfo()
        if createdWithUnsupportedVersion(cm):
            return False
        if not (cm.modelCreated or cm.animated):
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        if matrixReallyIsDirty(cm):
            layout.label(text="Matrix is dirty!")
            return
        if not cacheExists(cm):
            layout.label(text="Matrix not cached!")
            return

        col1 = layout.column(align=True)
        row = col1.row(align=True)
        row.prop(cm, "activeKey", text="")

        if cm.animated:
            bricksDict = getBricksDict(cm, dType="ANIM", curFrame=getAnimAdjustedFrame(scn.frame_current, cm.lastStartFrame, cm.lastStopFrame))
        elif cm.modelCreated:
            bricksDict = getBricksDict(cm)
        if bricksDict is None:
            layout.label(text="Matrix not available")
            return
        try:
            dictKey = listToStr(tuple(cm.activeKey))
            brickD = bricksDict[dictKey]
        except Exception as e:
            layout.label(text="No brick details available")
            if len(bricksDict) == 0:
                print("[Bricker] Skipped drawing Brick Details")
            elif str(e)[1:-1] == dictKey:
                pass
                # print("[Bricker] Key '" + str(dictKey) + "' not found")
            elif dictKey is None:
                print("[Bricker] Key not set (entered else)")
            else:
                print("[Bricker] Error fetching brickD:", e)
            return

        col1 = layout.column(align=True)
        split = layout_split(col1, factor=0.35)
        # hard code keys so that they are in the order I want
        keys = ["name", "val", "draw", "co", "near_face", "near_intersection", "near_normal", "mat_name", "custom_mat_name", "rgba", "parent", "size", "attempted_merge", "top_exposed", "bot_exposed", "type", "flipped", "rotated", "created_from"]
        # draw keys
        col = split.column(align=True)
        col.scale_y = 0.65
        row = col.row(align=True)
        row.label(text="key:")
        for key in keys:
            row = col.row(align=True)
            row.label(text=key + ":")
        # draw values
        col = split.column(align=True)
        col.scale_y = 0.65
        row = col.row(align=True)
        row.label(text=dictKey)
        for key in keys:
            row = col.row(align=True)
            row.label(text=str(brickD[key]))

class VIEW3D_PT_bricker_export(Panel):
    """ Export Bricker Model """
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Bake/Export"
    bl_idname      = "VIEW3D_PT_bricker_export"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settingsCanBeDrawn():
            return False
        scn, cm, _ = getActiveContextInfo()
        if createdWithUnsupportedVersion(cm):
            return False
        if not (cm.modelCreated or cm.animated):
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = getActiveContextInfo()

        col = layout.column(align=True)
        col.operator("bricker.bake_model", icon="OBJECT_DATA")
        col = layout.column(align=True)
        col.prop(cm, "exportPath", text="")
        col = layout.column(align=True)
        if (cm.modelCreated or cm.animated) and cm.brickType != "CUSTOM":
            row = col.row(align=True)
            row.operator("bricker.export_ldraw", text="Export Ldraw", icon="EXPORT")
        if bpy.props.Bricker_developer_mode > 0:
            row = col.row(align=True)
            row.operator("bricker.export_model_data", text="Export Model Data", icon="EXPORT")
