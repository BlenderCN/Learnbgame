bl_info = {
    "name":        "Array Splitter",
    "description": "Split an objects with array modifiers to individual objects",
    "author":      "Shahzod Boyxonov",
    "version":     (1, 0, 0),
    "blender":     (2, 80, 0),
    "location":    "CTRL+T > Split Array Modifiers",
    "category": "Learnbgame",
}

import bpy

def select_obj(obj,context):
    bpy.ops.object.select_all(action = 'DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    
def copy_transform(dst,mat):
    dst.location       = mat.to_translation()
    dst.rotation_euler = mat.to_euler()
    dst.scale          = mat.to_scale()
            
def calc_curve_length(curve,context):
    select_obj(curve,context)
    bpy.ops.object.duplicate(linked = False)
    curve = context.object
    while len(curve.data.splines)>1:
        curve.data.splines.remove(curve.data.splines[1])
        
    bpy.ops.object.transform_apply(scale = True)
    bpy.ops.object.convert(target = 'MESH',keep_original = False)
    
    curve_length = 0
    for edge in context.object.data.edges:
        v1 = context.object.data.vertices[edge.vertices[0]].co
        v2 = context.object.data.vertices[edge.vertices[1]].co
        curve_length += (v1 - v2).length
    
    active_data = context.object.data
    bpy.data.objects.remove(context.object)
    bpy.data.meshes.remove(active_data)
    return curve_length
    
def remove_array_mods(obj,mod_show_list):
    i = 0
    for mod in obj.modifiers:
        mod.show_viewport = mod_show_list[i]
        i+=1
        if mod.type != 'ARRAY': continue
        obj.modifiers.remove(mod)

class ArraySplitter(bpy.types.Operator):
    """Split Array Modifier"""
    bl_idname = "array_splitter.split"
    bl_label = "Split Array Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    select : bpy.props.BoolProperty(
            name="Select",
            default=True)
    linked : bpy.props.BoolProperty(
            name="Linked",
            default=True)

    def execute(self, context):
        scene = context.scene
        active_obj = context.object
        objs = [obj for obj in context.selected_objects]
        offset_obj = bpy.data.objects.new('Array_Offset_Object',None)
        context.collection.objects.link(offset_obj)
        all_generated_objs = []
        
        for obj in objs:
            generated_objs = []
            generated_objs.append(obj)
            
            mod_show_list = []
            for mod in obj.modifiers:
                mod_show_list.append(mod.show_viewport)
                mod.show_viewport = False
                scene.update()
                
            for mod in obj.modifiers:
                if mod.type != 'ARRAY': 
                    mod.show_viewport = True
                    scene.update()
                    continue
                
                offset_obj.parent = None
                offset_obj.location       = 0,0,0
                offset_obj.rotation_euler = 0,0,0
                offset_obj.scale          = 1,1,1
                
                if mod.use_object_offset:
                    if mod.offset_object:
                        copy_transform(offset_obj, mod.offset_object.matrix_world)
                        select_obj(obj,context)
                        offset_obj.select_set(True)
                        bpy.ops.object.parent_set(keep_transform = True)
                        offset_obj.location       = offset_obj.matrix_local.to_translation()
                        offset_obj.rotation_euler = offset_obj.matrix_local.to_euler()
                        offset_obj.scale          = offset_obj.matrix_local.to_scale()
                        offset_obj.parent = None
                if mod.use_constant_offset:
                    offset_obj.location[0] += mod.constant_offset_displace[0]
                    offset_obj.location[1] += mod.constant_offset_displace[1]
                    offset_obj.location[2] += mod.constant_offset_displace[2]
                if mod.use_relative_offset:
                    offset_obj.location[0] += mod.relative_offset_displace[0] * (obj.dimensions[0]/obj.scale[0])
                    offset_obj.location[1] += mod.relative_offset_displace[1] * (obj.dimensions[1]/obj.scale[1])
                    offset_obj.location[2] += mod.relative_offset_displace[2] * (obj.dimensions[2]/obj.scale[2])
                
                if mod.fit_type == 'FIXED_COUNT':
                    array_counter = 1
                elif mod.fit_type == 'FIT_LENGTH':
                    length_counter = 0
                    tar_length = mod.fit_length
                elif mod.fit_type == 'FIT_CURVE':
                    length_counter = 0
                    if mod.curve:
                        tar_length = calc_curve_length(mod.curve,context)
                    else:
                        tar_length = mod.fit_length
                    
                parent_obj = obj
                select_obj(obj,context)
                for obj2 in generated_objs:
                    obj2.select_set(True)
                    
                while True:
                    bpy.ops.object.duplicate(linked = self.linked)
                    copy_transform(context.object, offset_obj.matrix_local)
                    context.object.parent = parent_obj
                    parent_obj = context.object
                    remove_array_mods(parent_obj,mod_show_list)
                    
                    if   mod.fit_type == 'FIXED_COUNT':
                        array_counter += 1
                        generated_objs.extend(context.selected_objects)
                        if array_counter>=mod.count:break
                    elif mod.fit_type == 'FIT_LENGTH' or mod.fit_type == 'FIT_CURVE':
                        length_counter += offset_obj.location.length
                        if length_counter>=tar_length:
                            context.view_layer.objects.active = parent_obj.parent
                            bpy.data.objects.remove(parent_obj)
                            parent_obj = context.object
                            break
                        generated_objs.extend(context.selected_objects)
                    else:
                        break
                
                if mod.start_cap:
                    select_obj(mod.start_cap,context)
                    bpy.ops.object.duplicate(linked = self.linked)
                    copy_transform(context.object, offset_obj.matrix_local.inverted_safe())
                    context.object.parent = obj
                    generated_objs.append(context.object)
                
                if mod.end_cap:
                    select_obj(mod.end_cap,context)
                    bpy.ops.object.duplicate(linked = self.linked)
                    copy_transform(context.object, offset_obj.matrix_local)
                    context.object.parent = parent_obj
                    generated_objs.append(context.object)
                
                mod.show_viewport = True
                scene.update()
                
            remove_array_mods(obj,mod_show_list)
            
            if self.select:
                all_generated_objs.extend(generated_objs)
            for obj2 in generated_objs:
                obj2.select_set(True)
            if obj.parent:
                obj.parent.select_set(True)
                context.view_layer.objects.active = obj.parent
                bpy.ops.object.parent_set(keep_transform = True)
            else:
                bpy.ops.object.parent_clear(type = 'CLEAR_KEEP_TRANSFORM')
                
        bpy.data.objects.remove(offset_obj)
        bpy.ops.object.select_all(action = 'DESELECT')
        if self.select:
            for obj in all_generated_objs:
                obj.select_set(True)
        else:
            for obj in objs:
                obj.select_set(True)
        context.view_layer.objects.active = active_obj
        return {'FINISHED'}

def menu_func(self,context):
    self.layout.operator("array_splitter.split")

def register():
    bpy.utils.register_class(ArraySplitter)
    bpy.types.VIEW3D_MT_object_apply.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ArraySplitter)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_func)

if __name__ == "__main__":
    register()
