bl_info = {
    "name": "Parent to Empty",
    "author": "liero",
    "version": (0, 3, 2),
    "blender": (2, 5, 5),
    "api": 33333,
    "location": "View3D > Tool Shelf",
    "description": "Parent selected objects to a new Empty",
    "category": "Learnbgame",
}

import bpy
from bpy.props import StringProperty, BoolProperty

def centro(objetos):
    x = sum([obj.location[0] for obj in objetos])/len(objetos)
    y = sum([obj.location[1] for obj in objetos])/len(objetos)
    z = sum([obj.location[2] for obj in objetos])/len(objetos)
    return (x,y,z)

class P2E(bpy.types.Operator):
    bl_idname = 'object.parent_to_empty'
    bl_label = 'Parent to Empty'
    bl_description = 'Parent selected objects to a new Empty'
    bl_options = {'REGISTER', 'UNDO'}

    nombre = StringProperty(name='', default='OBJECTS', description='Give the empty / group a name')
    grupo = bpy.props.BoolProperty(name='Create Group', default=False, description='Also link objects to a new group')
    cursor = bpy.props.BoolProperty(name='Cursor Location', default=False, description='Add the empty at cursor / selection center')
    renombrar = bpy.props.BoolProperty(name='Rename Objects', default=False, description='Rename child objects')

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.select)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'nombre')
        column = layout.column(align=True)
        column.prop(self,'grupo')
        column.prop(self,'cursor')
        column.prop(self,'renombrar')

    def execute(self, context):
        objs = bpy.context.selected_objects
        bpy.ops.object.mode_set()
        if self.cursor:
            loc = context.scene.cursor_location
        else:
            loc = centro(objs)
        bpy.ops.object.add(type='EMPTY',location=loc)
        bpy.context.object.name = self.nombre
        if self.grupo:
            bpy.ops.group.create(name=self.nombre)
            bpy.ops.group.objects_add_active()
        for o in objs:
            o.select = True
            if not o.parent:
                    bpy.ops.object.parent_set(type='OBJECT')
            if self.grupo:
                bpy.ops.group.objects_add_active()
            o.select = False
        for o in objs:
            if self.renombrar:
                o.name = self.nombre+'_'+o.name
        return {'FINISHED'}

class PanelP2E(bpy.types.Panel):
    bl_label = 'Parent to Empty'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        layout.operator('object.parent_to_empty')

def register():
    bpy.utils.register_class(P2E)
    bpy.utils.register_class(PanelP2E)

def unregister():
    bpy.utils.unregister_class(P2E)
    bpy.utils.unregister_class(PanelP2E)

if __name__ == '__main__':
    register()