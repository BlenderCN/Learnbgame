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
import os
import subprocess

# Blender imports
import bpy
from bpy.types import Operator, Panel

# Addon imports
from ..classes.JobManager import *
from ..functions.common import *


class VIEW3D_PT_background_processing_info(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_label       = "Job Info"
    bl_idname      = "VIEW3D_PT_background_processing_info"
    bl_context     = "objectmode"
    bl_category    = "BackProc"

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        # get the desired JobManager instance (in this case, it uses the scene
        # property which can be exposed to the interface with the commented out
        # code a few lines further down)
        manager = JobManager.get_instance(scn.backproc_manager_index)

        # NOTE: Include the following code if using multiple instances of
        #       JobManager to allow the user to choose the JobManager index.
        # col = layout.column(align=True)
        # row = col.row(align=True)
        # row.prop(scn, "backproc_manager_index")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scn, "backproc_job_type")

        col = layout.column(align=True)
        col.scale_y = 0.7
        row = col.row(align=True)
        row.label(text="Pending Jobs: " + str(manager.num_pending_jobs()))
        row = col.row(align=True)
        row.label(text="Running Jobs: " + str(manager.num_running_jobs()))
        row = col.row(align=True)
        row.label(text="Completed Jobs: " + str(manager.num_completed_jobs()))
        row = col.row(align=True)
        row.label(text="Dropped Jobs: " + str(manager.num_dropped_jobs()))
        row = col.row(align=True)
        row.label(text="Available Workers: " + str(manager.num_available_workers()))

        if scn.backproc_job_type == "QUEUED":
            jobs = manager.get_queued_job_names()
        elif scn.backproc_job_type == "ACTIVE":
            jobs = manager.get_active_job_names()
        elif scn.backproc_job_type == "COMPLETED":
            jobs = manager.get_completed_job_names()
        elif scn.backproc_job_type == "DROPPED":
            jobs = manager.get_dropped_job_names()
        else:
            jobs = manager.get_job_names()
        col = layout.column(align=True)
        i = 0
        for job in sorted(jobs):
            i += 1
            row = col.row(align=True)
            row.label(text="%(i)s) %(job)s" % locals())
            row = col.row(align=True)
            job_status = manager.get_job_status(job)
            if job_status == "ACTIVE":
                split = layout_split(row, factor=0.85)
                col1 = split.column(align=True)
                col1.label(text="Status: " + job_status.capitalize())
                col1 = split.column(align=True)
                col1.operator("backproc.kill_job", text="", icon="CANCEL").job_name = job
            else:
                row.label(text="Status: " + job_status.capitalize())
            layout.separator()
