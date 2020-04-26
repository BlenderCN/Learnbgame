import bpy

import json


#
#
# ShapeKeys Generation

class CreateShapeKeys(bpy.types.Operator):
    """Create new Shape Keys, using existing ones, as described in an external json file."""
    bl_idname = "object.create_shape_keys"
    bl_label = "Create ShapeKeys from File"

    shape_keys_filename = bpy.props.StringProperty(name="ShapeKeysFile",
                                                   description="The json file with the description of the new ShapeKeys",
                                                   subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'MESH':
                if context.mode == 'OBJECT':
                    return True

        return False

    def execute(self, context):
        #
        # Check for the existence of all the required shapekeys
        obj = context.active_object
        mesh = obj.data
        key_block_names = [kb.name for kb in mesh.shape_keys.key_blocks]

        with open(self.shape_keys_filename, 'r') as keyshapes_file:
            keyshapes_db = json.load(keyshapes_file)

        for viseme, db_entry in keyshapes_db.items():
            for shape_key_name, weight in db_entry.items():
                if shape_key_name not in key_block_names:
                    self.report({'ERROR'}, "Object doesn't have a key_block named '{}'.".format(shape_key_name))
                    return {'CANCELLED'}

        #
        # Build the new visemes, one-by-one
        for vis in keyshapes_db:
            # First, reset the face shape
            for kb in mesh.shape_keys.key_blocks:
                kb.value = 0.0
            # Set the values
            viseme_spec_dict = keyshapes_db[vis]
            for expression_name in viseme_spec_dict:
                expression_val = viseme_spec_dict[expression_name]
                mesh.shape_keys.key_blocks[expression_name].value = expression_val

            # bpy.ops.object.shape_key_add(from_mix=True)
            sk = obj.shape_key_add(name=vis, from_mix=True)

        # Reset back to 0. Just handy for further work.
        for kb in mesh.shape_keys.key_blocks:
            kb.value = 0.0

        return {'FINISHED'}


class RemoveShapeKeys(bpy.types.Operator):
    """Remove the shape keys listed as keys of the provided shapekeys database."""
    bl_idname = "object.remove_shape_keys"
    bl_label = "Remove ShapeKeys from File"

    shape_keys_filename = bpy.props.StringProperty(name="ShapeKeysFile",
                                                   description="The json file with the description of the new ShapeKeys",
                                                   subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'MESH':
                if context.mode == 'OBJECT':
                    return True

        return False

    def execute(self, context):
        with open(self.shape_keys_filename, 'r') as keyshapes_file:
            keyshapes_db = json.load(keyshapes_file)

        #
        # Check for the existence of all the required shapekeys
        obj = context.active_object
        assert isinstance(obj, bpy.types.Object)
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        key_block_names = [kb.name for kb in mesh.shape_keys.key_blocks]

        for kb in key_block_names:
            dotpos = kb.find('.')
            kb_nodot = kb[:dotpos] if dotpos != -1 else kb
            if kb_nodot in keyshapes_db.keys():
                obj.shape_key_remove(mesh.shape_keys.key_blocks[kb])

        return {'FINISHED'}


# Use:
# Enter Armature Edit mode (To create new bones) and invoke:
# bpy.ops.object.create_shape_key_control_bones()
class CreateShapeKeyControlBones(bpy.types.Operator):
    """Create the bones to drive the mouth shapes"""
    bl_idname = "object.create_shape_key_control_bones"
    bl_label = "Create Shape Key Control Bones"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'ARMATURE':
                if context.mode == 'EDIT_ARMATURE':
                    return True

        return False

    def execute(self, context):

        selected_objs = context.selected_objects

        if len(selected_objs) != 2:
            self.report({'ERROR'}, "Need to select TWO objects: mesh first and armature later.")
            return {'CANCELLED'}

        armature_obj, mesh_obj = selected_objs

        if armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "The last selected object {} must be an ARMATURE: found {}".format(armature_obj.name, armature_obj.type))
            return {'CANCELLED'}

        if mesh_obj.type != 'MESH':
            self.report({'ERROR'}, "The first selected object {} must be a MESH: found {}".format(mesh_obj.name, mesh_obj.type))
            return {'CANCELLED'}

        armature = armature_obj.data
        mesh = mesh_obj.data

        shape_key_names = [kb.name for kb in mesh.shape_keys.key_blocks]

        x = 0
        z = 2

        for sk in shape_key_names:
            bl_bone = armature.edit_bones.new('shapekey-' + sk)
            bl_bone.head = (x, 0, z)
            bl_bone.tail = (x, 0, z + 0.1)

            x += 0.1

        return {'FINISHED'}


class RemoveShapeKeyControlBones(bpy.types.Operator):
    """Remove the bones to drive the key shapes"""
    bl_idname = "object.remove_shape_key_control_bones"
    bl_label = "Remove Shape Key Control Bones"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'ARMATURE':
                if context.mode == 'EDIT_ARMATURE':
                    return True

        return False

    def execute(self, context):

        armature = context.active_object.data

        edit_bones_list = [b for b in armature.edit_bones]

        for eb in edit_bones_list:
            ebname = eb.name
            if ebname.startswith('shapekey-'):
                armature.edit_bones.remove(eb)

        return {'FINISHED'}


#
#
# Control Drivers generation


# Use:
# Enter Object mode and invoke:
# bpy.ops.object.drive_shape_keys()
class DriveShapeKeys(bpy.types.Operator):
    """Add the drivers to the shape keys in order to control them with the control bones."""
    bl_idname = "object.drive_shape_keys"
    bl_label = "Add Shape Key Control Bone Drivers"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'MESH':
                if context.mode == 'OBJECT':
                    return True

        return False

    def execute(self, context):

        mesh_obj = context.active_object
        mesh = mesh_obj.data

        # Check for the existance of all control bones in the parent armature
        parent_arm = bpy.context.active_object.parent
        if parent_arm is None:
            self.report({'ERROR'}, "Object doesn't have a parent armature.")
            return {'CANCELLED'}

        shape_key_names = [kb.name for kb in mesh.shape_keys.key_blocks]
        parent_arm_bone_names = [b.name for b in parent_arm.pose.bones]
        for sk in shape_key_names:
            control_name = 'shapekey-' + sk
            if control_name not in parent_arm_bone_names:
                self.report({'ERROR'}, "Parent armature {} has no bone {}".format(parent_arm.name, control_name))
                return {'CANCELLED'}

        mesh = context.active_object.data

        for sk in shape_key_names:
            print("Adding driver to " + sk)

            target_bone = parent_arm.pose.bones['shapekey-' + sk]
            print("Targeting " + target_bone.name)

            shapekey = mesh.shape_keys.key_blocks[sk]
            assert type(shapekey) == bpy.types.ShapeKey

            driving_fcurve = shapekey.driver_add('value')
            assert type(driving_fcurve) == bpy.types.FCurve

            driver = driving_fcurve.driver
            driver.type = 'AVERAGE'

            # Remove default generator
            while len(driving_fcurve.modifiers) > 0:
                driving_fcurve.modifiers.remove(driving_fcurve.modifiers[0])

            v = driver.variables.new()
            v.name = 'var'
            v.type = 'TRANSFORMS'

            # There is one target by default
            assert (len(v.targets) == 1)

            # Set the target
            # v.targets[0].id_type = 'OBJECT'
            v.targets[0].id = parent_arm
            v.targets[0].bone_target = target_bone.name
            v.targets[0].data_path = 'location[1]'
            v.targets[0].transform_space = 'LOCAL_SPACE'
            v.targets[0].transform_type = 'LOC_Y'

        return {'FINISHED'}


# Use:
# Select the mesh, enter Object mode and invoke:
# bpy.ops.object.undrive_shape_keys()
class UndriveShapeKeys(bpy.types.Operator):
    """Remove the drivers from the shape keys"""
    bl_idname = "object.undrive_shape_keys"
    bl_label = "Remove Shape Key Control Bone Drivers"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type == 'MESH':
                if context.mode == 'OBJECT':
                    return True

        return False

    def execute(self, context):

        mesh_obj = context.active_object
        mesh = mesh_obj.data

        # Check for the existance of all control bones in the parent armature
        parent_arm = bpy.context.active_object.parent
        if parent_arm is None:
            self.report({'ERROR'}, "Object doesn't have a parent armature.")
            return {'CANCELLED'}

        shape_key_names = [kb.name for kb in mesh.shape_keys.key_blocks]
        parent_arm_bone_names = [b.name for b in parent_arm.pose.bones]
        for sk in shape_key_names:
            control_name = 'shapekey-' + sk
            if control_name not in parent_arm_bone_names:
                self.report({'ERROR'}, "Parent armature {} has no bone {}".format(parent_arm.name, control_name))
                return {'CANCELLED'}

        mesh = context.active_object.data

        for sk in shape_key_names:
            print("Removing driver from " + sk)

            shapekey = mesh.shape_keys.key_blocks[sk]
            assert type(shapekey) == bpy.types.ShapeKey

            shapekey.driver_remove('value')

        return {'FINISHED'}


#
# (UN)REGISTER
#
def register():
    bpy.utils.register_class(CreateShapeKeys)
    bpy.utils.register_class(RemoveShapeKeys)
    bpy.utils.register_class(CreateShapeKeyControlBones)
    bpy.utils.register_class(RemoveShapeKeyControlBones)
    bpy.utils.register_class(DriveShapeKeys)
    bpy.utils.register_class(UndriveShapeKeys)


def unregister():
    bpy.utils.unregister_class(CreateShapeKeys)
    bpy.utils.unregister_class(RemoveShapeKeys)
    bpy.utils.unregister_class(CreateShapeKeyControlBones)
    bpy.utils.unregister_class(RemoveShapeKeyControlBones)
    bpy.utils.unregister_class(DriveShapeKeys)
    bpy.utils.unregister_class(UndriveShapeKeys)


if __name__ == "__main__":
    register()
