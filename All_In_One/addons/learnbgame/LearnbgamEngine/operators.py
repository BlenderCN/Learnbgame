import os
import subprocess

import bpy
from bpy_extras.io_utils import ExportHelper

import pman


def update_blender_path():
    startdir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None
    if pman.config_exists(startdir):
        user_config = pman.get_user_config(startdir)
        if 'blender' not in user_config:
            user_config['blender'] = {
                'use_last_path': True
            }
        user_config['blender']['last_path'] = bpy.app.binary_path
        pman.write_user_config(user_config)


class ExportBam(bpy.types.Operator, ExportHelper):
    """Export to Panda3D's BAM file format"""
    bl_idname = 'learnbgame_engine.export_bam'
    bl_label = 'Export BAM'

    # copy_images : bpy.props.BoolProperty(
    #     default=True,
    # )

    skip_up_to_date : bpy.props.BoolProperty(
        default=False,
    )

    # For ExportHelper
    filename_ext = '.bam'
    filter_glob : bpy.props.StringProperty(
        default='*.bam',
        options={'HIDDEN'},
    )

    def execute(self, _context):
        filedir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.path.dirname(self.filepath)
        try:
            config = pman.get_config(filedir)
        except pman.NoConfigError as err:
            config = None
        if config:
            user_config = pman.get_user_config(config['internal']['projectdir'])
        else:
            user_config = None

        try:
            pycmd = pman.get_python_program(config)
        except pman.CouldNotFindPythonError as err:
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}

        use_legacy_mats = (
            config is None or
            config['general']['material_mode'] == 'legacy'
        )
        material_mode = 'legacy' if use_legacy_mats else 'pbr'

        # Check if we need to convert the file
        try:
            if self.skip_up_to_date and os.stat(bpy.data.filepath).st_mtime <= os.stat(self.filepath).st_mtime:
                print('"{}" is already up-to-date, skipping'.format(self.filepath))
                return {'FINISHED'}
        except FileNotFoundError:
            # The file doesn't exist, so we cannot skip conversion
            pass

        # Create a temporary blend file to convert
        tmpfname = os.path.join(filedir, '__bp_temp__.blend')
        bpy.ops.wm.save_as_mainfile(filepath=tmpfname, copy=True)

        # Now convert the data to bam
        blend2bam_args = [
            '--blender-dir', os.path.dirname(bpy.app.binary_path),
            '--material-mode', material_mode,
        ]
        blend2bam_args += [
            tmpfname,
            self.filepath
        ]

        retval = {'FINISHED'}
        try:
            if user_config is not None and user_config['python']['in_venv']:
                # Use blend2bam from venv
                pman.run_program(config, ['blend2bam'] + blend2bam_args)
            else:
                # Use bundled blend2bam
                scriptloc = os.path.join(
                    os.path.dirname(__file__),
                    'blend2bam_wrapper.py'
                )
                args = [
                    pycmd,
                    scriptloc
                ] + blend2bam_args
                if subprocess.call(args) != 0:
                    retval = {'CANCELLED'}
        finally:
            # Remove the temporary blend file
            os.remove(tmpfname)

        return retval


class CreateProject(bpy.types.Operator):
    """Setup a new project directory"""
    bl_idname = 'learnbgame_engine.create_project'
    bl_label = 'Create New Project'

    directory : bpy.props.StringProperty(
        name='Project Directory',
        subtype='DIR_PATH',
    )

    switch_dir : bpy.props.BoolProperty(
        name='Switch to directory',
        default=True,
    )

    def execute(self, _context):
        pman.create_project(self.directory)
        config = pman.get_config(self.directory)
        user_config = pman.get_user_config(self.directory)

        from pman import hooks # pylint:disable=no-name-in-module
        hooks.create_blender(self.directory, config, user_config)

        if self.switch_dir:
            os.chdir(self.directory)

        update_blender_path()

        return {'FINISHED'}

    def invoke(self, context, _event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, _context):
        layout = self.layout

        layout.prop(self, 'switch_dir')

class UpdateProject(bpy.types.Operator):
    """Re-copies any missing project files"""
    bl_idname = 'learnbgame_engine.update_project'
    bl_label = 'Update Project Files'

    def execute(self, _context):
        try:
            config = pman.get_config(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None)
            pman.create_project(config['internal']['projectdir'], ['blender'])
            return {'FINISHED'}
        except pman.PManException as err:
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}



class SwitchProject(bpy.types.Operator):
    """Switch to an existing project directory"""
    bl_idname = 'learnbgame_engine.switch_project'
    bl_label = 'Switch Project'

    directory : bpy.props.StringProperty(
        name='Project Directory',
        subtype='DIR_PATH',
    )

    def execute(self, _context):
        os.chdir(self.directory)

        return {'FINISHED'}

    def invoke(self, context, _event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BuildProject(bpy.types.Operator):
    """Build the current project"""
    bl_idname = 'learnbgame_engine.build_project'
    bl_label = 'Build Project'

    def execute(self, _context):
        try:
            config = pman.get_config(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None)
            pman.build(config)
            return {'FINISHED'}
        except pman.PManException as err:
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}


class RunProject(bpy.types.Operator):
    """Run the current project"""
    bl_idname = 'learnbgame_engine.run_project'
    bl_label = 'Run Project'

    def execute(self, _context):
        try:
            config = pman.get_config(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None)
            if config['run']['auto_save']:
                bpy.ops.wm.save_mainfile()
            pman.run(config)
            return {'FINISHED'}
        except pman.PManException as err:
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}


def menu_func_export(self, _context):
    self.layout.operator(ExportBam.bl_idname, text="Panda3D (.bam)")

classes = [
    ExportBam,
    CreateProject,
    UpdateProject,
    SwitchProject,
    BuildProject,
    RunProject,
]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
