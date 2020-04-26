import bpy
from . Functions import *
    
class Test_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.cursor_center"
    bl_label = "Simple operator"
    bl_description = "Center 3d cursor"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()

        return{'FINISHED'}


class Circle_Array_Operator(bpy.types.Operator):
    bl_idname = "object.circle_array_operator"
    bl_label = "Array object in circle"
    bl_description = "Arrays object in a circle.Center of circle will be object orgin)."

    def execute(self, context):
        #-----Get active Object-----#
        act_obj = bpy.context.active_object

        loc = act_obj.location

        #-----Add empty for driver-----#
        mt_d = bpy.data.objects.new('Empty_Driver', None)
        bpy.context.collection.objects.link(mt_d)
        mt_d.location = loc

        #-----modifier to Active Object-----#
        mod = act_obj.modifiers.new(name='Circle_Array',type='ARRAY')
        mod.count = 6
        mod.use_object_offset = True
        mod.use_relative_offset = False
        mod.use_merge_vertices = True
        mod.offset_object = mt_d
        #-----Driver to Empty-----#
        driver = mt_d.driver_add("rotation_euler", 2).driver
        driver.type = 'SCRIPTED'
        driver.expression = '2 * pi / var'
        #-----Variable setup-----#
        var = driver.variables.new()
        target = var.targets[0]
        target.id_type = 'OBJECT'
        target.id = act_obj
        target.data_path = 'modifiers["'+ mod.name +'"].count'

        #-----Add empty Sphere as PARENT object-----#
        mt_p = bpy.data.objects.new('Empty_Parent', None)
        bpy.context.collection.objects.link(mt_p)
        
        mt_p.location = loc
        mt_p.empty_display_type = 'SPHERE'
        mt_p.empty_display_size = 5
        
        bpy.context.scene.update()
        
        act_obj.parent = mt_p
        act_obj.matrix_parent_inverse = mt_p.matrix_world.inverted()
        mt_d.parent = mt_p
        mt_d.matrix_parent_inverse = mt_p.matrix_world.inverted()
        
        #-----Make Collection-----#
        collect_ob = act_obj, mt_p, mt_d 
        new_collection(bpy.context, 'Circle Array',collect_ob, act_obj, False)
        return {'FINISHED'}

class Array_Path_OperatorOperator(bpy.types.Operator):
    bl_idname = "object.array_path_operator"
    bl_label = "Array_Path_Operator"

    def execute(self, context):
        act_ob = bpy.context.active_object
        cs_loc = bpy.context.scene.cursor.location

        act_ob_loc = act_ob.location
        co_2 = cs_loc - act_ob_loc
        coords = [(0,0,0), co_2]

        #-----Add curve-----#
        curveData = bpy.data.curves.new('Path', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2

        polyline = curveData.splines.new('POLY')
        polyline.points.add(len(coords) - 1)

        for i, coord in enumerate(coords):
            x,y,z = coord
            polyline.points[i].co = (x, y, z, 1)

        path_ar = bpy.data.objects.new('Path', curveData)
        path_ar.location = act_ob_loc   
        bpy.context.collection.objects.link(path_ar)

        #-----Add plane & Array-----#
        bpy.ops.mesh.primitive_plane_add(location=act_ob_loc)
        ar_plane = bpy.context.selected_objects[0]
        ar_plane.display_type = 'WIRE'
        ar_plane.instance_type = 'FACES'
        ar_plane.show_instancer_for_render = True
        act_ob.parent = ar_plane
        act_ob.matrix_parent_inverse = ar_plane.matrix_world.inverted()


        mod = ar_plane.modifiers.new(type='ARRAY', name='Path_Array')
        mod.fit_type = 'FIT_CURVE'
        mod.curve = path_ar
        mod_2 = ar_plane.modifiers.new(type='CURVE', name='Path_Curve')
        mod_2.object = path_ar

        #-----Add & Parent to Empty-----#
        em = bpy.data.objects.new('Path_Parent', None)
        bpy.context.collection.objects.link(em)
        em.location = act_ob_loc
        em.empty_display_size = 2
        child_ob = path_ar, ar_plane
        
        bpy.context.scene.update()

        for ob in child_ob:
            ob.parent = em
            ob.matrix_parent_inverse = em.matrix_world.inverted()
            
        
        #-----Make Collection-----#
        collect_ob = act_ob, path_ar, ar_plane, em
        new_collection(bpy.context, 'Path Array',collect_ob, act_ob, False)           

        return {'FINISHED'}


class Instance_Collection_Operator(bpy.types.Operator):
    bl_idname = "object.instance_collection"
    bl_label = "Instance_Collection"
    bl_description = "Instances a new collection on the faces of selected object"

    def execute(self, context):
        act_ob = bpy.context.active_object
        new_collect = new_collection(bpy.context, 'Instanced', None , act_ob, True)

        mt = bpy.data.objects.new('Empty_Instance_'+ new_collect.name, None)
        bpy.context.collection.objects.link(mt)
        mt.empty_display_type = 'SINGLE_ARROW'
        mt.empty_display_size = 2
        mt.hide_render = True
        mt.location = act_ob.matrix_world.translation


        mt.instance_type = 'COLLECTION'
        mt.instance_collection = new_collect

        act_ob.instance_type = 'FACES'
        
        parent(mt, act_ob)       


        return {'FINISHED'}
