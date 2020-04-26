# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# Blender Libs
import bpy, bl_operators
import os, re, mathutils, tempfile, shutil, urllib.request, urllib.error, zipfile

# PBRTv3 Libs
from .. import PBRTv3Addon

# Per-IDPropertyGroup preset handling

class PBRTv3_MT_base(bpy.types.Menu):
    preset_operator = "script.execute_preset"

    def draw(self, context):
        return bpy.types.Menu.draw_preset(self, context)


@PBRTv3Addon.addon_register_class
class PBRTv3_MT_presets_engine(PBRTv3_MT_base):
    bl_label = "PBRTv3 Engine Presets"
    preset_subdir = "luxrender/engine"


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_preset_engine_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    """Save the current settings as a preset"""
    bl_idname = 'luxrender.preset_engine_add'
    bl_label = 'Add PBRTv3 Engine settings preset'
    preset_menu = 'PBRTv3_MT_presets_engine'
    preset_values = []
    preset_subdir = 'luxrender/engine'

    def execute(self, context):
        self.preset_values = [
                                 'bpy.context.scene.pbrtv3_engine.%s' % v['attr'] for v in
                                 bpy.types.pbrtv3_engine.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.pbrtv3_sampler.%s' % v['attr'] for v in
                                 bpy.types.pbrtv3_sampler.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.pbrtv3_integrator.%s' % v['attr'] for v in
                                 bpy.types.pbrtv3_integrator.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.pbrtv3_volumeintegrator.%s' % v['attr'] for v in
                                 bpy.types.pbrtv3_volumeintegrator.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.pbrtv3_filter.%s' % v['attr'] for v in
                                 bpy.types.pbrtv3_filter.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.pbrtv3_accelerator.%s' % v['attr'] for v in
                                 bpy.types.pbrtv3_accelerator.get_exportable_properties()
                             ]
        return super().execute(context)


@PBRTv3Addon.addon_register_class
class PBRTv3_MT_presets_networking(PBRTv3_MT_base):
    bl_label = "PBRTv3 Networking Presets"
    preset_subdir = "luxrender/networking"


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_preset_networking_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    '''Save the current settings as a preset'''
    bl_idname = 'luxrender.preset_networking_add'
    bl_label = 'Add PBRTv3 Networking settings preset'
    preset_menu = 'PBRTv3_MT_presets_networking'
    preset_values = []
    preset_subdir = 'luxrender/networking'

    def execute(self, context):
        self.preset_values = [
            'bpy.context.scene.pbrtv3_networking.%s' % v['attr'] for v in
            bpy.types.pbrtv3_networking.get_exportable_properties()
        ]
        return super().execute(context)


# Volume data handling

