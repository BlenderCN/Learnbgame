# Orox uses Animated or MoCap walkcycles to generate footstep driven walks
# Copyright (C) 2012  Bassam Kurdali
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>
import bpy
import imp
from copy import deepcopy
from pprint import pprint
from mathutils import Vector, Quaternion, Matrix, Euler, Color


try:
    from . import parambulator
    from .utils import *
except:
    import parambulator
    import utils
    imp.reload(utils)
    from utils import *
    imp.reload(parambulator)
# I now deem this temporarily OK:
walkers = []
walkers_per_rig = {}
myfile = ""

# for now the following are globals that specify the part of a step safe to
# rotate a foot, based on how far it's location is from the contacts, contact
# 1 being 0.0, and contact 2 being 1.0
in_air_start = 0.2
in_air_end = 0.8


def reference_action_list(self, context):
    '''
    Returns an enum property list of possible actions for the given walker
    '''
    scene = context.scene
    action_list = walkers_per_rig[self.autorig][0].actions
    return([tuple([i] * 3) for i in action_list])


def assign_action(self, context):
    '''
    updates the walkers, selected or all, in the rig type, with the actions
    '''
    scene = context.scene
    for walker in walkers_per_rig[self.autorig]:
        if scene.use_autowalk_all or walker.object.select:
            walker.action = self.action
            walker.injest_action()


class AutoWalkerRigTypes(bpy.types.PropertyGroup):
    '''
    Different types of Autowalker and their action selection
    '''
    autorig = bpy.props.StringProperty(default="")
    autorig_first_index = bpy.props.IntProperty(default=0)
    action = bpy.props.EnumProperty(
        items=reference_action_list, update=assign_action)


def update_prop(self, context):
    '''
    property updater
    '''
    scene = context.scene
    global walkers, walkers_per_rig
    for walker in walkers_per_rig[self.autorig]:
        if scene.use_autowalk_all or walker.object.select:
            walker.prep_action()
            walker.bake_walk(context)   


def stride_multiply(self, context):
    '''
    property updater
    '''
    scene = context.scene
    global walkers
    for walker in walkers:
        if self.use_autowalk_all or walker.object.select:
            walker.footstep_stride_multiplier = self.stride_multiplier  


class AutoWalkerParams(bpy.types.PropertyGroup):
    '''
    Parameters for the autowalkers
    '''
    autorig = bpy.props.StringProperty(default="")
    value = bpy.props.FloatProperty(
        default=0.0, min=-1.0, max=1.0, update=update_prop)


class ActionSelectionUl(bpy.types.UIList):
    '''
    data is the RNA object containing the collection,
    item is the current drawn item of the collection,
    active_data is the RNA object containing the active property for the
      collection (i.e. integer pointing to the active item of the collection).
    active_propname is the name of the active property (
      use 'getattr(active_data, active_propname)').
    index is index of the current item in the collection.
    '''
    def draw_item(
            self, context, layout, data, item, icon,
            active_data, active_propname, index):
        layer_holder = data
        rig_type = item
        layout.label(
            text="{} action:".format(
                rig_type.autorig), translate=False, icon_value=icon)
        layout.prop(rig_type, 'action', text="")


class ParamSelectionUl(bpy.types.UIList):
    '''
    UI for autowalker params
    '''
    def draw_item(
            self, context, layout, data, item, icon,
            active_data, active_propname, index):
        param = item
        layout.label(
            text="{} {}".format(param.autorig, param.name),
            translate=False, icon_value=icon)
        layout.prop(param, 'value', slider=True, text="")


def remove_footsteps(scene):
    '''
    remove all footsteps from the scene
    '''
    for walker in walkers:
        walker.remove_walker_footsteps(scene)


