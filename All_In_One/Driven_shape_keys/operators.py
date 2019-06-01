import bpy
import bmesh
from mathutils import Vector


class SplitShapes(bpy.types.Operator):
    bl_idname = "driven.splitshapes"
    bl_label = "Splitshapes"
    bl_description = "Separate the active shape key in their components folowing the bone orientation"
    bl_options = {"REGISTER", "UNDO"}
    
    create_x = bpy.props.BoolProperty("Create X", default = True)
    create_y = bpy.props.BoolProperty("Create y", default = True)
    create_z = bpy.props.BoolProperty("Create Z", default = True)
    
    @classmethod
    def poll(cls, context):
        if context.active_bone:
            if len(context.selected_objects) == 2:
                if "MESH" in [ob.type for ob in context.selected_objects]:
                    return True
        else:
            return False
    
    def execute(self, context):
        '''
        This operator basicaly gets the morphy coordinates
        of each vertex subtracts by its basis coordinates
        and project the new vector on a bone component.
        so just add the basis coodinates for create a
        projection of the shape key in each bone transform
        components.
        By adding the three new shape keys we get the original shape
        '''
        bone = context.active_pose_bone
        
        x = Vector((1, 0, 0))
        y = Vector((0, 1, 0))
        z = Vector((0, 0, 1))
        rot = bone.matrix.to_euler()
        
        x.rotate(rot)
        y.rotate(rot)
        z.rotate(rot)
        vecs = [x, y, z]
        
        mesh = [ob for ob in context.selected_objects if ob.type == "MESH"][0]
        
        shape_name = mesh.active_shape_key.name
        
        for create, sufix, vec in zip([self.create_x, self.create_y, self.create_z], ["_X", "_Y", "_Z"], vecs):
            new_shape_name = shape_name + sufix
            
            if not new_shape_name in mesh.data.shape_keys.key_blocks:
                mesh.shape_key_add(new_shape_name)
            print(mesh)
            
            bm = bmesh.new()
            bm.from_mesh(mesh.data)
            bm.verts.ensure_lookup_table()
            
            shape_layer = bm.verts.layers.shape.get(shape_name)
            n_shape_layer = bm.verts.layers.shape.get(new_shape_name)
            
            for vert in bm.verts:
                base_co = vert.co.xyz
                shape_co = vert[shape_layer].xyz
                delta = shape_co - base_co
                projection = delta.project(vec)
                vert[n_shape_layer].xyz = base_co + projection
            
            bm.to_mesh(mesh.data)
        
        return {"FINISHED"}


class DrivenShapeKey(bpy.types.Operator):
    bl_idname = "driven.add_driver_to_shape_key"
    bl_label = "Add driver to shape key"
    bl_description = "Add driver from bone to shape key"
    bl_options = {"REGISTER", "UNDO"}
    
    axis_items = [("LOC_X", "Location X", "Axis to use from bone"),
                  ("LOC_Y", "Location Y", "Axis to use from bone"),
                  ("LOC_Z", "Location Z", "Axis to use from bone"),
                  ("ROT_X", "Rotation X", "Axis to use from bone"),
                  ("ROT_Y", "Rotation Y", "Axis to use from bone"),
                  ("ROT_Z", "Rotation Z", "Axis to use from bone"),
                  ("SCALE_X", "Scale X", "Axis to use from bone"),
                  ("SCALE_Y", "Scale Y", "Axis to use from bone"),
                  ("SCALE_Z", "Scale Z", "Axis to use from bone"), ]
    axis = bpy.props.EnumProperty(items = axis_items, name = "Axis")
    
    space_items = [("LOCAL_SPACE", "Local Space", "Transform Space"),
                   ("WORLD_SPACE", "World Space", "Transform Space"),
                   ("TRANSFORM_SPACE", "Transform Space", "Transform Space"), ]
    space = bpy.props.EnumProperty(items = space_items, name = "Transform Space")
    scale = bpy.props.FloatProperty(name = "Scale", default = 1)
    set_min = bpy.props.FloatProperty("Min", description = "Set shape key min value", default = -5)
    set_max = bpy.props.FloatProperty("Min", description = "Set shape key max value", default = 5)
    use_normalized = bpy.props.BoolProperty(name = "Use normalized", default = True)
    
    @classmethod
    def poll(cls, context):
        if context.active_bone:
            if len(context.selected_objects) == 2:
                if "MESH" in [ob.type for ob in context.selected_objects]:
                    return True
        return False
    
    def execute(self, context):
        
        bone = context.active_pose_bone
        ob = [ob for ob in context.selected_objects if ob.type == "MESH"][0]
        
        key = ob.active_shape_key
        if not key:
            return {"CANCELLED"}
        
        key.driver_remove("value")
        driver = key.driver_add("value").driver
        vars = driver.variables
        var = vars.new()
        var.type = "TRANSFORMS"
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = bone.name
        var.targets[0].transform_type = self.axis
        var.targets[0].transform_space = self.space
        var.name = "x"
        
        if "ROT_" in self.axis or "SCALE_" in self.axis:
            key.slider_min = -10
            key.slider_max = 10
            driver.expression = "x"
            context.scene.frame_set(context.scene.frame_current)
            val = key.value
            if self.use_normalized and val != 0:
                driver.expression = "(x / {}) * {}".format(val, self.scale)
            else:
                driver.expression = "x * {}".format(self.scale)
            context.scene.frame_set(context.scene.frame_current)
        
        else:
            val = 1
            if self.axis == "LOC_X":
                val = bone.location.x
            
            elif self.axis == "LOC_Y":
                val = bone.location.y
            
            elif self.axis == "LOC_Z":
                val = bone.location.z
            
            if self.use_normalized and val != 0:
                driver.expression = "x / {} * {}".format(val, self.scale)
            else:
                driver.expression = "x * {}".format(self.scale)
        
        key.slider_min = self.set_min
        key.slider_max = self.set_max
        
        return {"FINISHED"}


class UndrivenShapeKey(bpy.types.Operator):
    bl_idname = "driven.remove_driver_from_shape_key"
    bl_label = "Remove driver"
    bl_description = "Remove driver from active shape key"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        if context.active_bone:
            if len(context.selected_objects) == 2:
                if "MESH" in [ob.type for ob in context.selected_objects]:
                    return True
        elif context.active_object.type == "MESH":
            return True
        else:
            return False
    
    def execute(self, context):
        if context.active_bone:
            mesh = [ob for ob in context.selected_objects if ob.type == "MESH"][0]
            if mesh.context.active_shape_key:
                mesh.active_shape_key.driver_remove("value")
        else:
            context.active_object.active_shape_key.driver_remove("value")
        return {"FINISHED"}
