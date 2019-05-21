# Workflow enhancements for Proxies in Sequencer
# Copyright (C) 2013  Bassam Kurdali
#
# ##### BEGIN GPL LICENSE BLOCK #####
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

# <pep8-80 compliant>
bl_info = {
    'name': 'proxy_workflow',
    'author': 'Bassam Kurdali',
    'version': '0.2',
    'blender': (2, 7, 6),
    'location': 'Video Sequence Editor',
    'description': 'Proxy Workflow enhancement for Sequencer',
    'wiki_url': '',
    'category': 'VSE'}

__bpydoc__ = """
Allow Setting custom directory path rules for a lot of sequences at once, makes
proxy workflow a bit easier
"""
import bpy
import os


def full_path(blender_path):
    '''
    return a demangled filepath
    '''
    return os.path.abspath(bpy.path.abspath(blender_path))


def make_render_remote(remote, local):
    ''' make the symlink between remote and local paths '''
    default_path = os.getcwd()
    os.chdir(local)
    try:
        os.unlink("render_root")
    except:
        pass
    remote = ''.join(remote.split())
    os.symlink(remote,"render_root")
    os.chdir(default_path)


def path_exists(blender_path):
    '''
    demangle a potentially relative path and tell us if it exists
    '''
    return os.path.exists(full_path(blender_path))


def return_scene_path(stored_paths, strip):
    '''
    return the scene path for a strip, create if it doesn't exist
    '''
    if strip.name in stored_paths:
        scene_path = stored_paths[strip.name]
    else:
        scene_path = stored_paths.add()
        scene_path.name = strip.name
        if strip.type == 'MOVIE':
            scene_path.filepath = strip.filepath
        elif strip.type == 'IMAGE':
            scene_path.filepath = strip.directory
    return scene_path


def make_movie_offline(strip, stored_paths):
    '''
    take a strip offline
    '''
    proxy_files = [
        fl for fl in os.listdir(full_path(strip.proxy.directory)) if
        fl.startswith('proxy')]
    proxy_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    largest = proxy_files[-1]
    largest = os.path.join(strip.proxy.directory, largest)
    original = strip.filepath
    scene_path = return_scene_path(stored_paths, strip)
    scene_path.filepath = original
    scene_path.is_offline = True
    strip.filepath = largest


def make_movie_online(strip, stored_paths):
    '''
    take it back online
    '''
    scene_path = stored_paths[strip.name]
    strip.filepath = scene_path.filepath
    scene_path.is_offline = False


def is_linable(strip):
    '''
    tell us if we can go offline
    '''
    return strip.type == 'MOVIE' and all((
                    strip.use_proxy,
                    strip.use_proxy_custom_directory,
                    strip.proxy.directory,
                    path_exists(strip.proxy.directory)))


class OfflineProxiedStrips(bpy.types.Operator):
    '''
    allow fast editing of offline strips by switching actual path
    with largest proxy path - if they use a custom proxy directory
    '''
    bl_idname = 'sequence.offline_proxied_strips'
    bl_label = 'Offline Proxy strips'

    def execute(self, context):
        stored_paths = context.scene.sequencer_paths
        for strip in context.selected_sequences:
            if is_linable(strip):
                if not strip.name in stored_paths or not\
                        stored_paths[strip.name].is_offline:
                    make_movie_offline(strip, stored_paths)
        return {'FINISHED'}


class OnlineProxiedStrips(bpy.types.Operator):
    '''
    return to normal with the strips, where the proxy path is no longer the
    image path, keeps it sane
    '''
    bl_idname = 'sequence.online_proxied_strips'
    bl_label = 'Online Proxy Strips'

    def execute(self, context):
        stored_paths = context.scene.sequencer_paths
        for strip in context.selected_sequences:
            if is_linable(strip):
                if strip.name in stored_paths and\
                        stored_paths[strip.name].is_offline:
                    make_movie_online(strip, stored_paths)
        return {'FINISHED'}


def make_time_stamp(strip):
    '''
    creates a timestamp for the currently selected sequence_strip
    '''
    if strip.type == 'MOVIE':
        path = full_path(strip.filepath)
        time_stamp = os.path.getmtime(path)
        print("path: ", path, ", timestamp: ", time_stamp)
    elif strip.type == 'IMAGE': # only image and move supported
        folder = strip.directory
        elements = strip.elements
        time_stamps = [
            os.path.getmtime(full_path(os.path.join(folder, element.filename)))
                for element in elements]
        time_stamps.sort()
        time_stamp = time_stamps[-1]
    else:
        time_stamp = 0.0
    return time_stamp


def make_timed_proxies(context):
    '''
    create a bunch of proxies but update the timestamps
    '''
    stored_paths = context.scene.sequencer_paths
    bpy.ops.sequencer.rebuild_proxy()
    for strip in context.selected_sequences:
        scene_path = return_scene_path(stored_paths, strip)
        scene_path.time_stamp = make_time_stamp(strip)
        scene_path.has_proxy = True


def check_stale(context, strip):
    '''
    return true if a strip needs its proxy rebuilt
    '''
    scene = context.scene
    stored_paths = scene.sequencer_paths
    if strip.name in stored_paths:
        current = make_time_stamp(strip)
        old = stored_paths[strip.name].time_stamp
        stale = int(current) > int(old)
    else:
        stale = True
    return stale


def check_online(context, strip):
    '''
    return true if strip is online or has never been offlined
    '''
    stored_paths = context.scene.sequencer_paths
    if strip.name not in stored_paths: return True
    return not stored_paths[strip.name].is_offline


