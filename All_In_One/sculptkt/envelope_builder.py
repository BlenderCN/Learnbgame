import bpy
from .multifile import register_class
import os

ARMATURE_PRESETS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "envelope_presets")

def get_armature_filenames():
    for name in os.listdir(ARMATURE_PRESETS_PATH):
        filepath = os.path.join(ARMATURE_PRESETS_PATH, name)
        if os.path.isfile(filepath):
            if name.lower().endswith(".blend"):
                yield name, name[:-6], filepath


def lerp(a, b, f):
    return a * (1 - f) + b * f


@register_class
class SaveEnvelopeArmatute(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.save_envelope_armature"
    bl_label = "Save Envelope Armature"
    bl_description = "Save selected armature as an envelope base"
    bl_options = {"REGISTER"}

    name: bpy.props.StringProperty(
        name="Name"
    )

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == "ARMATURE"

    def invoke(self, context, event):
        self.name = context.active_object.name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object
        obj.name = self.name
        obj.data.display_type = "ENVELOPE"
        path = os.path.join(ARMATURE_PRESETS_PATH, self.name + ".blend")
        bpy.data.libraries.write(path, {obj})
        return {"FINISHED"}


class ArmatureDeleteChecker:
    name = ""
    path = None
    valid = False

    @classmethod
    def check(cls, name):
        cls.name = name
        path = os.path.join(ARMATURE_PRESETS_PATH, name + ".blend")
        cls.valid = os.path.isfile(path)
        cls.path = path

    @classmethod
    def delete(cls, name):
        cls.check(name)
        if cls.valid:
            os.remove(cls.path)

@register_class
class DeleteEnvelopeArmature(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.delete_envelope_armature"
    bl_label = "Delete Envelope Armature"
    bl_description = "Remove permanently a envelope armature preset"
    bl_options = {"REGISTER"}

    name: bpy.props.StringProperty(
        name="Name",
        update=lambda self, context: ArmatureDeleteChecker.check(self.name),
        options={"TEXTEDIT_UPDATE"}
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        if not ArmatureDeleteChecker.valid:
            layout.label(text="File doesn't exists", icon="CANCEL")
        else:
            layout.label(text="Are you sure you want to delete?")


    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        ArmatureDeleteChecker.delete(self.name)
        return {"FINISHED"}


@register_class
class LoadEnvelopeArmature(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.load_envelope_armature"
    bl_label = "Add armature preset"
    bl_description = "Add an envelope base"
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.EnumProperty(
        items=lambda scene, context: sorted(get_armature_filenames(), reverse=True),
        name="Type",
        description="The preset of armature to load"
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print(self.type)
        file = os.path.join(ARMATURE_PRESETS_PATH, self.type)
        with bpy.data.libraries.load(file) as (data_from, data_to):
            data_to.objects = [data_from.objects[0]]
        data_to.objects[0].location = context.scene.cursor.location
        context.collection.objects.link(data_to.objects[0])
        context.view_layer.objects.active = data_to.objects[0]
        data_to.objects[0].select_set(True)
        return {"FINISHED"}


@register_class
class ConvertEnvelopeArmature(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.convert_envelope_armature"
    bl_label = "Convert Envelope To Mesh"
    bl_description = "Create a mesh out of the envelope base"
    bl_options = {"REGISTER", "UNDO"}

    min_steps: bpy.props.IntProperty(
        name="Min Steps",
        description="The minimum amount of metaballs used per bone",
        default=15
    )

    step_size: bpy.props.FloatProperty(
        name="Step Size",
        description="The distance between metaballs",
        default=0.2
    )
    resolution: bpy.props.FloatProperty(
        name="Resolution",
        description="resolution as a scale of armature size",
        default=0.03
    )
    delete_armature: bpy.props.BoolProperty(
        name="Delete Armature",
        description="Remove Original Armature",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == "ARMATURE"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object
        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.select_all(action="SELECT")
        bpy.ops.pose.armature_apply()
        bpy.ops.object.mode_set(mode="OBJECT")

        armature = obj.data
        resolution = min(obj.dimensions) * self.resolution
        mat = obj.matrix_world

        bpy.ops.object.metaball_add()
        context.active_object.matrix_world = mat
        context.active_object.name = obj.name + "_mesh"
        meta = context.active_object.data
        meta.threshold = 0.001
        meta.resolution = resolution
        meta.elements.remove(meta.elements[0])

        for bone in armature.bones:
            head = bone.head_local
            tail = bone.tail_local
            h_radius = bone.head_radius
            t_radius = bone.tail_radius
            dist = (head - tail).length

            size = (h_radius + t_radius) / 2 * self.step_size
            steps = int(dist / size)

            if steps < self.min_steps:
                steps = self.min_steps

            for i in range(steps + 1):
                i /= steps
                location = lerp(head, tail, i)
                radius = lerp(h_radius, t_radius, i)
                ball = meta.elements.new(type="BALL")
                ball.co = location
                ball.radius = radius
                ball.stiffness = 10.0
        bpy.ops.object.convert(target="MESH")

        if self.delete_armature:
            bpy.data.armatures.remove(armature)

        return {"FINISHED"}
