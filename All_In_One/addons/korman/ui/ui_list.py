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

def draw_list(layout, listtype, context_attr, prop_base, collection_name, index_name, **kwargs):
    """Draws a generic UI list, including add/remove buttons. Note that in order to use this,
       the parent datablock must be available in the context provided to operators. This should
       always be true, but this is Blender...
       Arguments:
       - layout: required
       - listtype: bpy.types.UIList subclass
       - context_attr: attribute name to get the properties from in the current context
       - prop_base: property group owning the collection
       - collection_name: name of the collection property
       - index_name: name of the active element index property
       - name_prefix: (optional) prefix to apply to display name of new elements
       - name_prop: (optional) property for each element's display name
       *** any other arguments are passed as keyword arguments to the template_list call 
    """
    prop_path = prop_base.path_from_id()
    name_prefix = kwargs.pop("name_prefix", "")
    name_prop = kwargs.pop("name_prop", "")

    row = layout.row()
    row.template_list(listtype, collection_name, prop_base, collection_name,
                      prop_base, index_name, **kwargs)
    col = row.column(align=True)
    op = col.operator("ui.plasma_collection_add", icon="ZOOMIN", text="")
    op.context = context_attr
    op.group_path = prop_path
    op.collection_prop = collection_name
    op.index_prop = index_name
    op.name_prefix = name_prefix
    op.name_prop = name_prop
    op = col.operator("ui.plasma_collection_remove", icon="ZOOMOUT", text="")
    op.context = context_attr
    op.group_path = prop_path
    op.collection_prop = collection_name
    op.index_prop = index_name

def draw_modifier_list(layout, listtype, prop_base, collection_name, index_name, **kwargs):
    draw_list(layout, listtype, "object", prop_base, collection_name, index_name, **kwargs)
