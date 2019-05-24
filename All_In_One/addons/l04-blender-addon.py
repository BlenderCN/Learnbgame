bl_info = {
    "name": "Matrix Extrude Add-on",
    "author": "Benedikt Grether",
    "version": (1,0,0),
    "blender": (2, 7, 9),
    "description":"",
    "category": "Learnbgame",
    "support": "TESTING",
    "location": "VIEW 3D > EDIT MODE > MESH",
}

import bpy

class MatrixExtrude(bpy.types.Operator):
    bl_idname = "hfu.matrix_extude"
    bl_label = "Matrix Extrude"
    bl_options = {'REGISTER', 'UNDO'}

    #Variablen

    #TransformTranslate
    transformTranslateX = -2
    transformTranslateY = 7
    transformTranslateZ = 1

    #TransformResize
    transforResizeX = 0.805539
    transforResizeY = 0.805539
    transforResizeZ = 0.805539

    #TransformRotate
    transformRotate = -0.475515

    #proberties vordefiniert
    extrusion_step = bpy.props.IntProperty(default=5, min=1, max=20)
    extrusion_offset = bpy.props.FloatProperty(defualt=-0.5)
    scale = bpy.props.FloatProperty(default=0.8)

    # i Range
    rangeI = 5

    def execute(self, context):
        for i in range(self.extrusion_step):
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(self.transformTranslateX , self.transformTranslateY, self.transformTranslateZ), "constraint_axis":(False, False, True), "constraint_orientation":'NORMAL'})
            bpy.ops.transform.resize(value=(self.transforResizeX, self.transforResizeY, self.transforResizeZ), constraint_axis=(False, False, False))
            bpy.ops.transform.rotate(value= self.transformRotate, axis=(1, 0, 1), constraint_axis=(True, True, False))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MatrixExtrude)
    print("Hello World")
def unregister():
    bpy.utils.unregister_class(MatrixExtrude)
    print("Goodbye World")