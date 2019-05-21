import bpy,subprocess,shlex,os,pathlib



def tetgen(discrete_method, obj_name):
    raw_path = os.getcwd()
    script_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
    os.chdir(os.path.join(script_path, 'lib', 'tetgen1.5.1','build'))
    
    exe = './tetgen'
    input_path = '../../' + discrete_method + '/input/' + obj_name + "/"
    model_path = input_path + obj_name +'.ply'
    vtk_path = input_path + obj_name +'.vtk'
    # res_path = input_path + obj_name +'.1.vtk'
    res = subprocess.run(['./tetgen', '-Ykq1.3a1.0', model_path])
    all_files = os.listdir(input_path)
    res_path = input_path + [k for k in all_files if "vtk" in k][0]
    os.rename(res_path, vtk_path)
    os.chdir(raw_path)
    return res

def bake(discrete_method, obj, if_tetgen):
    """ Wirte by this way temporarily"""
    if(if_tetgen):
        tet_res = tetgen(discrete_method, obj.name)
    
    raw_path = os.getcwd()
    script_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    os.chdir(os.path.join(script_path,'lib', discrete_method,'bin'))
    # json_path = '../blender_physics.json'
    json_path = os.path.join('..', 'input', obj.name, 'blender_physics.json')
    sim_res = subprocess.run(['./blender_' + discrete_method, json_path])
    os.chdir(raw_path)
    if(if_tetgen):
        return tet_res.returncode and sim_res.returncode
    else:
        return sim_res.returncode