def draw_matrix(name, mat):
    '''
    test function to check if our math is correct
    '''
    scene = bpy.context.scene
    try:
        ob = bpy.data.objects[name]
    except:
        ob = bpy.data.objects.new(name=name, object_data=None)
        scene.objects.link(ob)
    ob.layers = scene.layers
    ob.location = mat.to_translation()
    ob.rotation_euler = mat.to_euler()
    ob.scale = mat.to_scale()

def test_footsteps(frames):
    '''
    test footsteps by making empties.
    '''
    scene = bpy.context.scene
    flip = scene.flip_walker
    for walker in walkers:
        for foot in walker.feet:
            for i in range(0, len(foot.steps) - 1, 1):
                loc_1 = foot.steps[i]['location']
                loc_2 = foot.steps[i + 1]['location']
                mat = offset_matrix(
                    loc_1, loc_2, flip_axis(foot.forward, flip), foot.up)
                draw_matrix('{}_{}'.format(foot.name, i), mat)


def add_paramameter_to_datablock(datablock, param, rig_type):
    '''
    add a parameter to a datablocks collection property
    '''
    newparam = datablock.autowalker_params.add()
    newparam.name = param
    newparam.autorig = rig_type


def import_params(context):
    '''
    glob the parameters onto our rigs and our scene for use by the UI
    '''
    global walkers
    scene = context.scene
    walker_params = {}
    for walker in walkers:

        params = [
            param for param in dir(walker.params)
            if not param.startswith('_')]
        for param in params:
            add_parameter_to_datablock(scene, param, walker.rig)
        walker_params[walker.object] = params
    return walker_params


class BakeAutoWalk(bpy.types.Operator):
    '''
    Autowalk Baking class
    '''
    bl_idname = "object.bake_autowalk"
    bl_label = "Bake Walk"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global walkers, walkers_per_rig
        for walker in walkers:
            if context.scene.use_autowalk_all or walker.object.select:
                walker.prep_action(blank=True)
                walker.bake_walk(context)
        return {'FINISHED'}


class AutoFootsteps(bpy.types.Operator):
    '''
    auto footstep generation class
    '''
    bl_idname = "object.auto_footsteps"
    bl_label = "Generate Footsteps"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global walkers
        scene = context.scene
        frames = range(scene.frame_preview_start, scene.frame_preview_end)
        for walker in walkers:
            walker.offset_targets()
            print(walker.reference_object)
            if walker.reference_object:
                ref = walker.reference_object
                walker.make_footsteps(ref, frames)
        return {'FINISHED'}


class FootStepEdit(bpy.types.Operator):
    '''
    editable the Footsteps
    '''
    bl_idname = "object.edit_steps"
    bl_label = "Edit Footsteps"

    output = bpy.props.BoolProperty(name="output", default=True)

    def execute(self, context):
        scene = context.scene
        output = self.properties.output
        frames = range(
            scene.frame_preview_start, scene.frame_preview_end)
        if output:
            for walker in walkers:
                walker.draw_footsteps(scene)
        else:
            for walker in walkers:
                walker.injest_footsteps(scene)
        return {'FINISHED'}


class CreateFootSteps(bpy.types.Operator):
    '''
    create new footstep group
    '''
    bl_idname = "object.new_footsteps"
    bl_label = "New Footsteps"

    walker_id = bpy.props.IntProperty(name="walker_id", default=0)

    def execute(self, context):
        scene = context.scene
        walker_id = self.properties.walker_id
        walker = walkers[walker_id]
        foot_count = len(walkers[walker_id].feet)
        space = [
            space for space in context.area.spaces if
            space.type == 'VIEW_3D'][0]
        scene = context.scene
        frame = context.scene.frame_current
        current_steps = [
            [step for step in foot.steps] for foot in walker.feet]
        if frame in [
                step['frame'] for steps in current_steps for
                step in steps]:
            return {'CANCELLED'}
        avg_location = space.cursor_location
        #find closest frame step 'pair'
        step_pairs = [pair for pair in zip(*current_steps)]
        mystep = [{
            'location': avg_location,
            'rotation': Quaternion((1, 0, 0, 0)),
            'frame': frame} for i in range(foot_count)]
        step_pairs.append(mystep)
        step_pairs.sort(key=lambda x: x[0]['frame'])
        my_rank = step_pairs.index(mystep)
        closest = 0 if my_rank == 0 else my_rank - 1
        step_closest = step_pairs[closest]
        average_closest = average(
            [step['location'] for step in step_closest])
        for index, step in enumerate(step_closest):
            location = avg_location + step['location'] - average_closest
            walker.feet[index].steps.append(
                {'frame': frame, 'location': location})
        for foot in walker.feet:
            foot.steps.sort(key=lambda x: x['frame'])
        draw_footsteps(scene, walker)
        return {'FINISHED'}


