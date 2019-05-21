'''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''

# blender info
bl_info = {
    'name': 'Armature Panel',
    'author': 'Trentin Frederick (proxe)',
    'version': (0, 1, 0),
    'blender': (2, 60, 0),
    'location': '3D View \N{Rightwards Arrow} Properties Panel \N{Rightwards Arrow} Armature',
    'description': 'Custom bone shape alignment and shortcut panel.',
    'tracker_url': 'https://github.com/trentinfrederick/armature-data-panel/issues',
    'category': 'Rigging'
}

# Imports
import bpy
from bpy.types import Operator
from mathutils import Matrix
from bpy.types import PropertyGroup, Panel
from bpy.props import *

# custom shape to bone
class POSE_OT_custom_shape_to_bone(Operator):
    '''
        Align currently assigned custom bone shape on a visible scene layer to active pose bone.
    '''
    bl_idname = 'pose.custom_shape_to_bone'
    bl_label = 'Align to Bone'
    bl_description = 'Align currently assigned custom bone shape on a visible scene layer to this bone.'
    bl_options = {'REGISTER', 'UNDO'}

    # show wire
    showWire = BoolProperty(
        name='Draw Wire',
        description='Turn on the bones draw wire option when the shape is aligned to the bone (Bone is always drawn as a wire-frame regardless of the view-port draw mode.)',
        default=False
    )

    # wire draw type
    wireDrawType = BoolProperty(
        name='Wire Draw Type',
        description='Change the custom shape object draw type to wire, when the shape is aligned to the bone.',
        default=False
    )

    # name custom shape
    nameCustomShape = BoolProperty(
        name='Auto-Name',
        description='Automatically name and prefix the custom shape based on the bone it is assigned to.',
        default=False
    )

    # prefix shape name
    prefixShapeName = StringProperty(
        name='Prefix',
        description='Use this prefix when naming a custom bone shape. (Erase if you do not wish to prefix the name.)',
        default='WGT-'
    )

    # prefix shape data name
    prefixShapeDataName = BoolProperty(
        name='Prefix Shape Data Name',
        description='Prefix the custom shape\'s object data name in addition to prefixing the custom shapes name.',
        default=False
    )

    # add armature name
    addArmatureName = BoolProperty(
        name='Include Armature Name',
        description='Include the armature name when renaming the custom shape.',
        default=False
    )

    # separate name
    separateName = StringProperty(
        name='Separator',
        description='Separate the name of the armature and the name of the bone with this character.',
        default='_'
    )

    # poll
    @classmethod
    def poll(cls, context):
        '''
            Must have an active bone selected and be in pose mode.
        '''
        return context.active_bone
        return context.mode in 'POSE'

    # draw
    def draw(self, context):
        '''
            The operator options.
        '''

        # layout
        layout = self.layout

        # column
        column = layout.column()

        # show wire
        column.prop(self, 'showWire', text='Wireframe')

        # wire draw type
        column.prop(self, 'wireDrawType')

        # separater
        column.separator()

        # name custom shape
        column.prop(self, 'nameCustomShape', text='Auto Name')

        # prefix shape name
        column.prop(self, 'prefixShapeName')

        # add armature name
        column.prop(self, 'addArmatureName')

        # separate name
        column.prop(self, 'separateName')

    # main
    def main(self, context, armature, active, pose):
        '''
            Operator main function.
        '''

        # custom shape transform
        if pose.custom_shape_transform:

            # target matrix
            targetMatrix = armature.matrix_world * pose.custom_shape_transform.matrix

        # custom shape transform
        else:

            # target matrix
            targetMatrix = armature.matrix_world * active.matrix_local

        # location
        pose.custom_shape.location = targetMatrix.to_translation()

        # rotation mode
        pose.custom_shape.rotation_mode = 'XYZ'

        # rotation euler
        pose.custom_shape.rotation_euler = targetMatrix.to_euler()

        # target scale
        targetScale = targetMatrix.to_scale()

        # scale average
        scaleAverage = (targetScale[0] + targetScale[1] + targetScale[2]) / 3

        # scale
        pose.custom_shape.scale = ((active.length * scaleAverage), (active.length * scaleAverage), (active.length * scaleAverage))

        # show wire
        if self.showWire:
            active.show_wire = True

        # wire draw type
        if self.wireDrawType:
            pose.custom_shape.draw_type = 'WIRE'

        # name custom shape
        if self.nameCustomShape:
            pose.custom_shape.name = pose.name

            # add armature name
            if self.addArmatureName:
             pose.custom_shape.name = armature.name + self.separateName + pose.custom_shape.name

            # assign name
            pose.custom_shape.name = self.prefixShapeName + pose.custom_shape.name

            # prefix shape data name
            if self.prefixShapeDataName:
                pose.custom_shape.data.name = self.prefixShapeName + pose.custom_shape.name

            # prefix shape data name
            else:
                pose.custom_shape.data.name = pose.custom_shape.name

    # execute
    def execute(self, context):
        '''
            Execute the operator.
        '''

        # do nothing

        return {'FINISHED'}


    def invoke(self, context, event):
        '''
            Invoke the operator
        '''

        if event.alt:
            for bone in context.selected_pose_bones:
                try:
                    self.main(context, context.active_object, context.active_object.data.bones[bone.name], bone)
                except:
                    print('The bone \'' + bone.name + '\' did not have an assigned custom shape.')

        else:
            try:
                self.main(context, context.active_object, context.active_bone, context.active_pose_bone)
            except:
                self.report({'INFO'}, 'Must assign a custom shape.')

        return self.execute(context)

# armature data property group
class armatureData(PropertyGroup):
    '''
        Armature Data Panel property group
    '''

    # display mode
    displayMode = BoolProperty(
        name = 'Display Mode',
        description = 'Use this to hide many of the options below that are generally needed while rigging. (Useful for animating.)',
        default=False
    )

    # deform options
    deformOptions = BoolProperty(
        name = 'Deform Options',
        description = 'Display the deform options for this bone.',
        default = False
    )

# armature data
class VIEW3D_PT_armature_data(Panel):    # TODO: Account for linked armatures.
    '''
        Armature data panel.
    '''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Armature'

    # poll
    @classmethod
    def poll(cls, context):
        '''
            Must be in either pose mode or armature edit mode.
        '''

        # context mode in pose or edit
        return context.mode in {'POSE', 'EDIT_ARMATURE'} and context.active_bone

    # draw header
    def draw_header(self, context):
        '''
            Armature data panel header.
        '''

        # layout
        layout = self.layout

        # armature data ui props
        armatureDataUIProps = context.window_manager.armatureDataUI

        # display mode
        layout.prop(armatureDataUIProps, 'displayMode', text='')

    # draw
    def draw(self, context):
        '''
            Armature data panel body.
        '''

        # layout
        layout = self.layout

        # column
        column = layout.column(align=True)

        # armature data
        armatureData = context.window_manager.armatureDataUI

        # active armature
        activeArmature = context.active_object

        # active bone
        activeBone = context.active_bone

        # pose mode
        if context.mode in 'POSE':

            # active pose bone
            activePoseBone = activeArmature.data.bones[activeBone.name]

            # row
            row = column.row(align=True)

            # pose position
            row.prop(activeArmature.data, 'pose_position', expand=True)

            # column
            column = layout.column(align=True)

        else:
            activePoseBone = activeArmature.data.edit_bones[activeBone.name]

        # label
        column.label(text='Layers:')

        # separator
        column.separator()

        # layers
        column.prop(activeArmature.data, 'layers', text='')

        # not display mode
        if not armatureData.displayMode:

            # separator
            column.separator()

            # layers
            column.prop(activeBone, 'layers', text='')

        # separator
        column.separator()

        # label
        column.label(text='Display:')

        # separator
        column.separator()

        # row
        row = column.row(align=True)

        # label
        # row.label(icon='BLANK1')

        # draw type
        row.prop(activeArmature.data, 'draw_type', text='')

        # row
        row = column.row(align=True)

        # show names
        row.prop(activeArmature.data, 'show_names', text='Names', toggle=True)

        # show group colors
        row.prop(activeArmature.data, 'show_group_colors', text='Colors', toggle=True)

        # row
        row = column.row(align=True)

        # show axes
        row.prop(activeArmature.data, 'show_axes', text='Axes', toggle=True)

        # show x-ray
        row.prop(activeArmature, 'show_x_ray', text='X-Ray', toggle=True)

        # pose mode
        if context.mode in 'POSE':

            # row
            row = column.row(align=True)

            # scale
            row.scale_y = 1.25

            # show bone custom shapes
            row.prop(activeArmature.data, 'show_bone_custom_shapes', text='Shapes', toggle=True)

            # row
            row = column.row(align=True)

            # scale
            row.scale_y = 1.25

            # use deform layer
            row.prop(activeArmature.data, 'use_deform_delay', text='Delay Refresh', toggle=True)

        # not display mode
        if not armatureData.displayMode:

            # column
            column = layout.column(align=True)

            # label
            column.label(text='Relations:')

            # row
            row = column.row()

            # separator
            row.separator()

            # row
            row = column.row(align=True)

            # label
            # row.label(icon='BLANK1')

            # parent
            row.prop_search(activeBone, 'parent', activeArmature.data, 'edit_bones', text='')

            # edit mode
            if context.mode in 'EDIT_ARMATURE':

                # row
                row = column.row(align=True)

                # use connect
                row.prop(activeBone, 'use_connect', toggle=True)

                # row
                row = column.row(align=True)

                # use local location
                row.prop(activeBone, 'use_local_location', text='Loc', toggle=True)

                # use inherit rotation
                row.prop(activeBone, 'use_inherit_rotation', text='Rot', toggle=True)

                # use inherit scale
                row.prop(activeBone, 'use_inherit_scale', text='Scale', toggle=True)

            # pose mode
            if context.mode in 'POSE':

                # row
                row = column.row(align=True)

                # bone group search
                row.prop_search(bpy.data.objects[activeArmature.name].pose.bones[activePoseBone.name], 'bone_group', activeArmature.pose, 'bone_groups', text='')

            # column
            column = layout.column(align=True)

            # row
            row = column.row(align=True)

            # scale
            row.scale_y = 1.25

            # sub
            sub = row.row(align=True)

            # scale
            sub.scale_y = 1.25
            sub.scale_x = 1.5

            # deform options
            sub.prop(armatureData, 'deformOptions', text='', icon='RADIOBUT_ON' if armatureData.deformOptions else 'RADIOBUT_OFF')

            # use deform
            row.prop(activeBone, 'use_deform', text='Deform:', toggle=True)

            # deform options
            if armatureData.deformOptions:

                # box
                box = layout.column(align=True).box().column(align=True)

                # active
                box.active = activeBone.use_deform

                # box
                box = box.column(align=True)

                # envelope distance
                box.prop(activeBone, 'envelope_distance', text='Distance')

                # box
                box = box.column(align=True)

                # envelope weight
                box.prop(activeBone, 'envelope_weight', text='Weight')

                # box
                box = box.column(align=True)

                # box
                box.prop(activeBone, 'use_envelope_multiply', text='Multiply', toggle=True)

                # separator
                box.separator()

                # box
                box = box.column(align=True)

                # head radius
                box.prop(activeBone, 'head_radius', text='Head')

                # box
                box = box.column(align=True)

                # tail radius
                box.prop(activeBone, 'tail_radius', text='tail')

                # separator
                box.separator()

                # box
                box = box.column(align=True)

                # bbone segments
                box.prop(activeBone, 'bbone_segments', text='Segments')

                # box
                box = box.column(align=True)

                # bbone in
                box.prop(activeBone, 'bbone_in', text='Ease In')

                # box
                box = box.column(align=True)

                # bbone out
                box.prop(activeBone, 'bbone_out', text='Ease Out')

            # pose mode
            if context.mode in 'POSE':

                # column
                column = layout.column(align=True)

                # label
                column.label(text='Custom Shape:')

                # separator
                column.separator()

                # row
                row = column.row(align=True)

                # label
                # row.label(text='', icon='BLANK1')

                # custom shape
                row.prop(bpy.data.objects[activeArmature.name].pose.bones[activePoseBone.name], 'custom_shape', text='')

                sub = row.row(align=True)
                sub.operator('pose.custom_shape_to_bone', icon='ALIGN', text='')

                # row
                row = column.row(align=True)

                # custom shape transform
                row.prop_search(bpy.data.objects[activeArmature.name].pose.bones[activePoseBone.name], 'custom_shape_transform', activeArmature.pose, 'bones', text='')

                # custom shape
                if bpy.data.objects[activeArmature.name].pose.bones[activePoseBone.name].custom_shape:

                    # row
                    row = column.row(align=True)

                    # hide
                    row.prop(activeBone, 'hide', toggle=True)

                    # show wire
                    row.prop(activeBone, 'show_wire', text='Wireframe', toggle=True)

                    # column
                    column = layout.column(align=True)

                    # row
                    row = column.row(align=True)

                    # scale
                    row.scale_y = 1.25

# button
def button(self, context):
    '''
        The custom shape to bone button
    '''
    self.layout.operator('pose.custom_shape_to_bone', icon='ALIGN')

# Register
def register():
    '''
        Register
    '''

    # register module
    registerModule = bpy.utils.register_module

    # window manager
    windowManager = bpy.types.WindowManager

    # pointer property
    pointerProperty = bpy.props.PointerProperty

    # register
    registerModule(__name__)

    # armature data ui pointer property
    windowManager.armatureDataUI = pointerProperty(type=armatureData)

    # button
    bpy.types.BONE_PT_display.append(button)

    # Unregister
def unregister():
    '''
        Unregister
    '''

    # unregister module
    unregisterModule = bpy.utils.unregister_module

    # window manager
    windowManager = bpy.types.WindowManager

    # unregister
    unregisterModule(__name__)

    # delete armature data ui
    del windowManager.armatureDataUI

if __name__ in '__main__':
    register()
