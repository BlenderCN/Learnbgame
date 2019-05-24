bl_info = {
    "name": "Ramp Object",
    "category": "Learnbgame",
}

import bpy
import bmesh
import math
import mathutils

class RampObject(bpy.types.Operator):
    """Ramp Object"""
    bl_idname = "object.ramp_object"
    bl_label = "Ramp Object"
    bl_options = {'REGISTER', 'UNDO'}

    rampHeight = bpy.props.IntProperty(name="Height", default=2, min=1, max=100)
    rampWidth = bpy.props.IntProperty(name="Width", default=4, min=1, max=100)
    rampMaxInclination = bpy.props.FloatProperty(name="Inclination", default=60.0, min=1.0, max=89.0)
    # curveVerticalOffsetScale = bpy.props.FloatProperty(name="Offset Scale", default=0.05, min=0.0, max=0.5)
    curveVerticalOffsetScale = 0.0
    rampLength = bpy.props.IntProperty(name="Length", default=4, min=1, max=100)


    def execute(self, context):
        # print('\n------Script Start------\n')
        scene = context.scene
        cursor = scene.cursor_location

        # print('create ramp curve...')
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
        rampCurveObject = context.object

        # print('lengthen ramp curve...')
        bpy.ops.transform.resize(value=[self.rampLength/2, 0, 0])

        # print('select first segment...')
        bpy.ops.curve.select_all(action='DESELECT')
        bpy.ops.curve.de_select_first()

        # print('straighten and pull up...')
        bpy.ops.transform.rotate(value=math.radians(-45), axis=[0, 0, 1])
        bpy.ops.transform.resize(value=[2 * (10/7), 0, 0])
        bpy.ops.transform.rotate(value=math.radians(self.rampMaxInclination), axis=[0, 1, 0])
        bpy.ops.transform.translate(value=[0, 0, self.rampHeight * (1 + self.curveVerticalOffsetScale) / 2 ])

        # print('select second segment...')
        bpy.ops.curve.select_all(action='DESELECT')
        bpy.ops.curve.de_select_last()

        # print('pull down...')
        bpy.ops.transform.translate(value=[0, 0, -self.rampHeight * (1 + self.curveVerticalOffsetScale) / 2])

        # print('enter object mode...')
        bpy.ops.object.mode_set(mode='OBJECT')

        # print('create plane to be cut...')
        bpy.ops.mesh.primitive_plane_add();
        rampPlaneToCutObject = context.object

        # print('transform plane...')
        bpy.ops.transform.rotate(value=math.radians(90), axis=[1, 0, 0])
        bpy.ops.transform.resize(value=[self.rampLength/2, 0, self.rampHeight/2])
        bpy.ops.transform.translate(value=[0, -self.rampWidth/2, 0])

        # print('select curve then cube...')
        rampCurveObject.select = True
        rampPlaneToCutObject.select = True

        # print('enter edit mode...')
        bpy.ops.object.mode_set(mode='EDIT')

        # print('cut plane via knife project...')
        # get reference to SpaceView3D object
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                break
        for region in area.regions:
            if region.type == "WINDOW":
                break
        space = area.spaces[0]
        oldViewPerspective = space.region_3d.view_perspective
        oldViewMatrix = space.region_3d.view_matrix.copy()
        # set view to FRONT, ORHTOGRAPHIC
        space.region_3d.view_perspective = 'ORTHO'
        space.region_3d.view_rotation = mathutils.Euler((math.radians(90.0), 0.0, 0.0)).to_quaternion()
        space.region_3d.update()
        # call knife_project() with custom context
        myContext = context.copy()
        myContext['area'] = area
        myContext['region'] = region
        myContext['space_data'] = space
        bpy.ops.mesh.knife_project(myContext)
        # cleanup
        space.region_3d.view_matrix = oldViewMatrix
        space.region_3d.view_perspective = oldViewPerspective
        space.region_3d.update()

        # print('select larger face of plane...')
        bpy.ops.mesh.select_mode(type='FACE')
        planeBm = bmesh.from_edit_mesh(rampPlaneToCutObject.data)
        highArea = 0
        highIndex = -1
        for index, ele in enumerate(planeBm.faces):
            ele.select = False
            area = ele.calc_area()
            if(area > highArea):
                highArea = area
                highIndex = index
        planeBm.faces.ensure_lookup_table()
        planeBm.faces[highIndex].select = True
        planeBm.select_flush(True)
        bpy.ops.mesh.delete(type='FACE')
        # TODO: fix bug when adjusting height quickly: 
        # Traceback (most recent call last):
        #     File "D:\Documents\Blender\RampTests\RampTests2.blend\RampCreator.py", line 113, in execute
        #         planeBm.faces.ensure_lookup_table()
        # IndexError: BMElemSeq[index]: index 0 out of range
        planeBm.faces.ensure_lookup_table()
        rampFace = planeBm.faces[0]
        rampFace.select = True

        # print('remove curve...')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        rampCurveObject.select = True
        bpy.ops.object.delete()
        rampPlaneToCutObject.select = True
        bpy.ops.object.mode_set(mode='EDIT')

        # print('extrude plane along y...')
        # bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={'value':(0, self.rampWidth, 0)})
        bpy.ops.object.mode_set(mode='OBJECT')

        # print('\n------Script End------')
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(RampObject.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(RampObject)
    # bpy.types.INFO_MT_add.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either, so we have to check this
    # to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(RampObject.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
        # kmi.properties.total = 4
        addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap 
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(RampObject)
    # bpy.types.INFO_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()