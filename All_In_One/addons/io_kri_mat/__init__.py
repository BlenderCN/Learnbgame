# <pep8 compliant>

bl_info = {
    'name': 'KRI Material Library',
    'author': 'Dzmitry Malyshau',
    'version': (0, 1, 0),
    'blender': (2, 7, 9),
    'api': 36079,
    'location': 'File > Export > Kri Material (.xml)',
    'description': 'Export all materials into Kri XML scene file, compose GLSL shaders.',
    'warning': '',
    'wiki_url': 'http://code.google.com/p/kri/wiki/Exporter',
    'tracker_url': '',
    'category': 'Import-Export'}

extension = '.xml'

# To support reload properly, try to access a package var, if it's there, reload everything
if 'bpy' in locals():
	import imp
	if 'export_kri_mat' in locals():
	        imp.reload(export_kri_mat)


import bpy
from bpy.props			import *
from bpy_extras.io_utils	import ImportHelper, ExportHelper
from io_kri.common		import Settings
from io_kri_mat.mat		import save_mat


class ExportMat( bpy.types.Operator, ExportHelper ):
	'''Export materials to Kri XML library format'''
	bl_idname	= 'export_mat.kri_mat'
	bl_label	= '-= KRI Material Library=- (%s)' % extension
	filename_ext	= extension

	filepath	= StringProperty( name='File Path',
		description='Filepath used for exporting Kri materials',
		maxlen=1024, default='')
	show_info	= BoolProperty( name='Show infos',
		description='Print information messages (i)',
		default=Settings.showInfo )
	show_warn	= BoolProperty( name='Show warnings',
		description='Print warning messages (w)',
		default=Settings.showWarning )
	break_err	= BoolProperty( name='Break on error',
		description='Stop the process on first error',
		default=Settings.breakError )

	def execute(self, context):
		Settings.showInfo		= self.properties.show_info
		Settings.showWarning	= self.properties.show_warn
		Settings.breakError		= self.properties.break_err
		save_mat(self.properties.filepath, context)
		return {'FINISHED'}


# Add to a menu
def menu_func(self, context):
	self.layout.operator( ExportMat.bl_idname, text= ExportMat.bl_label )

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == '__main__':
	register()
