import bpy,os
import bmesh
from . import bake
from . import save_inputs
class BakePhysiKaSimulation(bpy.types.Operator):
    bl_idname = "physika_operators.bake_physika_simulation"
    bl_label = "Bake Fluid Simulation"
    bl_description = "Run fluid simulation"
    bl_options = {'REGISTER'}



    def triangulate_object(self, obj):
        me = obj.data
        # Get a BMesh representation
        bm = bmesh.new()
        bm.from_mesh(me)

        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)

        # Finish up, write the bmesh back to the mesh
        bm.to_mesh(me)
        bm.free()

    def save_input_files(self,context, obj):
        script_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        discrete_method = obj.physika.physika_para.physika_discrete

        input_path = os.path.join(script_path,'lib',discrete_method,'input')
        save_inputs.clear_cache(context, discrete_method, input_path)
        
        obj_name = obj.name
        input_path = os.path.join(input_path, obj_name)
        
        if_tetgen = save_inputs.save_model(context, discrete_method, input_path)
        save_inputs.save_constraint(context, input_path)
        save_inputs.save_parameters(context, discrete_method, input_path)
        save_inputs.save_obstacles(context, input_path)

        return if_tetgen
        

        
    def run_simulation(self, obj, if_tetgen):
        res = bake.bake(obj.physika.physika_para.physika_discrete,obj,if_tetgen)
        if res is 0:
            obj.physika.bake.is_bake_finished = True

    
    def execute(self, context):
        print(os.path.realpath(__file__))
        obj = context.scene.objects.active
        self.triangulate_object(obj)
        if_tetgen = self.save_input_files(context, obj)
        
        if obj.physika.is_active is True:
            self.run_simulation(obj, if_tetgen)
        return {'RUNNING_MODAL'}
    
def register():
    bpy.utils.register_class(BakePhysiKaSimulation)

def unregister():
    bpy.utils.unregister_class(BakePhysiKaSimulation)
