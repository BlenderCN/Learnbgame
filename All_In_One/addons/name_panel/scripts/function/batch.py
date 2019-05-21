
# imports
import bpy
import re
from random import random
from . import shared
from .. import storage

# main
def main(self, context):
    '''
        Send datablock values to populate then send collections to process, action group & lineset names are sent to name.
    '''

    # panel
    panel = context.scene.NamePanel

    # option
    option = context.window_manager.BatchName

    # quick batch
    if self.quickBatch:

        # display names
        if panel.displayNames:

            # mode
            if panel.mode == 'SELECTED':

                for object in context.selected_objects:

                    # quick
                    quick(self, context, object, panel, option)

            # mode
            else: # panel.mode == 'LAYERS'
                for object in context.scene.objects:
                    if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]:

                        # quick
                        quick(self, context, object, panel, option)

        # display names
        else: # not panel.displayNames

            # quick
            quick(self, context, context.active_object, panel, option)

        # all
        all = [
            # groups
            self.groups,

            # actions
            self.actions,

            # grease pencil
            self.greasePencils,

            # object
            self.objects,

            # cameras
            self.cameras,

            # meshes
            self.meshes,

            # curves
            self.curves,

            # lamps
            self.lamps,

            # lattices
            self.lattices,

            # metaballs
            self.metaballs,

            # speakers
            self.speakers,

            # armatures
            self.armatures,

            # bones
            self.bones,

            # materials
            self.materials,

            # textures
            self.textures,

            # particle settings
            self.particleSettings
        ]

        # process
        for collection in all:
            if collection != []:

                # process
                process(self, context, collection, option)

    # quick batch
    else: # not quickBatch

        # mode
        if option.mode in {'SELECTED', 'OBJECTS'}:

            # actions
            if option.actions:
                for object in bpy.data.objects:
                    if hasattr(object.animation_data, 'action'):

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, object.animation_data.action, object.animation_data)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, object.animation_data.action, object.animation_data)

                        # mode
                        else:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, object.animation_data.action, object.animation_data)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, object.animation_data.action, object.animation_data)

                # clear duplicates
                actions = []
                [actions.append(item) for item in self.actions if item not in actions]
                self.actions.clear()

                # process
                process(self, context, actions, option)

            # action groups
            if option.actionGroups:
                for object in bpy.data.objects:
                    if hasattr(object.animation_data, 'action'):
                        if hasattr(object.animation_data.action, 'name'):

                            # mode
                            if option.mode in 'SELECTED':
                                if object.select:

                                    # object type
                                    if option.objectType in 'ALL':

                                        # populate
                                        populate(self, context, object.animation_data.action)

                                    # object type
                                    elif option.objectType in object.type:

                                        # populate
                                        populate(self, context, object.animation_data.action)

                            # mode
                            else:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, object.animation_data.action)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, object.animation_data.action)

                # clear duplicates
                actions = []
                [actions.append(item) for item in self.actions if item not in actions]
                self.actions.clear()

                # name action groups
                for action in actions:
                    for group in action[1][1].groups:

                        # new name
                        newName = rename(self, context, group.name, option) if not option.suffixLast else rename(self, context, group.name, option) + option.suffix

                        # update
                        if group.name != newName:

                            # name
                            group.name = newName

                            # count
                            self.count += 1

            # grease pencil
            if option.greasePencil:
                for object in bpy.data.objects:
                    if hasattr(object.grease_pencil, 'name'):

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, object.grease_pencil, object)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, object.grease_pencil, object)

                        # mode
                        else:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, object.grease_pencil, object)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, object.grease_pencil, object)

                # process
                process(self, context, self.greasePencils, option)

                # clear storage
                self.greasePencils.clear()

            # pencil layers
            if option.pencilLayers:
                for object in bpy.data.objects:
                    if hasattr(object.grease_pencil, 'name'):

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:

                                # object type
                                if option.objectType in 'ALL':

                                    # layers
                                    for layer in object.grease_pencil.layers:

                                        # populate
                                        populate(self, context, layer)

                                # object type
                                elif option.objectType in object.type:

                                    # layers
                                    for layer in object.grease_pencil.layers:

                                        # populate
                                        populate(self, context, layer)

                        # mode
                        else:

                            # object type
                            if option.objectType in 'ALL':

                                # layers
                                for layer in object.grease_pencil.layers:

                                    # populate
                                    populate(self, context, layer)

                            # object type
                            elif option.objectType in object.type:

                                # layers
                                for layer in object.grease_pencil.layers:

                                    # populate
                                    populate(self, context, layer)

                        # process
                        process(self, context, self.pencilLayers, option)

                        # clear storage
                        self.pencilLayers.clear()

            # objects
            if option.objects:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, object)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, object)

                    # mode
                    else:

                        # object type
                        if option.objectType in 'ALL':

                            # populate
                            populate(self, context, object)

                        # object type
                        elif option.objectType in object.type:

                            # populate
                            populate(self, context, object)

                # process
                process(self, context, self.objects, option)

                # clear storage
                self.objects.clear()

            # groups
            if option.groups:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:

                            # object type
                            if option.objectType in 'ALL':
                                for group in bpy.data.groups:
                                    if object in group.objects[:]:

                                        # populate
                                        populate(self, context, group)


                            # object type
                            elif option.objectType in object.type:
                                for group in bpy.data.groups:
                                    if object in group.objects[:]:

                                        # populate
                                        populate(self, context, group)

                    # mode
                    else:

                        # object type
                        if option.objectType in 'ALL':
                            for group in bpy.data.groups:
                                if object in group.objects[:]:

                                    # populate
                                    populate(self, context, group)

                        # object type
                        elif option.objectType in object.type:
                            for group in bpy.data.groups:
                                if object in group.objects[:]:

                                    # populate
                                    populate(self, context, group)

                # clear duplicates
                objectGroups = []
                [objectGroups.append(item) for item in self.groups if item not in objectGroups]

                # clear storage
                self.groups.clear()

                # process
                process(self, context, objectGroups, option)

            # constraints
            if option.constraints:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:
                            for constraint in object.constraints:

                                # constraint type
                                if option.constraintType in 'ALL':

                                    # populate
                                    populate(self, context, constraint)

                                # constraint type
                                elif option.constraintType in constraint.type:

                                    # populate
                                    populate(self, context, constraint)

                    # mode
                    else:
                        for constraint in object.constraints:

                            # constraint type
                            if option.constraintType in 'ALL':

                                # populate
                                populate(self, context, constraint)

                            # constraint type
                            elif option.constraintType in constraint.type:

                                # populate
                                populate(self, context, constraint)

                    # process
                    process(self, context, self.constraints, option)

                    # clear storage
                    self.constraints.clear()

            # modifiers
            if option.modifiers:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:
                            for modifier in object.modifiers:

                                # modifier type
                                if option.modifierType in 'ALL':

                                    # populate
                                    populate(self, context, modifier)

                                # modifier tye
                                elif option.modifierType in modifier.type:

                                    # populate
                                    populate(self, context, modifier)

                    # mode
                    else:
                        for modifier in object.modifiers:

                            # modifier type
                            if option.modifierType in 'ALL':

                                # populate
                                populate(self, context, modifier)

                            # modifier tye
                            elif option.modifierType in modifier.type:

                                # populate
                                populate(self, context, modifier)

                    # process
                    process(self, context, self.modifiers, option)

                    # clear storage
                    self.modifiers.clear()

            # object data
            if option.objectData:
                for object in bpy.data.objects:
                    if object.type not in 'EMPTY':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, object.data, object)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, object.data, object)

                        # mode
                        else:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, object.data, object)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, object.data, object)

                # object data
                objectData = [
                    self.curves,
                    self.cameras,
                    self.meshes,
                    self.lamps,
                    self.lattices,
                    self.metaballs,
                    self.speakers,
                    self.armatures
                ]

                # process collection
                for collection in objectData:
                    if collection != []:

                        # process
                        process(self, context, collection, option)

                        # clear storage
                        collection.clear()

            # bone groups
            if option.boneGroups:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:
                            if object.type in 'ARMATURE':
                                for group in object.pose.bone_groups:
                                    if object.select:

                                        # populate
                                        populate(self, context, group)

                    # mode
                    else:
                        if object.type in 'ARMATURE':
                            for group in object.pose.bone_groups:

                                # populate
                                populate(self, context, group)

                    # process
                    process(self, context, self.boneGroups, option)

                    # clear storage
                    self.boneGroups.clear()

            # bones
            if option.bones:
                for object in bpy.data.objects:
                    if object.type in 'ARMATURE':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:

                                # edit mode
                                if object.mode in 'EDIT':
                                    for bone in bpy.data.armatures[object.data.name].edit_bones:
                                        if bone.select:

                                            # populate
                                            populate(self, context, bone)

                                # pose or object mode
                                else:
                                    for bone in bpy.data.armatures[object.data.name].bones:
                                        if bone.select:

                                            # populate
                                            populate(self, context, bone)

                        # mode
                        else:

                            # edit mode
                            if object.mode in 'EDIT':
                                for bone in bpy.data.armatures[object.data.name].edit_bones:

                                        # populate
                                        populate(self, context, bone)

                            # pose or object mode
                            else:
                                for bone in bpy.data.armatures[object.data.name].bones:

                                        # populate
                                        populate(self, context, bone)

                        # process
                        process(self, context, self.bones, option)

                        # clear storage
                        self.bones.clear()

            # bone constraints
            if option.boneConstraints:
                for object in bpy.data.objects:
                    if object.type in 'ARMATURE':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:
                                for bone in object.pose.bones:
                                    if bone.bone.select:
                                        for constraint in bone.constraints:

                                            # constraint type
                                            if option.constraintType in 'ALL':

                                                # populate
                                                populate(self, context, constraint)

                                            # constraint type
                                            elif option.constraintType in constraint.type:

                                                # populate
                                                populate(self, context, constraint)

                                        # process
                                        process(self, context, self.constraints, option)

                                        # clear storage
                                        self.constraints.clear()

                        # mode
                        else:
                            for bone in object.pose.bones:
                                for constraint in bone.constraints:

                                    # constraint type
                                    if option.constraintType in 'ALL':

                                        # populate
                                        populate(self, context, constraint)

                                    # constraint type
                                    elif option.constraintType in constraint.type:

                                        # populate
                                        populate(self, context, constraint)

                                # process
                                process(self, context, self.constraints, option)

                                # clear storage
                                self.constraints.clear()

            # vertex groups
            if option.vertexGroups:
                for object in bpy.data.objects:
                    if hasattr(object, 'vertex_groups'):

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:
                                for group in object.vertex_groups:

                                    # object type
                                    if option.objectType in 'ALL':

                                        # populate
                                        populate(self, context, group)

                                    # object type
                                    elif option.objectType in object.type:

                                        # populate
                                        populate(self, context, group)

                                # process
                                process(self, context, self.vertexGroups, option)

                                # clear storage
                                self.vertexGroups.clear()

                        # mode
                        else:
                            for group in object.vertex_groups:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, group)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, group)

                            # process
                            process(self, context, self.vertexGroups, option)

                            # clear storage
                            self.vertexGroups.clear()

            # shapekeys
            if option.shapekeys:
                for object in bpy.data.objects:
                    if hasattr(object.data, 'shape_keys'):
                        if hasattr(object.data.shape_keys, 'key_blocks'):

                            # mode
                            if option.mode in 'SELECTED':
                                if object.select:
                                    for block in object.data.shape_keys.key_blocks:

                                        # object type
                                        if option.objectType in 'ALL':

                                            # populate
                                            populate(self, context, block)

                                        # object type
                                        elif option.objectType in object.type:

                                            # populate
                                            populate(self, context, block)

                            # mode
                            else:
                                for block in object.data.shape_keys.key_blocks:

                                    # object type
                                    if option.objectType in 'ALL':

                                        # populate
                                        populate(self, context, block)

                                    # object type
                                    elif option.objectType in object.type:

                                        # populate
                                        populate(self, context, block)

                            # process
                            process(self, context, self.shapekeys, option)

                            # clear storage
                            self.shapekeys.clear()

            # uvs
            if option.uvs:
                for object in bpy.data.objects:
                    if object.type in 'MESH':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:
                                for uv in object.data.uv_textures:

                                    # populate
                                    populate(self, context, uv)

                        # mode
                        else:
                         for uv in object.data.uv_textures:

                                # populate
                                populate(self, context, uv)

                        # process
                        process(self, context, self.uvs, option)

                        # clear storage
                        self.uvs.clear()

            # vertex colors
            if option.vertexColors:
                for object in bpy.data.objects:
                    if object.type in 'MESH':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:
                                for color in object.data.vertex_colors:

                                    # populate
                                    populate(self, context, color)

                        # mode
                        else:
                            for color in object.data.vertex_colors:

                                # populate
                                populate(self, context, color)

                        # process
                        process(self, context, self.vertexColors, option)

                        # clear storage
                        self.vertexColors.clear()

            # materials
            if option.materials:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:
                            for slot in object.material_slots:
                                if slot.material != None:

                                    # object type
                                    if option.objectType in 'ALL':

                                        # populate
                                        populate(self, context, slot.material, slot)

                                    # object type
                                    elif option.objectType in object.type:

                                        # populate
                                        populate(self, context, slot.material, slot)

                    # mode
                    else:
                        for slot in object.material_slots:
                            if slot.material != None:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, slot.material, slot)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, slot.material, slot)

                # process
                process(self, context, self.materials, option)

                # clear storage
                self.materials.clear()

            # textures
            if option.textures:
                for object in bpy.data.objects:
                    if context.scene.render.engine not in 'CYCLES':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:
                                for slot in object.material_slots:
                                    if slot.material != None:
                                        for texslot in slot.material.texture_slots:
                                            if texslot != None:

                                                # object type
                                                if option.objectType in 'ALL':

                                                    # populate
                                                    populate(self, context, texslot.texture, texslot)

                                                # object type
                                                elif option.objectType in object.type:

                                                    # populate
                                                    populate(self, context, texslot.texture, texslot)

                        # mode
                        else:
                            for slot in object.material_slots:
                                if slot.material != None:
                                    for texslot in slot.material.texture_slots:
                                        if texslot != None:

                                            # object type
                                            if option.objectType in 'ALL':

                                                # populate
                                                populate(self, context, texslot.texture, texslot)

                                            # object type
                                            elif option.objectType in object.type:

                                                # populate
                                                populate(self, context, texslot.texture, texslot)

                # process
                process(self, context, self.textures, option)

                # clear storage
                self.textures.clear()

            # particle systems
            if option.particleSystems:
                for object in bpy.data.objects:
                    if object.type in 'MESH':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:
                                for system in object.particle_systems:

                                    # object type
                                    if option.objectType in 'ALL':

                                        # populate
                                        populate(self, context, system)

                                    # object type
                                    elif option.objectType in object.type:

                                        # populate
                                        populate(self, context, system)

                        # mode
                        else:
                            for system in object.particle_systems:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, system)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, system)

                        # process
                        process(self, context, self.particleSystems, option)

                        # clear storage
                        self.particleSystems.clear()

            # particle settings
            if option.particleSettings:
                for object in bpy.data.objects:
                    if object.type in 'MESH':

                        # mode
                        if option.mode in 'SELECTED':
                            if object.select:
                                for system in object.particle_systems:

                                    # object type
                                    if option.objectType in 'ALL':

                                        # populate
                                        populate(self, context, system.settings, system)

                                    # object type
                                    elif option.objectType in object.type:

                                        # populate
                                        populate(self, context, system.settings, system)

                        # mode
                        else:
                            for system in object.particle_systems:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, system.settings, system)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, system.settings, system)

                # process
                process(self, context, self.particleSettings, option)

                # clear storage
                self.particleSettings.clear()

            # sensors
            if option.sensors:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                for sensor in object.game.sensors:
                                    populate(self, context, sensor)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                for sensor in object.game.sensors:
                                    populate(self, context, sensor)

                    # mode
                    else:

                        # object type
                        if option.objectType in 'ALL':

                            # populate
                            for sensor in object.game.sensors:
                                populate(self, context, sensor)

                        # object type
                        elif option.objectType in object.type:

                            # populate
                            for sensor in object.game.sensors:
                                populate(self, context, sensor)

                    # process
                    process(self, context, self.sensors, option)

                    # clear storage
                    self.sensors.clear()

            # controllers
            if option.controllers:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                for controller in object.game.controllers:
                                    populate(self, context, controller)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                for controller in object.game.controllers:
                                    populate(self, context, controller)

                    # mode
                    else:

                        # object type
                        if option.objectType in 'ALL':

                            # populate
                            for controller in object.game.controllers:
                                populate(self, context, controller)

                        # object type
                        elif option.objectType in object.type:

                            # populate
                            for controller in object.game.controllers:
                                populate(self, context, controller)

                    # process
                    process(self, context, self.controllers, option)

                    # clear storage
                    self.controllers.clear()

            # actuators
            if option.actuators:
                for object in bpy.data.objects:

                    # mode
                    if option.mode in 'SELECTED':
                        if object.select:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                for actuator in object.game.actuators:
                                    populate(self, context, actuator)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                for actuator in object.game.actuators:
                                    populate(self, context, actuator)

                    # mode
                    else:

                        # object type
                        if option.objectType in 'ALL':

                            # populate
                            for actuator in object.game.actuators:
                                populate(self, context, actuator)

                        # object type
                        elif option.objectType in object.type:

                            # populate
                            for actuator in object.game.actuators:
                                populate(self, context, actuator)

                    # process
                    process(self, context, self.actuators, option)

                    # clear storage
                self.actuators.clear()

        # mode
        if option.mode in 'SCENE':

            # actions
            if option.actions:
                for object in context.scene.objects:
                    if hasattr(object.animation_data, 'action'):
                        if hasattr(object.animation_data.action, 'name'):

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, object.animation_data.action, object.animation_data)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, object.animation_data.action, object.animation_data)

                # clear duplicates
                actions = []
                [actions.append(item) for item in self.actions if item not in actions]

                # clear storage
                self.actions.clear()

                # process
                process(self, context, actions, option)

            # action groups
            if option.actionGroups:
                for object in context.scene.objects:
                    if hasattr(object.animation_data, 'action'):
                        if hasattr(object.animation_data.action, 'name'):

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, object.animation_data.action)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, object.animation_data.action)

                # clear duplicates
                actions = []
                [actions.append(item) for item in self.actions if item not in actions]
                self.actions.clear()

                # name action groups
                for action in actions:
                    for group in action[1][1].groups:

                        # new name
                        newName = rename(self, context, group.name, option) if not option.suffixLast else rename(self, context, group.name, option) + option.suffix

                        # update
                        if group.name != newName:

                            # name
                            group.name = newName

                            # count
                            self.count += 1

            # grease pencil
            if option.greasePencil:
                for object in context.scene.objects:
                    if hasattr(object.grease_pencil, 'name'):

                        # object type
                        if option.objectType in 'ALL':

                            # populate
                            populate(self, context, object.grease_pencil, object)

                        # object type
                        elif option.objectType in object.type:

                            # populate
                            populate(self, context, object.grease_pencil, object)

                # process
                process(self, context, self.greasePencils, option)

                # clear storage
                self.greasePencils.clear()

            # pencil layers
            if option.pencilLayers:
                for object in context.scene.objects:
                    if hasattr(object.grease_pencil, 'name'):

                        # object type
                        if option.objectType in 'ALL':

                            # layers
                            for layer in object.grease_pencil.layers:

                                # populate
                                populate(self, context, layer)

                        # object type
                        elif option.objectType in object.type:

                            # layers
                            for layer in object.grease_pencil.layers:

                                # populate
                                populate(self, context, layer)

                        # process
                        process(self, context, self.pencilLayers, option)

                        # clear storage
                        self.pencilLayers.clear()

            # objects
            if option.objects:
                for object in context.scene.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        populate(self, context, object)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        populate(self, context, object)

                # process
                process(self, context, self.objects, option)

                # clear storage
                self.objects.clear()

            # groups
            if option.groups:
                for object in context.scene.objects:

                    # object type
                    if option.objectType in 'ALL':
                        for group in bpy.data.groups:
                            if object in group.objects[:]:

                                # populate
                                populate(self, context, group)

                    # object type
                    elif option.objectType in object.type:
                        for group in bpy.data.groups:
                            if object in group.objects[:]:

                                # populate
                                populate(self, context, group)

                # clear duplicates
                objectGroups = []
                [objectGroups.append(item) for item in self.groups if item not in objectGroups]

                # clear storage
                self.groups.clear()

                # process
                process(self, context, objectGroups, option)

            # constraints
            if option.constraints:
                for object in context.scene.objects:
                    for constraint in object.constraints:

                        # constraint type
                        if option.constraintType in 'ALL':

                            # populate
                            populate(self, context, constraint)

                        # constraint type
                        elif option.constraintType in constraint.type:

                            # populate
                            populate(self, context, constraint)

                    # process
                    process(self, context, self.constraints, option)

                    # clear storage
                    self.constraints.clear()

            # modifiers
            if option.modifiers:
                for object in context.scene.objects:
                    for modifier in object.modifiers:

                        # modifier type
                        if option.modifierType in 'ALL':

                            # populate
                            populate(self, context, modifier)

                        # modifier tye
                        elif option.modifierType in modifier.type:

                            # populate
                            populate(self, context, modifier)

                    # process
                    process(self, context, self.modifiers, option)

                    # clear storage
                    self.modifiers.clear()

            # object data
            if option.objectData:
                for object in context.scene.objects:
                    if object.type not in 'EMPTY':

                        # object type
                        if option.objectType in 'ALL':

                            # populate
                            populate(self, context, object.data, object)

                        # object type
                        elif option.objectType in object.type:

                            # populate
                            populate(self, context, object.data, object)

                # object data
                objectData = [
                    self.curves,
                    self.cameras,
                    self.meshes,
                    self.lamps,
                    self.lattices,
                    self.metaballs,
                    self.speakers,
                    self.armatures
                ]
                for collection in objectData:
                    if collection != []:

                        # process
                        process(self, context, collection, option)

                        # clear storage
                        collection.clear()

            # bone groups
            if option.boneGroups:
                for object in context.scene.objects:
                    if object.type in 'ARMATURE':
                        for group in object.pose.bone_groups:

                            # populate
                            populate(self, context, group)

                    # process
                    process(self, context, self.boneGroups, option)

                    # clear storage
                    self.boneGroups.clear()

            # bones
            if option.bones:
                for object in context.scene.objects:
                    if object.type in 'ARMATURE':

                        # edit mode
                        if object.mode in 'EDIT':
                            for bone in bpy.data.armatures[object.data.name].edit_bones:

                                    # populate
                                    populate(self, context, bone)

                        # pose or object mode
                        else:
                            for bone in bpy.data.armatures[object.data.name].bones:

                                    # populate
                                    populate(self, context, bone)

                        # process
                        process(self, context, self.bones, option)

                        # clear storage
                        self.bones.clear()

            # bone constraints
            if option.boneConstraints:
                for object in context.scene.objects:
                    if object.type in 'ARMATURE':
                        for bone in object.pose.bones:
                            for constraint in bone.constraints:

                                # constraint type
                                if option.constraintType in 'ALL':

                                    # populate
                                    populate(self, context, constraint)

                                # constraint type
                                elif option.constraintType in constraint.type:

                                    # populate
                                    populate(self, context, constraint)

                            # process
                            process(self, context, self.constraints, option)

                            # clear storage
                            self.constraints.clear()

            # vertex groups
            if option.vertexGroups:
                for object in context.scene.objects:
                    if hasattr(object, 'vertex_groups'):
                        for group in object.vertex_groups:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, group)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, group)

                        # process
                        process(self, context, self.vertexGroups, option)

                        # clear storage
                        self.vertexGroups.clear()

            # shapekeys
            if option.shapekeys:
                for object in context.scene.objects:
                    if hasattr(object.data, 'shape_keys'):
                        if hasattr(object.data.shape_keys, 'key_blocks'):
                            for block in object.data.shape_keys.key_blocks:

                                # object type
                                if option.objectType in 'ALL':

                                    # populate
                                    populate(self, context, block)

                                # object type
                                elif option.objectType in object.type:

                                    # populate
                                    populate(self, context, block)

                            # process
                            process(self, context, self.shapekeys, option)

                            # clear storage
                            self.shapekeys.clear()

            # uvs
            if option.uvs:
                for object in context.scene.objects:
                    if object.type in 'MESH':
                        for uv in object.data.uv_textures:

                            # populate
                            populate(self, context, uv)

                        # process
                        process(self, context, self.uvs, option)

                        # clear storage
                        self.uvs.clear()

            # vertex colors
            if option.vertexColors:
                for object in context.scene.objects:
                    if object.type in 'MESH':
                        for color in object.data.vertex_colors:

                            # populate
                            populate(self, context, color)

                        # process
                        process(self, context, self.vertexColors, option)

                        # clear storage
                        self.vertexColors.clear()

            # materials
            if option.materials:
                for object in context.scene.objects:
                    for slot in object.material_slots:
                        if slot.material != None:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, slot.material, slot)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, slot.material, slot)

                # process
                process(self, context, self.materials, option)

                # clear storage
                self.materials.clear()

            # textures
            if option.textures:
                for object in context.scene.objects:
                    if context.scene.render.engine not in 'CYCLES':
                        for slot in object.material_slots:
                            if slot.material != None:
                                for texslot in slot.material.texture_slots:
                                    if texslot != None:

                                        # object type
                                        if option.objectType in 'ALL':

                                            # populate
                                            populate(self, context, texslot.texture, texslot)

                                        # object type
                                        elif option.objectType in object.type:

                                            # populate
                                            populate(self, context, texslot.texture, texslot)

                # process
                process(self, context, self.textures, option)

                # clear storage
                self.textures.clear()

            # particle systems
            if option.particleSystems:
                for object in context.scene.objects:
                    if object.type in 'MESH':
                        for system in object.particle_systems:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, system)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, system)

                        # process
                        process(self, context, self.particleSystems, option)

                        # clear storage
                        self.particleSystems.clear()

            # particle settings
            if option.particleSettings:
                for object in context.scene.objects:
                    if object.type in 'MESH':
                        for system in object.particle_systems:

                            # object type
                            if option.objectType in 'ALL':

                                # populate
                                populate(self, context, system.settings, system)

                            # object type
                            elif option.objectType in object.type:

                                # populate
                                populate(self, context, system.settings, system)

                # process
                process(self, context, self.particleSettings, option)

                # clear storage
                self.particleSettings.clear()

            # sensors
            if option.sensors:
                for object in context.scene.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        for sensor in object.game.sensors:
                            populate(self, context, sensor)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        for sensor in object.game.sensors:
                            populate(self, context, sensor)

                    # process
                    process(self, context, self.sensors, option)

                    # clear storage
                    self.sensors.clear()

            # controllers
            if option.controllers:
                for object in context.scene.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        for controller in object.game.controllers:
                            populate(self, context, controller)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        for controller in object.game.controllers:
                            populate(self, context, controller)

                    # process
                    process(self, context, self.controllers, option)

                    # clear storage
                    self.controllers.clear()

            # actuators
            if option.actuators:
                for object in context.scene.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        for actuator in object.game.actuators:
                            populate(self, context, actuator)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        for actuator in object.game.actuators:
                            populate(self, context, actuator)

                    # process
                    process(self, context, self.actuators, option)

                    # clear storage
                    self.actuators.clear()

        # mode
        elif option.mode in 'GLOBAL':

            # actions
            if option.actions:
                for action in bpy.data.actions:

                    # populate
                    populate(self, context, action)

                # process
                process(self, context, self.actions, option)

                # clear storage
                self.actions.clear()

            # action groups
            if option.actionGroups:
                for action in bpy.data.actions:

                    # populate
                    populate(self, context, action)

                # process
                for action in self.actions:
                    for group in action[1][1].groups:

                        # new name
                        newName = rename(self, context, group.name, option) if not option.suffixLast else rename(self, context, group.name, option) + option.suffix

                        # update
                        if group.name != newName:

                            # name
                            group.name = newName

                            # count
                            self.count += 1

                    # bones
                    if option.bones:

                        # fix paths
                        for curve in action[1][1].fcurves:
                            if 'pose' in curve.data_path:
                                if not re.search(re.escape(']['), curve.data_path) and not re.search('constraints', curve.data_path):
                                    try: curve.data_path = 'pose.bones["' + curve.group.name + '"].' + (curve.data_path.rsplit('.', 1)[1]).rsplit('[', 1)[0]
                                    except: pass

                # clear storage
                self.actions.clear()

            # grease pencil
            if option.greasePencil:
                for pencil in bpy.data.grease_pencil:

                    # populate
                    populate(self, context, pencil)

                # process
                process(self, context, self.greasePencils, option)

                # clear storage
                self.greasePencils.clear()

            # pencil layers
            if option.pencilLayers:
                for pencil in bpy.data.grease_pencil:

                    # layers
                    for layer in pencil.layers:

                        # populate
                        populate(self, context, layer)

                    # process
                    process(self, context, self.pencilLayers, option)

                    # clear storage
                    self.pencilLayers.clear()

            # objects
            if option.objects:
                for object in bpy.data.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        populate(self, context, object)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        populate(self, context, object)

                # process
                process(self, context, self.objects, option)

                # clear storage
                self.objects.clear()

            # groups
            if option.groups:
                for group in bpy.data.groups:

                    # populate
                    populate(self, context, group)

                # process
                process(self, context, self.groups, option)

                # clear storage
                self.groups.clear()

            # constraints
            if option.constraints:
                for object in bpy.data.objects:
                    for constraint in object.constraints:

                        # object type
                        if option.objectType in 'ALL':

                            # constraint type
                            if option.constraintType in 'ALL':

                                # populate
                                populate(self, context, constraint)

                            # constraint type
                            elif option.constraintType in constraint.type:

                                # populate
                                populate(self, context, constraint)

                        # object type
                        elif option.objectType in object.type:

                            # constraint type
                            if option.constraintType in 'ALL':

                                # populate
                                populate(self, context, constraint)

                                # constraint type
                            elif option.constraintType in constraint.type:

                                # populate
                                populate(self, context, constraint)

                    # process
                    process(self, context, self.constraints, option)

                    # clear storage
                    self.constraints.clear()

            # modifiers
            if option.modifiers:
                for object in bpy.data.objects:
                    for modifier in object.modifiers:

                        # object type
                        if option.objectType in 'ALL':

                            # modifier type
                            if option.modifierType in 'ALL':

                                # populate
                                populate(self, context, modifier)

                            # modifier type
                            elif option.modifierType in modifier.type:

                                # populate
                                populate(self, context, modifier)

                        # object type
                        elif option.objectType in object.type:

                            # modifier type
                            if option.modifierType in 'ALL':

                                # populate
                                populate(self, context, modifier)

                            # modifier type
                            elif option.modifierType in modifier.type:

                                # populate
                                populate(self, context, modifier)

                    # process
                    process(self, context, self.modifiers, option)

                    # clear storage
                    self.modifiers.clear()

            # object data
            if option.objectData:

                # cameras
                for camera in bpy.data.cameras:

                    # populate
                    populate(self, context, camera)

                # process
                process(self, context, self.cameras, option)

                # clear storage
                self.cameras.clear()

                # meshes
                for mesh in bpy.data.meshes:

                    # populate
                    populate(self, context, mesh)

                # process
                process(self, context, self.meshes, option)

                # clear storage
                self.meshes.clear()

                # curves
                for curve in bpy.data.curves:

                    # populate
                    populate(self, context, curve)

                # process
                process(self, context, self.curves, option)

                # clear storage
                self.curves.clear()

                # lamps
                for lamp in bpy.data.lamps:

                    # populate
                    populate(self, context, lamp)

                # process
                process(self, context, self.lamps, option)

                # clear storage
                self.lamps.clear()

                # lattices
                for lattice in bpy.data.lattices:

                    # populate
                    populate(self, context, lattice)

                # process
                process(self, context, self.lattices, option)

                # clear storage
                self.lattices.clear()

                # metaballs
                for metaball in bpy.data.metaballs:

                    # populate
                    populate(self, context, metaball)

                # process
                process(self, context, self.metaballs, option)

                # clear storage
                self.metaballs.clear()

                # speakers
                for speaker in bpy.data.speakers:

                    # populate
                    populate(self, context, speaker)

                # process
                process(self, context, self.speakers, option)

                # clear storage
                self.speakers.clear()

                # armatures
                for armature in bpy.data.armatures:

                    # populate
                    populate(self, context, armature)

                # process
                process(self, context, self.armatures, option)

                # clear storage
                self.armatures.clear()

            # bone groups
            if option.boneGroups:
                for object in bpy.data.objects:
                    if object.type in 'ARMATURE':
                        for group in object.pose.bone_groups:

                            # populate
                            populate(self, context, group)

                        # process
                        process(self, context, self.boneGroups, option)

                        # clear storage
                        self.boneGroups.clear()

            # bones
            if option.bones:
                for armature in bpy.data.armatures:
                    for bone in armature.bones:

                        # populate
                        populate(self, context, bone)

                    # process
                    process(self, context, self.bones, option)

                    # clear storage
                    self.bones.clear()

            # bone constraints
            if option.boneConstraints:
                for object in bpy.data.objects:
                    if object.type in 'ARMATURE':
                        for bone in object.pose.bones:
                            for constraint in bone.constraints:

                                # populate
                                populate(self, context, constraint)

                            # process
                            process(self, context, self.constraints, option)

                            # clear storage
                            self.constraints.clear()

            # vertex groups
            if option.vertexGroups:
                for object in bpy.data.objects:
                    if object.type in {'MESH', 'LATTICE'}:
                        for group in object.vertex_groups:

                            # populate
                            populate(self, context, group)

                        # process
                        process(self, context, self.vertexGroups, option)

                        # clear storage
                        self.vertexGroups.clear()

            # shape keys
            if option.shapekeys:
                for shapekey in bpy.data.shape_keys:

                        # populate
                        populate(self, context, shapekey)
                        for block in shapekey.key_blocks:

                            # populate
                            populate(self, context, block)

                        # process
                        process(self, context, self.shapekeys, option)

                        # clear storage
                        self.shapekeys.clear()

            # uvs
            if option.uvs:
                for object in bpy.data.objects:
                    if object.type in 'MESH':
                        for uv in object.data.uv_textures:

                            # populate
                            populate(self, context, uv)

                        # process
                        process(self, context, self.uvs, option)

                        # clear storage
                        self.uvs.clear()

            # vertex colors
            if option.vertexColors:
                for object in bpy.data.objects:
                    if object.type in 'MESH':
                        for color in object.data.vertex_colors:

                            # populate
                            populate(self, context, color)

                        # process
                        process(self, context, self.vertexColors, option)

                        # clear storage
                        self.vertexColors.clear()

            # materials
            if option.materials:
                for material in bpy.data.materials:

                    # populate
                    populate(self, context, material)

                # process
                process(self, context, self.materials, option)

                # clear storage
                self.materials.clear()

            # textures
            if option.textures:
                for texture in bpy.data.textures:

                    # populate
                    populate(self, context, texture)

                # process
                process(self, context, self.textures, option)

                # clear storage
                self.textures.clear()

            # particles systems
            if option.particleSystems:
                for object in bpy.data.objects:
                    if object.type in 'MESH':
                        for system in object.particle_systems:

                            # populate
                            populate(self, context, system)

                        # process
                        process(self, context, self.particleSystems, option)

                        # clear storage
                        self.particleSystems.clear()

            # particles settings
            if option.particleSettings:
                for settings in bpy.data.particles:

                    # populate
                    populate(self, context, settings)

                # process
                process(self, context, self.particleSettings, option)

                # clear storage
                self.particleSettings.clear()

            # sensors
            if option.sensors:
                for object in bpy.data.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        for sensor in object.game.sensors:
                            populate(self, context, sensor)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        for sensor in object.game.sensors:
                            populate(self, context, sensor)

                    # process
                    process(self, context, self.sensors, option)

                    # clear storage
                    self.sensors.clear()

            # controllers
            if option.controllers:
                for object in bpy.data.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        for controller in object.game.controllers:
                            populate(self, context, controller)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        for controller in object.game.controllers:
                            populate(self, context, controller)

                    # process
                    process(self, context, self.controllers, option)

                    # clear storage
                    self.controllers.clear()

            # actuators
            if option.actuators:
                for object in bpy.data.objects:

                    # object type
                    if option.objectType in 'ALL':

                        # populate
                        for actuator in object.game.actuators:
                            populate(self, context, actuator)

                    # object type
                    elif option.objectType in object.type:

                        # populate
                        for actuator in object.game.actuators:
                            populate(self, context, actuator)

                    # process
                    process(self, context, self.actuators, option)

                    # clear storage
                    self.actuators.clear()

        # line sets
        if option.lineSets:
            for scene in bpy.data.scenes:
                for layer in scene.render.layers:
                    for lineset in layer.freestyle_settings.linesets:
                        if hasattr(lineset, 'name'):

                            # new name
                            newName = rename(self, context, lineset.name, option) if not option.suffixLast else rename(self, context, lineset.name, option) + option.suffix

                            # update
                            if lineset.name != newName:

                                # name
                                lineset.name = newName

                                # count
                                self.count += 1

        # linestyles
        if option.linestyles:
            for scene in bpy.data.scenes:
                for layer in scene.render.layers:
                    for lineset in layer.freestyle_settings.linesets:
                        if hasattr(lineset, 'name'):

                            # populate
                            populate(self, context, lineset.linestyle, lineset)

            # process
            process(self, context, self.linestyles, option)

            # clear storage
            self.linestyles.clear()

        # linestyle modifiers
        if option.linestyleModifiers:
            for style in bpy.data.linestyles:


                # color
                for modifier in style.color_modifiers:

                    # linestyle modifier type
                    if option.linestyleModifierType in 'ALL':

                        # populate
                        populate(self, context, modifier)

                    # linestyle modifier type
                    elif option.linestyleModifierType in modifier.type:

                        # populate
                        populate(self, context, modifier)

                # process
                process(self, context, self.modifiers, option)

                # clear storage
                self.modifiers.clear()


                # alpha
                for modifier in style.alpha_modifiers:

                    # linestyle modifier type
                    if option.linestyleModifierType in 'ALL':

                        # populate
                        populate(self, context, modifier)

                    # linestyle modifier type
                    elif option.linestyleModifierType in modifier.type:

                        # populate
                        populate(self, context, modifier)

                # process
                process(self, context, self.modifiers, option)

                # clear storage
                self.modifiers.clear()


                # thickness
                for modifier in style.thickness_modifiers:

                    # linestyle modifier type
                    if option.linestyleModifierType in 'ALL':

                        # populate
                        populate(self, context, modifier)

                    # linestyle modifier type
                    elif option.linestyleModifierType in modifier.type:

                        # populate
                        populate(self, context, modifier)

                # process
                process(self, context, self.modifiers, option)

                # clear storage
                self.modifiers.clear()


                # geometry
                for modifier in style.geometry_modifiers:

                    # linestyle modifier type
                    if option.linestyleModifierType in 'ALL':

                        # populate
                        populate(self, context, modifier)

                    # linestyle modifier type
                    elif option.linestyleModifierType in modifier.type:

                        # populate
                        populate(self, context, modifier)

                # process
                process(self, context, self.modifiers, option)

                # clear storage
                self.modifiers.clear()

        # scenes
        if option.scenes:
            for scene in bpy.data.scenes:

                # populate
                populate(self, context, scene)

            # process
            process(self, context, self.scenes, option)

            # clear storage
            self.scenes.clear()

        # render layers
        if option.renderLayers:
            for scene in bpy.data.scenes:
                for layer in scene.render.layers:

                    # populate
                    populate(self, context, layer)

                # process
                process(self, context, self.renderLayers, option)

                # clear storage
                self.renderLayers.clear()

        # worlds
        if option.worlds:
            for world in bpy.data.worlds:

                # populate
                populate(self, context, world)

            # process
            process(self, context, self.worlds, option)

            # clear storage
            self.worlds.clear()

        # libraries
        if option.libraries:
            for library in bpy.data.libraries:

                # populate
                populate(self, context, library)

            # process
            process(self, context, self.libraries, option)

            # clear storage
            self.libraries.clear()

        # images
        if option.images:
            for image in bpy.data.images:

                # populate
                populate(self, context, image)

            # process
            process(self, context, self.images, option)

            # clear storage
            self.images.clear()

        # masks
        if option.masks:
            for mask in bpy.data.masks:

                # populate
                populate(self, context, mask)

            # process
            process(self, context, self.masks, option)

            # clear storage
            self.masks.clear()

        # sequences
        if option.sequences:
            for scene in bpy.data.scenes:
                if hasattr(scene.sequence_editor, 'sequence_all'):
                    for sequence in scene.sequence_editor.sequences_all:

                        # populate
                        populate(self, context, sequence)

                    # process
                    process(self, context, self.sequences, option)

                    # clear storage
                    self.sequences.clear()

        # movie clips
        if option.movieClips:
            for clip in bpy.data.movieclips:

                # populate
                populate(self, context, clip)

            # process
            process(self, context, self.movieClips, option)

            # clear storage
            self.movieClips.clear()

        # sounds
        if option.sounds:
            for sound in bpy.data.sounds:

                # populate
                populate(self, context, sound)

            # process
            process(self, context, self.sounds, option)

            # clear storage
            self.sounds.clear()

        # screens
        if option.screens:
            for screen in bpy.data.screens:

                # populate
                populate(self, context, screen)

            # process
            process(self, context, self.screens, option)

            # clear storage
            self.screens.clear()

        # keying sets
        if option.keyingSets:
            for scene in bpy.data.scenes:
                for keyingSet in scene.keying_sets:

                    # populate
                    populate(self, context, keyingSet)

                # process
                process(self, context, self.keyingSets, option)

                # clear storage
                self.keyingSets.clear()

        # palettes
        if option.palettes:
            for palette in bpy.data.palettes:

                # populate
                populate(self, context, palette)

            # process
            process(self, context, self.palettes, option)

            # clear storage
            self.palettes.clear()

        # brushes
        if option.brushes:
            for brush in bpy.data.brushes:

                # populate
                populate(self, context, brush)

            # process
            process(self, context, self.brushes, option)

            # clear storage
            self.brushes.clear()

        # nodes
        if option.nodes:

            # shader
            for material in bpy.data.materials:
                if hasattr(material.node_tree, 'nodes'):
                    for node in material.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodes, option)

                    # clear storage
                    self.nodes.clear()

            # compositing
            for scene in bpy.data.scenes:
                if hasattr(scene.node_tree, 'nodes'):
                    for node in scene.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodes, option)

                    # clear storage
                    self.nodes.clear()

            # texture
            for texture in bpy.data.textures:
                if hasattr(texture.node_tree, 'nodes'):
                    for node in texture.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodes, option)

                    # clear storage
                    self.nodes.clear()

            # groups
            for group in bpy.data.node_groups:
                for node in group.nodes:

                    # populate
                    populate(self, context, node)

                # process
                process(self, context, self.nodes, option)

                # clear storage
                self.nodes.clear()

        # node labels
        if option.nodeLabels:

            # tag
            self.tag = True

            # shader
            for material in bpy.data.materials:
                if hasattr(material.node_tree, 'nodes'):
                    for node in material.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodeLabels, option)

                    # clear storage
                    self.nodeLabels.clear()

            # compositing
            for scene in bpy.data.scenes:
                if hasattr(scene.node_tree, 'nodes'):
                    for node in scene.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodeLabels, option)

                    # clear storage
                    self.nodeLabels.clear()

            # texture
            for texture in bpy.data.textures:
                if hasattr(texture.node_tree, 'nodes'):
                    for node in texture.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodeLabels, option)

                    # clear storage
                    self.nodeLabels.clear()

            # groups
            for group in bpy.data.node_groups:
                for node in group.nodes:

                    # populate
                    populate(self, context, node)

                # process
                process(self, context, self.nodeLabels, option)

                # clear storage
                self.nodeLabels.clear()

            # tag
            self.tag = False

        # node groups
        if option.nodeGroups:
            for group in bpy.data.node_groups:

                # populate
                populate(self, context, group)

            # process
            process(self, context, self.nodeGroups, option)

            # clear storage
            self.nodeGroups.clear()

        # texts
        if option.texts:
            for text in bpy.data.texts:

                # populate
                populate(self, context, text)

            # process
            process(self, context, self.texts, option)

            # clear storage
            self.texts.clear()

        # frame nodes
        if option.frameNodes:

            # shader
            for material in bpy.data.materials:
                if hasattr(material.node_tree, 'nodes'):
                    for node in material.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodes, option)

                    # clear storage
                    self.nodes.clear()

            # compositing
            for scene in bpy.data.scenes:
                if hasattr(scene.node_tree, 'nodes'):
                    for node in scene.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodes, option)

                    # clear storage
                    self.nodes.clear()

            # texture
            for texture in bpy.data.textures:
                if hasattr(texture.node_tree, 'nodes'):
                    for node in texture.node_tree.nodes:

                        # populate
                        populate(self, context, node)

                    # process
                    process(self, context, self.nodes, option)

                    # clear storage
                    self.nodes.clear()

            # groups
            for group in bpy.data.node_groups:
                for node in group.nodes:

                    # populate
                    populate(self, context, node)

                # process
                process(self, context, self.nodes, option)

                # clear storage
                self.nodes.clear()

