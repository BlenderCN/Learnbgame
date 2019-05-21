bl_info = {
    "name": "Improved Origin Pie",
    "author": "Martynas Žiemys",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "alt+ctrl+shift+c",
    "description": "Improved Origin Pie Menu",
    "warning": "Might brake undo functionality when used from edit mode.",
    "category": "Pie Menus",
    }

import bpy
import mathutils
from mathutils import Matrix as M


################################## Functions ##################################


def AlignOriginLocation(obj, piv): 
    if obj.data is not None:     
        trans_v = (
            (obj.matrix_world.inverted() * piv.matrix_world).to_translation()
            )
        trans = M.Translation(-trans_v)   
        obj.data.transform(trans)
        obj.location = piv.location - obj.delta_location
        
                
def AlignOriginRotation(obj, piv):   
    if obj.data is not None:
        rot = (
            obj.matrix_world.to_quaternion().inverted()
            * piv.matrix_world.to_quaternion()
            ).inverted().to_matrix().to_4x4()
        obj.data.transform(rot)
        
        if len(piv.rotation_mode) < 4:
            obj.rotation_euler = piv.rotation_euler
        elif obj.rotation_mode == 'QUATERNION':
            obj.rotation_quaternion = piv.rotation_quaternion
        else:
            obj.rotation_axis_angle = piv.rotation_axis_angle


def MatchOriginScale(obj, piv):
    if obj.data is not None:
        scale = piv.scale.copy()
        scale.x /= obj.scale.x
        scale.y /= obj.scale.y
        scale.z /= obj.scale.z
        scale_m = M.Scale(scale.x,4,(1,0,0))
        scale_m *= M.Scale(scale.y,4,(0,1,0))
        scale_m *= M.Scale(scale.z,4,(0,0,1))
        scale_m.invert()
        obj.data.transform(scale_m)
        obj.scale = piv.scale


def CopyOrigin(obj,piv):
    AlignOriginLocation(obj, piv)
    AlignOriginRotation(obj, piv)
    MatchOriginScale(obj, piv)


################################## Operators ##################################

class MZTransformOrientationToRotation(bpy.types.Operator):
    bl_idname = "object.mz_trans_orient_to_rot"
    bl_label = "Align Origin to Active Transform orientation"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        poll = False
        for every_area in bpy.context.screen.areas:
            if every_area.type == 'VIEW_3D':
                name = every_area.spaces.active.transform_orientation
                default_orientations = {
                    'GLOBAL',
                    'LOCAL',
                    'NORMAL',
                    'GIMBAL',
                    'VIEW'
                }
                if name not in default_orientations:
                    poll = True
                
        return context.object and context.object.data and poll
    
    def execute(self, context):
        original_mode = context.object.mode
        bpy.ops.object.mode_set(mode = 'OBJECT')
        the_object = bpy.context.scene.objects.active
        selection = list()
        if len(context.selected_objects):
            for obj in context.selected_objects:
                selection.append(obj)
        for every_area in bpy.context.screen.areas:
            if every_area.type == 'VIEW_3D':
                name = every_area.spaces.active.transform_orientation
                transform_orientation = bpy.context.scene.orientations[name]
        for obj in selection:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            pivot_empty_name = "Origin of " + obj.name
            tempPivot = bpy.data.objects.new(pivot_empty_name, None)
            tempPivot.matrix_world = transform_orientation.matrix.to_4x4()
            bpy.context.scene.objects.link(tempPivot)
            AlignOriginRotation(obj,tempPivot)
            bpy.ops.object.select_all(action='DESELECT')
            tempPivot.select = True
            bpy.ops.object.delete()
        # Clean up 
        bpy.ops.object.select_all(action='DESELECT')
        if selection:
            for obj in selection:
                obj.select = True
            bpy.context.scene.objects.active = the_object
        bpy.ops.object.mode_set(mode = original_mode) 
        return {'FINISHED'}
    
