import bpy
import os


def main(context):
    #obtain path to get the blend file in
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)

    # define things nessicary to extrat armor stand from blend file
    blendfile = os.path.join(directory,"resources","armor_stand.blend")
    section = "\\Group\\"
    blend_object = "ArmorStand"

    # translate into terms the append function likes
    filepath = blendfile+section+blend_object
    directory = blendfile+section
    filename = blend_object
    
    # append the armor stand
    bpy.ops.wm.append(
        filepath=filepath,
        filename=filename,
        directory=directory
    )


class operator_rig_import(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mcanim.import_rig"
    bl_label = "Spawn armor stand rig"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        main(context)

        return {'FINISHED'}


def register():
    print("Registeregit d Import Armor Stand")
    #bpy.utils.register_class(operator_rig_import)


def unregister():
    print("unregistered")
    #bpy.utils.unregister_class(operator_rig_import)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.mcanim.import_rig()
