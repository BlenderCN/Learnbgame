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
    "name"        : "Render Farm Client",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (0, 7, 5),
    "blender"     : (2, 78, 0),
    "description" : "Render your scene on a custom server farm with this addon.",
    "location"    : "View3D > Tools > Render",
    "warning"     : "Relatively stable but still work in progress",
    "wiki_url"    : "",
    "tracker_url" : "",
    "category"    : "Render"}

# System imports
#None!!

# Blender imports
import bpy
from bpy.types import Operator, Scene
from bpy.props import *

# Render Farm imports
from .ui import *
from .lib import *
from .buttons import *
from .functions import *

# store keymaps here to access after registration
addon_keymaps = []

def more_menu_options(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("render_farm.render_frame_on_servers", text="Render Image on Servers", icon='RENDER_STILL')
    layout.operator("render_farm.render_animation_on_servers", text="Render Animation on Servers", icon='RENDER_ANIMATION')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_render.append(more_menu_options)

    bpy.props.rfc_module_name = __name__
    bpy.props.rfc_version = str(bl_info["version"])[1:-1].replace(", ", ".")

    Scene.rfc_showAdvanced = BoolProperty(
        name="Show Advanced",
        description="Display advanced remote server settings",
        default=False)

    Scene.rfc_killPython = BoolProperty(
        name="Kill Python",
        description="Run 'killall -9 python' on host server after render process cancelled",
        default=False)

    Scene.rfc_compress = BoolProperty(
        name="Compress",
        description="Send compressed Blender file to host server (slower local save, faster file transfer)",
        default=True)

    Scene.rfc_frameRanges = StringProperty(
        name="Frames",
        description="Define frame ranges to render, separated by commas (e.g. '1,3,6-10')",
        default="")

    Scene.rfc_tempLocalDir = StringProperty(
        name="Temp Local Path",
        description="File path on local drive to store temporary project files",
        maxlen=128,
        default="/tmp/",
        subtype="DIR_PATH")

    Scene.rfc_renderDumpLoc = StringProperty(
        name="Output",
        description="Output path for render files (empty folder recommended)",
        maxlen=128,
        default="//render-dump/",
        subtype="FILE_PATH")

    Scene.rfc_maxServerLoad = IntProperty(
        name="Max Server Load",
        description="Maximum number of frames to be handled at once by each server",
        min=1, max=8,
        default=1)

    Scene.rfc_timeout = FloatProperty(
        name="Timeout",
        description="Time (in seconds) to wait for client servers to respond",
        min=.001, max=1,
        default=.01)

    Scene.rfc_samplesPerFrame = IntProperty(
        name="Samples Per Job",
        description="Number of samples to render per job when rendering current frame (try increasing if your image previews are losing light)",
        min=10, max=999,
        default=10)

    Scene.rfc_maxSamples = IntProperty(
        name="Max Samples",
        description="Maximum number of samples to render when rendering current frame",
        min=100, max=9999,
        default=1000)

    Scene.rfc_renderDevice = EnumProperty(
        name="Device",
        description="Device to use for remote rendering",
        items=[("GPU", "GPU Compute", "Use GPU compute device for remote rendering"),
               ("CPU", "CPU", "Use CPU for remote rendering")],
        default="CPU")
    Scene.rfc_renderTiles = IntVectorProperty(
        name="Render Tiles",
        description="Tile size to use for remote rendering",
        size=2,
        subtype="XYZ",
        default=[32, 32])
    Scene.rfc_cyclesComputeDevice = EnumProperty(
        name="Cycles Compute Device",
        description="Cycles compute device for remote rendering",
        items=[("DEFAULT", "Default", "Use default compute device on remote server"),
               ("NONE", "None", "Don't use compute device"),
               ("CUDA", "CUDA", "Use CUDA for remote rendering if available"),
               ("OPENCL", "OpenCL", "Use OpenCL for remote rendering if available")],
        default="DEFAULT")

    Scene.rfc_imagePreviewAvailable = BoolProperty(default=False)
    Scene.rfc_animPreviewAvailable = BoolProperty(default=False)
    Scene.rfc_imageRenderStatus = StringProperty(name="Image Render Status", default="None")
    Scene.rfc_animRenderStatus = StringProperty(name="Image Render Status", default="None")

    # Initialize server and login variables
    Scene.rfc_serverGroups = EnumProperty(
        attr="serverGroups",
        name="Servers",
        description="Choose which hosts to use for render processes",
        items=[("All Servers", "All Servers", "Render on all servers")],
        default="All Servers")
    bpy.props.rfc_lastServerGroup = StringProperty(name="Last Server Group", default="All Servers")
    bpy.props.rfc_serverPrefs = {"servers":None, "login":None, "path":None, "hostConnection":None}
    Scene.rfc_availableServers = IntProperty(name="Available Servers", default=0)
    Scene.rfc_offlineServers = IntProperty(name="Offline Servers", default=0)
    bpy.props.rfc_needsUpdating = BoolProperty(default=True)

    Scene.rfc_nameAveragedImage = StringProperty(default="")
    Scene.rfc_nameImOutputFiles = StringProperty(default="")
    Scene.rfc_imExtension = StringProperty(default="")
    Scene.rfc_animExtension = StringProperty(default="")
    Scene.rfc_imFrame = IntProperty(default=-1)
    bpy.props.rfc_animFrameRange = None

    # register app handlers
    bpy.app.handlers.load_post.append(refresh_servers)
    bpy.app.handlers.load_post.append(verify_render_status_on_load)

    # handle the keymaps
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon: # check this to avoid errors in background case
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        keymaps.addKeymaps(km)
        addon_keymaps.append(km)

def unregister():
    # handle the keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

    # unregister app handlers
    bpy.app.handlers.load_post.remove(refresh_servers)
    bpy.app.handlers.load_post.remove(verify_render_status_on_load)

    del bpy.props.rfc_animFrameRange
    del Scene.rfc_imFrame
    del Scene.rfc_animExtension
    del Scene.rfc_nameImOutputFiles
    del Scene.rfc_imExtension
    del Scene.rfc_nameAveragedImage
    del bpy.props.rfc_serverPrefs
    del Scene.rfc_offlineServers
    del Scene.rfc_availableServers
    del bpy.props.rfc_needsUpdating
    del bpy.props.rfc_lastServerGroup
    del Scene.rfc_serverGroups
    del Scene.rfc_animRenderStatus
    del Scene.rfc_imageRenderStatus
    del Scene.rfc_animPreviewAvailable
    del Scene.rfc_imagePreviewAvailable
    del Scene.rfc_maxSamples
    del Scene.rfc_samplesPerFrame
    del Scene.rfc_timeout
    del Scene.rfc_maxServerLoad
    del Scene.rfc_renderDumpLoc
    del Scene.rfc_tempLocalDir
    del Scene.rfc_frameRanges
    del Scene.rfc_compress
    del Scene.rfc_killPython
    del Scene.rfc_showAdvanced

    bpy.types.INFO_MT_render.remove(more_menu_options)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
