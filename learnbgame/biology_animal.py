import os
import bpy
from bpy.types import Operator

animal_dir = os.path.join(os.path.dirname(__file__), "biology/animal")

class BIOLOGY_ANIMAL_ARMADILLO_ADD(Operator):
    bl_idname = "biology_animal.armadillo"
    bl_label = "armadillo"
    bl_description = "Create a armadillo"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/armadillo/armadillo.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Armadillo"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_BEAR_ADD(Operator):
    bl_idname = "biology_animal.bear"
    bl_label = "bear"
    bl_description = "Create a bear"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/bear/bear.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Bear"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_BIRD_ADD(Operator):
    bl_idname = "biology_animal.bird"
    bl_label = "bird"
    bl_description = "Create a bird"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/bird/bird.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Bird"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_BISON_ADD(Operator):
    bl_idname = "biology_animal.bison"
    bl_label = "bison"
    bl_description = "Create a bison"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/bison/bison.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Bison"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
                                

class BIOLOGY_ANIMAL_CAT_ADD(Operator):
    bl_idname = "biology_animal.cat"
    bl_label = "cat"
    bl_description = "Create a cat"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/cat/cat.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Cat"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_COW_ADD(Operator):
    bl_idname = "biology_animal.cow"
    bl_label = "cow"
    bl_description = "Create a cow"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/cow/cow.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Cow"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_CRAB_ADD(Operator):
    bl_idname = "biology_animal.crab"
    bl_label = "crab"
    bl_description = "Create a crab"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/crab/crab.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Crab"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_CROCODILE_ADD(Operator):
    bl_idname = "biology_animal.crocodile"
    bl_label = "crocodile"
    bl_description = "Create a crocodile"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/crocodile/crocodile.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Crocodile"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_CROW_ADD(Operator):
    bl_idname = "biology_animal.crow"
    bl_label = "crow"
    bl_description = "Create a crow"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/crow/crow.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Crow"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_DEER_ADD(Operator):
    bl_idname = "biology_animal.deer"
    bl_label = "deer"
    bl_description = "Create a deer"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/deer/deer.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Deer"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}


class BIOLOGY_ANIMAL_DOG_ADD(Operator):
    bl_idname = "biology_animal.dog"
    bl_label = "dog"
    bl_description = "Create a dog"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/dog/dog.obj")

        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Dog"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            ##context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_DOLPHIN_ADD(Operator):
    bl_idname = "biology_animal.dolphin"
    bl_label = "dolphin"
    bl_description = "Create a dolphin"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/dolphin/dolphin.obj")
        #context.view_layer.objects.active = 
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Dolphin"
        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            ##context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

		
class BIOLOGY_ANIMAL_DUCK_ADD(Operator):
    bl_idname = "biology_animal.duck"
    bl_label = "duck"
    bl_description = "Create a duck"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/duck/duck.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Duck"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        