class MZOriginToSelected(bpy.types.Operator):
    bl_idname = "object.mz_origin_to_selected"
    bl_label = "Origin to Selection"
    bl_options = {'REGISTER','UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data
    
    def execute(self, context):
        toggleMode = False
        cur_loc = bpy.context.scene.cursor_location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()
        if context.object.mode != 'OBJECT':
            toggleMode = True
            original_mode = context.object.mode
            bpy.ops.object.mode_set(mode = 'OBJECT')        
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')    
        if toggleMode == True:
            bpy.ops.object.mode_set(mode = original_mode)
            toggleMode = False   
        bpy.context.scene.cursor_location = cur_loc
        return {'FINISHED'}

class MZOriginToCursorEditMode(bpy.types.Operator):
    bl_idname = "object.mz_origin_to_cursor"
    bl_label = "Origin to 3d Cursor"

    @classmethod
    def poll(cls, context):
        return context.object.data

    def execute(self, context):
        original_mode = context.object.mode
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.object.mode_set(mode = original_mode)
        return {'FINISHED'}


class MZOriginToGeometryCenterEditMode(bpy.types.Operator):
    bl_idname = "object.mz_origin_to_center_em"
    bl_label = "Origin to Center of Mass mz"

    @classmethod
    def poll(cls, context):
        condition = (
                context.object.data
                and context.object.mode != 'OBJECT'
            )
        return condition

    def execute(self, context):
        original_mode = context.object.mode
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.origin_set(
                type='ORIGIN_GEOMETRY',
                center='BOUNDS'
            )
        bpy.ops.object.mode_set(mode = original_mode)
        return {'FINISHED'}


class MZOriginToBottomEditMode(bpy.types.Operator):
    bl_idname = "object.mz_origin_to_bottom_em"
    bl_label = "Origin to Bottom"
    operation = bpy.props.EnumProperty(
                    name="Origin to:",
                    items=(
                        ('BOTTOM', "Bottom", ""),
                        ('TOP', "Top", "")
                    ),
                    default='BOTTOM'
                )
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data

    def execute(self, context):
        bpy.ops.object.mz_origin_to_bottom(
                operation = self.operation,
                center = True
            )
        return {'FINISHED'}
        
    
class MZOriginToBottom(bpy.types.Operator):
    bl_idname = "object.mz_origin_to_bottom"
    bl_label = "Origin to Bottom (+)"
    bl_options = {'REGISTER','UNDO'}
    center = bpy.props.BoolProperty(
                name = 'Center as well',
                description = 'Center origin in the other two axis '
                             +'in addition to moving it in the one',
                default = True
            )
    operation = bpy.props.EnumProperty(
                    name="Origin to:",
                    items=(
                        ('BOTTOM', "Bottom", ""),
                        ('TOP', "Top", ""),
                        ('X', "X", ""),
                        ('-X', "-X", ""),
                        ('Y', "Y", ""),
                        ('-Y', "-Y", "")
                    ),
                    default='BOTTOM'
                )

    @classmethod
    def poll(cls, context):
        return context.object and context.object.data
    
    def execute(self, context):
        original_mode = context.object.mode
        bpy.ops.object.mode_set(mode = 'OBJECT')
        the_object = bpy.context.scene.objects.active
        selection = list()
        if len(context.selected_objects):
            for obj in context.selected_objects:
                selection.append(obj)
        for obj in selection:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            if self.center:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN') 
            pivot_empty_name = "Origin of " + obj.name
            tempPivot = bpy.data.objects.new(pivot_empty_name, None)
            tempPivot.matrix_world = bpy.context.scene.objects.active.matrix_world
            bpy.context.scene.objects.link(tempPivot)
            tempPivot.select = True
            if self.operation == 'BOTTOM':
                direction = 'OPT_1'
                axis = 'Z'
            elif self.operation == 'TOP':
                direction = 'OPT_3'
                axis = 'Z'
            elif self.operation == 'X':
                direction = 'OPT_3'
                axis = 'X'
            elif self.operation == '-X':
                direction = 'OPT_1'
                axis = 'X'
            elif self.operation == 'Y':
                direction = 'OPT_3'
                axis = 'Y'
            elif self.operation == '-Y':
                direction = 'OPT_1'
                axis = 'Y'
            bpy.ops.object.align(
                bb_quality=True,
                align_mode=direction,
                relative_to='OPT_4',
                align_axis={axis}
            )
            AlignOriginLocation(obj,tempPivot)
            bpy.ops.object.select_all(action='DESELECT')
            tempPivot.select = True
            bpy.ops.object.delete()
        # Clean up 
        bpy.ops.object.select_all(action='DESELECT')
        if selection:
            for obj in selection:
                obj.select = True
            bpy.context.scene.objects.active = the_object
        bpy.ops.object.mode_set(mode = original_mode) 
        return {'FINISHED'}


class MZOriginTransform(bpy.types.Operator):
    bl_idname = "object.mz_origin_transform"
    bl_label = "Transform Origin" 
    bl_options = {'REGISTER','UNDO'}
    operation = bpy.props.EnumProperty(
                    items=(
                        ('GRAB', "GRAB", ""),
                        ('ROTATE', "ROTATE", ""),
                        ('SCALE', "SCALE", "")
                    ),
                    default='GRAB'
                )
    start = 0
    selection = list()

    @classmethod
    def poll(cls, context):
        return context.object and context.object.data

    def modal(self, context, event):
        def cleanup():
            bpy.ops.object.delete()
            if self.selection:
                for obj in self.selection:
                    obj.select = True
            bpy.context.scene.objects.active = the_object
            bpy.ops.object.mode_set(mode = self.original_mode) 
        self.start += 1
        the_object = bpy.data.objects[self.object_name]       
        if self.start == 1:
            if self.operation == 'ROTATE':
                bpy.ops.transform.rotate('INVOKE_DEFAULT')
            elif self.operation == 'GRAB':
                bpy.ops.transform.transform('INVOKE_DEFAULT')
            elif self.operation == 'SCALE':
                bpy.ops.transform.resize('INVOKE_DEFAULT')
        if event.type in {'RET', 'NUMPAD_ENTER', 'LEFTMOUSE'}:
            CopyOrigin(the_object, bpy.context.scene.objects.active)    
            cleanup()
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC', 'SPACE'}:
            cleanup()
            self.report({'INFO'}, 'Cancelled')
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.original_mode = context.object.mode
        self.object_name = context.active_object.name
        bpy.ops.object.mode_set(mode = 'OBJECT')
        if len(context.selected_objects):
            for objs in context.selected_objects:
                self.selection.append(objs)
            bpy.ops.object.select_all(action='DESELECT')
        pivot_empty_name = "Origin of " + self.object_name
        tempPivot = bpy.data.objects.new(pivot_empty_name, None)
        tempPivot.show_x_ray = 1
        tempPivot.show_axis = 1

        # Place temp empty at the center of the object
        # and match rotation and scale:
        tempPivot.matrix_world = bpy.context.scene.objects.active.matrix_world
        bpy.context.scene.objects.link(tempPivot)

        # To add the empty to local view we need to go out of local view,
        # add the empty to selection and come back to local view,
        # viewport position needs to be saved and restored as well.
        #
        # The following code messes up windows with different local
        # views. This doesn't bother me, but if you know a way to
        # avoid this, please let me know martynasziemys@gmail.com
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces[0]
                if space.local_view:
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region}
                            view_matrix = space.region_3d.view_matrix.copy()
                            bpy.ops.view3d.localview(override)
                            tempPivot.select = True
                            bpy.ops.view3d.localview(override)
                            space.region_3d.view_matrix = view_matrix
        bpy.ops.object.select_all(action='DESELECT')
        tempPivot.select = True
        bpy.context.scene.objects.active = tempPivot
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class MZCopyOrigin(bpy.types.Operator):
    bl_idname = "object.mz_copy_origin"
    bl_label = "Copy Origin From Active to Selected"
    bl_options = {"REGISTER", "UNDO"}
    Pos = bpy.props.BoolProperty(
        name = "Location",
        description = "Copy origin's location from active to selected objects",
        default = True
    )
    Rot = bpy.props.BoolProperty(
        name = "Rotation",
        description = "Copy origin's rotation from active to selected objects",
        default = True
    )
    Sca = bpy.props.BoolProperty(
        name = "Scale",
        description = "Copy origin's scale from active to selected objects",
        default = True
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        active_object = bpy.context.active_object
        for every_obj in bpy.context.selected_objects:
            if every_obj != active_object:
                if self.Pos == True:
                    AlignOriginLocation(every_obj, active_object)
                if self.Rot == True:
                    AlignOriginRotation(every_obj, active_object)
                if self.Sca == True:
                    MatchOriginScale(every_obj, active_object) 
        return {'FINISHED'}


###################################### UI #####################################


class MZOriginPieMenu(bpy.types.Menu):
    bl_idname = "origin.mz_origin_menu"
    bl_label = "Origin"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        if context.object:
            
            pie.operator(
                    'object.mz_origin_transform',
                    text = 'Transform origin ( G | R | S )',
                    icon = 'MANIPUL'
                    )
            pie.operator(
                    'object.mz_origin_to_cursor',
                    text = 'Origin to 3D Cursor',
                    icon='CURSOR'
                )
            if context.object.mode == 'OBJECT': 
                # OBJECT MODE
                pie.operator(
                        'object.mz_origin_to_bottom',
                        text = 'Origin to Bottom',
                        icon = 'TRIA_DOWN'
                    ).operation = 'BOTTOM'
                pie.operator(
                        'object.mz_origin_to_bottom',
                        text = 'Origin to Top',
                        icon = 'TRIA_UP'
                    ).operation = 'TOP'
                pie.operator(
                        "object.origin_set",
                        text="Origin to Center",
                        icon='ROTATE'
                    ).type = 'ORIGIN_GEOMETRY'               

                pie.operator(
                        'object.mz_copy_origin',
                        text = 'Copy Origin (Active to Selected)',
                        icon='EXPORT'
                    )
            else: 
                # EDIT MODE
                pie.operator(
                        'object.mz_origin_to_bottom_em',
                        text = 'Origin to Bottom',
                        icon = 'TRIA_DOWN'
                    ).operation = 'BOTTOM'
                pie.operator(
                        'object.mz_origin_to_bottom_em',
                        text = 'Origin to Top',
                        icon = 'TRIA_UP'
                    ).operation = 'TOP'
                pie.operator(
                        'object.mz_origin_to_center_em',
                        text = 'Origin to Center of Bounds',
                        icon='ROTATE'
                    )
                pie.operator(
                        'object.mz_origin_to_selected',
                        text = 'Origin to Selected',
                        icon = 'UV_SYNC_SELECT'
                    )
            pie.operator("object.origin_set", text="Geometry to Origin",
                    icon='BBOX').type = 'GEOMETRY_ORIGIN'
            pie.operator(
                    'object.mz_trans_orient_to_rot',
                    text = 'Align Origin to Active Transform Orientation',
                    icon = 'MAN_ROT'
                    )                


################################# Registration ################################


classes = (
    MZCopyOrigin,
    MZOriginTransform,
    MZOriginToBottom,
    MZOriginToBottomEditMode,
    MZOriginToCursorEditMode,
    MZOriginPieMenu,
    MZOriginToGeometryCenterEditMode,
    MZOriginToSelected,
    MZTransformOrientationToRotation
)
addon_keymaps = []
def registerKeymaps():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS', shift=True, alt=True,ctrl=True)
        kmi.properties.name = "origin.mz_origin_menu"
        addon_keymaps.append((km, kmi))


def unregisterKeymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def deactivateConflictingKeymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs['Blender User']
    possibleConflicts = {
            'Object Non-modal',
            '3D View Generic',
            '3D View',
            'Object Mode',
            'Window'
        }
    for km in kc.keymaps:
        if km.name in possibleConflicts:
            for kmi in km.keymap_items:
                condition = (
                        kmi.type == 'C'
                        and kmi.shift
                        and kmi.ctrl
                        and kmi.alt
                    )
                if condition:
                    kmi.active = False
 
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    registerKeymaps()
    deactivateConflictingKeymaps()


def unregister():
    unregisterKeymaps()
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
        
if __name__ == "__main__":
    register()