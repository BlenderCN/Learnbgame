'''operators for autosmoothextras'''
import bpy
import bmesh
from bpy.props import FloatProperty, StringProperty, EnumProperty, BoolProperty

def __edgelistbyangle(self, angle):
    pass

class MarkSharps(bpy.types.Operator):
    bl_idname = "mesh.auto_smooth_mark_sharps"
    bl_label = "Mark Sharps"
    bl_description = "Enhances mesh property normals Auto Smooth function with possibility mark Sharp edges by auto smooth angle"
    bl_options = {"INTERNAL", "UNDO"}
    sharpen_concave = BoolProperty (name='Sharpen Concave', default=True)
    sharpen_convex = BoolProperty(name='Sharpen Convex', default=True)

    @classmethod
    def poll(cls, context):
           return True

    def execute(self, context):
        '''create bmesh representation of active object and calculate sharp edges based on angle of autosmooth and face angles'''
        obj = bpy.context.active_object
        asa = obj.data.auto_smooth_angle
        md = obj.data
        if 'OBJECT' in obj.mode:
            bm = bmesh.new()
            bm.from_mesh(md)
            bm.edges.ensure_lookup_table()
            for edge in bm.edges:
                if edge.calc_face_angle() >= asa:
                    edge.smooth = False
                else :pass
            bm.edges.ensure_lookup_table()             
            bm.to_mesh(md)
            bm.free()
            
        elif 'EDIT' in obj.mode:
            bm = bmesh.from_edit_mesh(md)
            bm.edges.ensure_lookup_table()
            for edge in bm.edges:
                if edge.calc_face_angle() >= asa:
                    edge.smooth = False
                else :pass
            bm.edges.ensure_lookup_table()         
            bmesh.update_edit_mesh(md)
        md.update()        
        if md.use_auto_smooth is False:
            md.use_auto_smooth = True
        return {"FINISHED"}

class MarkEdgeCrease(bpy.types.Operator):
    bl_idname = "mesh.auto_smooth_mark_edgecrease"
    bl_label = "Mark Edge Crease"
    bl_description = "Enhances mesh property normals Auto Smooth function with possibility mark Edge Crease by auto smooth angle"
    bl_options = {"INTERNAL", "UNDO"}
    crease_value = FloatProperty(name='Edge Crease', description='Edge crease value', default=1.0, min=0.0, max=1.0)
    crease_concave = BoolProperty (name='Crease Concave', default=True)
    crease_convex = BoolProperty(name='Crease Convex', default=True)        
    crease_fallof_max = FloatProperty(name='Edge crease max',description='Edge crease max value',  default=0.766, min=0.0, max=1.000, soft_min=0.0, soft_max=1.000)
    crease_fallof_min = FloatProperty(name='Edge crease min',description='Edge crease min value',  default=0.333, min=0.0, max=1.000, soft_min=0.0, soft_max=1.000)
    crease_fallof_type = EnumProperty(
        items=(
        ('RANDOM', 'Random', 'set falloff to random'), 
        ('CONSTANT', 'Constant', 'set falloff to constant'),
        ('LINEAR', 'Linear', 'set falloff to linear'),
        ('SHARP', 'Sharp', 'set falloff to sharp'),
        ('INVERSESQR', 'Inverse square', 'set falloff to inversesqr'),
        ('ROOT', 'Root', 'set texturesize to root'),
        ('SPHERE', 'Sphere', 'set falloff to sphere'),
        ('SMOOTH', 'Smooth', 'set falloff to smooth'),
        ), name = "Edge crease falloff", default = 'LINEAR'
    )

    @classmethod
    def poll(cls, context):
           return True

    def execute(self, context):
        '''create bmesh representation of active object and calculate sharp edges based on angle of autosmooth and face angles'''
        obj = bpy.context.active_object
        asa = obj.data.auto_smooth_angle
        md = obj.data

        if 'OBJECT' in obj.mode:
            bm = bmesh.new()
            bm.from_mesh(md)
            bm.edges.ensure_lookup_table()
            key = bm.edges.layers.crease.verify()
            for edge in bm.edges:
                if edge.calc_face_angle() >= asa:
                    edge[key] = self.crease_value
                else :pass
            bm.edges.ensure_lookup_table()
            bm.to_mesh(md)
            bm.free()
            
        elif 'EDIT' in obj.mode:
            bm = bmesh.from_edit_mesh(md)
            bm.edges.ensure_lookup_table()
            key = bm.edges.layers.bevel_weight.verify()
            for edge in bm.edges:
                if edge.calc_face_angle() >= asa:
                    edge[key] = self.crease_value
                else :pass
            bm.edges.ensure_lookup_table() 
            bmesh.update_edit_mesh(md)
        md.update()
        return {"FINISHED"}    
  
