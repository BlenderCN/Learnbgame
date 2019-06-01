#------------------------------------------------------------------------------
# Reynolds-Blender | The Blender add-on for Reynolds, an OpenFoam toolbox.
#------------------------------------------------------------------------------
# Copyright|
#------------------------------------------------------------------------------
#     Deepak Surti       (dmsurti@gmail.com)
#     Prabhu R           (IIT Bombay, prabhu@aero.iitb.ac.in)
#     Shivasubramanian G (IIT Bombay, sgopalak@iitb.ac.in)
#------------------------------------------------------------------------------
# License
#
#     This file is part of reynolds-blender.
#
#     reynolds-blender is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     reynolds-blender is distributed in the hope that it will be useful, but
#     WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#     Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with reynolds-blender.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

# -----------
# bpy imports
# -----------
import bpy

from bpy.props import IntProperty
from bpy.types import PropertyGroup, UIList

# --------------
# python imports
# --------------
import inspect
import os
import sys
import yaml

# ------------------------
# reynolds blender imports
# ------------------------
from .register import register_classes

# ---------------
# custom operator
# ---------------

def create_custom_operator(class_name, id_name, label, description,
                           func_module_name, exec_func):
    module = sys.modules[func_module_name]
    all_functions = dict([f for f in inspect.getmembers(module,
                                                        inspect.isfunction)
                          if inspect.getmodule(f[1]) == module])
    opclass = type(class_name, (bpy.types.Operator, ),
                   {"bl_idname": id_name, "bl_label": label,
                    "bl_description": description,
                    "execute": all_functions[exec_func]})
    print('Registering ', class_name, ' in module',
          getattr(opclass, '__module__', None))
    bpy.utils.register_class(opclass)

#---------------
# custom UI list
#---------------

def create_custom_list_operator(class_name, id_name, label, description,
                                data_prop, id_prop):
    list_actions = bpy.props.EnumProperty(
            items=(
                ('UP', "Up", ""),
                ('DOWN', "Down", ""),
                ('REMOVE', "Remove", ""),
                ('ADD', "Add", ""),
            )
        )

    def execute_func(self, context):
        return self.invoke(context, None)

    def invoke_func(self, context, event):
        scn = context.scene

        print('data prop ', data_prop)
        item_coll = getattr(scn, data_prop)
        print('id prop ', id_prop)
        item_idx = getattr(scn, id_prop)

        try:
            item = item_coll[item_idx]
        except IndexError:
            pass

        if self.action == 'REMOVE':
            item = item_coll[item_idx]
            info = 'Item %s removed from list' % (item.name)
            setattr(scn, id_prop, item_idx - 1)
            self.report({'INFO'}, info)
            item_coll.remove(item_idx)

        if self.action == 'ADD':
            item = item_coll.add()
            item.id = len(item_coll)
            setattr(scn, id_prop, len(item_coll) - 1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}

    opclass = type(class_name, (bpy.types.Operator, ),
                   {"bl_idname": id_name, "bl_label": label,
                    "bl_description": description,
                    "execute": execute_func, "invoke": invoke_func,
                    "action": list_actions})

    print('Registering ', class_name, ' in module',
          getattr(opclass, '__module__', None))
    bpy.utils.register_class(opclass)

# --------------------------------------------
# custom rendering of each item in the list UI
# --------------------------------------------

class ReynoldsListItems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        split = layout.split(0.3)
        split.label("%d" % (index))
        split.prop(item, "name", text="", emboss=False, translate=False,
                   icon='BORDER_RECT')

    def invoke(self, context, event):
        pass

# -----------------------------------------------
# custom property group for list collection index
# -----------------------------------------------

class ReynoldsListLabel(bpy.types.PropertyGroup):
    id = IntProperty()

# -----------------------
# Create custom operators
# -----------------------

def create_custom_operators(operators_filename, func_module_name):
    current_dir = os.path.realpath(os.path.dirname(__file__))
    operators_file = os.path.join(current_dir, "../yaml", "panels",
                                    operators_filename)
    with open(operators_file) as f:
        d = yaml.load(f)
        for operator in d['operators'].items():
            op_id, props = operator
            op_type = props.get('operator_type', None)
            class_name = props.get('class_name', None)
            label = props.get('label', None)
            description = props.get('description', None)

            if op_type == 'ListOperator':
                data_prop = props.get('data_prop', None)
                id_prop = props.get('id_prop', None)
                create_custom_list_operator(class_name, op_id, label,
                                            description,
                                            data_prop, id_prop)
            if op_type == 'Operator':
                exec_func = props.get('execute_func', None)
                create_custom_operator(class_name, op_id, label,
                                       description, func_module_name,
                                       exec_func)

# ---------------------------------------------------------------------
# Register the classes for loading UI scene attrs and rendering UI list
# ---------------------------------------------------------------------
register_classes(__name__)
