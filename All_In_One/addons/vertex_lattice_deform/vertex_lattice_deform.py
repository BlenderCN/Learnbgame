#    <Vertex Lattice Deform, Blender addon for quickly creating lattice deformations on objects.>
#    Copyright (C) <2017> <Nikko Miu>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy


bl_info = {
    'name': 'Vertex Lattice Deform',
    'description': 'Adds a menu in the operator panel for quickly creating, applying, and cleaning up vertex lattice deformation modifiers',
    'category': '3D View',
    'author': 'Nikko Miu',
    'version': (1,0,3),
    'support': 'COMMUNITY',
    'location': 'View3D > Tools > Vertex Lattice Deform'
}

scale_padding = 0.2
lattice_prop_name = 'vertex_lattice_props'
lattice_mod_name = 'Vertex_Lattice'

class OBJECT_OT_create_lattice_deform(bpy.types.Operator):
    bl_label = "Create Lattice Deform"
    bl_idname = "object.create_lattice_deform"
    bl_description = "Create a new vertex lattice deform on the selected verticies"

    lattice_points = bpy.props.IntProperty(name='Lattice Point')

    def execute(self, context):
        try:
            create_vert_lattice(self.lattice_points)

            return {'FINISHED'}
        except Exception as err:
            self.report({'ERROR'}, str(err.args[0]))

            return {'CANCELLED'}

class OBJECT_OT_finish_lattice_deform_confirm(bpy.types.Operator):
    bl_label = "Apply Lattice Deform"
    bl_idname = 'object.confirm_lattice_deform'
    bl_description = 'Apply the Lattice Deform and remove the vertex group'

    confirm_lattice = bpy.props.BoolProperty(name='Should Confirm the Lattice Deformation')

    def execute(self, context):
        try:
            if is_vert_lattice():
                if self.confirm_lattice:
                    apply_vert_lattice()
                else:
                    cancel_vert_lattice()
            else:
                raise Exception('Lattice is not vertex lattice modifier')

            return {'FINISHED'}
        except Exception as err:
            self.report({'ERROR'}, str(err.args[0]))

            return {'CANCELLED'}

class OBJECT_OT_lattice_deform_custom(bpy.types.Operator):
    bl_idname = 'object.custom_lattice_deform'
    bl_label = 'Custom Size Vertex Lattice Deform'

    u_prop = bpy.props.IntProperty(name='U', min=1, max=64)
    v_prop = bpy.props.IntProperty(name='V', min=1, max=64)
    w_prop = bpy.props.IntProperty(name='H', min=1, max=64)

    def execute(self, context):
        create_vert_lattice((self.u_prop, self.v_prop, self.w_prop))

        return {'FINISHED'}

    def invoke(self, context, event):
        global vert_lattice_props_u, vert_lattice_props_v, vert_lattice_props_w

        self.u_prop = vert_lattice_props_u
        self.v_prop = vert_lattice_props_v
        self.w_prop = vert_lattice_props_w

        return context.window_manager.invoke_props_dialog(self)

class OBJECT_PT_lattice_deform(bpy.types.Panel):
    bl_label = 'Vertex Lattice Deform'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = 'Tools'
    bl_context = 'mesh_edit'

    def draw(self, context):
        self.layout.label('Add:')

        row = self.layout.row(align=True)
        row.alignment = 'EXPAND'

        # Standard Buttons
        b2 = row.operator('object.create_lattice_deform', text='2x2x2')
        b3 = row.operator('object.create_lattice_deform', text='3x3x3')
        b4 = row.operator('object.create_lattice_deform', text='4x4x4')

        b2.lattice_points = 2
        b3.lattice_points = 3
        b4.lattice_points = 4

        # Custom Button
        global vert_lattice_props_u, vert_lattice_props_v, vert_lattice_props_w

        vert_lattice_props_u = 2
        vert_lattice_props_v = 2
        vert_lattice_props_w = 2

        self.layout.row().operator('object.custom_lattice_deform', text='Custom')

class OBJECT_PT_lattice_deform_confirm(bpy.types.Panel):
    bl_category = "Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "lattice_edit"
    bl_label = "Vertex Lattice Deform"

    @classmethod
    def poll(cls, context):
        return is_vert_lattice()

    def draw(self, context):
        self.layout.row().operator('object.confirm_lattice_deform', text='Apply Deform', icon='FILE_TICK').confirm_lattice = True
        self.layout.row().operator('object.confirm_lattice_deform', text='Discard Deform', icon='CANCEL').confirm_lattice = False

