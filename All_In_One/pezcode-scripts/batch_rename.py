import bpy
import math
import functools
import operator

# TODO:
# - preview of changes
# - warn about selected objects that are not editable
#    - when are objects ever not editable?
# - warn about non-selected objects that would get renamed

class ObjectBatchRename(bpy.types.Operator):
    bl_idname = "object.batch_rename"
    bl_label = "Batch rename"
    bl_options = {'REGISTER', 'UNDO'}

    name_template = bpy.props.StringProperty(
        name="New name",
        description="New name of the objects\nNumbers get appended, so add any delimiters you want at the end:\n'Cube_' -> Cube_1, Cube_2, ...")

    start_num = bpy.props.IntProperty(
        name="Start counting at",
        description="Start counting and renaming from this number",
        default=1,
        min=0,
        max=100000) # reasonable(?) upper limit

    sort_mode = bpy.props.EnumProperty(
        items=[
            ('NONE',     "None",                 "Keep the order given by Blender (This is not the selection order! It's essentially random)"),
            ('COORD_X',  "X coordinate",         "Sort by increasing X coordinates"),
            ('COORD_Y',  "Y coordinate",         "Sort by increasing Y coordinates"),
            ('COORD_Z',  "Z coordinate",         "Sort by increasing Z coordinates"),
            ('DISTANCE', "Distance from center", "Sort by distance from the scene center"),
            ('SIZE',     "Size",                 "Sort by increasing volume of the bounding box"),
            ('RANDOM',   "Randomize",            "Shuffle order randomly")
        ],
        name="Sort by",
        description="Sort mode",
        default='NONE')

    reverse = bpy.props.BoolProperty(
        name="Reverse",
        description="Sort in reverse direction",
        default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len(context.selected_editable_objects) >= 2

    def invoke(self, context, event):
        active = context.active_object
        if active is not None:
            self.name_template = active.name
        else:
            self.name_template = context.selected_editable_objects[0]
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        objects = self.sort(context.selected_editable_objects)
        if self.reverse:
            objects.reverse()
        count = len(objects)
        for i in range(count):
            new_name = self.format_name(objects[i], self.start_num + i, count + self.start_num - 1)
            objects[i].name = new_name
        self.report({'INFO'}, "{0} items renamed".format(count))
        return {'FINISHED'}

    def sort(self, objects):
        keys = {
            'COORD_X':  lambda o: o.location.x,
            'COORD_Y':  lambda o: o.location.y,
            'COORD_Z':  lambda o: o.location.z,
            'DISTANCE': lambda o: sum([d ** 2 for d in o.location]) ** 0.5,
            'SIZE':     lambda o: functools.reduce(operator.mul, o.dimensions),
            'RANDOM':   lambda o: random.random()
        }
        if self.sort_mode == 'NONE':
            sorted_objects = objects
        else:
            sorted_objects = sorted(objects, key=keys[self.sort_mode])
        return sorted_objects

    def format_name(self, object, num, highest_num):
        padding = math.floor(math.log(highest_num, 10) + 1)
        formatstr = "{{0}}{{1:0>{0:.0f}}}".format(padding)
        name = formatstr.format(self.name_template, num)
        return name
