import bpy


class NeutralizeParentInverseOperator(bpy.types.Operator):
    """Clear the parent inverse matrix while maintaining objects' current transforms"""
    bl_idname = "object.neutralize_parent_inverse"
    bl_label = "Neutralize Parent Inverse"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.parent:
                # Merge the inverse into the object's transforms
                ob.matrix_basis = ob.matrix_parent_inverse * ob.matrix_basis
                # Clear the parent inverse matrix
                ob.matrix_parent_inverse.identity()
        return {'FINISHED'}


class NeutralizeTransformsOperator(bpy.types.Operator):
    """Set the parent inverse matrix to current object transforms then clear all transforms"""
    bl_idname = "object.neutralize_transforms"
    bl_label = "Neutralize Transforms"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.parent:
                # Merge the inverse into the object's transforms
                ob.matrix_parent_inverse = ob.matrix_parent_inverse * ob.matrix_basis
                # Nullify the vestigial inverse matrix
                ob.matrix_basis.identity()
        return {'FINISHED'}


class RelateDriversOperator(bpy.types.Operator):
    """Set driver variable targets to relative objects (based on variable names containing 'self' and/or 'parent')"""
    bl_idname = "object.relate_drivers"
    bl_label = "Relate Drivers"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.animation_data is not None and ob.animation_data.drivers is not None:
                for driver in ob.animation_data.drivers:
                    for variable in driver.driver.variables:
                        name = variable.name
                        print(type(variable.targets))
                        for t in range(len(variable.targets)):
                            print("name: " + name)
                            print("iteration: " + str(t))
                            print("index of 'self': " + str(name.find('self')))
                            print("index of 'parent': " + str(name.find('parent')))
                            self_index = name.find('self')
                            parent_index = name.find('parent')
                            print(self_index != -1)
                            if (self_index < parent_index and self_index != -1) or (self_index > parent_index and parent_index == -1):
                                    variable.targets[t].id = ob
                                    name = name[self_index+4:len(name)]
                            elif (parent_index < self_index and parent_index != - 1) or (parent_index > self_index and self_index == - 1):
                                    variable.targets[t].id = ob.parent
                                    name = name[parent_index+6:len(name)]
        return {'FINISHED'}


# Create Parent Tools UI in the Tool Shelf of the 3D View
class ParentToolsUI(bpy.types.Panel):
    """Better Parenting"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Parent Tools"
    bl_context = "objectmode"
    bl_category = "Custom Tools"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.neutralize_parent_inverse")

        row = layout.row()
        row.operator("object.neutralize_transforms")

        row = layout.row()
        row.operator("object.relate_drivers")



# Create Parent Data UI in the Tool Shelf of the 3D View under within the Parent Tools category
class ParentDataUI(bpy.types.Panel):
    """Better Parenting"""
    bl_space_type = 'VIEW_3D'
    bl_context = "objectmode"
    bl_region_type = 'TOOLS'
    bl_category = "Custom Tools"
    bl_label = "Parent Data"

    def draw(self, context):

        ob = bpy.context.object
        layout = self.layout

        row = layout.row()
        row.label(text="Object: " + ob.name)

        if ob.parent:
          row = layout.row()
          row.label(text="Child of: " + ob.parent.name)

          row = layout.row()
          row.label(text="Parent Inverse:")

          loc, rot, scale = ob.matrix_parent_inverse.decompose()

          row = layout.row()
          row.label(text="Loc: " + str(round(loc[0], 2)) + ", " + str(round(loc[1], 2)) + ", " + str(round(loc[2], 2)))

          row = layout.row()
          row.label(text="Rot: " + str(round(rot[0], 2)) + ", " + str(round(rot[1], 2)) + ", " + str(round(rot[2], 2)) + ", " + str(round(rot[3], 2)))

          row = layout.row()
          row.label(text="Scale: " + str(round(scale[0], 2)) + ", " + str(round(scale[1], 2)) + ", " + str(round(scale[2], 2)))
