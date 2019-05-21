import os
import bpy
from bpy.props import StringProperty
from .. utils.asset_loader import blends_folder, update_asset_loaders
from .. import M3utils as m3


class RemoveDecal01(bpy.types.Operator):
    bl_idname = "machin3.remove_decal01"
    bl_label = "Remove Decal01"

    decal01_name = StringProperty()

    def execute(self, context):
        m3.clear()
        remove_decal01(self.decal01_name)
        context.area.tag_redraw()
        return {"FINISHED"}


def remove_decal01(decal01_name):
    if decal01_name.startswith("c_"):
        filepath = os.path.join(blends_folder("decals01", custom=True), decal01_name + ".blend")
    else:
        filepath = os.path.join(blends_folder("decals01"), decal01_name + ".blend")

    print("removing '%s'" % (decal01_name))

    # get filenames
    blend = filepath
    icon = os.path.join(os.path.dirname(filepath), "..", "icons", decal01_name + ".png")
    texturespath = os.path.join(os.path.dirname(filepath), "textures")

    textures = []
    for texture in os.listdir(texturespath):
        if texture.startswith(decal01_name.replace("decal", "decals")):
            textures.append(os.path.join(texturespath, texture))

    # delete blend, icon and textures
    os.remove(blend)
    print("removed '%s'" % blend)

    os.remove(icon)
    print("removed '%s'" % icon)

    for t in textures:
        os.remove(t)
        print("removed '%s'" % t)

    # update asset loader, so the just removed decal cant be inserted
    update_asset_loaders(category="decals01")

    # delete decals of the deleted kind in the current scene
    for obj in bpy.data.objects:
        if obj.name.startswith(decal01_name) or obj.name.startswith("projected_" + decal01_name):
            print("removing decal obj '%s'" % (obj.name))
            mat = obj.material_slots[0].material
            bpy.data.objects.remove(obj, do_unlink=True)

            if mat is not None:
                print("removing decal material '%s'" % (mat.name))
                bpy.data.materials.remove(mat, do_unlink=True)
