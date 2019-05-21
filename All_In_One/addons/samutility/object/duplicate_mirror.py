### Duplicate the mesh with rotation mirrored

import bpy
C = bpy.context


class Duplicate_mirrored(bpy.types.Operator):
    bl_idname = "samutils.duplicate_mirrored"
    bl_label = "Duplicate object mirror"
    bl_description = "duplicate mesh (copy data) with rotation mirrored"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects != []

    def execute(self, context):
        #TODO : make available through bones
        sel = [o for o in bpy.context.selected_objects]
        for ob in bpy.context.selected_objects :

            if ob.name.find(".R")!=-1:
                mirrorObName = ob.name.replace(".R",".L")
            elif ob.name.find(".L")!=-1:
                mirrorObName = ob.name.replace(".L",".R")
            else :
                mirrorObName = ob.name+"_mirror"

            mirrorOb = ob.copy()
            bpy.context.scene.objects.link(mirrorOb)

            mirrorOb.name = mirrorObName
            mirrorOb.layers = ob.layers

            mirrorOb.location[0] =-ob.location[0]
            mirrorOb.location[1] =ob.location[1]
            mirrorOb.location[2] =ob.location[2]

            mirrorOb.rotation_euler[0] =ob.rotation_euler[0]
            mirrorOb.rotation_euler[1] =-ob.rotation_euler[1]
            mirrorOb.rotation_euler[2] =-ob.rotation_euler[2]

            mirrorOb.scale[0] =-ob.scale[0]
            mirrorOb.scale[1] =ob.scale[1]
            mirrorOb.scale[2] =ob.scale[2]

            #vertex groups
            for vg in mirrorOb.vertex_groups :
                if vg.name.endswith(".R"):
                    vg.name = vg.name.replace(".R",".L")
                elif vg.name.endswith(".L"):
                    vg.name = vg.name.replace(".L",".R")
            #groups
            for group in ob.users_group :
                group.objects.link(mirrorOb)

        #deselect previous:
        for o in sel:
            o.select = False

        return {"FINISHED"}
