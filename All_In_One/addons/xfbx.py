### BEGIN GPL LICENSE BLOCK #####
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

bl_info = {
    "name": "XFBX",
    "description": "Custom FBX Exporter",
    "author": "Tri Sulistiono",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > XFBX",
    #"warning": "For internal use only!",
    "wiki_url": "https://github.com/stricmp/xfbx/wiki",
    "tracker_url": "https://github.com/stricmp/xfbx/issues",
    "support": "COMMUNITY",
    "category": "Learnbgame",
}

import bpy

from bpy.app.handlers import persistent
from bpy.types import Scene, Panel, Operator
from bpy.utils import register_class, unregister_class, user_resource
from bpy.props import *

import os
import json

# ---------------------------------------------------------------------------
#
# Global vars
#

bInitialized = False
bError = False
aConfig = None
sConfigFile = ""

sPath = ""
sName = ""
bCenter = False
bCollision = False
bTangent = False
eForward = '-Z'
eUp = 'Y'
eSmoothing = 'OFF'


# ---------------------------------------------------------------------------
#
# Make user preferences persistant
#


def SaveConfig(scene):
    #print("*XFBX* Saving " + sConfigFile)

    config = {
        'path': sPath,
        'center': bCenter,
        'collision': bCollision,
        'tangent': bTangent,
        'forward': eForward,
        'up': eUp,
        'smoothing': eSmoothing
        }

    file = open(sConfigFile, "w")
    json.dump(config, file)
    file.close()


def LoadJSON(path):
    #print("*XFBX* Loading " + path)

    if os.path.isfile(path):
        file = open(path, "r")
        data = None
        try:
            data = json.load(file)
        except:
            print("*XFBX* ERROR: Failed to load " + path)
        file.close()
        return data
    else:
        return None


def LoadConfig(scene):

    global aConfig
    global bError
    global sPath
    global bCenter
    global bCollision
    global bTangent
    global eForward
    global eUp
    global eSmoothing

    bError = False
    aConfig = LoadJSON(sConfigFile)

    if aConfig:

        if 'path' in aConfig:
            sPath = aConfig['path']
        else:
            bError = True

        if 'center' in aConfig:
            bCenter = aConfig['center']
        else:
            bError = True

        if 'collision' in aConfig:
            bCollision = aConfig['collision']
        else:
            bError = True

        if 'tangent' in aConfig:
            bTangent = aConfig['tangent']
        else:
            bError = True

        #if 'forward' in aConfig:
        #    eForward = aConfig['forward']
        #else:
        #    bError = True

        #if 'up' in aConfig:
        #    eUp = aConfig['up']
        #else:
        #    bError = True

        #if 'smoothing' in aConfig:
        #    eSmoothing = aConfig['smoothing']
        #else:
        #    bError = True

    else:
        bError = True

    #print("*XFBX* Config error = " + str(bError))


# ---------------------------------------------------------------------------
#
# UI props and callbacks
#


def BCenter_update(scene, context):
    global bCenter
    bCenter = scene.BCenter
    #print("*XFBX* bCenter = " + str(bCenter))
    SaveConfig(scene)


def BCollision_update(scene, context):
    global bCollision
    bCollision = scene.BCollision
    #print("*XFBX* bCollision = " + str(bCollision))
    SaveConfig(scene)


def BTangent_update(scene, context):
    global bTangent
    bTangent = scene.BTangent
    #print("*XFBX* bTangent = " + str(bTangent))
    SaveConfig(scene)


def EForward_update(scene, context):
    global eForward
    eForward = scene.EForward
    #print("*XFBX* eForward = " + str(eForward))
    SaveConfig(scene)


def EUp_update(scene, context):
    global eUp
    eUp = scene.EUp
    #print("*XFBX* eUp = " + str(eUp))
    SaveConfig(scene)


def ESmoothing_update(scene, context):
    global eSmoothing
    eSmoothing = scene.ESmoothing
    #print("*XFBX* eSmoothing = " + str(eSmoothing))
    SaveConfig(scene)


def SPath_update(scene, context):
    global sPath
    sPath = scene.SPath
    #print("*XFBX* sPath = " + sPath)
    SaveConfig(scene)


