import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

def read_some_data(context, filepath):
    scale_f = 1000   # factor to downscale the data

    ''' read swc file '''
    #neuron_file = '/home/martin/Programs/Lmv5.2_32bit/entho.CNG.swc'
    print(filepath)
    f = open(filepath)
    lines = f.readlines()
    f.close()

    ''' find starting point '''
    x = 0
    while lines[x][0] is '#':
        x += 1
        
    ''' Create a dictionary with the first item '''
    data = lines[x].strip().split(' ')    
    neuron = {float(data[0]): [float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6])]}
    x += 1
        
    ''' Read the rest of the lines to the dictionary '''
    for l in lines[x:]:
        data = l.strip().split(' ')
        neuron[float(data[0])] = [float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6])]
        
    bpy.ops.object.empty_add(type='ARROWS', location=(neuron[1][1] / scale_f, neuron[1][2] / scale_f, neuron[1][3] / scale_f), rotation=(0, 0, 0))
    a = bpy.context.selected_objects[0]    
    a.name = 'neuron_swc'

    last = -10.0

    ''' Create object '''
    for key, value in neuron.items():
        
        if value[-1] == -1:
            continue
        
        if value[0] == 10:
            continue

        # if we need to start a new bezier curve
        if (value[-1] != last):
             # trace the origins
            tracer = bpy.data.curves.new('tracer','CURVE')
            tracer.dimensions = '3D'
            spline = tracer.splines.new('BEZIER')

            curve = bpy.data.objects.new('curve',tracer)
            bpy.context.scene.objects.link(curve)
            
            # render ready curve
            tracer.resolution_u = 8
            tracer.bevel_resolution = 8 # Set bevel resolution from Panel options
            tracer.fill_mode = 'FULL'
            tracer.bevel_depth = 0.001 # Set bevel depth from Panel options
            
            # move nodes to objects
            p = spline.bezier_points[0]
            p.co = [neuron[value[-1]][1] / scale_f, neuron[value[-1]][2] / scale_f, neuron[value[-1]][3] / scale_f]
            p.radius = neuron[value[-1]][5] / scale_f
            p.handle_right_type='VECTOR'
            p.handle_left_type='VECTOR'
            
            if (last > 0):
                spline.bezier_points.add(1)            
                p = spline.bezier_points[-1]
                p.co = [value[1]/scale_f, value[2]/scale_f, value[3]/scale_f]
                p.radius = value[5] / scale_f
                p.handle_right_type='VECTOR'
                p.handle_left_type='VECTOR'

            curve.parent = a
        
        # if we can continue the last bezier curve
        if value[-1] == last:
            spline.bezier_points.add(1)
            p = spline.bezier_points[-1]
            p.co = [value[1]/scale_f, value[2]/scale_f, value[3]/scale_f]
            p.radius = value[5] / scale_f
            p.handle_right_type='VECTOR'
            p.handle_left_type='VECTOR'
        
        last = key

    return {'FINISHED'}

class ImportSWCData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_mesh.swc"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import SWC-Files"

    # ImportHelper mixin class uses this
    filename_ext = ".swc"

    filter_glob = StringProperty(
            default="*.swc",
            options={'HIDDEN'},
            )

    def execute(self, context):
        return read_some_data(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSWCData.bl_idname, text="SWC Importer")


def register():
    bpy.utils.register_class(ImportSWCData)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSWCData)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
