import bpy, gpu
uniform_types = {}
for k,v in gpu.__dict__.items():
    if isinstance(v,int) and k.startswith('GPU_DYNAMIC_'):
        uniform_types[v] = k[12:]

data_types = ['0','1i','1f','2f','3f','4f','m3','m4','4ub']

attr_types = {6: 'CD_MCOL', 5: 'CD_MTFACE', 14: 'CD_ORCO', 18: 'CD_TANGENT'}

shader = gpu.export_shader(bpy.context.scene, bpy.context.object.material_slots[0].material)
shader['uniforms'].sort(key=lambda e: uniform_types.get(e['type'],'zzz'))
print('------')
for uniform in shader['uniforms']:
    ucopy = uniform.copy()
    if 'texpixels' in ucopy:
        del ucopy['texpixels']
    del ucopy['type']
    del ucopy['datatype']
    #del ucopy['varname']
    utype_str = uniform_types.get(uniform['type'],'unknown '+str(uniform['type']))
    print(utype_str, data_types[uniform['datatype']], ucopy)