class DeleteAllFootSteps(bpy.types.Operator):
    '''
    delete current steps
    '''
    bl_idname = "object.delete_all_footsteps"
    bl_label = "Delete All Footsteps"

    def execute(self, context):
        scene = context.scene
        remove_footsteps(scene)
        return {'FINISHED'}


def add_parameter_to_datablock(datablock, param, rig_type):
    '''
    add it
    '''
    if not (param, rig_type) in [
            (a.name, a.autorig) for a in datablock.autowalker_params]:
        newparam = datablock.autowalker_params.add()
        newparam.name = param
        newparam.autorig = rig_type


def register_walker(walker, scene):
    '''
    register a walker into our global data structures
    '''
    global walkers, walkers_per_rig
    walkers.append(walker)
    try:
        walkers_per_rig[walker.rig].append(walker)
    except:
        walkers_per_rig[walker.rig] = [walker]
    autorigs = [a.autorig for a in scene.autorig_actions]
    if not walker.rig in autorigs:
        a = scene.autorig.actions.add()
        a.autorig = walker.rig


def bunch(rig_params, scene):
    '''
    grabs all the walkers in the scene, and uses the rig_params file to
    make everything lekker for the autowalker to run
    '''
    global walkers, walkers_per_rig
    autorigs = {param['rig']: index for index, param in enumerate(rig_params)}
    '''
    current_scene_rigs = [a.autorig for a in scene.autorig_actions]
    for rig in autorigs:
        if not rig in current_scene_rigs:
            a = scene.autorig_actions.add()
            a.autorig = rig
    '''
    for rig in scene.objects:
        if rig.type == 'ARMATURE' and rig.data.name in autorigs:
            print('adding walker')
            mydict = deepcopy(rig_params[autorigs[rig.data.name]])
            walker = parambulator.Parambulator(
                    mydict,
                    rig)
            register_walker(walker, scene)


def initialize_file(context):
    '''
    get a specific file loaded with autowalkeration
    '''
    global walkers, walkers_per_rig, myfile
    scene = context.scene

    # get teh auto rig description, if it exists, as a thing.
    try:
        raw_data = bpy.data.texts['auto_rig_desc.py'].as_string()
    except:
        print('oops')
        return False
    rig_params = eval(raw_data.replace("rig_params = ", ""))
    exec(raw_data)
    print(rig_params)
    autorigs = {param['rig']: index for index, param in enumerate(rig_params)}
    print("BOOOO",autorigs)
    current_scene_rigs = [a.autorig for a in scene.autorig_actions]
    for rig in autorigs:
        if not rig in current_scene_rigs:
            a = scene.autorig_actions.add()
            a.autorig = rig
    # get our walkers all happy in a data structure
    bunch(rig_params, scene)
       
    params = import_params(context)
    myfile = context.blend_data.filepath
    print('yesss')
    return True


