import bpy,zipfile,os
class physika_export_operator(bpy.types.Operator):
    bl_idname = "physika_operators.export_result"
    bl_label = "Export Results"
    bl_options = {'REGISTER'}

    def execute(self, context):
        path = context.scene.physika_export.export_path
        obj = context.object
        discrete_method = context.scene.physika_para.physika_discrete
        
        raw_path = os.getcwd()
        script_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        os.chdir(os.path.join(script_path,'lib', discrete_method, 'output'))

        
        res_zip = zipfile.ZipFile(os.path.join(path,obj.name + '.zip'), 'w', zipfile.ZIP_DEFLATED)
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('vtk')]
        print(files)
        for res in files:
            res_zip.write(res)
        res_zip.close()

        return {'FINISHED'}
def register():
    bpy.utils.register_class(physika_export_operator)

def unregister():
    bpy.utils.unregister_class(physika_export_operator)
