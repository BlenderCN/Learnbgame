from bpy.types import Operator

class BIOLOGY_ANIMAL_DOG_ADD(Operator):
    bl_idname = "biology.animal.dog"
    bl_label = "dog"
    bl_description = "Create a dog"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Dog")
        obj = bpy.data.objects.new("Dog", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
		

class BIOLOGY_ANIMAL_CAT_ADD(Operator):
    bl_idname = "biology.animal.cat"
    bl_label = "cat"
    bl_description = "Create a cat"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Cat")
        obj = bpy.data.objects.new("Cat", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_SHEEP_ADD(Operator):
    bl_idname = "biology.animal.sheep"
    bl_label = "sheep"
    bl_description = "Create a sheep"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Sheep")
        obj = bpy.data.objects.new("Sheep", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}


class BIOLOGY_ANIMAL_HORSE_ADD(Operator):
    bl_idname = "biology.animal.horse"
    bl_label = "horse"
    bl_description = "Create a horse"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Horse")
        obj = bpy.data.objects.new("Horse", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_FISH_ADD(Operator):
    bl_idname = "biology.animal.fish"
    bl_label = "fish"
    bl_description = "Create a fish"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Fish")
        obj = bpy.data.objects.new("Fish", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_PIG_ADD(Operator):
    bl_idname = "biology.animal.pig"
    bl_label = "pig"
    bl_description = "Create a pig"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Pig")
        obj = bpy.data.objects.new("Pig", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}


class BIOLOGY_ANIMAL_ELEPHANT_ADD(Operator):
    bl_idname = "biology.animal.elephant"
    bl_label = "elephant"
    bl_description = "Create a elephant"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Elephant")
        obj = bpy.data.objects.new("Elephant", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_SNAKE_ADD(Operator):
    bl_idname = "biology.animal.snake"
    bl_label = "snake"
    bl_description = "Create a snake"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        mesh = bpy.data.meshes.new("Snake")
        obj = bpy.data.objects.new("Snake", mesh)
        context.view_layer.objects.active = obj
        return obj

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

