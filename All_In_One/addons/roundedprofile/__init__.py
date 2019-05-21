# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    "name": "Add rounded profile",
    "category": "Mesh",
    'author': 'Piotr Komisarczyk (komi3D)',
    'version': (0, 0, 1),
    'blender': (2, 7, 6),
    'location': 'SHIFT-A > Mesh > Rounded profile',
    'description': 'Add rounded profile',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh'
}

import os
import sys

TESTS = False

if TESTS == False:
    import bpy

    # To support reload properly, try to access a package var, if it's there, reload everything
    if "local_var" in locals():
        import imp
        imp.reload(RoundedProfilePanel)
        imp.reload(RoundedProfileDetailsPanel)
        imp.reload(AddRoundedProfile)
        imp.reload(ConnectionProperties)
        imp.reload(CornerProperties)
        imp.reload(RoundedProfileProperties)
        imp.reload(Updater)
        imp.reload(RoundedProfileRemoveCorner)
        imp.reload(RoundedProfileAddCorner)
        imp.reload(RoundedProfileResetCounters)

    else:
        from roundedprofile.mesh_add_rounded_panel import RoundedProfilePanel
        from roundedprofile.mesh_add_rounded_panel import RoundedProfileDetailsPanel
        from roundedprofile.custom_properties import ConnectionProperties
        from roundedprofile.custom_properties import CornerProperties
        from roundedprofile.custom_properties import RoundedProfileProperties
        from roundedprofile.mesh_add_rounded_profile import AddRoundedProfile
        from roundedprofile.mesh_updater import Updater
        from roundedprofile.rounded_profile_ops import RoundedProfileRemoveCorner
        from roundedprofile.rounded_profile_ops import RoundedProfileAddCorner
        from roundedprofile.rounded_profile_ops import RoundedProfileResetCounters

    local_var = True

    def menu_func(self, context):
        self.layout.operator(AddRoundedProfile.bl_idname, text = bl_info['name'], icon = "PLUGIN")

    def register():
        bpy.utils.register_class(RoundedProfileRemoveCorner)
        bpy.utils.register_class(RoundedProfileAddCorner)
        bpy.utils.register_class(RoundedProfileResetCounters)
        bpy.utils.register_class(RoundedProfilePanel)
        bpy.utils.register_class(RoundedProfileDetailsPanel)
        bpy.utils.register_class(AddRoundedProfile)
        bpy.utils.register_class(CornerProperties)
        bpy.utils.register_class(ConnectionProperties)
        bpy.utils.register_class(RoundedProfileProperties)
        bpy.types.Object.RoundedProfileProps = bpy.props.CollectionProperty(type = RoundedProfileProperties)
        bpy.types.INFO_MT_mesh_add.append(menu_func)
        pass

    def unregister():
        bpy.utils.unregister_class(RoundedProfileRemoveCorner)
        bpy.utils.unregister_class(RoundedProfileAddCorner)
        bpy.utils.unregister_class(RoundedProfileResetCounters)
        bpy.utils.unregister_class(RoundedProfilePanel)
        bpy.utils.unregister_class(RoundedProfileDetailsPanel)
        bpy.utils.unregister_class(AddRoundedProfile)
        bpy.utils.unregister_class(CornerProperties)
        bpy.utils.unregister_class(ConnectionProperties)
        bpy.utils.unregister_class(RoundedProfileProperties)
        bpy.types.INFO_MT_mesh_add.remove(menu_func)
        pass

if __name__ == "__main__":
    register()