class CreateCrowdFromObjects(bpy.types.Operator):
    '''
    Create Autowalkers from selected objects
    '''
    bl_label = "Selected To Crowd"
    bl_idname = "scene.create_crowd_selected"

    def execute(self, context):
        global walkers, walkers_per_rig

        scene = context.scene
        selected = context.selected_objects
        active = context.active_object
        rig_type = scene.autorig_actions[scene.active_autorig_action].autorig
        rig_params = get_params()
        autorigs = {param['rig']: index for index, param in enumerate(rig_params)} 
        if not rig_params:
            return {'ABORTED'}
        for obj in selected:
            mydict = deepcopy(rig_params[autorigs[rig_type]])
            walker = parambulator.Parambulator(
                mydict,
                walker_object=None,
                reference=obj)
            register_walker(walker, scene)
        return {'FINISHED'}


class InitializeBlend(bpy.types.Operator):
    '''
    this is all that gets displayed by default
    '''
    bl_idname = 'scene.initialize_blend'
    bl_label = 'Initialize Blend File'

    def execute(self, context):
        result = initialize_file(context)
        if result:
            return {'FINISHED'}
        else:
            return {'ERROR'}

panel_label = "Autowalk Control"
panel_space_type = 'VIEW_3D'
panel_region_type = 'TOOLS'
panel_category = 'OROX'


def panel_draw_header(self, context, icon):
    '''
    draw the panel header
    '''
    layout = self.layout
    scene = context.scene
    layout.prop(
        scene, 'use_autowalk_all', text="",
        icon='UNPINNED' if scene.use_autowalk_all else 'PINNED',
        emboss=False)
    layout.operator(
        "scene.initialize_blend", icon=icon,
        text="", emboss=False)


class AutoInitPanel(bpy.types.Panel):
    '''
    Main Control Panel for AutoMin system
    '''
    bl_label = panel_label
    bl_idname = "SCENE_PT_automin_init"
    bl_space_type = panel_space_type
    bl_region_type = panel_region_type
    bl_category = panel_category

    @classmethod
    def poll(cls, context):
        return "auto_rig_desc.py" in bpy.data.texts and\
            walkers == [] or\
            myfile == "" or myfile != context.blend_data.filepath

    def draw_header(self, context):
        panel_draw_header(self, context, 'QUIT')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.operator(
            "scene.create_crowd_selected", icon='POSE_HLT')
        '''
        row = layout.row()
        # first we need to have the reference action ui
        row.template_list(
            "ActionSelectionUl", "",
            scene, "autorig_actions",
            scene, "active_autorig_action")       
        '''


class AutoMinControl(bpy.types.Panel):
    '''
    Main Control Panel for AutoMin system
    '''
    bl_label = panel_label
    bl_idname = "SCENE_PT_automin"
    bl_space_type = panel_space_type
    bl_region_type = panel_region_type
    bl_category = panel_category

    @classmethod
    def poll(cls, context):
        return "auto_rig_desc.py" in bpy.data.texts and\
            walkers != [] and\
            myfile != "" and myfile == context.blend_data.filepath

    def draw_header(self, context):
        panel_draw_header(self, context, 'FILE_REFRESH')

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row()
        row.operator("scene.create_crowd_selected", icon='POSE_HLT')
        row = layout.row()
        row.operator("object.bake_autowalk", icon='POSE_HLT', text="bake!")
        row = layout.row()
        row.label("Reference Actions:")
        row = layout.row()
        # first we need to have the reference action ui
        row.template_list(
            "ActionSelectionUl", "",
            scene, "autorig_actions",
            scene, "active_autorig_action")

        # now we need the parameter ui
        row = layout.row()
        row.label("Parameters:")
        row = layout.row()
        row.template_list(
            "ParamSelectionUl", "",
            scene, "autowalker_params",
            scene, "active_autowalker_param")

        row = layout.row()
        row.label("Footsteps:")
        box = layout.box()
        row = box.row()
        row.operator(
            "object.auto_footsteps",
            icon='OUTLINER_DATA_ARMATURE',
            text="Footsteps")
        row = box.row()
        row.prop(
            scene, 'stride_multiplier',
            text="stride multiply", slider=True)
        row = box.row()
        row.prop(
            scene, 'footstep_scale', text="footstep_scale", slider=True)
        row = box.row(align=True)
        row.operator("object.edit_steps", text="draw steps").output = True
        row.operator("object.edit_steps", text="get steps").output = False
        row = box.row(align=True)
        col = row.column(align=True)
        col.prop(scene, 'offset_loc')