class MarkBewelWeights(bpy.types.Operator):
    bl_idname = "mesh.auto_smooth_mark_bewelweights"
    bl_label = "Mark Bewel Weights"
    bl_description = "Enhances mesh property normals Auto Smooth function with possibility mark Bewel Weight by auto smooth angle"
    bl_options = {"INTERNAL", "UNDO"}
    bevel_weight = FloatProperty(name='Bevel Weight', description='Bevel weight value', default=1.0, min=0.0, max=1.0)
    bevel_concave = BoolProperty (name='Bevel Concave', default=True)
    bevel_convex = BoolProperty(name='Bevel Convex', default=True)    
    bevel_fallof_max = FloatProperty(name='Bevel weight max', description='Bevel weight max value',default=0.766, min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
    bevel_fallof_min = FloatProperty(name='Bevel weight min', description='Bevel weight min value',default=0.333, min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
    bevel_fallof = EnumProperty(
        items=(
        ('RANDOM', 'Random', 'set falloff to random'), 
        ('CONSTANT', 'Constant', 'set falloff to constant'),
        ('LINEAR', 'Linear', 'set falloff to linear'),
        ('SHARP', 'Sharp', 'set falloff to sharp'),
        ('INVERSESQR', 'Inverse square', 'set falloff to inverse square'),
        ('ROOT', 'Root', 'set texturesize to root'),
        ('SPHERE', 'Sphere', 'set falloff to sphere'),
        ('SMOOTH', 'Smooth', 'set falloff to smooth'),
        ), name = "Bevel weight falloff type", default = 'LINEAR'
    )

    @classmethod
    def poll(cls, context):
           return True

    def execute(self, context):
        '''create bmesh representation of active object and calculate sharp edges based on angle of autosmooth and face angles'''
        obj = bpy.context.active_object
        asa = obj.data.auto_smooth_angle
        md = obj.data
        if 'OBJECT' in obj.mode:
            bm = bmesh.new()
            bm.from_mesh(md)
            bm.edges.ensure_lookup_table()
            key = bm.edges.layers.bevel_weight.verify()
            for edge in bm.edges:
                if edge.calc_face_angle() >= asa:
                    edge[key] = self.bevel_weight
                else :pass
            bm.edges.ensure_lookup_table()
            bm.to_mesh(md)                   
            bm.free()
            
        elif 'EDIT' in obj.mode:
            bm = bmesh.from_edit_mesh(md)
            bm.edges.ensure_lookup_table()
            key = bm.edges.layers.bevel_weight.verify()
            for edge in bm.edges:
                if edge.calc_face_angle() >= asa:
                    edge[key] = self.bevel_weight
                else :pass
            bm.edges.ensure_lookup_table() 
            bmesh.update_edit_mesh(md)
        md.update()
        return {"FINISHED"}
      
if __name__ == '__main__':
    def register():
        try: bpy.utils.register_module(__name__)
        except: traceback.print_exc()

        print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

    def unregister():
        try: bpy.utils.unregister_module(__name__)
        except: traceback.print_exc()
        
        print("Unregistered {}".format(bl_info["name"]))