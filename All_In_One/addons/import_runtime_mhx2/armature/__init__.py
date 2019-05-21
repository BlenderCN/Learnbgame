# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

if "bpy" in locals():
    print("Reloading MHX2 armature")
    import imp
    imp.reload(flags)
    imp.reload(utils)
    imp.reload(rig_joints)
    #imp.reload(rig_bones)
    imp.reload(rig_spine)
    imp.reload(rig_arm)
    imp.reload(rig_leg)
    imp.reload(rig_hand)
    #imp.reload(rig_muscle)
    imp.reload(rig_face)
    imp.reload(rig_control)
    imp.reload(rig_merge)
    imp.reload(rig_panel)
    imp.reload(rig_rigify)
    imp.reload(parser)
    imp.reload(constraints)
    imp.reload(rigify)
    imp.reload(build)
    imp.reload(rerig)
else:
    print("Loading MHX2 armature")
    from . import flags
    from . import utils
    from . import rig_joints
    #from . import rig_bones
    from . import rig_spine
    from . import rig_arm
    from . import rig_leg
    from . import rig_hand
    #from . import rig_muscle
    from . import rig_face
    from . import rig_control
    from . import rig_merge
    from . import rig_panel
    from . import rig_rigify
    from . import parser
    from . import constraints
    from . import rigify
    from . import build
    from . import rerig

import bpy
print("MHX2 armature loaded")
