import bpy

class View3DPanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll(cls, context):
        if context.object is not None:
            return (context.object.name.split('.')[0] == 'Randomize Obj')
        else:
            return False

class RandomizeObjectProperties(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_RandomizeObjectProperties"
    bl_label = "Randomize Object Properties"

    def draw(self, context):
        scene = context.scene
        layout=self.layout
        randomize_obj = context.object
        if len(randomize_obj.name) > 15:
            ending = '.' + randomize_obj.name.split('.')[1]
        else:
            ending = ''

        col = layout.column()
        row = col.row()
        row.prop(randomize_obj.random_props, 'location_enabled', text='')
        row.label('Location:')
        col.prop(randomize_obj.random_props, 'location', text='')
        col.prop(randomize_obj.random_props, 'seed_location', text='Seed')
        row = col.row()
        row.operator('object.key_child_delta_location', text='Key Location')
        row.operator('object.delete_child_delta_location', text='', icon='X')
        col.separator()

        row = col.row()
        row.prop(randomize_obj.random_props, 'rotation_enabled', text='')
        row.label('Rotation:')
        col.prop(randomize_obj.random_props, 'rotation', text='')
        col.prop(randomize_obj.random_props, 'seed_rotation', text='Seed')
        row = col.row()
        row.operator('object.key_child_delta_rotation', text='Key Rotation')
        row.operator('object.delete_child_delta_rotation', text='', icon='X')
        col.separator()

        row = col.row()
        row.prop(randomize_obj.random_props, 'scale_enabled', text='')
        row.label('Scale:')
        if randomize_obj.random_props.uniform_scale_enabled:
            col.prop(randomize_obj.random_props, 'uniform_scale', text='')
        else:
            col.prop(randomize_obj.random_props, 'scale', text='')
        col.prop(randomize_obj.random_props, 'seed_scale', text='Seed')
        col.prop(randomize_obj.random_props, 'uniform_scale_enabled', text='Uniform Scale')
        row = col.row()
        row.operator('object.key_child_delta_scale', text='Key Scale')
        row.operator('object.delete_child_delta_scale', text='', icon='X')
        col.separator()

        # Child object tools
        col.label('Child Operations')
        box = col.box()
        box.operator('object.child_separate_loose', text='Separate Loose')
        box.operator('object.child_origin_to_geometry', text='Origin to Geometry')
        col.separator()

def register():
    #bpy.utils.register_module(__name__)
    bpy.utils.register_class(RandomizeObjectProperties)

def unregister():
    #bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(RandomizeObjectProperties)