class BIOLOGY_ANIMAL_ELEPHANT_ADD(Operator):
    bl_idname = "biology_animal.elephant"
    bl_label = "elephant"
    bl_description = "Create a elephant"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/elephant/elefante.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Elephant"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_ELK_ADD(Operator):
    bl_idname = "biology_animal.elk"
    bl_label = "elk"
    bl_description = "Create a elk"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/elk/elk.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Elk"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_FISH_ADD(Operator):
    bl_idname = "biology_animal.fish"
    bl_label = "fish"
    bl_description = "Create a fish"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/fish/fish.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Fish"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_FROG_ADD(Operator):
    bl_idname = "biology_animal.frog"
    bl_label = "frog"
    bl_description = "Create a frog"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/frog/frog.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Frog"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_GIRAFFE_ADD(Operator):
    bl_idname = "biology_animal.giraffe"
    bl_label = "giraffe"
    bl_description = "Create a giraffe"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/giraffe/giraffe.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Giraffe"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_GOAT_ADD(Operator):
    bl_idname = "biology_animal.goat"
    bl_label = "goat"
    bl_description = "Create a goat"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/goat/goat.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Goat"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_GOLDFISH_ADD(Operator):
    bl_idname = "biology_animal.goldfish"
    bl_label = "goldfish"
    bl_description = "Create a goldfish"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/goldfish/goldfish.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Goldfish"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_GORILLA_ADD(Operator):
    bl_idname = "biology_animal.gorilla"
    bl_label = "gorilla"
    bl_description = "Create a gorilla"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/gorilla/gorilla.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Gorilla"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_HAWK_ADD(Operator):
    bl_idname = "biology_animal.hawk"
    bl_label = "hawk"
    bl_description = "Create a hawk"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/hawk/hawk.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Hawk"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_HORSE_ADD(Operator):
    bl_idname = "biology_animal.horse"
    bl_label = "horse"
    bl_description = "Create a horse"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/horse/horse.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Horse"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_KANGAROO_ADD(Operator):
    bl_idname = "biology_animal.kangaroo"
    bl_label = "kangaroo"
    bl_description = "Create a kangaroo"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/kangaroo/kangaroo.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Kangaroo"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_LION_ADD(Operator):
    bl_idname = "biology_animal.lion"
    bl_label = "lion"
    bl_description = "Create a lion"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/lion/lion.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Lion"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}


class BIOLOGY_ANIMAL_LIZARD_ADD(Operator):
    bl_idname = "biology_animal.lizard"
    bl_label = "lizard"
    bl_description = "Create a lizard"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/lizard/lizard.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Lizard"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_MONKEY_ADD(Operator):
    bl_idname = "biology_animal.monkey"
    bl_label = "monkey"
    bl_description = "Create a monkey"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/monkey/monkey.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Monkey"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_MUSKRAT_ADD(Operator):
    bl_idname = "biology_animal.muskrat"
    bl_label = "muskrat"
    bl_description = "Create a muskrat"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/muskrat/muskrat.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Muskrat"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_OSTRICH_ADD(Operator):
    bl_idname = "biology_animal.ostrich"
    bl_label = "ostrich"
    bl_description = "Create a ostrich"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/ostrich/ostrich.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Ostrich"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_PARROT_ADD(Operator):
    bl_idname = "biology_animal.parrot"
    bl_label = "parrot"
    bl_description = "Create a parrot"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/parrot/parrot.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Parrot"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_PENGUIN_ADD(Operator):
    bl_idname = "biology_animal.penguin"
    bl_label = "penguin"
    bl_description = "Create a penguin"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/penguin/penguin.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Penguin"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_PHEASANT_ADD(Operator):
    bl_idname = "biology_animal.pheasant"
    bl_label = "pheasant"
    bl_description = "Create a pheasant"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/pheasant/pheasant.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Pheasant"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        


class BIOLOGY_ANIMAL_PIG_ADD(Operator):
    bl_idname = "biology_animal.pig"
    bl_label = "pig"
    bl_description = "Create a pig"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/pig/pig.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Pig"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_RABBIT_ADD(Operator):
    bl_idname = "biology_animal.rabbit"
    bl_label = "rabbit"
    bl_description = "Create a rabbit"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/rabbit/rabbit.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Rabbit"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        
class BIOLOGY_ANIMAL_RACOON_ADD(Operator):
    bl_idname = "biology_animal.racoon"
    bl_label = "racoon"
    bl_description = "Create a racoon"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/racoon/racoon.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Racoon"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_SEAHORSE_ADD(Operator):
    bl_idname = "biology_animal.seahorse"
    bl_label = "seahorse"
    bl_description = "Create a seahorse"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/seahorse/seahorse.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Seahorse"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_SEALION_ADD(Operator):
    bl_idname = "biology_animal.sealion"
    bl_label = "sealion"
    bl_description = "Create a sealion"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/sealion/sealion.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Sealion"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        


