bl_info = {
    "name": "PBR Exporter",
    "category": "Learnbgame",
    "blender": (2, 80, 0),
    "author" : "Aetheris",
    "version" : (1, 1, 0),
    "description" :
            "Export Blender Objects and Textures",
}




import bpy
import os
import shutil
import sys

class BakeObjects(bpy.types.Operator):
    """Bake and export selected scene objects"""
    bl_idname = "bake.bakeobjects"
    bl_label = "Bake Textures"

    def execute(self, context):
        
        bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)       

        context.scene.render.engine = "CYCLES"
        
        bar_size = 20
        
        view_layer = bpy.context.view_layer

        obj_active = view_layer.objects.active
        selection = bpy.context.selected_objects
        
        options = bpy.context.window_manager.all_export_settings
        
        objnumber = len(selection)
        
        texture_number = 0
        
        
        if options.use_normal == True:
            texture_number += 1
        if options.use_rough == True:
            texture_number += 1
        if options.use_emit == True:
            texture_number += 1
        if options.use_combined == True:
            texture_number += 1
        if options.use_metal == True:
            texture_number += 1
        if options.use_albedo == True:
            texture_number += 1
        
        bake_number = texture_number*objnumber
        texture_percent = bar_size / bake_number
        one_percent = 100 / bake_number
        first = int(one_percent)
        one_percent = 0
        bake_progress = 0
        
        data = (bar_size, view_layer, obj_active, selection, options, objnumber, texture_number, bake_number, texture_percent, one_percent, first, one_percent, bake_progress)

        print("Starting Texture Baking:")    
        
        if (options.bake_materials == True):  
            
             bpy.ops.mesh.primitive_plane_add(size=2)
             bpy.context.active_object.name = "MATERIAL_BAKE_TARGET"
             object = bpy.context.active_object
             for material in bpy.data.materials:
                 object.name = material.name
                 try:
                    object.material_slots[0].material = material
                    BakeObjectMaterials(object, options, data)
                 except:
                    object.data.materials.append(material)
                    object.material_slots[0].material = material
                    BakeObjectMaterials(object, options, data)
        if (options.bake_materials == False):    
            for obj in selection:
                
                if obj.type == "MESH":
                        
                    BakeObjectMaterials(obj, options, data)
                    
        print("Baking Done                                                                                       ")
                
        for obj in selection:   

            if obj.type == "MESH":
                  
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                if (options.bake_materials == False):
                    SetupMaterialExport(obj)
                    
                if options.seperate_objects == True:
                    path = bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name+ "\\" + obj.name
                        
                    bpy.ops.export_scene.fbx(filepath=path+".fbx", use_selection=True)
                
            
        if options.seperate_objects == False:
            path = bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0]+ "\\" + bpy.data.filepath.split("\\")[-1].split(".")[0]
            print(path)
            SelectObjects(selection)
            bpy.ops.export_scene.fbx(filepath=path+".fbx", use_selection=True)
            
        bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
                
        return {'FINISHED'} 

