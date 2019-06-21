import bpy
import mathutils as mt


class ScalePlaneToUV(bpy.types.Operator):
    """Scale plane to UV"""
    bl_idname = "object.scale_plane_to_uv"
    bl_label = "Scale to UV"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def hw(self, lst, flip=False):
        x, y = lst[2] - lst[0]
        return abs(x) / abs(y) if flip else abs(y) / abs(x)
    
    def wh(self, lst):
        return self.hw(lst, True)
    
    def tx_denorm(self, plane):
        image = plane.data.uv_textures[0].data.values()[0].image
        w, h = image.size[0], image.size[1]
        return mt.Matrix.Scale(h / w, 2, mt.Vector((0, 1)))

    def execute(self, context):
        ops = bpy.ops
        ops.object.mode_set(mode="OBJECT")
        plane = context.active_object
        uvs = [d.uv for d in plane.data.uv_layers.active.data]
        uvs_center = sum(uvs, mt.Vector((0, 0)))
        uvs_center.magnitude /= len(uvs)
        t = self.tx_denorm(plane)
        uvso = [t * (uv - uvs_center) for uv in uvs]
        uvx = self.hw(uvso)
        poly = plane.data.polygons[0]
        vs = [plane.data.vertices[i].co.yz for i in poly.vertices]
        vx = self.hw(vs)
        vy = self.wh(vs)
        ops.object.mode_set(mode="EDIT")
        ops.mesh.select_all(action="SELECT")
        ops.transform.resize(value=(vx if vx < vy else 1, 1, vy if vy < vx else 1))
        ops.transform.resize(value=(1, 1, uvx))
        ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ScalePlaneToUV)


def unregister():
    bpy.utils.unregister_class(ScalePlaneToUV)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.scale_plane_to_uv()
