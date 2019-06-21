#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import inspect
from nodeitems_utils import NodeCategory, NodeItem
import nodeitems_utils

# Put all Korman node modules here...
from .node_avatar import *
from .node_conditions import *
from .node_core import *
from .node_deprecated import *
from .node_logic import *
from .node_messages import *
from .node_python import *
from .node_responder import *
from .node_softvolume import *

class PlasmaNodeCategory(NodeCategory):
    """Plasma Node Category"""

    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == "PlasmaNodeTree")

# Here's what you need to know about this...
# If you add a new category, put the pretty name here!
# If you're making a new Node, ensure that your bl_idname attribute is present AND matches
#     the class name. Otherwise, absolutely fascinating things will happen. Don't expect for me
#     to come and rescue you from it, either.
_kategory_names = {
    "AVATAR": "Avatar",
    "CONDITIONS": "Conditions",
    "LOGIC": "Logic",
    "MSG": "Message",
    "PYTHON": "Python",
    "SV": "Soft Volume",
}

class PlasmaNodeItem(NodeItem):
    def __init__(self, **kwargs):
        self._poll_add = kwargs.pop("poll_add", None)
        super().__init__(**kwargs)

    @staticmethod
    def draw(self, layout, context):
        # Blender's NodeItem completely unlists anything that polls False. We would rather
        # display the item but disabled so the user has a hint that it exists but cannot be
        # used at the present time.
        if self._poll_add is not None and not self._poll_add(context):
            row = layout.row()
            row.enabled = False
            NodeItem.draw(self, row, context)
        else:
            NodeItem.draw(self, layout, context)


# Now, generate the categories as best we can...
_kategories = {}
for cls in dict(globals()).values():
    if inspect.isclass(cls):
        item = {}
        if not issubclass(cls, PlasmaNodeBase):
            continue
        if not issubclass(cls, bpy.types.Node):
            continue
        if issubclass(cls, PlasmaDeprecatedNode):
            continue
        if issubclass(cls, PlasmaTreeOutputNodeBase):
            item["poll_add"] = PlasmaTreeOutputNodeBase.poll_add

        item["nodetype"] = cls.bl_idname
        item["label"] = cls.bl_label

        kat = _kategories.setdefault(cls.bl_category, [])
        kat.append(item)

_actual_kategories = []
for i in sorted(_kategories.keys(), key=lambda x: _kategory_names[x]):
    # Note that even though we're sorting the category names, Blender appears to not care...
    _kat_items = [PlasmaNodeItem(**j) for j in sorted(_kategories[i], key=lambda x: x["label"])]
    _actual_kategories.append(PlasmaNodeCategory(i, _kategory_names[i], items=_kat_items))

def register():
    nodeitems_utils.register_node_categories("PLASMA_NODES", _actual_kategories)

def unregister():
    nodeitems_utils.unregister_node_categories("PLASMA_NODES")
