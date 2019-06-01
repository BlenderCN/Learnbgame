import math
from . import esswriter

class EssExporter:
    def __init__(self):
        self.writer = esswriter.EssWriter()

    def BeginExport(self, filename):
        self.writer.Initialize(filename, True)
        self.mElInstances = []

    def EndExport(self):
        self.writer.BeginNode("instgroup", "groups")
        self.writer.AddRefGroup("instance_list", self.mElInstances)
        self.writer.EndNode()
        self.writer.AddRenderCommand("groups", "caminst", "opt")
        self.writer.Close()

    def SetOptions(self):
        self.writer.BeginNode("options", "opt")
        self.writer.AddInt("min_samples", 1)
        self.writer.AddInt("max_samples", 16)
        self.writer.AddBool("progressive", False)
        self.writer.AddInt("diffuse_samples", 4)
        self.writer.AddInt("sss_samples", 16)
        self.writer.AddInt("volume_indirect_samples", 8)
        self.writer.AddInt("filter", 4)
        self.writer.AddScaler("filter_size", 3.0)
        self.writer.AddScaler("light_cutoff", 0.01)
        self.writer.AddScaler("GI_cache_density", 1.0)
        self.writer.AddInt("GI_cache_passes", 100)
        self.writer.AddInt("GI_cache_points", 5)
        self.writer.AddEnum("GI_cache_preview", "accurate")
        self.writer.AddInt("diffuse_depth", 5)
        self.writer.AddInt("sum_depth", 10)
        self.writer.AddBool("caustic", False)
        self.writer.AddBool("motion", False)
        self.writer.AddBool("use_clamp", False)
        self.writer.AddScaler("clamp_value", 20.0)
        self.writer.AddBool("displace", False)
        self.writer.AddEnum("engine", "GI cache")
        self.writer.AddBool("GI_cache_no_leak", True)
        self.writer.AddScaler("display_gamma", 1.0)
        self.writer.AddScaler("texture_gamma", 2.2)
        self.writer.AddScaler("shader_gamma", 2.2)
        self.writer.AddScaler("light_gamma", 2.2)
        self.writer.AddBool("exposure", False)
        self.writer.AddScaler("GI_cache_screen_scale", 1.0)
        self.writer.AddScaler("GI_cache_radius", 0.0)
        self.writer.EndNode()

    def AddCameraData(self, width, height, fov, near, far, env_shader, matrix):
        self.writer.BeginNode("camera", "cam")
        self.writer.AddRef("env_shader", env_shader)
        self.writer.AddScaler("focal", 1.0)
        self.writer.AddScaler("aperture", math.tan(fov / 2.0) *2.0)
        self.writer.AddScaler("clip_hither", near)
        self.writer.AddScaler("clip_yon", far)
        self.writer.AddScaler("aspect", float(width) / float(height))
        self.writer.AddInt("res_x", width)
        self.writer.AddInt("res_y", height)
        self.writer.EndNode()

        instName = "caminst"

        self.writer.BeginNode("instance", instName)
        self.writer.AddRef("element", "cam")
        self.writer.AddMatrix("transform", matrix)
        self.writer.AddMatrix("motion_transform", matrix)
        self.writer.EndNode()

        self.mElInstances.append(instName)
        return  instName

    def AddDefaultMaterial(self):
        matName = "GlobalMaterial"

        self.writer.BeginNode("max_ei_standard", "DefaultMaterialShaderName")
        self.writer.EndNode()

        self.writer.BeginNode("max_result", "Result_DefaultMaterialShaderName")
        self.writer.LinkParam("input", "DefaultMaterialShaderName", "result")
        self.writer.EndNode();

        shaderNames = ["Result_DefaultMaterialShaderName"]

        self.writer.BeginNode("osl_shadergroup", "DefaultOSLShaderName")
        self.writer.AddRefGroup("nodes", shaderNames)
        self.writer.EndNode()

        self.writer.BeginNode("material", matName)
        self.writer.AddRef("surface_shader", "DefaultOSLShaderName")
        self.writer.EndNode()

        return matName

    def AddBackground(self, color):
        shaderName = "environment_shader"

        self.writer.BeginNode("output_result", "global_environment")
        self.writer.AddColor("input", color)
        self.writer.AddBool("env_emits_GI", True)
        self.writer.EndNode()

        nodes = ["global_environment"]
        self.writer.BeginNode("osl_shadergroup", "environment_shader")
        self.writer.AddRefGroup("nodes", nodes)
        self.writer.EndNode()

        return shaderName

    def AddDupliObj(self, obj, scene):
        name = obj.name
        obj.dupli_list_create(scene)
        for dupli in obj.dupli_list:
            if dupli.object.type == 'MESH':
                self.AddMeshObj(dupli.object, scene, name + ':' + dupli.object.name, dupli.matrix)
        obj.dupli_list_clear()

    def AddBlenderObj(self, obj, scene):

        if obj.type != 'MESH':
            return

        if obj.is_duplicator:
            self.AddDupliObj(obj, scene)
        else:
            self.AddMeshObj(obj, scene, obj.name, obj.matrix_world)    

    def AddMeshObj(self, obj, scene, name, matrix):
        matName = self.AddMaterial(obj, scene)

        mesh = obj.to_mesh(scene, True, 'RENDER', calc_tessface=True)
        
        elementName = name
        self.writer.BeginNode("poly", elementName + "_ply")
        self.writer.AddPointList("pos_list", mesh.vertices)
        self.writer.AddIndexList("triangle_list", mesh.tessfaces)
        self.writer.EndNode()

        instName = elementName + "_inst"
        mtl_list = [matName]
        self.writer.BeginNode("instance", instName)
        self.writer.AddRefGroup("mtl_list", mtl_list)
        self.writer.AddRef("element", elementName + "_ply")
        self.writer.AddMatrix("transform", matrix)
        self.writer.AddMatrix("motion_transform", matrix)
        self.writer.EndNode()

        self.mElInstances.append(instName)
    
    def AddObj(self, obj, scene):
        self.AddBlenderObj(obj, scene)
        self.AddLight(obj, scene)
        pass

    def AddLight(self, obj, scene):
        if obj.type != 'LAMP':
            return
        light_type = obj.data.type

        if light_type == 'AREA':
            self.AddQuadLight(obj, scene)
        elif light_type == 'POINT':
            self.AddPointLight(obj, scene)
        elif light_type == 'SUN':
            self.AddSun(obj, scene)

    def AddQuadLight(self, obj, scene):
        elementName = obj.name

        lamp = obj.data
        self.writer.BeginNode("quadlight", elementName + "_light")
        self.writer.AddScaler("intensity", lamp.energy)
        self.writer.AddColor("color", lamp.color)
        self.writer.AddScaler("width", lamp.size)
        if lamp.shape == 'SQUARE':
            self.writer.AddScaler("height", lamp.size)
        elif lamp.shape == 'RECTANGLE':
            self.writer.AddScaler("height", lamp.size_y)        
        self.writer.AddInt("samples", 8)
        self.writer.AddBool("both_sides", False)
        self.writer.AddInt("volume_samples", 16)
        self.writer.EndNode()

        instName = elementName + "_inst"
        self.writer.BeginNode("instance", instName)
        self.writer.AddBool("visible_primary", False)
        self.writer.AddBool("cast_shadow", True)
        self.writer.AddRef("element", elementName + "_light")
        self.writer.AddMatrix("transform", obj.matrix_world)
        self.writer.AddMatrix("motion_transform", obj.matrix_world)
        self.writer.EndNode()

        self.mElInstances.append(instName)

    def AddPointLight(self, obj, scene):
        elementName = obj.name

        lamp = obj.data
        self.writer.BeginNode("pointlight", elementName + "_light")
        self.writer.AddScaler("intensity", lamp.energy)
        self.writer.AddColor("color", lamp.color)
        self.writer.AddInt("volume_samples", 16)
        self.writer.EndNode()

        instName = elementName + "_inst"
        self.writer.BeginNode("instance", instName)
        self.writer.AddBool("visible_primary", False)
        self.writer.AddBool("cast_shadow", True)
        self.writer.AddRef("element", elementName + "_light")
        self.writer.AddMatrix("transform", obj.matrix_world)
        self.writer.AddMatrix("motion_transform", obj.matrix_world)
        self.writer.EndNode()

        self.mElInstances.append(instName)

    def AddSun(self, obj, scene):
        elementName = obj.name

        lamp = obj.data
        self.writer.BeginNode("directlight", elementName + "_light")
        self.writer.AddScaler("intensity", lamp.energy)
        self.writer.AddEnum("face", "both")
        self.writer.AddColor("color", lamp.color)
        self.writer.AddScaler("hardness", 0.9998);
        self.writer.AddInt("samples", 16)
        self.writer.EndNode()

        instName = elementName + "_inst"
        self.writer.BeginNode("instance", instName)
        self.writer.AddBool("visible_primary", True)
        self.writer.AddBool("cast_shadow", False)
        self.writer.AddBool("shadow", True)
        self.writer.AddRef("element", elementName + "_light")
        self.writer.AddMatrix("transform", obj.matrix_world)
        self.writer.AddMatrix("motion_transform", obj.matrix_world)
        self.writer.EndNode()

        self.mElInstances.append(instName)

    def AddMaterial(self, obj, scene):
        if obj.type != 'MESH':
            return

        if len(obj.material_slots) == 0:
            return "GlobalMaterial"

        material = obj.material_slots[0].material

        if material == None:
            print("Error Material Obj:%s Num Slot:%d"%(obj.name, len(obj.material_slots)))
            return "GlobalMaterial"

        elara_mat = material.elara_mat

        shaderName = material.name

        self.writer.BeginNode("max_ei_standard", shaderName + "_std")
        self.writer.AddColor("diffuse_color", elara_mat.diffuse_color)
        self.writer.AddScaler("diffuse_weight", elara_mat.diffuse_weight)
        self.writer.AddScaler("roughness", elara_mat.roughness)
        self.writer.AddScaler("backlighting_weight", elara_mat.backlighting_weight)

        self.writer.AddColor("specular_color", elara_mat.specular_color)
        self.writer.AddScaler("specular_weight", elara_mat.specular_weight)
        self.writer.AddScaler("specular_mode", elara_mat.specular_mode)
        self.writer.AddScaler("glossiness", elara_mat.glossiness)
        self.writer.AddScaler("anisotropy", elara_mat.anisotropy)
        self.writer.AddScaler("rotation", elara_mat.rotation)
        self.writer.AddScaler("fresnel_ior_glossy", elara_mat.fresnel_ior_glossy)

        self.writer.AddColor("transparency_color", elara_mat.transparency_color)
        self.writer.AddScaler("transparency_weight", elara_mat.transparency_weight)

        self.writer.AddColor("reflection_color", elara_mat.reflection_color)
        self.writer.AddScaler("reflection_weight", elara_mat.reflection_weight)
        self.writer.AddScaler("fresnel_ior", elara_mat.fresnel_ior)

        self.writer.AddColor("refraction_color", elara_mat.refraction_color)
        self.writer.AddScaler("refraction_weight", elara_mat.refraction_weight)
        self.writer.AddScaler("refraction_glossiness", elara_mat.refraction_glossiness)
        self.writer.AddScaler("ior", elara_mat.ior)
        self.writer.EndNode()


        self.writer.BeginNode("max_result", shaderName + "_result")
        self.writer.LinkParam("input", shaderName + "_std", "result")
        self.writer.EndNode();

        shaderNames = [shaderName + "_result"]

        self.writer.BeginNode("osl_shadergroup", shaderName + "_group")
        self.writer.AddRefGroup("nodes", shaderNames)
        self.writer.EndNode()

        matName = shaderName + "_mat"
        self.writer.BeginNode("material", matName)
        self.writer.AddRef("surface_shader", shaderName + "_group")
        self.writer.EndNode()

        return matName