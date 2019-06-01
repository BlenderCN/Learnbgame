
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
bl_info = {
    "name": "Multires Subdivision",
    "description": "Facilitate the use of multires subdivision",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


class TILA_multires_subdivision(bpy.types.Operator):
    bl_idname = "sculpt.tila_multires_subdivision"
    bl_label = "Multires Subdivision"

    subd = bpy.props.IntProperty(name='subd', default=0)
    relative = bpy.props.BoolProperty(name='relative', default=False)
    increase_subd = bpy.props.BoolProperty(name='increase_subd', default=False)

    multires_modifier = None
    active_object = None
    modifier_name = 'Multires'
    modifier_type = 'MULTIRES'

    def modal(self, context, event):
        pass

    def offset_subdivision(self):
        if self.multires_modifier.render_levels < self.multires_modifier.sculpt_levels + self.subd:
            if self.increase_subd:
                bpy.ops.object.multires_subdivide(modifier=self.multires_modifier.name)
        else:
            self.multires_modifier.sculpt_levels = self.multires_modifier.sculpt_levels + self.subd

        self.multires_modifier.levels = self.multires_modifier.levels + self.subd

    def set_subdivision(self):
        if self.multires_modifier.render_levels < self.subd:
            if self.increase_subd:
                for l in range(self.subd - self.multires_modifier.render_levels):
                    bpy.ops.object.multires_subdivide(modifier=self.multires_modifier.name)

        self.multires_modifier.sculpt_levels = self.subd
        self.multires_modifier.levels = self.subd

    def invoke(self, context, event):

        self.active_object = bpy.context.active_object

        if self.active_object is None:
            return {'CANCELLED'}

        self.multires_modifier = [m for m in self.active_object.modifiers if m.type == self.modifier_type]

        if not len(self.multires_modifier):
            self.multires_modifier = self.active_object.modifiers.new(name=self.modifier_name, type=self.modifier_type)
        else:
            self.multires_modifier = self.multires_modifier[0]

        if self.relative:
            self.offset_subdivision()
        else:
            self.set_subdivision()

        return {'FINISHED'}


classes = (
    TILA_multires_subdivision
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
