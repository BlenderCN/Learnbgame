import bpy
import bmesh
import mathutils
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class createCubeSphereNode(bpy.types.Node, AnimationNode):
    bl_idname = "createCubeSphereNode"
    bl_label = "Plot Spheres/Cubes in 3D View"
    bl_width_default = 180

    message1 = StringProperty("")
    frm_j = IntProperty(name = "Jump Frame", default = 1, min = 1)
    exe_b = BoolProperty(name = "Execute", default = False, update = propertyChanged)
    del_b = BoolProperty(name = "Delete Existing Mesh", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Boolean", "Sphere/Cube", "typ_b", default = False)
        self.newInput("Integer", "Start Frame", "frm_s")
        self.newInput("Integer", "End Frame", "frm_e")
        self.newInput("Float", "Diameter", "dia")
        self.newInput("Float", "X Scale", "fac_x")
        self.newInput("Float", "Y Offset", "fac_y")
        self.newInput("Float", "Z Offset", "fac_z")
        self.newInput("Integer", "U-Segs", "u_seg")
        self.newInput("Object", "Object", "obj")
        self.newOutput("Object", "Object", "obj")

    def draw(self,layout):
        layout.prop(self, "exe_b")
        layout.prop(self, "del_b")
        layout.prop(self, "typ_b")
        layout.prop(self, "frm_j")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def execute(self, typ_b, frm_s, frm_e, dia, fac_x, fac_y, fac_z, u_seg, obj):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        frm_c = bpy.context.scene.frame_current
        frm_i = frm_c - frm_s
        if self.frm_j == 1:
            run_b = True
        else:
            if frm_i % self.frm_j == 0:
                run_b = True
            else:
                run_b = False
        if not obj or u_seg < 8 or frm_e < frm_s or fac_x == 0:
            self.message1 = "Set Parameters/Object"
            return None
        elif frm_c > frm_e:
            self.message1 = "Completed"
            self.exe_b = False
        elif not self.exe_b:
            self.message1 = "Not Processing"
        elif not run_b:
            self.message1 = "Skipping this frame"
        else:
            if self.exe_b and run_b and frm_c >= frm_s and frm_c <= frm_e:
                bpy.context.scene.objects.active = obj
                sphereMesh = obj.data
                if self.del_b and frm_c == frm_s:
                    for v in bpy.context.object.data.vertices:
                        v.select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.delete(type='VERT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                bm = bmesh.new()
                bpy.ops.object.mode_set(mode='EDIT')
                bm.from_mesh(sphereMesh)
                bpy.ops.object.mode_set(mode='OBJECT')
                locMatrix = mathutils.Matrix.Translation(((frm_c*fac_x),fac_y,fac_z))
                if typ_b:
                    self.message1 = "Processing Spheres"
                    mesh = bmesh.ops.create_uvsphere(bm,
                                u_segments=u_seg,
                                v_segments=(u_seg//2),
                                diameter=(dia/2),
                                matrix=locMatrix)
                    for v in mesh['verts']:
                        for f in v.link_faces:
                            f.material_index = 0
                else:
                    self.message1 = "Processing Cubes"
                    mesh = bmesh.ops.create_cube(bm,
                                size=dia,
                                matrix=locMatrix)
                    for v in mesh['verts']:
                        for f in v.link_faces:
                            f.material_index = 1
                bm.to_mesh(sphereMesh)
                bm.free()
                for f in sphereMesh.polygons:
                    f.use_smooth = True

        return obj