def get_new_vert_group_name(obj):
    vg_name = 'Vertex_Lattice'

    # Try to create the default Group with just Vertex_Lattice
    vg = obj.vertex_groups.get(vg_name)

    # If the default Vertex_Lattice group doesn't exist use that
    if vg is None:
        return vg_name

    iter = 1
    out_name = None

    # Create the Vertex_Lattice_XXX group
    while out_name is None:
        tmp_name = vg_name + '_' + str(iter).zfill(3)

        # Get the vertex group
        vg = obj.vertex_groups.get(tmp_name)

        # Create the vertex group if not exist (TODO INVERT TO ENSURE VERT GROUP DOES NOT GET OVERRDIEN)
        if vg is None:
            out_name = tmp_name
        else:
            iter += 1

    return out_name

def create_new_vert_group(obj):
    return obj.vertex_groups.new(name=get_new_vert_group_name(obj))

def get_selected_verts(obj):
    sel_verts = []
    sel_vert_ids = []

    for vert in obj.data.vertices:
        if vert.select:
            sel_verts.append(vert)
            sel_vert_ids.append(vert.index)

    if len(sel_verts) <= 1:
        raise Exception('Not enough vertices selected. Please select 2 or more verticies')

    return sel_verts, sel_vert_ids

def get_avg_from_min_max(min, max):
    return tuple((
        (min[0] + max[0]) / 2,
        (min[1] + max[1]) / 2,
        (min[2] + max[2]) / 2
    ))

def get_min_max_from_verts(verts, obj):
    max = [-9999999.0, -9999999,0, -9999999.0]
    min = [9999999.0, 9999999.0, 9999999.0]

    for vert in verts:
        world_coord = obj.matrix_world * vert.co

        # Check if bigger
        if world_coord.x > max[0]: max[0] = world_coord.x
        if world_coord.y > max[1]: max[1] = world_coord.y
        if world_coord.z > max[2]: max[2] = world_coord.z

        # Check if smaller
        if world_coord.x < min[0]: min[0] = world_coord.x
        if world_coord.y < min[1]: min[1] = world_coord.y
        if world_coord.z < min[2]: min[2] = world_coord.z

        print(obj.matrix_world)
        print(world_coord)

    return min, max

def get_scale_from_min_max(min, max, lattice_points):
    # Calc raw scale w/ padding
    scale = [
        max[0] - min[0] + scale_padding,
        max[1] - min[1] + scale_padding,
        max[2] - min[2] + scale_padding
    ]

    return (
        scale[0] * (1 / (lattice_points[0] - 1)),
        scale[1] * (1 / (lattice_points[1] - 1)),
        scale[2] * (1 / (lattice_points[2] - 1))
    )

def create_lattice_obj(loc, scale, lattice_points):
    bpy.ops.object.mode_set(mode='OBJECT')

    lattice = bpy.data.lattices.new('Lattice')

    # Set the number of points
    lattice.points_u = lattice_points[0]
    lattice.points_v = lattice_points[1]
    lattice.points_w = lattice_points[2]

    lattice_obj = bpy.data.objects.new('Lattice', lattice)
    lattice_obj.location = loc
    lattice_obj.scale = scale

    bpy.context.scene.objects.link(lattice_obj)

    return lattice_obj

def create_vert_lattice(lattice_points):
    try:
        if type(lattice_points) is int:
            lattice_points = (lattice_points, lattice_points, lattice_points)

        # Get the current object
        obj = bpy.context.scene.objects.active

        # Create the new vertex group
        vg = create_new_vert_group(obj)

        # Set mode to object
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get the selected verts
        verts, vert_ids = get_selected_verts(obj)

        # Add the verts to the vertex group
        vg.add(vert_ids, 1.0, 'ADD')

        # Get the min/max for all verts
        min, max = get_min_max_from_verts(verts, obj)

        # Create the lattice
        lattice_obj = create_lattice_obj(get_avg_from_min_max(min, max), get_scale_from_min_max(min, max, lattice_points), lattice_points)

        # Create the lattice modifier
        mod = obj.modifiers.new(lattice_mod_name, 'LATTICE')
        mod.vertex_group = vg.name
        mod.object = lattice_obj

        lattice_obj[lattice_prop_name] = { "object_name": obj.name, "mod_name": mod.name, 'vert_group_name': vg.name }

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Set selected object to lattice
        lattice_obj.select = True
        bpy.context.scene.objects.active = lattice_obj

        # Update the scene
        bpy.context.scene.update()

    except Exception as err:
        if bpy.context.object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj

        raise Exception(err.args[0])

    finally:
        # Go back to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

