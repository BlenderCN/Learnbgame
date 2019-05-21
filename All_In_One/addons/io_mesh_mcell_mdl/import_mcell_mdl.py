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

# <pep8 compliant>

from . import mdlmesh_parser
from . import import_shared


def load(operator, context, filepath="", add_to_model_objects=True):

    print("Calling mdlmesh_parser.mdl_parser(\'%s\')..." % (filepath))
    root_mdlobj = mdlmesh_parser.mdl_parser(filepath)
    print("Done calling mdlmesh_parser.mdl_parser(\'%s\')" % (filepath))

    obj_mat, reg_mat = import_shared.create_materials()
    mdlobj = root_mdlobj
    while not mdlobj is None:
        if mdlobj.object_type == 0:
            # META_OBJ
            p_mdlobj = mdlobj
            mdlobj = mdlobj.first_child
        else:
            # POLY_OBJ
            import_shared.import_obj(mdlobj, obj_mat, reg_mat, add_to_model_objects)

            mdlobj = mdlobj.next
            if mdlobj is None:
                mdlobj = p_mdlobj.next

    return {'FINISHED'}
