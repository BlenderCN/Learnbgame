import bpy
import os

class Operator_BlenRig5_Add_Biped(bpy.types.Operator):

    bl_idname = "blenrig5.add_biped_rig"
    bl_label = "BlenRig 5 Add Biped Rig"
    bl_description = "Generates BlenRig 5 biped rig"
    bl_options = {'REGISTER', 'UNDO',}


    @classmethod
    def poll(cls, context):                            #method called by blender to check if the operator can be run
        return bpy.context.scene != None

    def import_blenrig_biped(self, context):
        CURRENT_DIR = os.path.dirname(__file__)
        filepath =  os.path.join(CURRENT_DIR, "blenrig_biped.blend")
        scene = bpy.context.scene

        # Link the top-level collection into the file.
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.collections = ["blenrig_biped"]

        # Add the collection(s) to the scene.
        for collection in data_to.collections:
            scene.collection.children.link(collection)

    def execute(self, context):
        self.import_blenrig_biped(context)
        return{'FINISHED'}