# quick
def quick(self, context, object, panel, option):
    '''
        Quick batch mode for batch name.
    '''

    # is object
    if object:

        # search
        search = panel.search if panel.regex else re.escape(panel.search)

        # search
        if search == '' or re.search(search, object.name, re.I):

            # ignore Object
            if not option.ignoreObject or self.simple:

                # populate
                populate(self, context, object)

        # action
        if panel.action:

            # ignore action
            if not option.ignoreAction or self.simple:
                if hasattr(object.animation_data, 'action'):
                    if hasattr(object.animation_data.action, 'name'):

                        # search
                        if search == '' or re.search(search, object.animation_data.action.name, re.I):

                            # populate
                            populate(self, context, object.animation_data.action, object.animation_data)

        # grease pencils
        if panel.greasePencil:

            # ignore grease pencil
            if not option.ignoreGreasePencil or self.simple:
                if hasattr(object.grease_pencil, 'name'):

                    # search
                    if search == '' or re.search(search, object.grease_pencil.name, re.I):

                        # populate
                        populate(self, context, object.grease_pencil, object)

                    # layers
                    for layer in object.grease_pencil.layers:

                        # search
                        if search == '' or re.search(search, layer.info, re.I):

                            # populate
                            populate(self, context, layer)

                    # process
                    process(self, context, self.pencilLayers, option)

                    # clear storage
                    self.pencilLayers.clear()

        # groups
        if panel.groups:

            # ignore group
            if not option.ignoreGroup or self.simple:
                for group in bpy.data.groups:
                    for groupObject in group.objects[:]:
                        if groupObject == object:

                            # search
                            if search == '' or re.search(search, group.name, re.I):

                                # populate
                                populate(self, context, group)

        # constraints
        if panel.constraints:

            # ignore constraint
            if not option.ignoreConstraint or self.simple:
                for constraint in object.constraints:

                    # search
                    if search == '' or re.search(search, constraint.name, re.I):

                        # populate
                        populate(self, context, constraint)

                # process
                process(self, context, self.constraints, option)

                # clear storage
                self.constraints.clear()

        # modifiers
        if panel.modifiers:

            # ignore modifier
            if not option.ignoreModifier or self.simple:
                for modifier in object.modifiers:

                    # search
                    if search == '' or re.search(search, modifier.name, re.I):

                        # populate
                        populate(self, context, modifier)

                # process
                process(self, context, self.modifiers, option)

                # clear storage
                self.modifiers.clear()

        # bone groups
        if panel.boneGroups:

            # ignore bone group
            if not option.ignoreBoneGroup or self.simple:
                if object.type in 'ARMATURE':
                    for group in object.pose.bone_groups:

                        # search
                        if search == '' or re.search(search, group.name, re.I):

                            # populate
                            populate(self, context, group)

                    # process
                    process(self, context, self.boneGroups, option)

                    # clear storage
                    self.boneGroups.clear()

        # bones
        if object == context.active_object:

            # ignore bone
            if not option.ignoreBone or self.simple:
                if object.type == 'ARMATURE':
                    if object.mode in {'POSE', 'EDIT'}:

                        # display bones
                        if panel.displayBones:

                            # bone mode
                            if panel.boneMode == 'SELECTED':

                                # pose
                                if object.mode == 'POSE':

                                    # bones
                                    bones = context.selected_pose_bones

                                # edit
                                elif object.mode == 'EDIT':

                                    # bones
                                    bones = context.selected_bones

                                # bone
                                for bone in bones:

                                    # search
                                    if search == '' or re.search(search, bone.name, re.I):

                                        # populate
                                        populate(self, context, bone)

                            # bone mode
                            else:

                                # pose
                                if object.mode == 'POSE':

                                    # bones
                                    bones = [bone for bone in object.data.bones if True in [x&y for (x, y) in zip(bone.layers, object.data.layers)]]

                                    # edit
                                elif object.mode == 'EDIT':

                                    # bones
                                    bones = [bone for bone in object.data.edit_bones if True in [x&y for (x, y) in zip(bone.layers, object.data.layers)]]

                                # bone
                                for bone in bones:

                                    # search
                                    if search == '' or re.search(search, bone.name, re.I):

                                        # populate
                                        populate(self, context, bone)

                        # display bones
                        else:

                            # mode
                            if object.mode == 'EDIT':

                                # is active bone
                                if context.active_bone:

                                    # search
                                    if search == '' or re.search(search, context.active_bone.name, re.I):

                                        # new name
                                        newName = rename(self, context, context.active_bone.name, option) if not option.suffixLast else rename(self, context, context.active_bone.name, option) + option.suffix

                                        # update
                                        if context.active_bone.name != newName:

                                            # name
                                            context.active_bone.name = newName

                                            # count
                                            self.count += 1

                            # mode
                            elif object.mode == 'POSE':

                                # is active pose bone
                                if context.active_pose_bone:

                                    # search
                                    if search == '' or re.search(search, context.active_pose_bone.name, re.I):

                                        # new name
                                        newName = rename(self, context, context.active_pose_bone.name, option) if not option.suffixLast else rename(self, context, context.active_pose_bone.name, option) + option.suffix

                                        # update
                                        if context.active_pose_bone.name != newName:

                                            # name
                                            context.active_pose_bone.name = newName

                                            # count
                                            self.count += 1

            # bone constraints
            if panel.boneConstraints:

                # ignore bone constraint
                if not option.ignoreBoneConstraint or self.simple:
                    if object.mode == 'POSE':

                        # display bones
                        if panel.displayBones:

                            # bone mode
                            if panel.boneMode == 'SELECTED':
                                for bone in context.selected_pose_bones:
                                    for constraint in bone.constraints:

                                        # search
                                        if search == '' or re.search(search, constraint.name, re.I):

                                            # append
                                            self.constraints.append([constraint.name, constraint.name, constraint.name, [constraint, '']])

                                    # process
                                    process(self, context, self.constraints, option)

                                    # clear storage
                                    self.constraints.clear()

                            # bone mode
                            else:
                                for bone in object.pose.bones:
                                    if True in [x&y for (x, y) in zip(bone.bone.layers, object.data.layers)]:
                                        for constraint in bone.constraints:

                                            # search
                                            if search == '' or re.search(search, constraint.name, re.I):

                                                # append
                                                self.constraints.append([constraint.name, constraint.name, constraint.name, [constraint, '']])

                                        # process
                                        process(self, context, self.constraints, option)

                                        # clear storage
                                        self.constraints.clear()

                        # display bones
                        else:
                            for constraint in context.active_pose_bone.constraints:

                                # search
                                if search == '' or re.search(search, constraint.name, re.I):

                                    # append
                                    self.constraints.append([constraint.name, constraint.name, constraint.name, [constraint, '']])

                            # process
                            process(self, context, self.constraints, option)

                            # clear storage
                            self.constraints.clear()

        # object data
        if object.type != 'EMPTY':

            # ignore object data
            if not option.ignoreObjectData or self.simple:

                # search
                if search == '' or re.search(search, object.data.name, re.I):

                    # populate
                    populate(self, context, object.data, object)

        # vertex groups
        if panel.vertexGroups:

            # ignore vertex group
            if not option.ignoreVertexGroup or self.simple:
                if hasattr(object, 'vertex_groups'):
                    for group in object.vertex_groups:

                        # search
                        if search == '' or re.search(search, group.name, re.I):

                            # populate
                            populate(self, context, group)

                    # process
                    process(self, context, self.vertexGroups, option)

                    # clear storage
                    self.vertexGroups.clear()

        # shapekeys
        if panel.shapekeys:

            # ignore shapekey
            if not option.ignoreShapekey or self.simple:
                if hasattr(object.data, 'shape_keys'):
                    if hasattr(object.data.shape_keys, 'key_blocks'):
                        for key in object.data.shape_keys.key_blocks:

                            # search
                            if search == '' or re.search(search, key.name, re.I):

                                # populate
                                populate(self, context, key)

                        # process
                        process(self, context, self.shapekeys, option)

                        # clear storage
                        self.shapekeys.clear()

        # uv maps
        if panel.uvs:

            # ignore uv
            if not option.ignoreUV or self.simple:
                if object.type in 'MESH':
                    for uv in object.data.uv_textures:

                        # search
                        if search == '' or re.search(search, uv.name, re.I):

                            # populate
                            populate(self, context, uv)

                    # process
                    process(self, context, self.uvs, option)

                    # clear storage
                    self.uvs.clear()

        # vertex colors
        if panel.vertexColors:

            # ignore vertex color
            if not option.ignoreVertexColor or self.simple:
                if object.type in 'MESH':
                    for vertexColor in object.data.vertex_colors:

                        # search
                        if search == '' or re.search(search, vertexColor.name, re.I):

                            # populate
                            populate(self, context, vertexColor)

                    # process
                    process(self, context, self.vertexColors, option)

                    # clear storage
                    self.vertexColors.clear()

        # materials
        if panel.materials:

            # ignore material
            if not option.ignoreMaterial or self.simple:
                for slot in object.material_slots:
                    if slot.material != None:

                        # search
                        if search == '' or re.search(search, slot.material.name, re.I):

                            # populate
                            populate(self, context, slot.material, slot)

        # textures
        if panel.textures:

            # ignore texture
            if not option.ignoreTexture or self.simple:

                # material textures
                for slot in object.material_slots:
                    if slot.material != None:
                        if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
                            for tslot in slot.material.texture_slots:
                                if hasattr(tslot, 'texture'):
                                    if tslot.texture != None:

                                        # search
                                        if search == '' or re.search(search, tslot.texture.name, re.I):

                                            # populate
                                            populate(self, context, tslot.texture, tslot)

                # particle system textures
                if panel.particleSystems:
                    for modifier in object.modifiers:
                        if modifier.type == 'PARTICLE_SYSTEM':
                            for slot in modifier.particle_system.settings.texture_slots:
                                if hasattr(slot, 'texture'):
                                    if slot.texture != None:

                                        # search
                                        if search == '' or re.search(search, slot.texture.name, re.I):

                                            # populate
                                            populate(self, context, slot.texture, slot)

                # modifier textures
                if panel.modifiers:
                    for modifier in object.modifiers:

                        # texture
                        if modifier.type in {'DISPLACE', 'WARP'}:
                            if modifier.texture:

                                # search
                                if search == '' or re.search(search, modifier.texture.name, re.I):

                                    # populate
                                    populate(self, context, modifier.texture, modifier)

                        # mask texture
                        elif modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:
                            if modifier.mask_texture:

                                # search
                                if search == '' or re.search(search, modifier.mask_texture.name, re.I):

                                    # populate
                                    populate(self, context, modifier.mask_texture)

        # particle systems
        if panel.particleSystems:

            # ignore particle system
            if not option.ignoreParticleSystem or self.simple:
                for modifier in object.modifiers:
                    if modifier.type in 'PARTICLE_SYSTEM':

                        # search
                        if search == '' or re.search(search, modifier.particle_system.name, re.I):

                            # populate
                            populate(self, context, modifier.particle_system)

                # process
                process(self, context, self.particleSystems, option)

                # clear storage
                self.particleSystems.clear()

        # particle settings
        if panel.particleSystems:

            # ignore particle setting
            if not option.ignoreParticleSetting or self.simple:
                for modifier in object.modifiers:
                    if modifier.type in 'PARTICLE_SYSTEM':

                        # search
                        if search == '' or re.search(search, modifier.particle_system.settings.name, re.I):

                            # populate
                            populate(self, context, modifier.particle_system.settings, modifier.particle_system)

