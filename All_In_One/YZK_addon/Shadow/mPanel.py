#
# @file    tools/plugin/blender/Shadow/mPanel.py
# @author  Luke Tokheim, luke@motionshadow.com
# @version 2.5
#
# (C) Copyright Motion Workshop 2017. All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Motion Workshop, which is protected by
# US federal copyright law and by international treaties.
#
# The Data may not be disclosed or distributed to third parties, in whole
# or in part, without the prior written consent of Motion Workshop.
#
# The Data is provided "as is" without express or implied warranty, and
# with no claim as to its suitability for any purpose.
#

import bpy
from . import MotionSDK as SDK


class ShadowPanel(bpy.types.Panel):
    """
    Basic Blender control panel for the Shadow commands. Just provide
    convenient access to preview, pose, and recording commands from the
    3D View > Tools (T) panel.
    """
    bl_idname = "ShadowPanel"
    bl_label = "Shadow"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("mdevice.start",
                     text="Start Preview")

        col = self.layout.column(align=True)
        col.operator("motion.lua",
                     text="Reset Position").command = "set_pose"
        col.operator("motion.lua",
                     text="Create Rest Pose").command = "set_pose_marker"

        col = self.layout.column(align=True)
        col.operator("motion.lua",
                     text="Start Take").command = "start_take"
        col.operator("motion.lua",
                     text="Stop Take").command = "stop_take"

        col = self.layout.column(align=True)
        col.operator("motion.import_take",
                     text="Import Take").filetype = "csv"


class LuaNode:
    """
    Container class for a static connection to the Lua console service.
    """
    # Static class members, MotionSDK.Client.
    Client = None
    Host = "127.0.0.1"
    Port = 32075

    def get_client(self):
        """
        Internal use. Return a LuaConsole scripting node to send remote
        commands to the server.
        """
        if LuaNode.Client is None:
            try:
                LuaNode.Client = SDK.Client(LuaNode.Host, LuaNode.Port)

                print("Connected to Lua console on device server at \"%s\""
                      % LuaNode.Host)
            except:
                LuaNode.Client = None
                raise RuntimeError("Failed to connect device server at \"%s\""
                                   % LuaNode.Host)

        return LuaNode.Client

    def get_node(self):
        """
        Internal use. Return a LuaConsole scripting node to send remote
        commands to the server.
        """
        return SDK.LuaConsole.Node(self.get_client())


class LuaOperator(bpy.types.Operator):
    """
    Generic wrapper for Lua calls to the Motion Service as a Blender Operator.
    Suitable for incorporation into a UI Panel. See the ShadowPanel class for
    example usage.
    """
    bl_idname = "motion.lua"
    bl_label = "Send a Lua command to the Motion Service"

    command = bpy.props.StringProperty()

    def execute(self, context):
        """
        Send the Lua command store in self.command to the Motion Service. For
        example, to start a take send:
          bpy.ops.motion.lua('EXEC_DEFAULT', command="start_take")
        """
        if len(self.command) > 0:
            node = LuaNode().get_node()
            getattr(node, self.command)()

        return {'FINISHED'}


class ImportOperator(bpy.types.Operator):
    """
    Import the current take in the Motion Service into the Blender scene.
    Includes automatic export to BVH, CSV, or FBX as the interchange format.
    """
    bl_idname = "motion.import_take"
    bl_label = "Import the most recent take from the Motion Service"

    filetype = bpy.props.StringProperty(default="csv")

    def execute(self, context):
        node = LuaNode().get_node()

        # Get the current take path name from the device server.
        rc, rs = node.get_take_path()

        if rc:
            # Remove whitespace. There is probably a newline at the end of
            # printed results from the device server.
            filepath = ""
            if rs:
                filepath = rs.strip()

            # Replace the extension.
            for ext in ["mTake", "xml"]:
                if filepath.endswith(ext):
                    filepath = "".join([filepath[0:len(filepath) - len(ext)],
                                       self.filetype])
                    break

            # Export the take from the device server using the requested
            # interchange format.
            if "csv" == self.filetype:
                rc, rs = node.export_stream(filepath)
            elif "bvh" == self.filetype:
                rc, rs = node.export(filepath)

            if not rc:
                raise RuntimeError("Device server failed to export take to"
                                   " %s: %s" % (self.filetype, rs))

            # Import the animation into the Blender scene.
            if rc:
                if "csv" == self.filetype:
                    bpy.ops.import_anim.shadow('EXEC_DEFAULT',
                                               filepath=filepath)
                elif "bvh" == self.filetype:
                    bpy.ops.import_anim.bvh('EXEC_DEFAULT',
                                            filepath=filepath,
                                            global_scale=0.1,
                                            use_fps_scale=True,
                                            axis_forward='X',
                                            axis_up='Y')
                elif "fbx" == self.filetype:
                    bpy.ops.import_scene.fbx('EXEC_DEFAULT',
                                             filepath=filepath,
                                             automatic_bone_orientation=True)
                else:
                    raise RuntimeError("No valid import file type selected")

                return {'FINISHED'}
        else:
            raise RuntimeError("No current take loaded in the Motion Service")

        return {'CANCELLED'}
