import bpy
from bpy.props import IntProperty, BoolProperty


class HOPS_OT_SimplifyLattice(bpy.types.Operator):
    bl_idname = "hops.simplify_lattice"
    bl_label = "Simplify Lattice"
    bl_description = "Simplifies lattice to 2 points on UVW"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.object.data.points_u = 2
        bpy.context.object.data.points_v = 2
        bpy.context.object.data.points_w = 2
        bpy.context.object.data.use_outside = True
        return {"FINISHED"}

#############################
# Array Operators Start Here
#############################

# Array Twist


class HOPS_OT_ArrayOperator(bpy.types.Operator):
    bl_idname = "array.twist"
    bl_label = "ArrayTwist"
    bl_description = "Adds an array while also deforming the mesh 360 degrees"
    bl_options = {'REGISTER', 'UNDO'}

    arrayCount : IntProperty(name="ArrayCount", description="Amount Of Clones", default=8, min=1, max=100)

    destructive : BoolProperty(default=False)

    # xy = BoolProperty(default = False)

    # ADD A DRAW FUNCTION TO DISPLAY PROPERTIES ON THE F6 MENU
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop(self, 'arrayCount', text="ArrayCount")
        box.prop(self, 'destructive', text="Destructive/Non")
        # box.prop( self, 'xy', text="Toggle X/Y")

    def execute(self, context):
        # Now Has A Custom Count
        arrayCount = self.arrayCount

        if self.destructive:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.context.object.modifiers["Array"].count = arrayCount
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.context.object.modifiers["SimpleDeform"].deform_method = 'BEND'
            bpy.context.object.modifiers["SimpleDeform"].angle = 6.28319
            bpy.context.object.modifiers["SimpleDeform"].deform_axis = 'Z'
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            bpy.ops.object.location_clear()

        else:
            # Now Has A Custom Count
            arrayCount = self.arrayCount

            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.context.object.modifiers["Array"].count = arrayCount
            bpy.context.object.modifiers["Array"].use_merge_vertices = True
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.context.object.modifiers["SimpleDeform"].deform_method = 'BEND'
            bpy.context.object.modifiers["SimpleDeform"].angle = 6.28319
            bpy.context.object.modifiers["SimpleDeform"].deform_axis = 'Z'
        return {'FINISHED'}


class HOPS_OT_SetAsAam(bpy.types.Operator):
    bl_idname = "hops.set_camera"
    bl_label = "Sets Camera"
    bl_description = "Sets object to camera"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.view3d.object_as_camera()
        return {"FINISHED"}

# EDIT MODE MESH DISPLAY EXP ____________________________________________________


class HOPS_OT_meshdispOperator(bpy.types.Operator):
    bl_idname = "hops.meshdisp"
    bl_label = "Mesh Disp"
    bl_description = "Toggles display of marked edges"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.object.data.show_edges:
            bpy.context.object.data.show_edge_seams = False
            bpy.context.object.data.show_edge_crease = False
            bpy.context.object.data.show_edges = False
            bpy.context.object.data.show_edge_bevel_weight = False
            bpy.context.object.data.show_edge_sharp = False
            bpy.context.object.data.show_faces = False
        else:
            bpy.context.object.data.show_edge_seams = True
            bpy.context.object.data.show_edge_crease = True
            bpy.context.object.data.show_edges = True
            bpy.context.object.data.show_edge_bevel_weight = True
            bpy.context.object.data.show_edge_sharp = True
            bpy.context.object.data.show_faces = True

        return {'FINISHED'}