# populate
def populate(self, context, datablock, source=None):
    '''
        Sort datablocks into proper storage list.
    '''

    # option
    option = context.window_manager.BatchName

    # objects
    if datablock.rna_type.identifier == 'Object':
        self.objects.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # groups
    if datablock.rna_type.identifier == 'Group':
        self.groups.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # actions
    if datablock.rna_type.identifier == 'Action':
        self.actions.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # grease pencils
    if datablock.rna_type.identifier == 'GreasePencil':
        self.greasePencils.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # pencil layers
    if datablock.rna_type.identifier == 'GPencilLayer':
        self.pencilLayers.append([datablock.info, datablock.info, datablock.info, [datablock, '']])

    # constraints
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Constraint':
            self.constraints.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # modifiers
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Modifier':
            self.modifiers.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # cameras
    if datablock.rna_type.identifier == 'Camera':
        self.cameras.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # meshes
    if datablock.rna_type.identifier == 'Mesh':
        self.meshes.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # curves
    if datablock.rna_type.identifier in {'SurfaceCurve', 'TextCurve', 'Curve'}:
        self.curves.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # lamps
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Lamp':
            self.lamps.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # lattices
    if datablock.rna_type.identifier == 'Lattice':
        self.lattices.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # metaballs
    if datablock.rna_type.identifier == 'MetaBall':
        self.metaballs.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # speakers
    if datablock.rna_type.identifier == 'Speaker':
        self.speakers.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # armatures
    if datablock.rna_type.identifier == 'Armature':
        self.armatures.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # bones
    if datablock.rna_type.identifier in {'PoseBone', 'EditBone', 'Bone'}:
        self.bones.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # vertex groups
    if datablock.rna_type.identifier == 'VertexGroup':
        self.vertexGroups.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # shapekeys
    if datablock.rna_type.identifier == 'ShapeKey':
        self.shapekeys.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # uvs
    if datablock.rna_type.identifier == 'MeshTexturePolyLayer':
        self.uvs.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # vertex colors
    if datablock.rna_type.identifier == 'MeshLoopColorLayer':
        self.vertexColors.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # materials
    if datablock.rna_type.identifier == 'Material':
        self.materials.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # textures
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Texture':
            self.textures.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # particle systems
    if datablock.rna_type.identifier == 'ParticleSystem':
        self.particleSystems.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # particle settings
    if datablock.rna_type.identifier == 'ParticleSettings':
        self.particleSettings.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # line style
    if datablock.rna_type.identifier == 'FreestyleLineStyle':
        self.linestyles.append([datablock.name, datablock.name, datablock.name, [datablock, '', source]])

    # line style modifiers
    if hasattr(datablock.rna_type.base, 'identifier'):
        if hasattr(datablock.rna_type.base.base, 'identifier'):
            if datablock.rna_type.base.base.identifier == 'LineStyleModifier':
                self.modifiers.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # sensors
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Sensor':
            self.sensors.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # controllers
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Controller':
            self.controllers.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # actuators
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Actuator':
            self.actuators.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # scenes
    if datablock.rna_type.identifier == 'Scene':
        self.scenes.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # render layers
    if datablock.rna_type.identifier == 'SceneRenderLayer':
        self.renderLayers.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # worlds
    if datablock.rna_type.identifier == 'World':
        self.worlds.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # libraries
    if datablock.rna_type.identifier == 'Library':
        self.libraries.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # images
    if datablock.rna_type.identifier == 'Image':
        self.images.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # masks
    if datablock.rna_type.identifier == 'Mask':
        self.masks.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # sequences
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'Sequence':
            self.sequences.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # movie clips
    if datablock.rna_type.identifier == 'MovieClip':
        self.movieClips.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # sounds
    if datablock.rna_type.identifier == 'Sound':
        self.sounds.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # screens
    if datablock.rna_type.identifier == 'Screen':
        self.screens.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # keying sets
    if datablock.rna_type.identifier == 'KeyingSet':
        self.keyingSets.append([datablock.bl_label, datablock.bl_label, datablock.bl_label, [datablock, '']])

    # palettes
    if datablock.rna_type.identifier == 'Palette':
        self.palettes.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # brushes
    if datablock.rna_type.identifier == 'Brush':
        self.brushes.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # nodes
    if hasattr(datablock.rna_type.base, 'base'):
        if hasattr(datablock.rna_type.base.base, 'base'):
            if hasattr(datablock.rna_type.base.base.base, 'identifier'):
                if datablock.rna_type.base.base.base.identifier == 'Node':
                    self.nodes.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

                    if self.tag:

                        # new name
                        newName = rename(self, context, datablock.label, option) if not option.suffixLast else rename(self, context, datablock.label, option) + option.suffix

                        # update
                        if datablock.label != newName:

                            # name
                            datablock.label = newName

                            # count
                            self.count += 1

    # node groups
    if hasattr(datablock.rna_type.base, 'identifier'):
        if datablock.rna_type.base.identifier == 'NodeTree':
            self.nodeGroups.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

    # frame nodes
    if datablock.rna_type.identifier == 'NodeFrame':
        self.nodes.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

        if self.tag:

            # new name
            newName = rename(self, context, datablock.label, option) if not option.suffixLast else rename(self, context, datablock.label, option) + option.suffix

            # update
            if datablock.label != newName:

                # name
                datablock.label = newName

                # count
                self.count += 1

    # texts
    if datablock.rna_type.identifier == 'Text':
        self.texts.append([datablock.name, datablock.name, datablock.name, [datablock, '']])

