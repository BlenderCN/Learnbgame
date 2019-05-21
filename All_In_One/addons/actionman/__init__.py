# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Action Man",
    "author": "Loïc Pinsard",
    "description": "",
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "category": "Learnbgame",
}

import bpy
from .operators.cleanaction import CleanAction
from .operators.create_action_constraint import CreateConstraintFromAction
from .operators.delete_useless_constraints import DeleteUselessActionConstraints
from .panels import ActionManPanel


CLASSES_TO_REGISTER = (
    CleanAction,
    CreateConstraintFromAction,
    DeleteUselessActionConstraints,
    ActionManPanel,
)


def register():
    """Register the addon."""
    bpy.types.Action.face_action = bpy.props.BoolProperty(name="Face Action")
    bpy.types.Action.name_backup = bpy.props.StringProperty(name="Name Backup")
    bpy.types.Action.target = bpy.props.StringProperty(name="Target")
    bpy.types.Action.subtarget = bpy.props.StringProperty(name="Sub Target")
    bpy.types.Action.transform_channel = bpy.props.EnumProperty(
        name="Controller Transform Channel",
        items=[
            ("LOCATION_X", " X Location", " X Location", 1),
            ("LOCATION_Y", " Y Location", " Y Location", 2),
            ("LOCATION_Z", " Z Location", " Z Location", 3),
            ("ROTATION_X", "X Rotation", "X Rotation", 4),
            ("ROTATION_Y", "Y Rotation", "Y Rotation", 5),
            ("ROTATION_Z", "Z Rotation", "Z Rotation", 6),
            ("SCALE_X", "X Scale", "X Scale", 7),
            ("SCALE_Y", "Y Scale", "Y Scale", 8),
            ("SCALE_Z", "Z Scale", "Z Scale", 9),
        ],
    )
    bpy.types.Action.activation_start = bpy.props.FloatProperty("Activation Start")
    bpy.types.Action.activation_end = bpy.props.FloatProperty("Activation End")
    for cls in CLASSES_TO_REGISTER:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister the addon."""
    for cls in CLASSES_TO_REGISTER:
        bpy.utils.unregister_class(cls)
    # Don't delete all the properties since they could be needeed even if the addon isn't loaded
    # del bpy.types.Action.face_action
    # del bpy.types.Action.target
    # del bpy.types.Action.subtarget
    # del bpy.types.Action.transform_channel
    # del bpy.types.Action.activation_start
    # del bpy.types.Action.activation_end
