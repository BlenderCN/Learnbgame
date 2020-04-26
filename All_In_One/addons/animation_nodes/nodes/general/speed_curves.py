import bpy
import bmesh
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class createCurvesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_createCurvesNode"
    bl_label = "Plot Graph in 3D View"
    bl_width_default = 180

    message1 = StringProperty("")
    message2 = StringProperty("")
    frm_j = IntProperty(name = "Jump Frame", default = 1, min = 1)
    exe_b = BoolProperty(name = "Execute", default = False, update = propertyChanged)
    del_b = BoolProperty(name = "Delete Existing Mesh", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Float", "Input", "val_i")
        self.newInput("Integer", "Start Frame", "frm_s")
        self.newInput("Integer", "End Frame", "frm_e")
        self.newInput("Float", "X Scale", "fac_x")
        self.newInput("Float", "Y Offset", "fac_y")
        self.newInput("Float", "Z Scale", "fac_z")
        self.newInput("Object", "Object", "obj")
        self.newOutput("Object", "Object", "obj")

    def draw(self,layout):
        layout.prop(self, "exe_b")
        layout.prop(self, "del_b")
        layout.prop(self, "frm_j")
        if (self.message2 != ""):
            layout.label(self.message2, icon = "INFO")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def execute(self, val_i, frm_s, frm_e, fac_x, fac_y, fac_z, obj):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if not obj:
            # MAke sure mesh object is selected
            self.message1 = "No Mesh Object"
            return None
        if self.exe_b:
            self.message2 = "Processing"
            frm_p = bpy.context.scene.frame_start
            if frm_e <= frm_s or frm_s <= frm_p or fac_x == 0 or fac_z == 0:
                self.message1 = "Set Frames/Scales, etc."
                self.exe_b = False
            else:
                frm_c = bpy.context.scene.frame_current
                frm_i = frm_c - frm_s
                if self.frm_j == 1:
                    run_b = True
                else:
                    if frm_i % self.frm_j == 0:
                        run_b = True
                    else:
                        run_b = False
                if not run_b:
                    self.message1 = "Skipping this frame"
                elif run_b and frm_c >= frm_s and frm_c <= frm_e:
                    self.message1 = "Building Curves"
                    # Add curve points
                    bpy.context.scene.objects.active = obj
                    mesh = obj.data
                    if self.del_b and frm_c == frm_s:
                        for v in bpy.context.object.data.vertices:
                            v.select = True
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.delete(type='VERT')
                        bpy.ops.object.mode_set(mode='OBJECT')
                    vert = ((frm_c * fac_x), fac_y, (val_i * fac_z)) # next vert made with XYZ coords
                    bm = bmesh.new()
                    # convert the current mesh to a bmesh (must be in edit mode)
                    bpy.ops.object.mode_set(mode='EDIT')
                    bm.from_mesh(mesh)
                    bpy.ops.object.mode_set(mode='OBJECT')  # return to object mode
                    bm.verts.new(vert)  # add a new vert
                    bm.verts.ensure_lookup_table() # reset table lookup
                    if len(mesh.vertices) > 0:
                        bm.edges.new((bm.verts[-1], bm.verts[-2])) # Add edge using last two verts
                    # make the bmesh the object's mesh
                    bm.to_mesh(mesh)
                    bm.free()  # always do this when finished
                elif frm_c > frm_e:
                    self.message1 = "Processing Complete"
                    self.exe_b = False # Stop node running again until user changes this
                else:
                    self.message1 = "Waiting for start frame"
        else:
            self.message2 = "Not Processing"
            self.message1 = ""

        return obj