def process(self, context, collection, option):
    '''
        Process collection, send names to rename and shared sort.
    '''

    # compare
    compare = []

    # clean
    clean = []

    # clean duplicates
    for name in collection:

        # remove duplicates
        if name[3][0] not in compare:

            # append
            compare.append(name[3][0])
            clean.append(name)

    # done with collection
    collection.clear()

    # process collection
    for name in clean:

        # rename
        name[1] = rename(self, context, name[1], option)
        # name[0] = name[1]

    # randomize names (prevents conflicts)
    for name in clean:

        # datablock
        datablock = name[3][0]

        # has name
        if hasattr(name[3][0], 'name'):

            # randomize name
            name[3][0].name = str(random())

        # has info
        if hasattr(name[3][0], 'info'):

            # randomize info
            name[3][0].info = str(random())

        # has bl_label
        if hasattr(name[3][0], 'bl_label'):

            # randomize bl_label
            name[3][0].bl_label = str(random())

    # simple
    if self.simple:

        # update
        for name in clean:

            # has name
            if hasattr(name[3][0], 'name'):
                name[3][0].name = name[1]

                # has info
            if hasattr(name[3][0], 'info'):
                name[3][0].info = name[1]

            # count
            if name[1] != name[2]:
                self.count += 1

    # isnt simple
    else:

        # is shared sort or shared count
        if context.window_manager.BatchShared.sort or context.window_manager.BatchShared.count:

            # sort
            shared.main(self, context, clean, context.window_manager.BatchShared)

        # isnt shared sort or shared count
        else:

            # apply names
            for name in clean:

                # has name
                if hasattr(name[3][0], 'name'):

                    # name
                    name[1] = name[1] + option.suffix if option.suffixLast else name[1]
                    name[3][0].name = name[1]

                # has info
                if hasattr(name[3][0], 'info'):

                    # info
                    name[1] = name[1] + option.suffix if option.suffixLast else name[1]
                    name[3][0].info = name[1]

                # has bl_label
                if hasattr(name[3][0], 'bl_label'):

                    # bl_label
                    name[1] = name[1] + option.suffix if option.suffixLast else name[1]
                    name[3][0].bl_label = name[1]

                # count
                if name[1] != name[2]:
                    self.count += 1

    # purge re
    re.purge()

