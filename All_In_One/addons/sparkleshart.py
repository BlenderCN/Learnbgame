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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    'name': 'sparkleshart',
    'author': 'Bassam Kurdali',
    'version': '0.3',
    'blender': (2, 6, 3),
    'location': 'Operator Search',
    'description': 'create production package for tube',
    'wiki_url': 'http://wiki.tube.freefac.org/wiki/sparklesharit',
    'category': 'Scene'}

__bpydoc__ = """
Sparkleshart

makes a production package from a blend file, and shares it via git/sparkleshare
"""

import bpy
from bpy.utils import blend_paths
import os
import shutil


def remote_command(ssh_prefix, command):
    return os.system(' '.join([ssh_prefix, command]))


def main(
    context, project, sparkle, git_path,
    ssh_user, ssh_pass, only_blends, git, me):
    ''' mega function that does all the work '''

	# ssher = os.path.join(project, "lib/python/ssh_gate.py")
    orig = [
        path for path in blend_paths(absolute=True)
            if '.blend' in path or not only_blends]
    my_path = context.blend_data.filepath
    orig.append(my_path)
    # me = os.path.split(my_path)[1].split('.')[0]
    package = os.path.join(sparkle, me)
    filemap = {path: path.replace(project, package) for path in orig}
    #if sparkleshare git doesn't exist, create it.
    # ssh_prefix = [ssher,'keg.hampshire.edu',ssh_user,ssh_pass]
    ssh_prefix = 'ssh {}@keg.hampshire.edu'.format(ssh_user)
    git_repo = os.path.join(git_path, me)
    if git:
        errors = remote_command(ssh_prefix, ' "ls {}"'.format(git_repo))
    else:
        errors = 1

    if git and errors != 0:
        remote_command(
            ssh_prefix,
            '"echo {}|sudo -S git init --bare {}"'.format(ssh_pass, git_repo))
        remote_command(
            ssh_prefix,
            '"echo {}|sudo -S chown -R git:1004 {}"'.format(ssh_pass, git_repo))


    #if local sparklshare doesn't exist, create it
    try:
        os.chdir(package)
    except OSError:
        os.chdir(sparkle)
        if git:
            #sparkleshare must be running!
            os.system(
                "git clone ssh://git@keg.hampshire.edu{}".format(
                    #ssh_pass,
                    os.path.join(git_path,me)))
        else:
            os.mkdir(me)
        os.chdir(package)
    for source in filemap:
        try:
            os.makedirs(os.path.split(filemap[source])[0])
        except OSError:
            print('dir exists')
        try:        
            shutil.copy(source, filemap[source])
        except IsADirectoryError:
            shutil.copytree(source, filemap[source])
    if git:
        os.system("git add *")

        os.system('git commit -m "initial package"')

        os.system("git push origin master")


class MakePackage(bpy.types.Operator):
    bl_idname = "file.make_package"
    bl_label = "Make Package"
    bl_options = {'REGISTER', 'UNDO'}

    project = bpy.props.StringProperty(
        name = "project",
        default = "/home/bassam/projects/hamp/tube")
    package = bpy.props.StringProperty(
        name = "package",
        default = "/home/bassam/packages/tube")
    git_home =bpy.props.StringProperty(
        name = "git_home",
        default = "/home/git/tube")
    ssh_user =bpy.props.StringProperty(
        name = "ssh_user",
        default = "anim")
    pw =bpy.props.StringProperty(
        name = "pw",
        default = "")
    only_blends = bpy.props.BoolProperty(
        name = "only_blends",
        default = True)
    git_it = bpy.props.BoolProperty(
        name = "git_it",
        default = True)
    package_name = bpy.props.StringProperty(name="package_name", default="")

    def invoke(self, context, event):
        self.properties.package_name = os.path.split(
            context.blend_data.filepath)[1].split('.')[0]
        wm = context.window_manager
        wm.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        props = self.properties
        main(
            context, props.project, props.package,
            props.git_home, props.ssh_user,
            props.pw, props.only_blends, props.git_it,
            props.package_name)
        props.pw = ""

        return {'FINISHED'}

    def draw(self, context):
        props = self.properties
        layout = self.layout
        row = layout.row()
        row.prop(props, "package_name")
        row = layout.row()
        row.prop(props, "project")
        row = layout.row()
        row.prop(props, "package")
        row = layout.row()
        row.prop(props, "git_home")
        row = layout.row()
        row.prop(props, "ssh_user")
        row.prop(props, "pw")
        row = layout.row()
        row.prop(props, "only_blends",text="Only blends?")
        row.prop(props, "git_it", text="Send to Git?")

def register():
    bpy.utils.register_class(MakePackage)

def unregister():
    bpy.utils.unregister_class(MakePackage)

if __name__ == "__main__":
    register()









