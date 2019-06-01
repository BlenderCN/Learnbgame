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


import bpy

from cellblender.utils import preserve_selection_use_operator


def import_obj(mdlobj, obj_mat, reg_mat, add_to_model_objects=True):
    """ Create a new Blender mesh object.

    Currently, this is used by both the swig and pyparsing based importers. In
    addition to creating a new mesh object, a red material is applied to all
    surface regions and a gray material is applied to the rest of the mesh.
    """

    meshes = bpy.data.meshes
    objs = bpy.data.objects
    scn = bpy.context.scene
    scn_objs = scn.objects

    objname = mdlobj.name
    print(objname, len(mdlobj.vertices), len(mdlobj.faces))
    obj = objs.get(objname)

    # Overwrite existing object if it has the same name as the object we are
    # trying to import
    if obj:
        scn.objects.unlink(obj)
        objs.remove(obj)

    mesh = meshes.new(objname)
    mesh.from_pydata(mdlobj.vertices, [], mdlobj.faces)

    mesh.materials.append(obj_mat)
    mesh.materials.append(reg_mat)

    obj = objs.new(objname, mesh)
    scn_objs.link(obj)

    # Object needs to be active to add a region to it because of how
    # init_region (called by add_region_by_name) works.
    scn.objects.active = obj
    
    all_regions = []
    for reg_name, regions in mdlobj.regions.items():
        obj.mcell.regions.add_region_by_name(bpy.context, reg_name)
        reg = obj.mcell.regions.region_list[reg_name]
        reg.set_region_faces(obj.data, regions.faces)
        all_regions.extend(regions.faces)

    # Get list of face indices
    face_list = [0] * len(mesh.polygons)
    mesh.polygons.foreach_get('index', face_list)

    # Create list of 1s and 0s. 1 if corresponding face index is in a region,
    # 0 otherwise.
    all_regions_set = set(all_regions)
    material_list = [1 if f in all_regions_set else 0 for f in face_list]

    # Faces that belong to a region are colored red
    mesh.polygons.foreach_set("material_index", material_list)

    if add_to_model_objects:
        preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)

    mesh.validate(verbose=True)
    mesh.update()


def create_materials():
    """ This function creates materials to be used later. """

    mats = bpy.data.materials

    # This material is used by all the faces that don't have a surface region
    obj_mat = mats.get('obj_mat')
    if not obj_mat:
        obj_mat = mats.new('obj_mat')
        obj_mat.diffuse_color = [0.7, 0.7, 0.7]

    # This material is used by all faces that do have a surface region.
    reg_mat = mats.get('reg_mat')
    if not reg_mat:
        reg_mat = mats.new('reg_mat')
        reg_mat.diffuse_color = [0.8, 0.0, 0.0]

    return (obj_mat, reg_mat)
