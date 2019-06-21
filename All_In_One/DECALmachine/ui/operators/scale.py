import bpy
from bpy.props import StringProperty
from ... utils.modifier import get_displace


class StoreIndividualDecalScale(bpy.types.Operator):
    bl_idname = "machin3.store_individual_decal_scale"
    bl_label = "MACHIN3: Store Individual Decal Scale"
    bl_description = "Store current Decal's Scale\nEMPTY: nothing stored for this type of decal\nHALF: scale is stored for this type of decal, but it's different than the current decal\nFULL: the current decal's scale is stored"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.DM.isdecal

    def execute(self, context):
        decal = context.active_object
        _, _, scale = decal.matrix_world.decompose()

        individualscales = context.scene.DM.individualscales

        if decal.DM.uuid in individualscales:
            ds = individualscales[decal.DM.uuid]
        else:
            ds = individualscales.add()
            ds.name = decal.DM.uuid

        ds.scale = scale

        return {'FINISHED'}


class ClearIndividualDecalScale(bpy.types.Operator):
    bl_idname = "machin3.clear_individual_decal_scale"
    bl_label = "MACHIN3: Clear Individual Decal Scale"
    bl_description = "Clear the Scale for this type of Decal"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.DM.isdecal

    def execute(self, context):
        decal = context.active_object
        individualscales = context.scene.DM.individualscales

        idx = individualscales.keys().index(decal.DM.uuid)

        individualscales.remove(idx)

        return {'FINISHED'}



class Reset(bpy.types.Operator):
    bl_idname = "machin3.reset_decal_scale"
    bl_label = "MACHIN3: Reset Decal Scale"
    bl_description = "Resets Global Scale, Panel Width or Decal Height to 1, 0.04 and 0.9999 accordingly."
    bl_options = {'REGISTER', 'UNDO'}

    mode: StringProperty(name="Mode", default="SCALE")

    def execute(self, context):
        dm = context.scene.DM

        if self.mode == 'SCALE':
            dm.globalscale = 1

        elif self.mode == 'WIDTH':
            dm.panelwidth = 0.04

        elif self.mode == 'HEIGHT':
            dm.height = 0.9999

        return {'FINISHED'}


class Set(bpy.types.Operator):
    bl_idname = "machin3.set_decal_scale"
    bl_label = "MACHIN3: Set Decal Scale"
    bl_description = "description"
    bl_options = {'REGISTER', 'UNDO'}

    mode: StringProperty(name="Mode", default="HEIGHT")

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.DM.isdecal and get_displace(context.active_object)

    def execute(self, context):
        dm = context.scene.DM

        if self.mode == 'HEIGHT':
            displace = get_displace(context.active_object)
            dm.height = displace.mid_level

        return {'FINISHED'}
