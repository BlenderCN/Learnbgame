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

bl_info = {
    "name"        : "Background Processing",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 0, 0),
    "blender"     : (2, 80, 0),
    "description" : "Process in the background with a separate instance of Blender",
    "location"    : "View3D > Tools > Bricker",
    "warning"     : "",  # used for warning icon and text in addons panel
    "wiki_url"    : "",
    "tracker_url" : "",
    "category"    : "Object"}

# Blender imports
import bpy
from bpy.types import Scene

# Addon imports
from .classes import *
from .ui import *
from .functions.common import *

classes = (
    SCENE_OT_add_job,
    SCENE_OT_kill_job,
    VIEW3D_PT_background_processing_tests,
    VIEW3D_PT_background_processing_info,
)

def register():
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    def updateMaxWorkers(self, context):
        curJobManager = JobManager.get_instance()
        curJobManager.max_workers = context.scene.backproc_max_workers

    Scene.backproc_max_workers = IntProperty(
        name="Maximum Workers",
        description="Maximum number of Blender instances to run in the background",
        min=0, max=100,
        update=updateMaxWorkers,
        default=5)

    Scene.backproc_manager_index = IntProperty(
        name="JobManager Index",
        description="Index for the desired JobManager instance",
        default=-1)

    Scene.backproc_job_type = EnumProperty(
        name="Job Type",
        description="Show info for jobs with this status",
        items=(("ALL", "All", ""),
               ("QUEUED", "Queued", ""),
               ("ACTIVE", "Active", ""),
               ("COMPLETED", "Completed", ""),
               ("DROPPED", "Dropped", ""),),
        default="ACTIVE")

def unregister():
    del Scene.backproc_job_type
    del Scene.backproc_manager_index
    del Scene.backproc_max_workers
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
