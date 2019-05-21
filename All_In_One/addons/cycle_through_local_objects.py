bl_info = {
  "name": "Cycle Through Objects",
  "author": "Sebastian Koenig",
  "version": (0, 0, 1),
  "blender": (2, 7, 2),
  "location": "3D View > Cycle Through Objects",
  "description": "Cycle through all objects while in Local View (a.k.a. Isolation Mode)",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "",
  "category": "3D View"
  }



import bpy

def view_local(context, ob):

    # if we are already in localview we should leave it first to select another object
    if context.space_data.local_view:
        bpy.ops.view3d.localview()

    # make sure nothing is selected and then pick next object
    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True

    # make it active and enter localview
    context.scene.objects.active = ob
    bpy.ops.view3d.localview()



def iterate(operator, context):
    # get the cycle direction from the property that got parsed to the class
    direction = operator.direction

    # filter out meshes
    meshes = []
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH" and ob.hide==False:
            meshes.append(ob)

    # iterate over objects
    for i, o in enumerate(meshes):
        if o == bpy.context.active_object:
            currentobject = o
           
            nextobject = meshes[(i + direction) % len(meshes)]
            context.scene.objects.active = nextobject

            # switch to localview with the next object
            view_local(context, nextobject)
            break


class VIEW3D_cycle_localview(bpy.types.Operator):
    bl_idname = "scene.cycle_localview"
    bl_label = "View Local"
    direction = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'VIEW_3D'

    def execute(self, context):
        if not context.object.mode=="OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        # if nothing is active localview doesn't make sense
        if not bpy.context.active_object:
            bpy.ops.view3d.localview()
            self.report({"INFO"}, "No active object, leaving local view")
        else:
            iterate(self, context)

        return {'FINISHED'}



########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_cycle_localview)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi = km.keymap_items.new('scene.cycle_localview', 'UP_ARROW', 'PRESS', alt=True)
    kmi.properties.direction = 1

    kmi = km.keymap_items.new('scene.cycle_localview', 'DOWN_ARROW', 'PRESS', alt=True)
    kmi.properties.direction = -1


def unregister():

    bpy.utils.unregister_class(VIEW3D_cycle_localview)

if __name__ == "__main__":
    register()