def BakeObjectMaterials(obj, options, data):
    bar_size, view_layer, obj_active, selection, options, objnumber, texture_number, bake_number, texture_percent, one_percent, first, one_percent, bake_progress = data
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)            
         
    if options.use_normal == True:
        print("Baking Normal on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")

        ConfigureMaterials(obj, "Normal")
        bpy.ops.object.bake(type="NORMAL")
    
        SaveImage(obj, "Normal")
        sys.stdout = sys.__stdout__
        
        bake_progress += texture_percent
        one_percent += first
        
            
    if options.use_rough == True:
        print("Baking Roughness on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        ConfigureMaterials(obj, "Roughness")
        bpy.ops.object.bake(type="ROUGHNESS")
    
        SaveImage(obj, "Roughness")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
        
                
    if options.use_emit == True:
        print("Baking Emission on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        ConfigureMaterials(obj, "Emission")
        sys.stdout = open(os.devnull, "w")
        bpy.ops.object.bake(type="EMIT")
    
        SaveImage(obj, "Emission")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
        
            
    if options.use_combined == True:
        bpy.context.scene.render.bake.use_pass_direct = True
        bpy.context.scene.render.bake.use_pass_indirect = True
        
        
        print("Baking Combined on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        ConfigureMaterials(obj, "Combined")
        bpy.ops.object.bake(type="COMBINED")
    
        SaveImage(obj, "Combined")
        
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
    
    if options.use_metal == True:
        print("Baking Metalic on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        if SetToEmissive(obj, principled_input="Metallic"):
            ConfigureMaterials(obj, "Metalness")
            bpy.ops.object.bake(type="EMIT")
        
            SaveImage(obj, "Metalness")
        else:
            ConfigureMaterials(obj, "Metalness")
            bpy.ops.object.bake(type="GLOSSY")
        
            SaveImage(obj, "Metalness")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
            
    if options.use_albedo == True:
        print("Baking Albedo on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        if SetToEmissive(obj):
            ConfigureMaterials(obj, "Albedo")
            bpy.ops.object.bake(type="EMIT")
        
            SaveImage(obj, "Albedo")
        else:
            ConfigureMaterials(obj, "Albedo")
            bpy.ops.object.bake(type="DIFFUSE")
        
            SaveImage(obj, "Albedo")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
            
    
    try:
        ReconfigureMaterials(obj)
    except:
        print("Failed to reconfigure materials on", obj.name)
        
def ReconfigureMaterials(obj):
    for mat in obj.material_slots:
        output = mat.material.node_tree.nodes["Material Output"]        
        principled = mat.material.node_tree.nodes["Principled BSDF"]
        
        mat.material.node_tree.links.new(output.inputs[0], principled.outputs[0])


def SetToEmissive(obj, principled_input="Base Color"):   
    try: 
        for mat in obj.material_slots:
            emission = mat.material.node_tree.nodes.new("ShaderNodeEmission")
            output = mat.material.node_tree.nodes["Material Output"]
            
            principled = mat.material.node_tree.nodes["Principled BSDF"]
               
            test = False     
            for link in mat.material.node_tree.links:
                if link.to_socket == principled.inputs[principled_input]:
                    node = link.from_socket
                    test=True
            if test == False:
                input = principled.inputs[principled_input]
                type = input.type
                if type == "VALUE":
                    emission.inputs[0].default_value = (input.default_value, input.default_value, input.default_value, 1)
                if type == "RGBA":
                    emission.inputs[0].default_value = input.default_value
            
            mat.material.node_tree.links.new(output.inputs[0], emission.outputs[0])
            if test == True:
                mat.material.node_tree.links.new(emission.inputs[0], node)
        return True
    except:
        print("Node Transfer Error Occured: using fallback bake type")
        return False

def SelectObjects(objs):
    for obj in objs:
        obj.select_set(True)

def SaveImage(obj, texture_type):
    image = bpy.data.images[obj.name+"_"+texture_type]
    try:
        image.save()
    except:
        try:
            if bpy.context.window_manager.all_export_settings.seperate_objects == True:
                os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name)
            else:
                os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0])
        except:
            os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0])
            os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name)
        image.save()

def SetupMaterialExport(obj):
    
    options = bpy.context.window_manager.all_export_settings
    
    for mat in obj.material_slots:
        
        bpy.data.materials.new(name=obj.name+"_"+mat.material.name)
        
        material = bpy.data.materials[obj.name+"_"+mat.material.name]
        material.use_nodes = True
        
        print(material)
        mat.material = material
        
        nodetree = material.node_tree
        
        principled = nodetree.nodes.new("ShaderNodeBsdfPrincipled")
        
        output = nodetree.nodes['Material Output'].inputs[0]
        
        nodetree.links.new(output, principled.outputs[0])
        
        if options.use_albedo == True:
            diffuse = nodetree.nodes.new("ShaderNodeTexImage")
            diffuse.image = bpy.data.images[obj.name+"_Albedo"]
            
            nodetree.links.new(principled.inputs["Base Color"], diffuse.outputs[0])
                
        if options.use_normal == True:
            normal = nodetree.nodes.new("ShaderNodeTexImage")
            normal.image = bpy.data.images[obj.name+"_Normal"]
            normal.color_space = "NONE"
            
            map = nodetree.nodes.new("ShaderNodeNormalMap")
            
            nodetree.links.new(map.inputs["Color"], normal.outputs[0])            
            
            nodetree.links.new(principled.inputs["Normal"], map.outputs[0])
                    
        if options.use_metal == True:
            gloss = nodetree.nodes.new("ShaderNodeTexImage")
            gloss.image = bpy.data.images[obj.name+"_Metalness"]
            gloss.color_space = "NONE" 
            
            nodetree.links.new(principled.inputs["Metallic"], gloss.outputs[0])
                    
        if options.use_rough == True:
            rough = nodetree.nodes.new("ShaderNodeTexImage")
            rough.image = bpy.data.images[obj.name+"_Roughness"]
            rough.color_space = "NONE"
            
            nodetree.links.new(principled.inputs["Roughness"], rough.outputs[0])


