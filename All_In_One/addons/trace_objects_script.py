#################################################################
# join selected objects with a curve + hooks to each node v 0.3 #
#################################################################

bl_info = {
    "name": "Connect Objects",
    "author": "liero",
    "version": (0, 3),
    "blender": (2, 6, 1),
    "location": "View3D > Tool Shelf",
    "description": "Connect selected objects with a curve + hooks",
    "category": "Learnbgame",
}

import bpy

bpy.types.WindowManager.modo = bpy.props.EnumProperty( name="", items=[('FREE','Free',''),('VECTOR','Vector',''),('ALIGNED','Aligned',''),('AUTO','Auto','')], description='Spline Type for the bezier points', default='VECTOR')

class TraceObjs(bpy.types.Operator):
    bl_idname = 'objects.trace'
    bl_label = 'Connect'
    bl_description = 'Connect selected objects with a curve + hooks'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (len(bpy.context.selected_objects) > 1)

    def execute(self, context):
        # list objects
        lista = []
        sce = bpy.context.scene
        wm = bpy.context.window_manager
        for a in bpy.context.selected_objects:
            lista.append(a)
            a.select = False

        # trace the origins
        tracer = bpy.data.curves.new('tracer','CURVE')
        spline = tracer.splines.new('BEZIER')
        spline.bezier_points.add(len(lista)-1)
        curva = bpy.data.objects.new('curva',tracer)
        bpy.context.scene.objects.link(curva)

        # make the curve visible
        tracer.dimensions = '3D'
        tracer.resolution_u = 64
        tracer.bevel_resolution = 1
        tracer.fill_mode = 'FULL'
        tracer.bevel_depth = 0.025

        # curve material
        if 'mat' not in bpy.data.materials:
            mat = bpy.data.materials.new('mat')
            mat.diffuse_color = [0,.5,1]
            mat.use_shadeless = True
        tracer.materials.append(bpy.data.materials.get('mat'))

        # move nodes to objects
        for i in range(len(lista)):
            p = spline.bezier_points[i]
            p.co = lista[i].location
            p.handle_right_type=wm.modo
            p.handle_left_type=wm.modo

        sce.objects.active = curva
        bpy.ops.object.mode_set()

        # place hooks
        for i in range(len(lista)):
            lista[i].select = True
            curva.data.splines[0].bezier_points[i].select_control_point = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.hook_add_selob()
            bpy.ops.object.editmode_toggle()
            curva.data.splines[0].bezier_points[i].select_control_point = False
            lista[i].select = False

        for a in lista:
            a.select = True
        return{'FINISHED'}

class PanelCO(bpy.types.Panel):
    bl_label = 'Connect Objects'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        obj = bpy.context.object
        layout = self.layout
        column = layout.column()
        column.operator('objects.trace')
        column.prop(context.window_manager, 'modo')
        if obj.type == 'CURVE':
            column = layout.column(align=True)
            column.label(text='Active curve settings:')
            column.prop(obj.data, 'bevel_depth')
            column.prop(obj.data, 'bevel_resolution')
            column.prop(obj.data, 'resolution_u')

def register():
    bpy.utils.register_class(TraceObjs)
    bpy.utils.register_class(PanelCO)

def unregister():
    bpy.utils.unregister_class(TraceObjs)
    bpy.utils.unregister_class(PanelCO)

if __name__ == '__main__':
    register()
