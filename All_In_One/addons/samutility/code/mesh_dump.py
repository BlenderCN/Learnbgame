##generate python dump mesh from selection
import bpy

def generateText(objname='Object'):
    C = bpy.context
    return(
'''import bpy
from mathutils import Vector

def add_object():
    name = "{name}"
    verts = {verts}
    edges = {edges}
    faces = {faces}

    me = bpy.data.meshes.new(name=name+"_mesh")
    ##useful for development when the mesh may be invalid.
    # me.validate(verbose=True)

    ob = bpy.data.objects.new(name, me)
    ob.location = (0,0,0)
    ob.show_name = True

    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    # create mesh from given verts, faces.
    me.from_pydata(verts, edges, faces)
    # Update mesh with new data
    me.update()
    return ob

add_object()
      '''.format(
      verts = [v.co for v in C.object.data.vertices],
      edges = C.object.data.edge_keys,
      faces = [[v for v in f.vertices] for f in C.object.data.polygons],
      name = objname)
      )



class SAM_OT_DumpMeshToPython(bpy.types.Operator):
    bl_idname = "samutility.dump_mesh_to_python"
    bl_label = "Dump active mesh to python"
    bl_description = "Create a text datablock with a script to generate active object mesh from python"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        act = context.active_object

        if act:
            if act.type == 'MESH':
                objname = act.name
                dump = generateText(objname)
                #write generated script in a new text block
                txt = bpy.data.texts.new(objname)
                txt.write(dump)

            else:
                self.report({'WARNING'}, 'active object must be of type mesh')
                #print('object must be of type mesh')
        else:
            self.report({'WARNING'}, 'you must have an active object')

        return {"FINISHED"}