def ConfigureMaterials(obj, texture_type):

    resoulution = int(bpy.context.window_manager.all_export_settings.texture_resoulution)

    bpy.ops.image.new(name=obj.name+"_"+texture_type, width=resoulution, height=resoulution)

    image = bpy.data.images[obj.name+"_"+texture_type]
    
    if bpy.context.window_manager.all_export_settings.seperate_objects == True:
        subdir = bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name
    else:
        subdir = bpy.data.filepath.split("\\")[-1].split(".")[0]
    
    image.filepath = bpy.context.scene.render.filepath + subdir + "\\" + obj.name+"_"+texture_type+".png"
    image.file_format = 'PNG'
    
    for mat in obj.material_slots:
        node = mat.material.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images[obj.name+"_"+texture_type]
        node.select = True
        mat.material.node_tree.nodes.active = node
        
class ExportPanel(bpy.types.Panel):
    """Export Menu"""
    bl_label = "Export Panel"
    bl_idname = "RENDER_PT_Exportpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        
        options = context.window_manager

        row = layout.row()
        row.label(text= "Select Textures to Export")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_albedo")
        row.prop(options.all_export_settings, "use_normal")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_metal")
        row.prop(options.all_export_settings, "use_rough")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_emit")
        
        row = layout.row(align=True)
        row.enabled = not options.all_export_settings.bake_materials
        if (options.all_export_settings.bake_materials):
            options.all_export_settings.use_combined = False
        row.prop(options.all_export_settings, "use_combined")

        row = layout.row()
        row.label(text= "Select the Texture Resoulution")

        row = layout.row()
        row.prop(options.all_export_settings, "texture_resoulution", expand=True)
        
        row = layout.row()
        
        row = layout.row()
        row.prop(options.all_export_settings, "seperate_objects")
        
        row = layout.row()
        row.prop(options.all_export_settings, "bake_materials")
        
        row = layout.row()
        row.label(text= "Export Selected Object")
        
        row = layout.row()
        row.prop(bpy.context.scene.render, "filepath")

        row = layout.row()
        row.operator("bake.bakeobjects", text='Export Objects')


class BakeObjectsSettings(bpy.types.PropertyGroup):    
    use_albedo: bpy.props.BoolProperty(name="Albedo", default=True)    
    use_normal: bpy.props.BoolProperty(name="Normal", default=True)    
    use_metal: bpy.props.BoolProperty(name="Metalness", default=True)    
    use_rough: bpy.props.BoolProperty(name="Roughness", default=True)    
    use_emit: bpy.props.BoolProperty(name="Emission", default=True)    
    use_combined: bpy.props.BoolProperty(name="Combined", default=False)

    seperate_objects: bpy.props.BoolProperty(name="Separate Objects", default=False)
    bake_materials: bpy.props.BoolProperty(name="Only Bake Materials", default=False)
    
    texture_resoulution: bpy.props.EnumProperty(
        name = "Resoulution",
        description = "Choose Texture Resolution",
        items = [
            ("1024", "1024", "Render a 1024 x 1024 texture"),
            ("2048", "2048", "Render a 2048 x 2048 texture"),
            ("4096", "4096", "Render a 4096 x 4096 texture"),
            ("8192", "8192", "Render a 8192 x 8192 texture"),
        ],
        default = '1024'
    )  

def register():
    bpy.utils.register_class(ExportPanel)    
    bpy.utils.register_class(BakeObjects)
    bpy.utils.register_class(BakeObjectsSettings)
        
    bpy.types.WindowManager.all_export_settings = bpy.props.PointerProperty(type=BakeObjectsSettings)


def unregister():
    bpy.utils.unregister_class(ExportPanel)
    bpy.utils.unregister_class(BakeObjects)
    bpy.utils.unregister_class(BakeObjectsSettings)


if __name__ == "__main__":
    register()
