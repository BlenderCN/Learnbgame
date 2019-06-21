bl_info = {
    "name": "Inertial-GNSS car data to blender",
    "author": "Federico Bertani",
    "location": "View3D > Tools",
    "description": "Blender simulation generator from inertial sensor data on vehicle",
    "category": "Learnbgame",
    "version": (2,0,0),
    "tracker_url" : "https://github.com/physycom/inertial_to_blender/issues"
}

import bpy
import sys, math, os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
# different name from project and deployed zip
from . import addon_updater_ops
from blender import bootstrap

from bpy.props import StringProperty, BoolProperty



bpy.types.Scene.datasetPath = StringProperty(
    name="Dataset path",
    description=":",
    default="",
    maxlen=2056,
)

bpy.types.Scene.use_gps = BoolProperty(
    name="Use GPS Data",
    description="Use GPS data",
    default = False)

bpy.types.Scene.crash = BoolProperty(
    name="Reconstruct crash",
    description="The dataset represent a crash, reconstruct it",
    default = False)

bpy.types.Scene.ignore_z = BoolProperty(
    name="Ignore vertical motion",
    description="Ignore movement on z axis",
    default = False)



class InertialBlenderPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_label = "Inertial-GNSS to blender"

    # bl_context = "object"

    def draw(self, context):
        layout = self.layout

        # Call to check for update in background
        # note: built-in checks ensure it runs at most once
        # and will run in the background thread, not blocking
        # or hanging blender
        # Internally also checks to see if auto-check enabled
        # and if the time interval has passed
        addon_updater_ops.check_for_update_background()

        col = layout.column()
        col.operator("physycom.load_dataset")
        col.prop(context.scene, "datasetPath")
        col.prop(context.scene, "use_gps", text="Use GPS")
        col.prop(context.scene, "crash", text="Reconstruct crash")
        col.prop(context.scene,"ignore_z", text="Ignore vertical movements")
        col.operator("physycom.reconstruct_dynamics")

        if addon_updater_ops.updater.update_ready == True:
            layout.label("Update available", icon="INFO")
        layout.label("")

        # call built-in function with draw code/checks
        addon_updater_ops.update_notice_box_ui(self, context)


