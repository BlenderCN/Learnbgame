# this script convert setting to monochrome lineart for comics
import bpy
# set white materials whole objects, then set edge and freestyle line
def whiteMaterialize(name="lineartWhite"):

    # apply white material and edge
    for item in bpy.data.objects:
        if item.type == 'MESH':
            item.data.materials.append(bpy.data.materials[name])
    return


# add lineart white material
def addLineartMaterial(name="lineartWhite"):
    mat = bpy.data.materials.new(name)
    mat.use_shadeless = False
    mat.diffuse_color = (float(1), float(1), float(1))
    return



# clear lamps and materials exist
def clearObjects():

    scn = bpy.context.scene
    for ob in scn.objects:
        if ob.type == 'LAMP':
        #    if ob.type == 'CAMERA' or ob.type == 'LAMP':
            scn.objects.unlink(ob)

    for item in bpy.data.objects:
        if item.type == 'MESH':
            while item.data.materials:
                item.data.materials.pop(0, update_data=True)
    return

################### add on setting section###########################
bl_info = {
    "name": "White Materialize",
    "category": "Learnbgame",
}

import bpy


class WhiteMaterial(bpy.types.Operator):
    """lineart converter"""
    bl_idname = "white.material"
    bl_label = "white material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):    
        clearObjects()
        addLineartMaterial()
        whiteMaterialize()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(WhiteMaterial)


def unregister():
    bpy.utils.unregister_class(WhiteMaterial)


if __name__ == "__main__":
    register()