class MakeTimedProxies(bpy.types.Operator):
    '''
    Make proxies with timestamps only if the strips need timestamps
    and if they have them if the timestamps are stale
    '''
    bl_idname = 'sequence.make_timed_proxies'
    bl_label = 'Make Timed Proxies'

    @classmethod
    def poll(cls, context):
        return context.area.type == 'SEQUENCE_EDITOR' and\
            context.selected_sequences

    def execute(self, context):
        selected_sequences = [seq for seq in context.selected_sequences]        
        do_sequences = [
            strip for strip in selected_sequences if
            strip.type in ('IMAGE', 'MOVIE') and
            check_stale(context, strip) and
            check_online(context, strip)]
        for seq in context.scene.sequence_editor.sequences_all:
            seq.select = True if seq in do_sequences else False
        make_timed_proxies(context)
        for seq in context.scene.sequence_editor.sequences_all:
            seq.select = True if seq in selected_sequences else False
        return {'FINISHED'}


class SetProxyPaths(bpy.types.Operator):
    '''
    Proxy paths for multiple selected things
    '''
    bl_idname = 'sequence.set_proxy_paths'
    bl_label = 'Set Proxy Paths'

    build_25 = bpy.props.BoolProperty(default=True)
    build_50 = bpy.props.BoolProperty(default=False)
    build_75 = bpy.props.BoolProperty(default=False)
    build_100 = bpy.props.BoolProperty(default=False)
    rebuild = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'SEQUENCE_EDITOR' and\
          context.selected_sequences

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        build_25 = self.properties.build_25
        build_50 = self.properties.build_50
        build_75 = self.properties.build_75
        build_100 = self.properties.build_100
        stored_paths = context.scene.sequencer_paths

        for strip in context.selected_sequences:
            if strip.type in ['MOVIE', 'IMAGE']:  # we can allow others later
                strip.use_proxy = True
                strip.proxy.use_proxy_custom_directory = True
                strip.proxy.use_proxy_custom_file = False
                strip.proxy.build_25 = build_25
                strip.proxy.build_50 = build_50
                strip.proxy.build_75 = build_75
                strip.proxy.build_100 = build_100
                if strip.type == 'IMAGE':
                    strip_path = strip.directory
                else:
                    strip_path = strip.filepath
                path = strip_path.translate({ord(k):None for k in ' ./'})
                mydir = "//Tproxy/{}/".format(path)
                strip.proxy.directory = mydir
                scene_path = stored_paths.add()
                scene_path.name = strip.name
                scene_path.filepath = strip_path
                scene_path.is_offline = False
                scene_path.has_proxy = False
            if self.properties.rebuild:
                make_timed_proxies(context)
        return {'FINISHED'}


class SceneCreateRenderPath(bpy.types.Operator):
    ''' Create Symlinks to Keg for Render '''
    bl_idname = 'scene.create_render_path'
    bl_label = 'Create Symlinks to Keg for Render'
    
    directory = bpy.props.StringProperty(
        default="/var/run/user/1000/gvfs/sftp:host=keg,user=anim/helga/tube",
        subtype='DIR_PATH')
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        directory = self.properties.directory
        remote = full_path(directory)
        local = os.path.split(bpy.data.filepath)[0]
        make_render_remote(remote, local)
        
        return {'FINISHED'}
    

class SequencerPaths(bpy.types.PropertyGroup):
    '''
    storage for sequncer online paths, indexed, sadly, by name
    '''
    filepath = bpy.props.StringProperty(name="filepath", subtype='FILE_PATH')
    is_offline = bpy.props.BoolProperty(default=False)
    time_stamp = bpy.props.IntProperty(default=0)
    has_proxy = bpy.props.BoolProperty(default=False)


def menu_func(self, context):
    self.layout.operator(MakeTimedProxies.bl_idname)
    self.layout.operator(OfflineProxiedStrips.bl_idname)
    self.layout.operator(OnlineProxiedStrips.bl_idname)
    self.layout.operator(SetProxyPaths.bl_idname)
    self.layout.operator(SceneCreateRenderPath.bl_idname)
    self.layout.label(text="Proxy Workflow:")
    self.layout.separator()


def add_hotkey(kc, mode_name, ot, key, shift=False, ctrl=False, alt=False):
        km = kc.keymaps.new(name=mode_name)
        kmi = km.keymap_items.new(
            ot, key, 'PRESS',
            shift=shift, ctrl=ctrl, alt=alt)


def del_hotkey(kc, mode_name, ot):
    km = kc.keymaps[mode_name]
    for kmi in km.keymap_items:
        if kmi.idname == ot:
            km.keymap_items.remove(kmi)


def register():
    bpy.utils.register_class(SequencerPaths)
    bpy.types.Scene.sequencer_paths = bpy.props.CollectionProperty(
        type=SequencerPaths)
    bpy.utils.register_class(MakeTimedProxies)
    bpy.utils.register_class(OfflineProxiedStrips)
    bpy.utils.register_class(OnlineProxiedStrips)
    bpy.utils.register_class(SetProxyPaths)
    bpy.utils.register_class(SceneCreateRenderPath)
    bpy.types.SEQUENCER_MT_strip.prepend(menu_func)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        add_hotkey(
                kc, 'SEQUENCER', 'sequence.set_proxy_paths',
                "A", shift=True, ctrl=True)

def unregister():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        del_hotkey(kc, 'SEQUENCER', 'sequence.set_proxy_paths')
    bpy.types.SEQUENCER_MT_strip.remove(menu_func)
    bpy.utils.unregister_class(MakeTimedProxies)
    bpy.utils.unregister_class(SetProxyPaths)
    bpy.utils.unregister_class(OfflineProxiedStrips)
    bpy.utils.unregister_class(OnlineProxiedStrips)
    bpy.utils.unregister_class(SceneCreateRenderPath)
    del bpy.types.Scene.sequencer_paths
    bpy.utils.unregister_class(SequencerPaths)

if __name__ == "__main__":
    register()