# noinspection SpellCheckingInspection
class LoadDataset(bpy.types.Operator):
    """Object Cursor Array"""
    # TODO use more standard name
    bl_idname = "physycom.load_dataset"
    bl_label = "Load dataset"
    bl_options = {'REGISTER', 'UNDO'}

    # must be called filepath because fileselect_add() in invoke() assume this
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.datasetPath = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ReconstructDynamics(bpy.types.Operator):
    """Object Cursor Array"""
    # TODO use more standard name
    bl_idname = "physycom.reconstruct_dynamics"
    bl_label = "Reconstruct Dynamics"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # call install dependencies to be sure that everything needed is present
        # because on auto-update register is not called
        bootstrap.install_dependencies()
        # import now get trajectory from path because some package could be still not installed if imported
        # in global scope
        from src import get_trajectory_from_path
        scene = context.scene
        if 'Camaro' not in scene.objects.keys():
            # path of .blend file with car included in the add-on
            carpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "camaro_for_link.blend")
            # append scene with car (this scene will be temporary but necessary)
            bpy.ops.wm.append(directory=carpath, filename="Scene/CamaroScene")
            # get car's scene object
            scene2 = bpy.data.scenes['CamaroScene']
            # get mesh object from car's scene
            camaro_obj = scene2.objects['Camaro']
            # move appended object to first scene
            scene.objects.link(camaro_obj)
            # make car object in first scene local so when the object in the second scene will be deleted
            # this object will not be
            obj = scene.objects['Camaro'].make_local()
            # for each material slot in the car object
            for material_slot in obj.material_slots:
                # set to not use nodes for material, so the car is not grey
                material_slot.material.use_nodes = False
            # TODO check if necessary to uncomment this
            # for object_ in scene2.objects:
            #    bpy.data.objects.remove(object_, True)
            # remove second temporary scene
            bpy.data.scenes.remove(scene2, True)
        # get car object from scene
        obj = scene.objects['Camaro']
        # set the car object as the active object in the first scene
        scene.objects.active = obj
        # get from checkbox if using gps data to reconstruct
        use_gps = scene.use_gps
        # get from checkbox if using crash mode
        # (searching for a high accelleration, removing unreliable records and use physics engine)
        crash = scene.crash
        # get from checkbox if ignoring vertical movements
        ignore_z = scene.ignore_z
        # get from textinput the dataset path
        datasetpath = scene.datasetPath
        # get current frame per seconds value
        fps = scene.render.fps
        # set to use meters for distance
        scene.unit_settings.system = 'METRIC'
        # reconstruct car trajectory
        positions, times, angular_positions = get_trajectory_from_path(datasetpath, use_gps, crash)
        # clear old animation data (if present)
        obj.animation_data_clear()
        obj.animation_data_create()
        # create a new animation data action
        obj.animation_data.action = bpy.data.actions.new(name="MyAction")
        # use directly quaternion for rotations
        obj.rotation_mode = 'QUATERNION'
        # set a step for avoiding set too much keyframes
        # ~ 1 keyframe for frame is enough
        total_time = times[-1] - times[0]
        total_frames = total_time * fps
        if positions.shape[1] > total_frames:
            # downsampling
            step = int(positions.shape[1] / total_frames)
        else:
            step = 1
        # number of keyframes that will be inserted
        n_keyframe = math.ceil(positions.shape[1] / step)
        scene.frame_start = 0
        if not crash:
            scene.frame_end = round(times[-1] * fps)
        else:
            bpy.ops.rigidbody.objects_add(type='ACTIVE')
            scene.frame_end = round(2 * (times[-1] * fps))
            rigidbody_world = scene.rigidbody_world
            # set car bounciness (value measured in real life scenario)

            rigidbody_world.steps_per_second = 1000
            rigidbody_world.solver_iterations = 100
            rigidbody_world.point_cache.frame_start = 0
            rigidbody_world.point_cache.frame_end = round(2 * round(times[-1] * fps))
            # set bounciness
            obj.rigid_body.restitution = 0.05
            # set mass
            obj.rigid_body.mass = 1600
            # set dumping to 0
            obj.rigid_body.linear_damping = 0
            # set keyframe at 0 using animation keyframe
            obj.animation_data.action = bpy.data.actions.new(name="Kinematic")
            fcurve_kinematic = obj.animation_data.action.fcurves.new(data_path="rigid_body.kinematic")
            fcurve_kinematic.keyframe_points.add(3)
            fcurve_kinematic.keyframe_points[0].co = 0, True
            obj.location.x = positions[0,-1]
            obj.location.y = positions[1,-1]
            if ignore_z:
                obj.location.z = 0.55
            # set keyframe at the end using physics engine
            fcurve_kinematic.keyframe_points[1].co = round((times[-1] * fps) - 10), True
            fcurve_kinematic.keyframe_points[2].co = round(times[-1] * fps), False
            for i in range(3):
                fcurve_kinematic.keyframe_points[i].interpolation = 'CONSTANT'

        if ignore_z:
            location_channels = [0,1]
            positions[2] = 0
            # set ground start vertical position
            obj.location.z = 0
            rotation_channels = [2]
        else:
            location_channels = rotation_channels = range(3)
        # create f-curve for each location axis
        for index in location_channels:
            fcurve_location = obj.animation_data.action.fcurves.new(data_path="location", index=index)
            fcurve_location.keyframe_points.add(n_keyframe)
            for i in range(0, positions.shape[1], step):
                keyframe_index = math.floor(i / step)
                # TODO change not constant
                fcurve_location.keyframe_points[keyframe_index].interpolation = 'LINEAR'
                fcurve_location.keyframe_points[keyframe_index].co = round(times[i] * fps), positions[index, i]
        # create f-curve for each quaternion component
        for index in range(4):
            fcurve_rotation = obj.animation_data.action.fcurves.new(data_path="rotation_quaternion", index=index)
            fcurve_rotation.keyframe_points.add(n_keyframe)
            for i in range(0, positions.shape[1], step):
                keyframe_index = math.floor(i / step)
                fcurve_rotation.keyframe_points[keyframe_index].interpolation = 'LINEAR'
                fcurve_rotation.keyframe_points[keyframe_index].co = round(times[i] * fps), angular_positions[index, i]
        print("Done adding keyframes!")

        if (crash):
            # bpy.ops.action.clean(channels=True)
            bpy.ops.ptcache.free_bake_all()
            bpy.ops.ptcache.bake_all()

        # create a curve that shows the vehicle path
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        polyline = curveData.splines.new('POLY')
        # -1 for avoiding closing curve
        polyline.points.add(positions.shape[1]-1)
        for i, location in enumerate(positions.T):
             # set x,y,z,weight
             polyline.points[i].co = (*location,1)
        curveOB = bpy.data.objects.new('myCurve', curveData)
        #attach curve to scene
        scene.objects.link(curveOB)

        return {'FINISHED'}

def register():
    # register auto-update module
    # placed this on top so the plugin degenerate to a non working version
    # this can be fixed by a new release
    addon_updater_ops.register(bl_info)
    bpy.utils.register_class(AutoUpdatePreferences)
    bootstrap.install_dependencies()
    bpy.utils.register_class(LoadDataset)
    bpy.utils.register_class(ReconstructDynamics)
    bpy.utils.register_class(InertialBlenderPanel)
    print("Done!")


def unregister():
    # TODO move to implicit unregistration (module)
    addon_updater_ops.unregister()
    bpy.utils.unregister_class(AutoUpdatePreferences)
    # commented out because it was a boggy solution and numpy is lightweight
    #bootstrap.uninstall_packages_from_requirements_file()
    bpy.utils.unregister_class(LoadDataset)
    bpy.utils.unregister_class(ReconstructDynamics)
    bpy.utils.unregister_class(InertialBlenderPanel)


class AutoUpdatePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # addon updater preferences

    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
    )

    updater_interval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_interval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
    )
    updater_interval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_interval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )


    def draw(self, context):
        layout = self.layout
        # col = layout.column() # works best if a column, or even just self.layout
        mainrow = layout.row()
        col = mainrow.column()
        # updater draw function
        # could also pass in col as third arg
        addon_updater_ops.update_settings_ui(self, context)

if __name__ == "__main__":
    register()