@PBRTv3Addon.addon_register_class
class PBRTv3_MT_presets_volume(PBRTv3_MT_base):
    bl_label = "PBRTv3 Volume Presets"
    preset_subdir = "luxrender/volume"


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_preset_volume_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    """Save the current settings as a preset"""
    bl_idname = 'luxrender.preset_volume_add'
    bl_label = 'Add PBRTv3 Volume settings preset'
    preset_menu = 'PBRTv3_MT_presets_volume'
    preset_values = []
    preset_subdir = 'luxrender/volume'

    def execute(self, context):
        ks = 'bpy.context.scene.pbrtv3_volumes.volumes[bpy.context.scene.pbrtv3_volumes.volumes_index].%s'
        pv = [
            ks % v['attr'] for v in bpy.types.pbrtv3_volume_data.get_exportable_properties()
        ]

        self.preset_values = pv
        return super().execute(context)


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_volume_add(bpy.types.Operator):
    """Add a new material volume definition to the scene"""

    bl_idname = "luxrender.volume_add"
    bl_label = "Add PBRTv3 Volume"

    new_volume_name = bpy.props.StringProperty(default='New Volume 1')

    def create_unique_name(self, context):
        volumes = context.scene.pbrtv3_volumes.volumes
        volume_names = [v.name for v in volumes]
        name = self.new_volume_name

        while name in volume_names:
            m = re.search(r'\d+$', name)

            if m is None: # Can not happen with 'New Volume 1', but leave it in case the default is changed
                # Append a new number
                name += ' 1'
            else:
                # Found a trailing number
                number = m.group()
                # Increment the old number and replace it
                name = name[:len(name) - len(number)] + str(int(name[-len(number):]) + 1)

        self.new_volume_name = name

    def invoke(self, context, event):
        self.new_volume_name = 'New Volume 1'
        volumes = context.scene.pbrtv3_volumes.volumes

        # Create unique volume name
        self.create_unique_name(context)

        volumes.add()
        new_vol = volumes[len(volumes) - 1]
        new_vol.name = self.properties.new_volume_name

        # Switch to the added volume
        context.scene.pbrtv3_volumes.volumes_index = len(volumes) - 1

        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_volume_remove(bpy.types.Operator):
    """Remove the selected material volume definition"""

    bl_idname = "luxrender.volume_remove"
    bl_label = "Remove PBRTv3 Volume"

    def invoke(self, context, event):
        w = context.scene.pbrtv3_volumes
        old_index = w.volumes_index
        w.volumes.remove(w.volumes_index)
        # Switch to the volume above the deleted volume
        w.volumes_index = max(old_index - 1, 0)
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_lightgroup_add(bpy.types.Operator):
    """Add a new light group definition to the scene"""

    bl_idname = "luxrender.lightgroup_add"
    bl_label = "Add PBRTv3 Light Group"

    lg_count = 0
    new_lightgroup_name = bpy.props.StringProperty(default='New Light Group ')

    def invoke(self, context, event):
        lg = context.scene.pbrtv3_lightgroups.lightgroups
        lg.add()
        new_lg = lg[len(lg) - 1]
        new_lg.name = self.properties.new_lightgroup_name + str(PBRTv3_OT_lightgroup_add.lg_count)
        PBRTv3_OT_lightgroup_add.lg_count += 1
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_lightgroup_remove(bpy.types.Operator):
    """Remove the selected lightgroup definition"""

    bl_idname = "luxrender.lightgroup_remove"
    bl_label = "Remove PBRTv3 Light Group"

    lg_index = bpy.props.IntProperty(default=-1)

    def invoke(self, context, event):
        w = context.scene.pbrtv3_lightgroups
        if self.properties.lg_index == -1:
            w.lightgroups.remove(w.lightgroups_index)
        else:
            w.lightgroups.remove(self.properties.lg_index)
        w.lightgroups_index = len(w.lightgroups) - 1
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_materialgroup_add(bpy.types.Operator):
    """Add a new material group definition to the scene"""

    bl_idname = "luxrender.materialgroup_add"
    bl_label = "Add PBRTv3 Material Group"

    mg_count = 0
    new_materialgroup_name = bpy.props.StringProperty(default='New Material Group ')

    def invoke(self, context, event):
        mg = context.scene.pbrtv3_materialgroups.materialgroups
        mg.add()
        new_mg = mg[len(mg) - 1]
        new_mg.name = self.properties.new_materialgroup_name + str(PBRTv3_OT_materialgroup_add.mg_count)
        PBRTv3_OT_materialgroup_add.mg_count += 1
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_materialgroup_remove(bpy.types.Operator):
    """Remove the selected materialgroup definition"""

    bl_idname = "luxrender.materialgroup_remove"
    bl_label = "Remove PBRTv3 Material Group"

    mg_index = bpy.props.IntProperty(default=-1)

    def invoke(self, context, event):
        w = context.scene.pbrtv3_materialgroups
        if self.properties.mg_index == -1:
            w.materialgroups.remove(w.materialgroups_index)
        else:
            w.materialgroups.remove(self.properties.mg_index)
        w.materialgroups_index = len(w.materialgroups) - 1
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_opencl_device_list_update(bpy.types.Operator):
    """Update the OpenCL device list"""

    bl_idname = "luxrender.opencl_device_list_update"
    bl_label = "Update the OpenCL device list"

    def invoke(self, context, event):
        devs = context.scene.luxcore_enginesettings.luxcore_opencl_devices
        # Clear the list
        for i in range(len(devs)):
            devs.remove(0)

        # Create the new list
        from ..outputs.luxcore_api import pyluxcore

        deviceList = pyluxcore.GetOpenCLDeviceList()
        for dev in deviceList:
            devs.add()
            index = len(devs) - 1
            new_dev = devs[index]
            new_dev.name = 'Device ' + str(index) + ': ' + dev[0] + ' (' + dev[1] + ')'

        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_update_luxblend(bpy.types.Operator):
    """Update LuxBlend to the latest version"""
    bl_idname = "luxrender.update_luxblend"
    bl_label = "Update LuxBlend"

    def execute(self, context):
        def recursive_overwrite(src, dest, ignore=None):
            if os.path.isdir(src):
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                files = os.listdir(src)
                if ignore is not None:
                    ignored = ignore(src, files)
                else:
                    ignored = set()
                for f in files:
                    if f not in ignored:
                        recursive_overwrite(os.path.join(src, f),
                                            os.path.join(dest, f),
                                            ignore)
            else:
                shutil.copyfile(src, dest)

        print('-' * 20)
        print('Updating LuxBlend...')

        with tempfile.TemporaryDirectory() as temp_dir_path:
            temp_zip_path = os.path.join(temp_dir_path, 'default.zip')

            # Download LuxBlend zip archive of latest default branch commit
            url = 'https://bitbucket.org/luxrender/luxblend25/get/default.zip'
            try:
                print('Downloading', url)

                with urllib.request.urlopen(url, timeout=60) as url_handle, \
                                   open(temp_zip_path, 'wb') as file_handle:
                    file_handle.write(url_handle.read())
            except urllib.error.URLError as err:
                self.report({'ERROR'}, 'Could not download: %s' % err)

            # Extract the zip
            print('Extracting ZIP archive')
            with zipfile.ZipFile(temp_zip_path) as zip:
                for member in zip.namelist():
                    if 'src/luxrender' in member:
                        # Remove the first two directories and the filename
                        # e.g. luxrender-luxblend25-bfb488c84111/src/luxrender/ui/textures/wrinkled.py
                        # becomes luxrender/ui/textures/
                        target_path = os.path.join(temp_dir_path,
                                        os.path.join(*member.split('/')[2:-1]))

                        filename = os.path.basename(member)
                        # Skip directories
                        if len(filename) == 0:
                            continue

                        # Create the target directory if necessary
                        if not os.path.exists(target_path):
                            os.makedirs(target_path)

                        source = zip.open(member)
                        target = open(os.path.join(target_path, filename), "wb")

                        with source, target:
                            shutil.copyfileobj(source, target)
                            print('copying', source, 'to', target)

            extracted_luxblend_path = os.path.join(temp_dir_path, 'luxrender')

            if not os.path.exists(extracted_luxblend_path):
                self.report({'ERROR'}, 'Could not extract ZIP archive! Aborting.')
                return {'FINISHED'}

            # Find the old LuxBlend files
            luxblend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            print('LuxBlend addon folder:', luxblend_dir)

            # TODO: Create backup


            # Delete old LuxBlend files (only directories and *.py files, the user might have other stuff in there!)
            print('Deleting old LuxBlend files')
            # remove __init__.py
            os.remove(os.path.join(luxblend_dir, '__init__.py'))
            # remove all folders
            DIRNAMES = 1
            for dir in next(os.walk(luxblend_dir))[DIRNAMES]:
                shutil.rmtree(os.path.join(luxblend_dir, dir))

            print('Copying new LuxBlend files')
            # copy new LuxBlend files
            # copy __init__.py
            shutil.copy2(os.path.join(extracted_luxblend_path, '__init__.py'), luxblend_dir)
            # copy all folders
            recursive_overwrite(extracted_luxblend_path, luxblend_dir)

        print('LuxBlend update finished, restart Blender for the changes to take effect.')
        print('-' * 20)
        self.report({'WARNING'}, 'Restart Blender!')
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_open_daily_builds_webpage(bpy.types.Operator):
    """Open the "daily builds" webpage"""
    bl_idname = 'luxrender.open_daily_builds_webpage'
    bl_label = 'Update PBRTv3'

    def execute(self, context):
        import webbrowser
        webbrowser.open('http://www.luxrender.net/forum/viewtopic.php?f=30&t=12147')
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_fix_color_management(bpy.types.Operator):
    """Reset "view", "exposure", "gamma", "look" and "use curves" values. Rendered images might look wrong when these settings are not not the defaults."""

    bl_idname = "luxrender.fix_color_management"
    bl_label = "Reset Color Management to Default"

    def execute(self, context):
        vs = context.scene.view_settings

        if vs.view_transform != 'Default':
            vs.view_transform = 'Default'

        if vs.exposure != 0:
            vs.exposure = 0

        if vs.gamma != 1:
            vs.gamma = 1

        if vs.look != 'None':
            vs.look = 'None'

        if vs.use_curve_mapping:
            vs.use_curve_mapping = False

        return {'FINISHED'}