def is_vert_lattice():
    # Only try if there is an active object
    if bpy.context.scene.objects.active:
        # It is a vert lattice if the object has props
        return lattice_prop_name in bpy.context.scene.objects.active
    else:
        return False

def apply_vert_lattice():
    try:
        lattice_obj = bpy.context.scene.objects.active

        # Stop execution if the object doesn't have lattice props
        if not lattice_prop_name in lattice_obj:
            raise Exception('Object does not have required vertex lattice deform props')

        lattice_props = lattice_obj[lattice_prop_name]

        # Set mode to object
        bpy.ops.object.mode_set(mode='OBJECT')

        # Make sure the target object exists
        if not lattice_props['object_name'] in bpy.data.objects:
            raise Exception('Object not found, ensure the object exists and is named ' + lattice_props['object_name'])

        obj = bpy.data.objects[lattice_props['object_name']]

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select and set obj as active
        obj.select = True
        bpy.context.scene.objects.active = obj

        # Check that modifier exists
        if not lattice_props['mod_name'] in obj.modifiers:
            raise Exception('Could not apply modifier on ' + obj.name)

        # Get the vertex group on the object
        obj_grp = obj.vertex_groups.get(lattice_props['vert_group_name'])
        if not obj_grp:
            raise Exception('Could not find vertex group ' + lattice_props['vert_group_name'] + ' on ' + obj.name)

        # Apply Modifier
        bpy.ops.object.modifier_apply(modifier=lattice_props['mod_name'])

        # Delete the Vertex Group
        obj.vertex_groups.remove(obj_grp)

        # Delete the Lattice
        bpy.data.objects.remove(lattice_obj, True)

    except Exception as err:
        bpy.ops.object.select_all(action='DESELECT')
        lattice_obj.select = True
        bpy.context.scene.objects.active = lattice_obj

        raise Exception(err.args[0])

    finally:
        # Go back to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

def cancel_vert_lattice():
    try:
        lattice_obj = bpy.context.scene.objects.active

        # Stop execution if the object doesn't have lattice props
        if not lattice_prop_name in lattice_obj:
            raise Exception('Object does not have required vertex lattice deform props')

        lattice_props = lattice_obj[lattice_prop_name]

        # Set mode to object
        bpy.ops.object.mode_set(mode='OBJECT')

        # Make sure the target object exists
        if not lattice_props['object_name'] in bpy.data.objects:
            raise Exception('Object not found, ensure the object exists and is named ' + lattice_props['object_name'])

        obj = bpy.data.objects[lattice_props['object_name']]

        # Get the vertex group
        obj_grp = obj.vertex_groups.get(lattice_props['vert_group_name'])
        if not obj_grp:
            raise Exception('Could not find vertex group ' + lattice_props['vert_group_name'] + ' on ' + obj.name)

        # Delete the Modifier
        obj_mod = obj.modifiers.get(lattice_props['mod_name'])
        if not obj_mod:
            raise Exception('Could not find modifier ' + lattice_props['mod_name'] + ' on ' + obj.name)

        # Remove the modifier
        obj.modifiers.remove(obj_mod)

        # Delete the Vertex Group
        obj.vertex_groups.remove(obj_grp)

        # Delete the Lattice
        bpy.data.objects.remove(lattice_obj, True)

        # Select and set obj as active
        obj.select = True
        bpy.context.scene.objects.active = obj

    except Exception as err:
        bpy.ops.object.select_all(action='DESELECT')
        lattice_obj.select = True
        bpy.context.scene.objects.active = lattice_obj

        raise Exception(err.args[0])

    finally:
        # Go back to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

def register():
    bpy.utils.register_class(OBJECT_OT_create_lattice_deform)
    bpy.utils.register_class(OBJECT_OT_finish_lattice_deform_confirm)
    bpy.utils.register_class(OBJECT_OT_lattice_deform_custom)
    bpy.utils.register_class(OBJECT_PT_lattice_deform)
    bpy.utils.register_class(OBJECT_PT_lattice_deform_confirm)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_create_lattice_deform)
    bpy.utils.unregister_class(OBJECT_OT_finish_lattice_deform_confirm)
    bpy.utils.unregister_class(OBJECT_OT_lattice_deform_custom)
    bpy.utils.unregister_class(OBJECT_PT_lattice_deform)
    bpy.utils.unregister_class(OBJECT_PT_lattice_deform_confirm)

if __name__ == '__main__':
    register()