# Register our UI properties
def SetupProps(scene):

    Scene.BCenter = BoolProperty(
        name = "Center Pivot",
        default = bCenter,
        update = BCenter_update,
        description = "Move object's pivot point to the world's origin")
    scene['BCenter'] = bCenter

    Scene.BCollision = BoolProperty(
        name = "Also Export Collision",
        default = bCollision,
        update = BCollision_update,
        description = "Auto-include UE4-ish collision objects in the export")
    scene['BCollision'] = bCollision

    Scene.BTangent = BoolProperty(
        name = "Include Tangent",
        default = bTangent,
        update = BTangent_update,
        description = "Include binormal and tangent vectors in the export")
    scene['BTangent'] = bTangent

    smoothing = [
        ('OFF', 'OFF', 'OFF'),
        ('FACE', 'FACE', 'FACE'),
        ('EDGE', 'EDGE' ,'EDGE')
        ]
    Scene.ESmoothing = EnumProperty(
        items = smoothing,
        name = "",
        default = 'OFF',
        update = ESmoothing_update,
        description = "Smoothing type to use")
    scene['ESmoothing'] = 0

    fwaxis = [
        ('X', "X Forward", ""),
        ('Y', "Y Forward", ""),
        ('Z', "Z Forward", ""),
        ('-X', "-X Forward", ""),
        ('-Y', "-Y Forward", ""),
        ('-Z', "-Z Forward", "")
        ]
    Scene.EForward = EnumProperty(
        items = fwaxis,
        name = "Forward",
        default = '-Z',
        update = EForward_update,
        description = "Set the Forward axis")
    scene['EForward'] = 5

    upaxis = [
        ('X', "X Up", ""),
        ('Y', "Y Up", ""),
        ('Z', "Z Up", ""),
        ('-X', "-X Up", ""),
        ('-Y', "-Y Up", ""),
        ('-Z', "-Z Up", "")
        ]
    Scene.EUp = EnumProperty(
        items = upaxis,
        name = "Up",
        default = 'Y',
        update = EUp_update,
        description = "Set the Up axis")
    scene['EUp'] = 1

    Scene.SPath = StringProperty(
        name = "Export Directory",
        default = sPath,
        description = "Export objects to this directory",
        update = SPath_update,
        subtype = 'DIR_PATH')
    scene['SPath'] = sPath


# ---------------------------------------------------------------------------
#
# Main exporter code
#

# Wrap the Blender FBX exporter
# See https://docs.blender.org/api/blender2.8/bpy.ops.export_scene.html
def ExportFBX(self, context):
    global bError

    path = bpy.path.abspath(sPath)

    try:
        bpy.ops.export_scene.fbx(
            filepath = path + sName + '.fbx',
            check_existing = True,
            filter_glob = "*.fbx",
            use_selection = True,
            apply_unit_scale = True,
            apply_scale_options  = 'FBX_SCALE_NONE',
            bake_space_transform = True,
            object_types = {'MESH'},
            use_mesh_modifiers = True,
            mesh_smooth_type = eSmoothing,
            use_mesh_edges = False,
            use_tspace = bTangent,
            use_custom_props = True,
            path_mode = 'AUTO',
            embed_textures = False,
            batch_mode = 'OFF',
            use_batch_own_dir = False,
            use_metadata = True,
            axis_forward = eForward,
            axis_up = eUp
            )
    except e:
        self.report({'ERROR'}, "*XFBX* ERROR! " + sName + " : " + repr(e))
        bError = True

    #print ("*XFBX* Exported: " + sName)