def register():

    bpy.utils.register_class(AutoWalkerParams)
    bpy.utils.register_class(AutoWalkerRigTypes)
    bpy.utils.register_class(ActionSelectionUl)
    bpy.utils.register_class(ParamSelectionUl)
    bpy.types.Scene.autorig_actions = bpy.props.CollectionProperty(
        type=AutoWalkerRigTypes)
    bpy.types.Scene.autowalker_params = bpy.props.CollectionProperty(
        type=AutoWalkerParams)
    bpy.types.Scene.active_autorig_action = bpy.props.IntProperty()
    bpy.types.Scene.active_autowalker_param = bpy.props.IntProperty()

    bpy.types.Scene.footstep_scale = bpy.props.FloatProperty(
        name="footstep_scale", default=1.0, min=0.1, max=3.0)
    bpy.types.Scene.stride_multiplier = bpy.props.FloatProperty(
        name="stride_multiplier", default=1.0, min=0.1, max=2.0,
        update=stride_multiply)
    bpy.types.Scene.flip_walker = bpy.props.BoolProperty(
        name="flip_walker", default=False)

    def change_offset(self, context):
        scene = context.scene
        mat = Matrix.Translation(scene.offset_loc)
        global walkers
        for walker in walkers:
            if scene.use_autowalk_all or walker.object.select:
                walker.reference_offset = mat        
    bpy.types.Scene.offset_loc = bpy.props.FloatVectorProperty(
        name="Offset Location",unit='LENGTH', subtype='TRANSLATION',
        default=(0.0,0.0,0.0), update=change_offset)
    bpy.types.Scene.use_autowalk_all = bpy.props.BoolProperty(default=True)

    bpy.utils.register_class(CreateCrowdFromObjects)
    bpy.utils.register_class(InitializeBlend)
    bpy.utils.register_class(AutoInitPanel)

    bpy.utils.register_class(CreateFootSteps)
    bpy.utils.register_class(DeleteAllFootSteps)
    bpy.utils.register_class(FootStepEdit)
    bpy.utils.register_class(BakeAutoWalk)
    bpy.utils.register_class(AutoFootsteps)
    bpy.utils.register_class(AutoMinControl)


def unregister():

    del(bpy.types.Scene.autorig_actions)
    del(bpy.types.Scene.autowalker_params)
    del(bpy.types.Scene.active_autorig_action)
    del(bpy.types.Scene.active_autowalker_param)
    bpy.utils.unregister_class(ActionSelectionUl)
    bpy.utils.unregister_class(ParamSelectionUl)
    bpy.utils.unregister_class(AutoWalkerRigTypes)
    bpy.utils.unregister_class(AutoWalkerParams)

    bpy.utils.unregister_class(CreateFootSteps)
    bpy.utils.unregister_class(DeleteAllFootSteps)
    bpy.utils.unregister_class(FootStepEdit)
    bpy.utils.unregister_class(BakeAutoWalk)
    bpy.utils.unregister_class(AutoFootsteps)
    bpy.utils.unregister_class(AutoMinControl)

    bpy.utils.unregister_class(AutoInitPanel)
    bpy.utils.unregister_class(InitializeBlend)
    bpy.utils.unregister_class(CreateCrowdFromObjects)
    del(bpy.types.Scene.footstep_scale)
    del(bpy.types.Scene.stride_multiplier)
    del(bpy.types.Scene.flip_walker)
    del(bpy.types.Scene.use_autowalk_all)
    del(bpy.types.Scene.offset_loc)


if __name__ == '__main__':
    register()
