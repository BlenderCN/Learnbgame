#######################################################

## Copy Blender Info	######
##
## v0.0.1
## Added
## 23-02-19 - Initial start addon & repo

## v0.0.2
## Added
## 23-02-19 - Feedback when data is copied (info sysbar)

## v0.0.3
## Changed
## 23-02-19 - Now using BL internal copy method, easier and less files (Thanks Oleg Stepanov)

## v0.0.4
## Added
## 26-02-19 - After copying bl info call url bugpost direct from this addon (now its just 1 click)

bl_info = {
	"name": "Copy Blender Info",
	"description": "Reports a bug but also copies Blender info such as version, hash, date & time commit. This is handy for when filing a bug",
	"location": "Help Menu > Report a Bug (+info)",
	"author": "Rombout Versluijs",
	"version": (0, 0, 4),
	"blender": (2, 80, 0),
	"wiki_url": "https://github.com/schroef/copy-blender-info",
	"tracker_url": "https://github.com/schroef/copy-blender-info/issues",
	"category": "Learnbgame",
}

import bpy

from bpy.types import (
	Operator
	)


class CAI_OT_CopyInfo(Operator):
	"""Copies Blender info to clipboard which is need to file a bug report"""
	bl_idname="cai.copy_info"
	bl_label="Report a Bug (+info)"

	def execute(self,context):
		version = bpy.app.version_string
		build = bpy.app.build_branch
		comDate = bpy.app.build_commit_date
		comTime = bpy.app.build_commit_time
		buildHash = bpy.app.build_hash
		buildType = bpy.app.build_type

		appInfo = version+", "+buildHash.decode()+", "+comDate.decode()+" "+comTime.decode()
		bpy.context.window_manager.clipboard=appInfo
		bpy.ops.wm.url_open(url="https://developer.blender.org/maniphest/task/edit/form/1")
		self.report({'INFO'}, 'Info copied, ready to paste :)')
		return {'FINISHED'}


def CAI_AddCopyOP(self, context):
	self.layout.operator("cai.copy_info",text="Report a Bug (+info)", icon='URL')#icon='COPYDOWN')

classes = (
	CAI_OT_CopyInfo
)


def register():
	#for cls in classes:
	#	bpy.utils.register_class(cls)
	bpy.utils.register_class(CAI_OT_CopyInfo)
	bpy.types.TOPBAR_MT_help.prepend(CAI_AddCopyOP)

def unregister():
	bpy.types.TOPBAR_MT_help.remove(CAI_AddCopyOP)
	#for cls in reversed(classes):
	#	bpy.utils.unregister_class(cls)
	bpy.utils.unregister_class(CAI_OT_CopyInfo)

if __name__ == "__main__":
	register()