# Main export procedure
def ExportObjects(self, context):
    global sName
    global bError
    global bTangent

    # Just so our user know that we are progressing
    self.report({'INFO'}, "*XFBX* Exporting... ")

    bError = False

    # Create a collection to process each selected object later
    exp = bpy.data.collections.new("_coexp_")
    bpy.context.scene.collection.children.link(exp)

    # Use a separate collection for collision objects
    if bCollision:
        col = bpy.data.collections.new("_cocol_")
        bpy.context.scene.collection.children.link(col)

    # Filter all selected objects into the collection
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            exp.objects.link(obj)

    # Clear selection
    bpy.ops.object.select_all(action = 'DESELECT')

    # Workaround to avoid runtime error when exporting tangent data
    btangent = bTangent

    # Now export each object into a separate .fbx file
    for obj in exp.objects:

        # Use object's name as the "base" of .fbx file name
        sName = obj.name

        # Select and save "base" object's location
        obj.select_set(True)
        cx = obj.location[0]
        cy = obj.location[1]
        cz = obj.location[2]

        # Check if we're ok to export tangent space data
        if btangent:
            bTangent = btangent
            mesh = obj.data
            for poly in mesh.polygons:
                if poly.loop_total > 4:  # Tangent space only support tri/quad
                    bTangent = False  # so we won't export tangent otherwise.
                    break

        # Move cursor to "base" object if needed
        if bCenter and bCollision:
            bpy.ops.view3d.snap_cursor_to_selected()

        # Now search for collision objects if the user want it
        # https://docs.unrealengine.com/en-us/Engine/Content/FBX/StaticMeshes
        if bCollision:

            # Search for base collision objects first
            bpy.ops.object.select_pattern(
                pattern = "U[BCS][PX]_" + sName,
                case_sensitive = True, extend = False)

            # then search for additional objects
            bpy.ops.object.select_pattern(
                pattern = "U[BCS][PX]_" + sName + "_[0-9]*",
                case_sensitive = True, extend = True)

            # Filter all selected objects into the collection
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    col.objects.link(ob)

            # Also do 'tangent check' on collision objects to avoid error
            if bTangent:
                for ob in col.objects:
                    mesh = obj.data
                    for poly in mesh.polygons:
                        if poly.loop_total > 4:
                            bTangent = False
                            break
                    if bTangent == False:
                        break

            # Move collision objects' pivot to "base" object's pivot
            # so all objects will have common pivot position
            if bCenter:
                for ob in col.objects:
                    bpy.ops.object.select_all(action = 'DESELECT')
                    ob.select_set(True)
                    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')

        # Now move all objects to the center
        if bCenter:
            bpy.ops.object.select_all(action = 'DESELECT')
            obj.select_set(True)
            bpy.ops.view3d.snap_cursor_to_center()
            bpy.ops.view3d.snap_selected_to_cursor(use_offset = False)

            if bCollision:
                for ob in col.objects:
                    bpy.ops.object.select_all(action = 'DESELECT')
                    ob.select_set(True)
                    bpy.ops.view3d.snap_selected_to_cursor(use_offset = False)

        # Reselect "base" object
        bpy.ops.object.select_all(action = 'DESELECT')
        obj.select_set(True)
        # and collision objects
        if bCollision:
            for ob in col.objects:
                ob.select_set(True)

        # Request Blender to export
        ExportFBX(self, context)

        bpy.ops.object.select_all(action = 'DESELECT')

        # Restore object position
        if bCenter:
            obj.select_set(True)
            obj.location = (cx,cy,cz)
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.view3d.snap_selected_to_cursor(use_offset = False)
            bpy.ops.object.select_all(action = 'DESELECT')

            # Also restore collision objects' position
            if bCollision:
                # Note: We leave all collision objects to have common origin.
                #   It is intended and what center pivot was initially meant.
                for ob in col.objects:
                    ob.select_set(True)
                    bpy.ops.view3d.snap_selected_to_cursor(use_offset = False)
                    bpy.ops.object.select_all(action = 'DESELECT')

        # Unlink collision objects
        if bCollision:
            for ob in col.objects:
                col.objects.unlink(ob)

        # Bail out on error!
        if bError:
            break

    # Unlink objects
    for obj in exp.objects:
        exp.objects.unlink(obj)

    # Remove all temp collections
    bpy.data.collections.remove(exp)
    if bCollision:
        bpy.data.collections.remove(col)

    if bError == False:
        self.report({'INFO'}, "*XFBX* EXPORT COMPLETE!")

    bTangent = btangent  # Restore global


# EXPORT button
class ExportOperator(Operator):
    """Export selected objects to .fbx file"""

    bl_idname = "xfbx.export"
    bl_label = "EXPORT"

    @classmethod
    def poll(self, context):
        # Ensure we have at least one selected MESH object
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                return True
        return False

    def execute(self, context):
        # Ensure the export path have been set
        if sPath == "":
            self.report({'ERROR'}, "You need to set the export path first!")
        else:
            ExportObjects(self, context)

        return {'FINISHED'}


#Initialize button
class InitOperator(Operator):
    """Initialize the XFBX tool"""

    bl_idname = "xfbx.init"
    bl_label = "Initialize"

    def execute (self, context):
        global bInitialized
        global sConfigFile

        config_path = user_resource('CONFIG')
        sConfigFile = os.path.join(config_path, "xfbx.json")

        LoadConfig(bpy.context.scene)
        SetupProps(bpy.context.scene)

        bInitialized = True

        return {'FINISHED'}


# The main UI
class MainPanel(Panel):
    """XFBX UI in the 3D Viewport"""

    bl_label = "XFBX Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'

    def draw(self, context):

        scene = context.scene

        if bInitialized == False:
            layout = self.layout
            row = layout.row()
            col = row.column(align = True)
            col.operator("xfbx.init", icon = 'VISIBLE_IPO_ON')

        if bInitialized:

            layout = self.layout

            box = layout.box()
            box.label(text = "Export Options", icon = 'EXPORT')

            box1 = box.box()
            col = box1.column()
            col.prop(scene, 'BCenter')
            col.prop(scene, 'BCollision')
            col.prop(scene, 'BTangent')

            box2 = box.box()
            row = box2.row()
            row.label(text = "Axis Settings:")
            col = box2.column()
            col.prop(scene, 'EForward')
            col.prop(scene, 'EUp')

            box3 = box.box()
            row = box3.row()
            row.label(text = "Smoothing:")
            col = box3.column()
            col.prop(scene, 'ESmoothing')

            box4 = box.box()
            row = box4.row()
            row.label(text = "Save To:")
            col = box4.column()
            col.prop(scene, 'SPath', text = "Path")

            col = box.column()
            col.operator("xfbx.export", icon = 'FORWARD')


@persistent
def ReloadConfig(dummy):
    LoadConfig(bpy.context.scene)
    SetupProps(bpy.context.scene)


bpy.app.handlers.load_post.append(ReloadConfig)


def register():
    register_class(MainPanel)
    register_class(InitOperator)
    register_class(ExportOperator)


def unregister():
    unregister_class(MainPanel)
    unregister_class(InitOperator)
    unregister_class(ExportOperator)


if __name__ == "__main__":
    register()
