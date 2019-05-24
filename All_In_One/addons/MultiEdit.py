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

bl_info = {
     "name": "MultiEdit",
     "author": "Antonis Karvelas",
     "version": (0, 5),
     "blender": (2, 7, 8),
     "location": "VIEW 3D > Tools > Multiple Objects Editing ",
     "description": "Allows you to edit multiple objects together in edit mode without destroying data",
     "warning": "Alpha Version 0.5, maybe has a few problems...",
     "wiki_url": "",
     "tracker_url": "",
     "category": "Learnbgame",
}

#Imports:
import bpy
import math

#Create a list to put the names of the selected objects:
name_list = []

#Create a list to put the names of the duplicated objects:
duplicated_list = []

#Create a list to put the vertex_groups that need to be maintained:
special_vgroups_list = []

#Create a dictionary to put the parents
parents_list = {}

class MultiEdit_Enter(bpy.types.Operator):
    bl_label = "MultiEdit Enter"
    bl_idname = "objects.multiedit_enter_operator"

    #The main function of the class:
    def execute(self, context):
        #Create a list with all the selected objects:
        selected_objects_list = bpy.context.selected_objects

        #Deselect all the non-mesh objects:
        for visible_object in selected_objects_list:
            if visible_object.type != "MESH":
                visible_object.select = False
            else:
                pass

        #Create a new list with all the selected objects:
        new_selected_objects_list = bpy.context.selected_objects

        #If there's only one selected object, enter Edit-mode, else create
        #a MultiEdit instance:
        if len(new_selected_objects_list) >= 2:

            #If the name_list contains elements, that means that there is
            #at least one more MultiEdit instance.
            if len(name_list) == 0:
                self.Create_MultiEdit(new_selected_objects_list)
            else:
                raise ValueError("A MultiEdit instance is already running!")
        else:
            bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}

    #The function that actually initiated a new MultiEdit:
    def Create_MultiEdit(self, objects):

        #Create a variable to keep track of the number of objects:
        copied_index = 0

        #Iterate through the given objects list:
        for object in objects:

            #Append the object's name to the name_list:
            name_list.append(object.name)

            #Call the Duplicate_Object function:
            new_object_name = object.name + "_dupl" + str(copied_index)
            self.Duplicate_Object(bpy.context.scene, (new_object_name),object)
            duplicated_list.append(new_object_name)

            #Increase the copied_index by 1:
            copied_index += 1

            #Call the Create_Vertex_Groups function:
            self.Create_Vertex_Groups(object)

            #Move duplicated objects to diferent layer:
            bpy.ops.object.select_all(action = 'DESELECT')
            bpy.data.objects[new_object_name].select = True
            layers = []
            for i in object.layers:
                layers.append(i)
            bpy.ops.object.move_to_layer(layers = layers)
            bpy.ops.object.hide_view_set()
            ##bpy.ops.object.move_to_layer(layers=((False,)*19 +(True,)))##

            #Call the Remove_Modifiers_and_Constraints function:
            self.Remove_Modifiers_and_Constraints(object)

        #Finally, join all the objects and enter Edit-mode:
        for object in objects:
            bpy.data.objects[object.name].select = True
        bpy.context.scene.objects.active = objects[0]
        bpy.ops.object.join()
        bpy.context.active_object.name = "MultiEdit"
        bpy.ops.object.mode_set(mode = 'EDIT')


    def Create_Vertex_Groups(self, object):

        ###Create the necessary vertex groups:###
        bpy.context.scene.objects.active = object
        for vertex_group in object.vertex_groups:
            special_vgroups_list.append(vertex_group.name) 
        
        #Create vertex groups containting all the vertices:
        object.vertex_groups.new(object.name)
        vertex_group = object.vertex_groups[-1]
        verts = [vert.index for vert in object.data.vertices]
        vertex_group.add(verts, 1.0, 'ADD')

        #####for vert in object.data.vertices:
        #####    verts.append(vert.index)
        #####    vertex_group.add(verts, 1.0, 'ADD')


    def Remove_Modifiers_and_Constraints(self, object):

        ###Remove all the modifiers and constraints from the objects:###
        object.select = True
        for modifier in object.modifiers:
            object.modifiers.remove(modifier)
        for constraint in object.constraints:
            object.constraints.remove(constraint)

    def Duplicate_Object(self, scene, name, old_object):

        ###Duplicate the given object:###

        #Create new mesh:
        mesh = bpy.data.meshes.new(name)

        #Create new object associated with the mesh:
        ob_new = bpy.data.objects.new(name, mesh)

        #Copy data block from the old object into the new object:
        ob_new.data = old_object.data.copy()
        ob_new.scale = old_object.scale
        ob_new.rotation_euler = old_object.rotation_euler
        ob_new.location = old_object.location

        #Link new object to the given scene and select it
        scene.objects.link(ob_new)

        #Copy all the modifiers:
        for mod in old_object.modifiers:
            mod_new = ob_new.modifiers.new(mod.name, mod.type)
            properties = [p.identifier for p in mod.bl_rna.properties
                          if not p.is_readonly]
            for prop in properties:
                setattr(mod_new, prop, getattr(mod, prop))

        #Copy all the constraints:
        for constr in old_object.constraints:
            constr_new = ob_new.constraints.new(constr.type)
            properties = [p.identifier for p in constr.bl_rna.properties
                          if not p.is_readonly]
            for prop in properties:
                setattr(constr_new, prop, getattr(constr, prop))

        #Copy all the vertex groups:
        for vertex_g in old_object.vertex_groups:
          vert_g_new = ob_new.vertex_groups.new(vertex_g.name)
          properties = [p.identifier for p in vertex_g.bl_rna.properties
                          if not p.is_readonly]
          for prop in properties:
               setattr(vert_g_new, prop, getattr(vertex_g, prop))

        #Copy all the object groups:
        for group in old_object.users_group:
            bpy.context.scene.objects.active = ob_new
            bpy.ops.object.group_link(group=group.name)
        
        #Copy parent object value
        try:
            parents_list[old_object.name] = (old_object.parent).name
        except:
            pass
        #Finally, return the new object:
        return ob_new


