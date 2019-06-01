bl_info = {
    "name": "Camswitch",
    "author": "nikitron.cc.ua",
    "version": (0, 0, 1),
    "blender": (2, 7, 9),
    "location": "View3D > Tool Shelf > 1D > camswitch",
    "description": "switch cameras",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy

class D1_camswitch(bpy.types.Operator):
    ''' \
    Следующая и предыдущая камера в сцене. \
    next & previous camera in ther scene. \
    '''
    bl_idname = "camera.camswitch"
    bl_label = "Camswitch"

    next = bpy.props.BoolProperty(name='next', default=True)

    def execute(self, context):
        cams = [k for k in bpy.data.objects if k.type=='CAMERA']
        print(cams)
        active = bpy.data.scenes[bpy.context.scene.name].camera
        for i,k in enumerate(cams):
            if self.next:
                if k == active and i < (len(cams)-1):
                    bpy.data.scenes[bpy.context.scene.name].camera = bpy.data.objects[cams[i+1].name]
                    break
                elif k == active:
                    bpy.data.scenes[bpy.context.scene.name].camera = bpy.data.objects[cams[0].name]
                    break
            else:
                if k == active and i > 0:
                    bpy.data.scenes[bpy.context.scene.name].camera = bpy.data.objects[cams[i-1].name]
                    break
                elif k == active:
                    bpy.data.scenes[bpy.context.scene.name].camera = bpy.data.objects[cams[-1].name]
                    break
        return {'FINISHED'}

class D1_camswitch_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Camswitch"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = '1D'
    

    def draw(self, context):
        ''' \
        Следукющая активная камера \
        Next active camera \
        '''
        layout = self.layout
        row = layout.row(align=True)
        row.operator('camera.camswitch', text='Prev',icon='TRIA_LEFT').next=False
        row.operator('camera.camswitch', text='Next',icon='TRIA_RIGHT').next=True

def register():
    bpy.utils.register_class(D1_camswitch)
    bpy.utils.register_class(D1_camswitch_panel)

def unregister():
    bpy.utils.unregister_class(D1_camswitch_panel)
    bpy.utils.unregister_class(D1_camswitch)
    

if __name__ == "__main__":
    register()
