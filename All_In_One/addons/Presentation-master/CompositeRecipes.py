
bl_info = {
    "name": "Composite Recipes",
    "description": "Blender projects can be generated with json files of a specific format.",
    "category": "Learnbgame",
    "author": "aporter",
    "version": (0,0,1,0),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    "location": "View3D"
}


from CompositeWriter import CompositeWriter
from BlenderToJson import BlenderToJson

import math
import mathutils
import bpy
import os.path
from bpy.props import *
import json
from os import listdir
from os.path import isfile, join
import bpy.types
import inspect
from types import *

from Constants import _keypoint_settings, KEYPOINT_SETTINGS, RENDERSETTINGS, IMAGE_SETTINGS, CYCLESRENDERSETTINGS, CONVERT_INDEX
debugmode = True
def debugPrint(val=None):
    if debugmode and val:
        print(val)

theRecipes = []
theRecipeValues = []

### Read files in directory
def getFilesInDirecotry(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return onlyfiles


def findRecipe(key):
    for n, recipe in enumerate(theRecipes):
        (key1, name, value) = recipe
        if key == key1:
            return n
    raise NameError("Unrecognized key %s" % key)

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class CompositeRecipes(bpy.types.Panel):
    """Composite Recipes"""
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Composite Recipes"
    bl_label = "Composite Recipes"
 
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "composite_recipe_directory")
        layout.operator("object.composite_recipes", text="Update")
        layout.separator()
        layout.prop_menu_enum(context.scene, "my_recipe")
        layout.operator("recipes.add", text="Add")

class CompositeRecipeOpAddButton(bpy.types.Operator):
    bl_idname = "recipes.add"
    bl_label = "Add Recipe"
 
    def execute(self, context):
        ob = context.scene
        ob.use_nodes = True
        
        n = findRecipe(ob.my_recipe)
        debugPrint("my recipe : {}, {}".format(ob.my_recipe, n))
        tree = context.scene.node_tree
        presentation_material_animation_points=[]
        debugPrint("len of recipe values : {}".format(len(theRecipeValues)))
        composite_settings = theRecipeValues[n]["recipe"]
        custom_mat = { "name":"composite", "value": composite_settings["composite"] }
        compositeWriter = CompositeWriter()
        compositeWriter.defineNodeTree(tree, custom_mat, presentation_material_animation_points)
        return{'FINISHED'} 

class CompositeRecipeOp(bpy.types.Operator):
    """Composite Recipe"""
    bl_idname = "object.composite_recipes"
    bl_label = "Composite Recipes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        try:
            composite_recipe_directory = context.scene.composite_recipe_directory
            recipes = readRecipesIn(composite_recipe_directory)
            del theRecipes[:]
            del theRecipeValues[:]
            for recipeData in recipes:
                theRecipes.append((recipeData["file"], recipeData["name"], recipeData["name"] ))
                theRecipeValues.append(recipeData)
            setRecipes()
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Looked up recipes")

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CompositeRecipeOp.bl_idname)

# store keymaps here to access after registration
# addon_keymaps = []
def register():
    bpy.utils.register_class(CompositeRecipeOp)
    bpy.utils.register_class(CompositeRecipeOpAddButton)
    bpy.utils.register_class(CompositeRecipes)
    bpy.types.Scene.composite_recipe_directory = bpy.props.StringProperty \
      (name = "Composite Recipe Directory",
        subtype = "FILE_PATH",
        default = "D:\\BlenderRecipes\\",
        description = "Path to the recipes")
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CompositeRecipeOp)
    bpy.utils.unregister_class(CompositeRecipeOpAddButton)
    bpy.utils.unregister_class(CompositeRecipes)
    del bpy.types.Scene.composite_recipe_directory
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()