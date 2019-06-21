
import os
import re
import time

import bpy

from . import convert


class JetFluidCreateStandartParticleSystem(bpy.types.Operator):
    bl_idname = "jet_fluid.create_particle_system"
    bl_label = "Create Standart Particle System"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        start_time = time.time()
        convert.convert_particles_to_standart_particle_system(context, obj)
        print('total time:', time.time() - start_time)
        return {'FINISHED'}


class JetFluidResetMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.reset_mesh"
    bl_label = "Reset Jet Fluid Cache"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        file_path = bpy.path.abspath(obj.jet_fluid.cache_folder)
        if not os.path.exists(file_path):
            return {'FINISHED'}
        for file_ in os.listdir(file_path):
            if re.search('mesh_[0-9]*.bin', file_):
                os.remove(file_path + file_)
        return {'FINISHED'}


class JetFluidResetParticles(bpy.types.Operator):
    bl_idname = "jet_fluid.reset_particles"
    bl_label = "Reset Jet Fluid Cache"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        file_path = bpy.path.abspath(obj.jet_fluid.cache_folder)
        if not os.path.exists(file_path):
            return {'FINISHED'}
        for file_ in os.listdir(file_path):
            if re.search('particles_[0-9]*.bin', file_) or re.search('fluid_[0-9]*_00.bphys', file_):
                os.remove(file_path + file_)
        return {'FINISHED'}


class JetFluidResetPhysicCache(bpy.types.Operator):
    bl_idname = "jet_fluid.reset_physic_cache"
    bl_label = "Reset Physic Cache"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        file_path = bpy.path.abspath(obj.jet_fluid.cache_folder)
        if not os.path.exists(file_path):
            return {'FINISHED'}
        for file_ in os.listdir(file_path):
            if re.search('fluid_[0-9]*_00.bphys', file_):
                os.remove(file_path + file_)
        return {'FINISHED'}


class JetFluidAdd(bpy.types.Operator):
    bl_idname = "jet_fluid.add"
    bl_label = "Add Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        obj.jet_fluid.is_active = True
        return {'FINISHED'}


class JetFluidRemove(bpy.types.Operator):
    bl_idname = "jet_fluid.remove"
    bl_label = "Remove Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        obj.jet_fluid.is_active = False
        obj.jet_fluid.object_type = 'NONE'
        return {'FINISHED'}


__CLASSES__ = [
    JetFluidAdd,
    JetFluidRemove,
    JetFluidResetParticles,
    JetFluidResetMesh,
    JetFluidCreateStandartParticleSystem,
    JetFluidResetPhysicCache
]


def register():
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