# name
def rename(self, context, oldName, option):
    '''
        Update string received from process.
    '''

    # option
    option = context.window_manager.BatchName

    # not simple
    if not self.simple:

        # numeral
        numeral = r'\W[0-9]*$|_[0-9]*$'

        # is custom
        if option.custom != '':

            # is insert
            if option.insert:
                newName = oldName[:option.insertAt] + option.custom + oldName[option.insertAt:]

            # isnt insert
            else:

                # new name
                newName = option.custom

        # isnt custom
        else:

            # new name
            newName = oldName

        # trim start
        newName = newName[option.trimStart:]

        # trim end
        if option.trimEnd > 0:
            newName = newName[:-option.trimEnd]

        # cut
        newName = newName[:option.cutStart] + newName[option.cutStart+option.cutAmount:]

        # is find
        if option.find != '':

            # find & replace
            if option.regex:
                try: newName = re.sub(option.find, option.replace, newName)
                except Exception as e: self.report({'WARNING'}, 'Regular expression: ' + str(e))
            else:
                newName = re.sub(re.escape(option.find), option.replace, newName)

        # split numeral & suffix
        try: newName = re.split(numeral, newName)[0] + option.suffix + re.search(numeral, newName).group(0) if not option.suffixLast else newName
        except: newName = newName + option.suffix if not option.suffixLast else newName

        # prefix
        newName = option.prefix + newName

    # is simple
    else:

        # new name
        newName = oldName

        # is search
        if context.scene.NamePanel.search != '':

            # find & replace
            if context.scene.NamePanel.regex:
                try: newName = re.sub(context.scene.NamePanel.search, option.replace, newName, re.I)
                except Exception as e: self.report({'WARNING'}, 'Regular expression: ' + str(e))
            else:
                newName = re.sub(re.escape(context.scene.NamePanel.search), option.replace, newName, re.I)

    # new name
    return newName