class MultiEdit_Exit(bpy.types.Operator):
    bl_label = "MultiEdit Exit"
    bl_idname = "objects.multiedit_exit_operator"
    bl_context = "editmode"

    #The main function of the class:
    def execute(self,context):

        #In case that any problems arise, just cancel the MultiEdit:
        try:
            bpy.context.scene.objects.active = bpy.data.objects["MultiEdit"]
        except:
            del name_list[:]
            del duplicated_list[:]
            del special_vgroups_list[:]
            parents_list.clear()

        #Create the necessary variables:
        active_object = bpy.context.active_object
        name = active_object.name
        vgroup_index = 0

        self.Separate_Objects(active_object, name, vgroup_index)
        self.Fix_Objects(active_object, name, vgroup_index)

        return {'FINISHED'}

    def Separate_Objects(self, active_object, name, vgroup_index):

        ###Separate given object according to the vertex_groups:
        for vertex_group in active_object.vertex_groups:
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.mesh.select_mode(type="VERT")
            bpy.ops.object.mode_set(mode = 'OBJECT')

            for vert in active_object.data.vertices:
                for vertGroup in vert.groups:
                    if vertGroup.group == vgroup_index:
                        if vertex_group.name in special_vgroups_list:
                            break
                        else:
                            vert.select = True
                    else:
                         pass



            bpy.ops.object.mode_set(mode = 'EDIT')
            try:
                bpy.ops.mesh.separate(type="SELECTED")
            except:
               pass
            vgroup_index += 1
        bpy.ops.object.mode_set(mode = 'OBJECT')


    def Fix_Objects(self, active_object, name, vgroup_index):

        existing_vg = []
        object_layer = bpy.context.scene.active_layer
        for object in bpy.context.selected_objects:
            bpy.context.scene.objects.active = object
            del existing_vg[:]
            vgroup_index = 0
            for vg in object.vertex_groups:
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                #Finding which vertex group has verts
                for vert in object.data.vertices:
                    for vertGroup in vert.groups:
                         if vertGroup.group == vgroup_index:
                              vert.select = True
                              if object.vertex_groups[vgroup_index].name in special_vgroups_list:
                                   pass
                              elif object.vertex_groups[vgroup_index].name in existing_vg:
                                   pass
                              else:
                                   existing_vg.append(object.vertex_groups[vgroup_index].name)

                    vgroup_index += 1
        
            #RENAME OBJECTS, ORGANIZES MATERIALS
            if len(existing_vg) < 2 and len(existing_vg) > 0:
                # try:
                    object.name = existing_vg[0]
                    wanted_object_name = duplicated_list[(name_list.index(object.name))]

                    mats = []

                    for slot in object.material_slots:
                        for slot_dupl in bpy.data.objects[wanted_object_name].material_slots:
                            if slot_dupl.name == slot.name:
                                mats.append(slot_dupl.name)
                            else:
                                pass

                    var = 0
                    for mat_index in range(len(object.material_slots)):
                        try:
                            if object.material_slots[mat_index - var].name in mats:
                                pass
                            else:
                                bpy.context.scene.objects.active = object
                                #mat_index = object.material_slots[slot_dupl].index
                                object.active_material_index = mat_index - var
                                bpy.ops.object.material_slot_remove()
                                var +=1
                        except:
                            pass

                    #Call the Copy_Data function:
                    self.Copy_Data(wanted_object_name, object)
                
            else:
                object.name = "New Geometry"

        #Call the Delete_Objects function:
        self.Delete_Objects()

        #Call the Preserve_Data function:
        self.Preserve_Data()

        #Unhide all objects:
        bpy.ops.object.hide_view_clear()

        #Delete duplicated objects
        bpy.ops.object.select_all(action="SELECT")
        for obj in bpy.context.selected_objects:
            if "dupl" not in obj.name:
                obj.select = False
        bpy.ops.object.delete()

        #Empty lists for future use
        del name_list[:]
        del duplicated_list[:]
        del special_vgroups_list[:]
        parents_list.clear()

    def Copy_Data(self, wanted_object_name, object):

        ###All those things copy modifiers, constraints etc. with all properties. Cool...###
        bpy.ops.object.select_all(action = 'DESELECT')
        object.select = True
        layers = []
        for i in bpy.data.objects[wanted_object_name].layers:
            layers.append(i)
        bpy.ops.object.move_to_layer(layers = layers)

        #Copy modifiers:
        properties = []
        for mod in bpy.data.objects[wanted_object_name].modifiers:
            mod_new = object.modifiers.new(mod.name, mod.type)
            properties = [p.identifier for p in mod.bl_rna.properties
                            if not p.is_readonly]
        for prop in properties:
            setattr(mod_new, prop, getattr(mod, prop))

        #Remove all existing groups:
        bpy.context.scene.objects.active = object
        bpy.ops.group.objects_remove_all()

        #Copy object groups:
        for group in bpy.data.objects[wanted_object_name].users_group:
            bpy.context.scene.objects.active = object
            bpy.ops.object.group_link(group=group.name)
            
        #Delete unnecessary vertex groups:
        for vg in object.vertex_groups:
            if vg.name in bpy.data.objects[(duplicated_list[(name_list.index(object.name))])].vertex_groups:
                pass
            else:
                object.vertex_groups.remove(vg)     
        
       #Copy constraints:
        for constr in bpy.data.objects[wanted_object_name].constraints:
            constr_new = object.constraints.new(constr.type)
            properties = [p.identifier for p in constr.bl_rna.properties
                          if not p.is_readonly]
            for prop in properties:
                setattr(constr_new, prop, getattr(constr, prop))

        #Copy shape keys:
        try:
            for shape_key in object.data.shape_keys.key_blocks:
                 try:
                      bpy.context.scene.objects.active = object
                      if shape_key.name in bpy.data.objects[(duplicated_list[(name_list.index(object.name))])].data.shape_keys.key_blocks:
                          pass
                      else:
                          idx = object.data.shape_keys.key_blocks.keys().index(shape_key.name)
                          object.active_shape_key_index = idx
                          bpy.ops.object.shape_key_remove()
                 except:
                      idx = object.data.shape_keys.key_blocks.keys().index(shape_key.name)
                      object.active_shape_key_index = idx
                      bpy.ops.object.shape_key_remove()
        except:
            pass

    def Preserve_Data(self):
        #Check if checkbox is true and preserve or not the rotation/scale values of the objects:
        if bpy.context.scene.Preserve_Location_Rotation_Scale:
          for obj in bpy.data.objects:
              self.Preserve_Parents(obj)
              for nam in name_list:
                if nam == obj.name:
                    obj.select = True
                    bpy.context.scene.objects.active = obj

                    #Location:
                    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
                    #Rotation:
                    rotation_values = bpy.data.objects[duplicated_list[name_list.index(nam)]].rotation_euler

                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

                    rot = (rotation_values[0]*(-1),
                           rotation_values[1]*(-1),
                           rotation_values[2]*(-1))

                    obj.rotation_mode = 'ZYX'
                    obj.rotation_euler = (rot)

                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

                    rot = (rotation_values[0],
                           rotation_values[1],
                           rotation_values[2])

                    obj.rotation_mode = 'XYZ'
                    obj.rotation_euler = (rot)

                    #Scale/Dimensions:
                    scales = bpy.data.objects[duplicated_list[name_list.index(nam)]].scale
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action = 'SELECT')
                    bpy.ops.transform.resize(value=(1.0/scales[0], 1.0/scales[1], 1.0/scales[2]))
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    obj.scale = scales
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.object.mode_set(mode = 'OBJECT')

                    bpy.context.scene.cursor_location = bpy.data.objects[duplicated_list[name_list.index(nam)]].location
                    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

                    #Deselect object:
                    obj.select = False

                else:
                  pass
        
        else:
          for obj in bpy.data.objects:
            for nam in name_list:
                self.Preserve_Parents(obj)
                if nam in obj.name:
                    obj.select = True

                    #Location:
                    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")

                    #Rotation/Scale:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                else:
                    pass
        
    #A function to preserve an object's parent:    
    def Preserve_Parents(self, obj):
        try:
            obj.parent = bpy.data.objects[parents_list[obj.name]]
        except:
            pass

    #Quite simple. Deletes the objects that don't have any geometry
    def Delete_Objects(self):

        bpy.ops.object.select_all(action="DESELECT")
        try:
            bpy.data.objects["New Geometry"].select = True
            vert_check = bpy.data.objects["New Geometry"]
            if len(vert_check.data.vertices) > 0:
                self.Clear_New_Geometry_Data("New Geometry")
            else:
                bpy.ops.object.delete()
        except:
            pass

        bpy.ops.object.select_all(action="DESELECT")
        try:
            bpy.data.objects["MultiEdit"].select = True
            vert_check = bpy.data.objects["MultiEdit"]
            if len(vert_check.data.vertices) > 0:
                bpy.data.objects["MultiEdit"].name = "New Geometry"
                self.Clear_New_Geometry_Data("New Geometry")
            else:
                bpy.ops.object.delete()
        except:
            pass

    #Clears all the new geometry's data.
    def Clear_New_Geometry_Data(self, obj_name):
        main_object = bpy.data.objects[obj_name]

        #Remove object groups:
        bpy.context.scene.objects.active = main_object
        bpy.ops.group.objects_remove_all()

        #Remove vertex groups:
        for vgroup in main_object.vertex_groups:
            main_object.vertex_groups.remove(vgroup)

        #Remove UV layers:
        for uv in main_object.data.uv_textures:
            main_object.data.uv_textures.remove(uv)

        #Set origin point to center of geometry:
        main_object.select = True
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")

        #Remove materials:
        while main_object.data.materials:
            main_object.data.materials.pop()



class MultiEdit_Panel(bpy.types.Panel):
    bl_label = "Multiple Objects Editing"
    bl_idname = "MultiEdit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"

    def draw(self, context):
         layout = self.layout
         sce = bpy.context.scene

         layout.operator(MultiEdit_Enter.bl_idname)
         layout.operator(MultiEdit_Exit.bl_idname)
         layout.prop(sce, "Preserve_Location_Rotation_Scale")

def register():
    bpy.utils.register_class(MultiEdit_Enter)
    bpy.utils.register_class(MultiEdit_Exit)
    bpy.utils.register_class(MultiEdit_Panel)
    bpy.types.Scene.Preserve_Location_Rotation_Scale = bpy.props.BoolProperty \
      (
        name = "Preserve Location/Rotation/Scale",
        description = "Preserve the Location/Rotation/Scale values of the objects.",
        default = True
      )

def unregister():
    bpy.utils.unregister_class(MultiEdit_Enter);
    bpy.utils.unregister_class(MultiEdit_Exit);
    bpy.utils.unregister_class(MultiEdit_Panel);

if __name__ == "__main__":
    register()