class BIOLOGY_ANIMAL_SHRIMP_ADD(Operator):
    bl_idname = "biology_animal.shrimp"
    bl_label = "shrimp"
    bl_description = "Create a shrimp"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/shrimp/shrimp.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Shrimp"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}



class BIOLOGY_ANIMAL_SNAKE_ADD(Operator):
    bl_idname = "biology_animal.snake"
    bl_label = "snake"
    bl_description = "Create a snake"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/snake/snake.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Snake"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_SPIDER_ADD(Operator):
    bl_idname = "biology_animal.spider"
    bl_label = "spider"
    bl_description = "Create a spider"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/spider/spider.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Spider"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}


class BIOLOGY_ANIMAL_SWAN_ADD(Operator):
    bl_idname = "biology_animal.swan"
    bl_label = "swan"
    bl_description = "Create a swan"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/swan/swan.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Swan"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
        

class BIOLOGY_ANIMAL_TURTLE_ADD(Operator):
    bl_idname = "biology_animal.turtle"
    bl_label = "turtle"
    bl_description = "Create a turtle"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/turtle/turtle.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Turtle"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_WALRUS_ADD(Operator):
    bl_idname = "biology_animal.walrus"
    bl_label = "walrus"
    bl_description = "Create a walrus"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/walrus/walrus.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Walrus"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}

class BIOLOGY_ANIMAL_WOLF_ADD(Operator):
    bl_idname = "biology_animal.wolf"
    bl_label = "wolf"
    bl_description = "Create a wolf"
    bl_category = 'Biology'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):


        bpy.ops.import_scene.obj(filepath=animal_dir+"/wolf/wolf.obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = "Wolf"

        return obj[0]

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            obj = self.create(context)
            obj.location = bpy.context.scene.cursor_location
            #obj.select_set(state=True)
            #context.view_layer.objects.active = obj
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archipack: Option only valid in Object mode")
            return {'CANCELLED'}
                


def register():

    bpy.utils.register_class(BIOLOGY_ANIMAL_ARMADILLO_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_BEAR_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_BIRD_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_BISON_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_CAT_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_COW_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_CRAB_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_CROCODILE_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_CROW_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_DEER_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_DOG_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_DOLPHIN_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_DUCK_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_ELEPHANT_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_ELK_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_FISH_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_FROG_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_GIRAFFE_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_GOAT_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_GOLDFISH_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_GORILLA_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_HAWK_ADD)    
    bpy.utils.register_class(BIOLOGY_ANIMAL_HORSE_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_KANGAROO_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_LION_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_LIZARD_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_MONKEY_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_MUSKRAT_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_OSTRICH_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_PARROT_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_PENGUIN_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_PHEASANT_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_PIG_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_RABBIT_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_RACOON_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_SEAHORSE_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_SEALION_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_SHRIMP_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_SNAKE_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_SPIDER_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_SWAN_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_TURTLE_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_WALRUS_ADD)
    bpy.utils.register_class(BIOLOGY_ANIMAL_WOLF_ADD)


def unregister():

    bpy.utils.unregister_class(BIOLOGY_ANIMAL_WOLF_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_WALRUS_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_TURTLE_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_SWAN_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_SPIDER_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_SNAKE_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_SHRIMP_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_SEALION_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_SEAHORSE_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_RACOON_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_RABBIT_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_PIG_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_PHEASANT_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_PENGUIN_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_PARROT_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_OSTRICH_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_MUSKRAT_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_MONKEY_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_LIZARD_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_LION_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_KANGAROO_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_HORSE_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_HAWK_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_GORILLA_ADD)    
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_GOLDFISH_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_GOAT_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_GIRAFFE_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_FROG_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_FISH_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_ELK_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_ELEPHANT_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_DUCK_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_DOLPHIN_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_DOG_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_DEER_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_CROW_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_CROCODILE_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_CRAB_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_COW_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_CAT_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_BISON_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_BIRD_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_BEAR_ADD)
    bpy.utils.unregister_class(BIOLOGY_ANIMAL_ARMADILLO_ADD)