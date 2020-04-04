bl_info = {
    "name": "Project",
    "author": "Swapnil Das",
    "version": (1, 0),
    "blender": (2, 7, 9),
    "location": "File > Import",
    "description": "Export Cube Vertices",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'TESTING',
    "category": "Learnbgame",
}

import bpy, os

class Export(bpy.types.Operator):
    # unique identifier for buttons and menu items to reference.
    bl_idname = "export.out"
    bl_label = "Export vertices of cube"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):

        scene = context.scene
        cube = scene.objects['Cube']
        
        file = open('/tmp/data_face.out', 'w')
        for polygon in cube.data.polygons:
            verts_in_face = polygon.vertices[:]
            # print("face index", polygon.index)
            # print("normal", polygon.normal)
            for vert in verts_in_face:
                # print("vert", vert, " vert co", cube.data.vertices[vert].co)
                file.writelines(str(vert) + ' ')
            
            file.writelines('\n')

        file.close()

        file = open('/tmp/data_pos.out', 'w')
        for vertex in cube.data.vertices:
            d = cube.matrix_world * vertex.co
            for coordinates in d:
                file.writelines(str(coordinates) + ' ')
            
            file.writelines('\n')

        file.close()

        os.system("python /home/swapnil/Project/src/coordi.py")
        print('Done')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(Export)

def unregister():
    bpy.utils.unregister_class(Export)

if __name__ == '__main__':
    register()
