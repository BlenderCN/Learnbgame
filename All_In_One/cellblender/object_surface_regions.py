# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.#
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

"""
This file contains the classes for Object Surface Regions.

"""

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent
import mathutils

# python imports
import re

import cellblender


# from . import ParameterSpace


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Object Surface Region Operators:

class MCELL_OT_region_add(bpy.types.Operator):
    bl_idname = "mcell.region_add"
    bl_label = "Add New Surface Region"
    bl_description = "Add a new surface region to an object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.mcell.regions.add_region(context)
        return {'FINISHED'}


class MCELL_OT_region_remove(bpy.types.Operator):
    bl_idname = "mcell.region_remove"
    bl_label = "Remove Surface Region"
    bl_description = "Remove selected surface region from object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.mcell.regions.remove_region(context)
        return {'FINISHED'}


class MCELL_OT_region_remove_all(bpy.types.Operator):
    bl_idname = "mcell.region_remove_all"
    bl_label = "Remove All Surface Regions"
    bl_description = "Remove all surface regions from object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.mcell.regions.remove_all_regions(context)
        return {'FINISHED'}


class MCELL_OT_region_faces_assign(bpy.types.Operator):
    bl_idname = "mcell.region_faces_assign"
    bl_label = "Assign Selected Faces To Surface Region"
    bl_description = "Assign selected faces to surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reg = context.object.mcell.regions.get_active_region()
        if reg:
            reg.assign_region_faces(context)
        return {'FINISHED'}


class MCELL_OT_region_faces_remove(bpy.types.Operator):
    bl_idname = "mcell.region_faces_remove"
    bl_label = "Remove Selected Faces From Surface Region"
    bl_description = "Remove selected faces from surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reg = context.object.mcell.regions.get_active_region()
        if reg:
            reg.remove_region_faces(context)
        return {'FINISHED'}


class MCELL_OT_region_faces_select(bpy.types.Operator):
    bl_idname = "mcell.region_faces_select"
    bl_label = "Select Faces of Selected Surface Region"
    bl_description = "Select faces of selected surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reg = context.object.mcell.regions.get_active_region()
        if reg:
            reg.select_region_faces(context)
        return {'FINISHED'}


class MCELL_OT_region_faces_deselect(bpy.types.Operator):
    bl_idname = "mcell.region_faces_deselect"
    bl_label = "Deselect Faces of Selected Surface Region"
    bl_description = "Deselect faces of selected surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reg = context.object.mcell.regions.get_active_region()
        if reg:
            reg.deselect_region_faces(context)
        return {'FINISHED'}


class MCELL_OT_face_get_regions(bpy.types.Operator):
    bl_idname = "mcell.face_get_regions"
    bl_label = "Get Region Membership of Selected Face"
    bl_description = "Get region membership of selected face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.mcell.regions.face_get_regions(context)
        return {'FINISHED'}


class MCELL_OT_faces_get_regions(bpy.types.Operator):
    bl_idname = "mcell.faces_get_regions"
    bl_label = "Get Region Membership of Selected Faces"
    bl_description = "Get region membership of selected faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.mcell.regions.faces_get_regions(context)
        return {'FINISHED'}


# Object Surface Region Panel:

class MCELL_UL_check_region(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


# Region Callbacks:

def region_update(self, context):
    context.object.mcell.regions.region_update()
    return


# CellBlender Properties Classes for Surface Regions:

class MCellSurfaceRegionProperty(bpy.types.PropertyGroup):
    id = IntProperty(name="Unique ID of This Region",default=-1)
    name = StringProperty(
        name="Region Name", default="Region", update=region_update)
    status = StringProperty(name="Status")


    def check_region_name(self, reg_name_list):
        """Checks for duplicate or illegal region name"""

        status = ""

        # Check for duplicate region name
        if reg_name_list.count(self.name) > 1:
            status = "Duplicate region: %s" % (self.name)

        # Check for illegal names (Starts with a letter. No special characters)
        reg_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
        m = re.match(reg_filter, self.name)
        if m is None:
            status = "Region name error: %s" % (self.name)

        self.status = status

        return


    def assign_region_faces(self, context):
        mesh = context.active_object.data
        if (mesh.total_face_sel > 0):
            face_set = self.get_region_faces(mesh) 
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    face_set.add(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            self.set_region_faces(mesh,face_set) 

        return {'FINISHED'}


    def remove_region_faces(self, context):
        mesh = context.active_object.data
        if (mesh.total_face_sel > 0):
            face_set = self.get_region_faces(mesh) 
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    if f.index in face_set:
                        face_set.remove(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            self.set_region_faces(mesh,face_set) 

        return {'FINISHED'}


    def select_region_faces(self, context):
        mesh = context.active_object.data
        face_set = self.get_region_faces(mesh)
        msm = context.scene.tool_settings.mesh_select_mode[0:3]
        context.scene.tool_settings.mesh_select_mode = (False, False, True)
        bpy.ops.object.mode_set(mode='OBJECT')
        for f in face_set:
            mesh.polygons[f].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        context.scene.tool_settings.mesh_select_mode = msm

        return {'FINISHED'}


    def deselect_region_faces(self, context):
        mesh = context.active_object.data
        face_set = self.get_region_faces(mesh)
        msm = context.scene.tool_settings.mesh_select_mode[0:3]
        context.scene.tool_settings.mesh_select_mode = (False, False, True)
        bpy.ops.object.mode_set(mode='OBJECT')
        for f in face_set:
            mesh.polygons[f].select = False
        bpy.ops.object.mode_set(mode='EDIT')
        context.scene.tool_settings.mesh_select_mode = msm

        return {'FINISHED'}


    def destroy_region(self, context):
        """Remove all region data from mesh"""
        id = str(self.id)

        # POSSIBLE FIXME? GET PARENT BLEND OBJECT OF THIS REGION_LIST
        obj = context.active_object
        mesh = obj.data
        for seg_id in mesh["mcell"]["regions"][id].keys():
            mesh["mcell"]["regions"][id][seg_id] = []
        mesh["mcell"]["regions"][id].clear()
        mesh["mcell"]["regions"].pop(id)


    def face_in_region(self, context, face_index):
        """Return True if face is in this region"""
        mesh = context.active_object.data
        reg_faces = self.get_region_faces(mesh)
        return(face_index in reg_faces)


    def init_region(self, context, id):

        self.id = id
        str_id = str(self.id)

        mesh = context.active_object.data
        if not mesh.get("mcell"):
            mesh["mcell"] = {}
        if not mesh["mcell"].get("regions"):
            mesh["mcell"]["regions"] = {}
        if not mesh["mcell"]["regions"].get(str_id):
            mesh["mcell"]["regions"][str_id] = {}


    def reset_region(self, context):

        id = str(self.id)

        mesh = context.active_object.data

        for seg_id in mesh["mcell"]["regions"][id].keys():
            mesh["mcell"]["regions"][id][seg_id] = []
        mesh["mcell"]["regions"][id].clear()


    def get_region_faces(self, mesh):
        """Given a mesh and a region id, return the set of region face indices"""

        id = str(self.id)

        face_rle = []
        for seg_id in mesh["mcell"]["regions"][id].keys():
          face_rle.extend(mesh["mcell"]["regions"][id][seg_id].to_list())
        if (len(face_rle) > 0): 
            face_set = set(self.rl_decode(face_rle))
        else:
            face_set = set([])

        return(face_set)


    def set_region_faces(self, mesh, face_set):
        """Set the faces of a given region id on a mesh, given a set of faces """

        id = str(self.id)
        face_list = list(face_set)
        face_list.sort()
        face_rle = self.rl_encode(face_list)

        # Clear existing faces from this region id
        mesh["mcell"]["regions"][id].clear()

        # segment face_rle into pieces <= max_len (i.e. <= 32767)
        #   and assign these segments to the region id
        max_len = 32767
        seg_rle = face_rle
        len_rle = len(seg_rle)
        seg_idx = 0
        while len_rle > 0:
          if len_rle <= 32767:
            mesh["mcell"]["regions"][id][str(seg_idx)] = seg_rle
            len_rle = 0
          else:
            mesh["mcell"]["regions"][id][str(seg_idx)] = seg_rle[0:max_len]
            tmp_rle = seg_rle[max_len:]
            seg_rle = tmp_rle
            len_rle = len(seg_rle)
          seg_idx += 1


    def rl_encode(self, l):
        """Run-length encode an array of face indices"""

        runlen = 0
        runstart = 0
        rle = []
        i = 0

        while (i < len(l)):
          if (runlen == 0):
            rle.append(l[i])
            runstart = l[i]
            runlen = 1
            i+=1
          elif (l[i] == (runstart+runlen)):
            if (i < (len(l)-1)):
              runlen += 1
            else:
              if (runlen == 1):
                rle.append(runstart+1)
              else:
                rle.append(-runlen)
            i+=1
          elif (runlen == 1):
            runlen = 0
          elif (runlen == 2):
            rle.append(runstart+1)
            runlen = 0
          else:
            rle.append(-(runlen-1))
            runlen = 0

        return(rle)


    def rl_decode(self, l):
        """Decode a run-length encoded array of face indices"""

        runlen = 0
        runstart = 0
        rld = []
        i = 0

        while (i < len(l)):
          if (runlen == 0):
            rld.append(l[i])
            runstart = l[i]
            runlen = 1
            i+=1
          elif (l[i] > 0):
            runlen = 0
          else:
            for j in range(1,-l[i]+1):
              rld.append(runstart+j)
            runlen = 0
            i+=1

        return(rld)


class MCellSurfaceRegionListProperty(bpy.types.PropertyGroup):
    region_list = CollectionProperty(
        type=MCellSurfaceRegionProperty, name="Surface Region List")
    active_reg_index = IntProperty(name="Active Region Index", default=0)
    id_counter = IntProperty(name="Counter for Unique Region IDs", default=0)
    get_region_info = BoolProperty(
        name="Toggle to enable/disable region_info", default=False)


    def get_active_region(self):
        reg = None
        if (len(self.region_list) > 0):
            reg = self.region_list[self.active_reg_index]
        return(reg)


    def allocate_id(self):
        """ Return a unique region ID for a new region """
        if (len(self.region_list) <= 0):
            # Reset the ID to 0 when there are no more regions
            self.id_counter = 0
        id = self.id_counter
        self.id_counter += 1
        return(id)


    def face_get_regions(self,context):
        """ Return the list of region IDs associated with one selected face """
        reg_list = ""
        mesh = context.active_object.data
        if (mesh.total_face_sel == 1):
          bpy.ops.object.mode_set(mode='OBJECT')
          face_index = [f.index for f in mesh.polygons if f.select][0]
          bpy.ops.object.mode_set(mode='EDIT')
          for reg in self.region_list: 
            if reg.face_in_region(context,face_index):
              reg_list = reg_list + " " + reg.name
        
        return(reg_list)


    def faces_get_regions(self,context):
        """ Return list of region names associated with the selected faces """
        reg_info = []
        mesh = context.active_object.data
        if (mesh.total_face_sel > 0):
          bpy.ops.object.mode_set(mode='OBJECT')
          selface_set = set([f.index for f in mesh.polygons if f.select])
          bpy.ops.object.mode_set(mode='EDIT')
          for reg in self.region_list: 
            reg_faces = reg.get_region_faces(mesh)
            if not selface_set.isdisjoint(reg_faces):
              reg_info.append(reg.name)

        return(reg_info)


    def add_region(self, context):
        """ Add a new region to the list of regions and set as the active region """
        id = self.allocate_id()
        new_reg=self.region_list.add()
        new_reg.init_region(context, id)
# FIXME: CHECK FOR NAME COLLISION HERE: FIX BY ALLOCATING NEXT ID...
        reg_name = "Region_%d" % (new_reg.id)
        new_reg.name = reg_name
        idx = self.region_list.find(reg_name)
        self.active_reg_index = idx


    def add_region_by_name(self, context, reg_name):
        """ Add a new region to the list of regions and set as the active region """
        curr_reg = self.get_active_region()

        id = self.allocate_id()
        new_reg=self.region_list.add()
        new_reg.init_region(context, id)
# FIXME: CHECK FOR NAME COLLISION HERE: FIX BY ALLOCATING NEXT ID...
        new_reg.name = reg_name

        if not curr_reg:
          curr_reg = new_reg
        idx = self.region_list.find(curr_reg.name)
        self.active_reg_index = idx


    def remove_all_regions(self, context):
        for i in range(len(self.region_list)):
            # First remove region data from mesh:
            reg = self.region_list[0]
            reg.destroy_region(context)

            # Now remove the region from the object
            self.region_list.remove(0)

        self.active_reg_index = 0


    def remove_region(self, context):

        # First remove region data from mesh:
        reg = self.get_active_region()
        if reg:
            reg.destroy_region(context)

            # Now remove the region from the object
            self.region_list.remove(self.active_reg_index)
            self.active_reg_index -= 1
            if (self.active_reg_index < 0):
                self.active_reg_index = 0


    def region_update(self):
        """Performs checks and sorts region list after update of region names"""

        if self.region_list:
            reg = self.get_active_region()
            reg.check_region_name(self.region_list.keys())
            self.sort_region_list()

        return


    def sort_region_list(self):
        """Sorts region list"""

        act_reg = self.get_active_region()
        act_reg_name = act_reg.name

        # Sort the region list
        self.inplace_quicksort(self.region_list, 0, len(self.region_list)-1)

        act_i = self.region_list.find(act_reg_name)
        self.active_reg_index = act_i

        return


    def inplace_quicksort(self, v, beg, end):  # collection array, int, int
        """
          Sorts a collection array, v, in place.
          Sorts according values in v[i].name
        """

        if ((end - beg) > 0):  # only perform quicksort if we are dealing with > 1 values
            pivot = v[beg].name  # we set the first item as our initial pivot
            i, j = beg, end

            while (j > i):
                while ((v[i].name <= pivot) and (j > i)):
                    i += 1
                while ((v[j].name > pivot) and (j >= i)):
                    j -= 1
                if (j > i):
                    v.move(i, j)
                    v.move(j-1, i)

            if (not beg == j):
                v.move(beg, j)
                v.move(j-1, beg)
            self.inplace_quicksort(v, beg, j-1)
            self.inplace_quicksort(v, j+1, end)
        return


    def draw_panel(self, context, panel):
        layout = panel.layout
        self.draw_layout ( context, layout )

    def draw_layout(self, context, layout):
        active_obj = context.active_object

        if active_obj.type == 'MESH':
            row = layout.row()
            # row.label(text="Defined Regions:", icon='FORCE_LENNARDJONES')
            row.label(text="Defined Surface Regions:", icon='SNAP_FACE')
            row = layout.row()
            col = row.column()
            col.template_list("MCELL_UL_check_region", "define_surf_regions",
                          self, "region_list",
                          self, "active_reg_index",
                          rows=2)
            col = row.column(align=True)
            col.operator("mcell.region_add", icon='ZOOMIN', text="")
            col.operator("mcell.region_remove", icon='ZOOMOUT', text="")
            col.operator("mcell.region_remove_all", icon='X', text="")

            # Could have region item draw itself in new row here:
            row = layout.row()
            if len(self.region_list) > 0:
                layout.prop(self.get_active_region(), "name")

            if active_obj.mode == 'EDIT' and (len(self.region_list)>0):
                row = layout.row()
                sub = row.row(align=True)
                sub.operator("mcell.region_faces_assign", text="Assign")
                sub.operator("mcell.region_faces_remove", text="Remove")
                sub = row.row(align=True)
                sub.operator("mcell.region_faces_select", text="Select")
                sub.operator("mcell.region_faces_deselect", text="Deselect")

                # Option to Get Region Info
                box = layout.box()
                row = box.row(align=True)
                row.alignment = 'LEFT'
                if self.get_region_info:
                    row.prop(self, "get_region_info", icon='TRIA_DOWN',
                             text="Region Info for Selected Faces",
                              emboss=False)
                    reg_info = self.faces_get_regions(context)
                    for reg_name in reg_info:
                        row = box.row()
                        row.label(text=reg_name)
                else:
                    row.prop(self, "get_region_info", icon='TRIA_RIGHT',
                             text="Region Info for Selected Faces",
                             emboss=False)


                


    def format_update(self, obj):
        """
          Update format of object regions.
          This is required to update regions from pre v1.0 format to new v1.0 format
        """

        mesh = obj.data
        if len(self.region_list) > 0:
            # We have object regions so check for pre v1.0 region format
            # We'll do that by checking the region name on the mesh.
            # If the first region on mesh is old then they're all old
            self.sort_region_list()
            # Check that the mesh has regions
            if mesh.get("mcell"):
                if mesh["mcell"].get("regions"):
                    mregs =  mesh["mcell"]["regions"]
                    if len(mregs.keys()) > 0:
                        # if reg_name is alpha followed by alphanumeric
                        #   then we've got an old format region
                        reg_name = mregs.keys()[0]
                        reg_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
                        m = re.match(reg_filter, reg_name)
                        if m is not None:
                            # We have old region format
                            # Make copies of all old regions
                            mreg_tmp = {}
                            for reg in self.region_list:
                                mreg_tmp[reg.name] = set(
                                    mregs[reg.name].to_list())
                            # Clear old regions from mesh
                            for key in mregs.keys():
                                mregs[key] = []
                            mregs.clear()
                            # Convert old regions to new format
                            self.id_counter = 0
                            for reg in self.region_list:
                                reg.id = self.allocate_id()
                                id = str(reg.id)
                                mregs[id] = {}
                                reg.set_region_faces(mesh,mreg_tmp[reg.name])
            else:
                # The mesh did not have regions so the object regions are
                # empty. But if id_counter is 0 then we have old object regions
                # so we need to generate id's for the empty regions
                if self.id_counter == 0:
                    for reg in self.region_list:
                        # Update the object region id's
                        reg.id = self.allocate_id()
        else:
            # There are no object regions but there might be mesh cruft
            # Remove any region cruft we find attached to mesh["mcell"]
            if mesh.get("mcell"):
                if mesh["mcell"].get("regions"):
                    mregs =  mesh["mcell"]["regions"]
                    for key in mregs.keys():
                        mregs[key] = []
                    mregs.clear()
                    mesh["mcell"].pop("regions")



# Properties Class for CellBlender Metadata on Blender Objects

class MCellObjectPropertyGroup(bpy.types.PropertyGroup):
    regions = PointerProperty(
        type=MCellSurfaceRegionListProperty, name="Defined Surface Regions")
    include = BoolProperty(name="Include Object in Model", default=False)

    def get_regions_dictionary (self, obj):
        """ Return a dictionary with region names """
        reg_dict = {}
        obj_regs = self.regions.region_list
        for reg in obj_regs:
            id = str(reg.id)
            mesh = obj.data
            #reg_faces = list(cellblender_operators.get_region_faces(mesh,id))
            reg_faces = list(reg.get_region_faces(mesh))
            reg_faces.sort()
            reg_dict[reg.name] = reg_faces
        return reg_dict



# Update format of object regions
# This is required to update regions from pre v1.0 format to new v1.0 format
# Note: This function is registered as a load_post handler
@persistent
def object_regions_format_update(context):

    if not context:
        context = bpy.context

    scn_objs = context.scene.objects
    objs = [obj for obj in scn_objs if obj.type == 'MESH']
    for obj in objs:
          obj.mcell.regions.format_update(obj)


    return




# Legacy code from when we used to store regions as vertex groups
#   Useful to run from Blender's python console on some older models
#   We'll eliminate this when our face regions have query features akin
#   to those available with vertex groups.
class MCELL_OT_vertex_groups_to_regions(bpy.types.Operator):
    bl_idname = "mcell.vertex_groups_to_regions"
    bl_label = "Convert Vertex Groups of Selected Objects to Regions"
    bl_description = "Convert Vertex Groups to Regions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        select_objs = context.selected_objects

        # For each selected object:
        for obj in select_objs:
            print(obj.name)
            scn.objects.active = obj
            obj.select = True
            obj_regs = obj.mcell.regions
            vert_groups = obj.vertex_groups

            # If there are vertex groups to convert:
            if vert_groups:
                mesh = obj.data

                # For each vertex group:
                for vg in vert_groups:

                    # Deselect the whole mesh:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')

                    # Select the vertex group:
                    print(vg.name)
                    bpy.ops.object.vertex_group_set_active(group=vg.name)
                    bpy.ops.object.vertex_group_select()

                    # If there are selected faces:
                    if (mesh.total_face_sel > 0):
                        print("  vg faces: %d" % (mesh.total_face_sel))

                        # Setup mesh regions IDProp if necessary:
                        if not mesh.get("mcell"):
                            mesh["mcell"] = {}
                        if not mesh["mcell"].get("regions"):
                            mesh["mcell"]["regions"] = {}

                        # look for vg.name in region_list and add if not found:
                        # method 1:
                        if (obj_regs.region_list.find(vg.name) == -1):
                            bpy.ops.mcell.region_add()
                            reg = obj_regs.region_list[
                                obj_regs.active_reg_index]
                            reg.name = vg.name
                        reg = obj_regs.region_list[vg.name]

                        # append faces in vertex group to faces in region:
                        # retreive or create region on mesh:
                        if not mesh["mcell"]["regions"].get(vg.name):
                            mesh["mcell"]["regions"][reg.name] = []
                        face_set = set([])
                        for f in mesh["mcell"]["regions"][reg.name]:
                            face_set.add(f)
                        print("  reg faces 0: %d" % (len(face_set)))
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for f in mesh.polygons:
                            if f.select:
                                face_set.add(f.index)
                        bpy.ops.object.mode_set(mode='EDIT')
                        reg_faces = list(face_set)
                        reg_faces.sort()
                        print("  reg faces 1: %d" % (len(reg_faces)))
                        mesh["mcell"]["regions"][reg.name] = reg_faces
                        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


