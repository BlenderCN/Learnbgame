# coding=UTF-8

import bpy
import os
from bpy.types import Operator, AddonPreferences, Panel, PropertyGroup

def get_preferences():
    name = get_addon_name()
    return bpy.context.user_preferences.addons[name].preferences

def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))

def assignMaterial():
    os.system('cls')

# inital setting
    tex_folder = bpy.context.scene.AutoPBRMapper_setting.filepath
    ext = bpy.context.scene.AutoPBRMapper_setting.filename_ext

    mBaseColor = bpy.context.scene.AutoPBRMapper_setting.suffix_basecolor
    mMetallic = bpy.context.scene.AutoPBRMapper_setting.suffix_metallic
    mSpecular = bpy.context.scene.AutoPBRMapper_setting.suffix_specular
    mRoughness = bpy.context.scene.AutoPBRMapper_setting.suffix_roughness
    mOpacity = bpy.context.scene.AutoPBRMapper_setting.suffix_opacity
    mNormal = bpy.context.scene.AutoPBRMapper_setting.suffix_normal
    
    mMaterialtype = bpy.context.scene.AutoPBRMapper_setting.materialtype
    mAssigntype = bpy.context.scene.AutoPBRMapper_setting.assigntype

    marggin = 100

    print (mAssigntype)

    if mAssigntype == 'All':
        materials = bpy.data.materials
    elif mAssigntype == 'Selected':
        selectedObjects = bpy.context.selected_objects
        materials = []
        for object in selectedObjects:
            material_slots = object.material_slots
            for slot in material_slots:
                materials.append(slot.material)


    for material in materials:
        main_name = material.name
        tempPathA = (tex_folder + '\\' + main_name + mBaseColor + ext)

        if material.use_nodes is not True:
            material.use_nodes = True
        # Test if path available
        if os.path.isfile(tempPathA):

            mat_nodes = material.node_tree.nodes
            mat_links = material.node_tree.links

            mat_nodes.clear() # remove all before create our own
            output_shader = mat_nodes.new("ShaderNodeOutputMaterial")

            mix = mat_nodes.new("ShaderNodeMixShader")
            mix.location = (-1 * (mix.width + marggin), 150)

            transparent = mat_nodes.new("ShaderNodeBsdfTransparent")
            transparent.location = (-1 * 2 *(transparent.width + marggin), 150)

            main_shader = mat_nodes.new("ShaderNodeBsdfPrincipled")
            main_shader.location = (-1 * 2 * (main_shader.width + marggin), 0)


            tex_base_color = mat_nodes.new("ShaderNodeTexImage")
            try:
                tex_base_color.image = bpy.data.images.load(os.path.join(tex_folder, (main_name + mBaseColor + ext)), check_existing=True)
            except RuntimeError as e:
                print(main_name + " has no baseColor map.\n" + str(e))
            tex_base_color.hide = True
            tex_base_color.location = (-1 * 3 * (tex_base_color.width + marggin), 0)


            tex_metallic = mat_nodes.new("ShaderNodeTexImage")
            try:
                tex_metallic.image = bpy.data.images.load(os.path.join(tex_folder, (main_name + mMetallic + ext)), check_existing=True)
            except RuntimeError as e:
                print(main_name + " has no metallic map.\n" + str(e))
            tex_metallic.color_space="NONE"
            tex_metallic.hide = True
            tex_metallic.location = (-1 * 4 * (tex_metallic.width + marggin), 0)


            tex_specular = mat_nodes.new("ShaderNodeTexImage")
            try:
                tex_specular.image = bpy.data.images.load(os.path.join(tex_folder, (main_name + mSpecular + ext)), check_existing=True)
            except RuntimeError as e:
                print(main_name + " has no specular map.\n" + str(e))
            tex_specular.color_space = "NONE"
            tex_specular.hide = True
            tex_specular.location = (-1 * 5 * (tex_specular.width + marggin), 0)


            tex_roughness = mat_nodes.new("ShaderNodeTexImage")
            try:
                tex_roughness.image = bpy.data.images.load(os.path.join(tex_folder, (main_name + mRoughness + ext)), check_existing=True)
            except RuntimeError as e:
                print(main_name + " has no roughness map.\n" + str(e))
            tex_roughness.color_space="NONE"
            tex_roughness.hide = True
            tex_roughness.location = (-1 * 6 * (tex_roughness.width + marggin), 0)


            opcity_exist = True
            tex_opacity = mat_nodes.new("ShaderNodeTexImage")
            try:
                tex_opacity.image = bpy.data.images.load(os.path.join(tex_folder, (main_name + mOpacity + ext)), check_existing=True)
            except RuntimeError as e:
                opcity_exist = False
                print(main_name + " has no opacity map.\n" + str(e))
            tex_opacity.color_space = "NONE"
            tex_opacity.hide = True
            tex_opacity.location = (-1 * 2 * (tex_opacity.width + marggin), 300)


            tex_normal = mat_nodes.new("ShaderNodeTexImage")
            try:
                tex_normal.image = bpy.data.images.load(os.path.join(tex_folder, (main_name + mNormal + ext)), check_existing=True)
            except RuntimeError as e:
                print(main_name + " has no normal map.\n" + str(e))
            tex_normal.color_space = "NONE"
            tex_normal.hide = True
            tex_normal.location = (-1 * 6.5 * (tex_normal.width + marggin), -400)


            # unitity nodes
            bump = mat_nodes.new("ShaderNodeBump")
            bump.location = (-1 * 4 * (bump.width + marggin), -400)
            normal_map = mat_nodes.new("ShaderNodeNormalMap")
            normal_map.location = (-1 * 5 * (normal_map.width + marggin), -400)
            combin = mat_nodes.new("ShaderNodeCombineRGB")
            combin.location = (-1 * 6 * (combin.width + marggin), -400)
            invert = mat_nodes.new("ShaderNodeInvert")
            invert.location = (-1 * 7 *(invert.width + marggin), -400)
            sp = mat_nodes.new("ShaderNodeSeparateRGB")
            sp.location = (-1 * 8 * (sp.width + marggin), -400)

            # link

            mat_links.new(tex_base_color.outputs["Color"], main_shader.inputs["Base Color"])
            mat_links.new(tex_metallic.outputs["Color"], main_shader.inputs["Metallic"])
            mat_links.new(tex_specular.outputs["Color"], main_shader.inputs["Specular"])
            mat_links.new(tex_roughness.outputs["Color"], main_shader.inputs["Roughness"])
      
            if opcity_exist:
                mat_links.new(tex_opacity.outputs["Color"], mix.inputs[0])

            if mMaterialtype == 'Principle':
                mat_links.new(mix.outputs["Shader"], output_shader.inputs["Surface"])
                mat_links.new(transparent.outputs["BSDF"], mix.inputs[1])
                mat_links.new(main_shader.outputs["BSDF"], mix.inputs[2])
                mat_links.new(bump.outputs["Normal"], main_shader.inputs["Normal"])
                mat_links.new(normal_map.outputs["Normal"], bump.inputs["Normal"])
                mat_links.new(combin.outputs["Image"], normal_map.inputs["Color"])
                mat_links.new(sp.outputs["R"], combin.inputs["R"])
                mat_links.new(sp.outputs["B"], combin.inputs["B"])
                mat_links.new(sp.outputs["G"], invert.inputs["Color"])
                mat_links.new(invert.outputs["Color"], combin.inputs["G"])
                mat_links.new(tex_normal.outputs["Color"], sp.inputs["Image"])

            elif mMaterialtype == 'gltf' :
                mat_links.new(main_shader.outputs["BSDF"], output_shader.inputs["Surface"])
                mat_links.new(bump.outputs["Normal"], main_shader.inputs["Normal"])
                mat_links.new(normal_map.outputs["Normal"], bump.inputs["Normal"])
                mat_links.new(tex_normal.outputs["Color"], normal_map.inputs["Color"])
                



            # print
            # print ( 'Material:{0} -- auto PBR assigned Success '.format(main_name) )

class AutoPBRMapper_Preferences(bpy.types.AddonPreferences):
    bl_idname = get_addon_name()

    suffix_basecolor: bpy.props.StringProperty(
        default="_BaseColor",
        name="BaseColor Suffix",
    )
    suffix_normal: bpy.props.StringProperty(
        default="_Normal",
        name="Normal Suffix"
    )
    suffix_metallic: bpy.props.StringProperty(
        default="_Metallic",
        name="Metallic Suffix"
    )
    suffix_roughnes: bpy.props.StringProperty(
        default="_Roughness",
        name="Roughnes Suffix"
    )
    suffix_specular: bpy.props.StringProperty(
        default="_Specular",
        name="Specular Suffix"
    )
    suffix_opacity: bpy.props.StringProperty(
        default="_Opacity",
        name="Opacity Suffix"
    )
    filename_ext : bpy.props.EnumProperty(
        items = [
            ('.png','.png','*.png'),
            ('.jpg','.jpg','*.jpg')
            
        ],
        name = 'File Extension'
    )
    materialtype: bpy.props.EnumProperty(
        items = [
            ('Principle','Principle','Principle for cycles or Eevee'),
            ('gltf','gltf','gltf for babylon js')
        
        ],
        name = 'Material Type'
    )

    preferences_tabs =  [("GENERAL", "General", ""),
                        ("KEYMAPS", "Keymaps", ""),
                        ("ABOUT", "About", "")]

    # tabs: bpy.props.EnumProperty(name="Tabs", items=preferences_tabs, default="GENERAL")

    # def draw(self, context):
    #     layout = self.layout
    #     layout.label(text="Auto PBR Map Importer Settings")

    #     column = layout.column(align=True)
    #     row = column.row()
    #     row.prop(self, "tabs", expand=True)

    #     box = column.box()
    #     split = box.split(factor = 0.75)
    #     groupBox = split.box()
    #     groupBox.label(text="Map FileName Setting")

    #     column = groupBox.column(align=True)
    #     column.prop(self, "suffix_basecolor")
    #     column.prop(self, "suffix_normal")
    #     column.prop(self, "suffix_metallic")
    #     column.prop(self, "suffix_roughnes")
    #     column.prop(self, "suffix_specular")
    #     column.prop(self, "suffix_opacity")
    #     row = groupBox.row(align=True)
    #     row.label(text="File Extension")
    #     row.prop(self, "filename_ext", expand=True)

    #     groupBox = split.box()
    #     groupBox.label(text="Material Type")
    #     column = groupBox.column(align=True)
    #     column.prop(self, "materialtype", expand=True)

class AutoPBRMapper_properties(bpy.types.PropertyGroup):

    filepath : bpy.props.StringProperty(
        default = "c:\\temp\\",
        subtype="FILE_PATH",
        name = "Texture Folder"
    )
    suffix_basecolor : bpy.props.StringProperty(
        default = "_BaseColor",
        name = "BaseColor Suffix",
    )
    suffix_normal : bpy.props.StringProperty(
        default = "_Normal",
        name = "Normal Suffix",
    )
    suffix_metallic: bpy.props.StringProperty(
        default = "_Metallic",
        name = "Metallic Suffix",
    )
    suffix_roughness : bpy.props.StringProperty(
        default = "_Roughness",
        name = "Roughness Suffix",
    )
    suffix_specular: bpy.props.StringProperty(
        default = "_Specular",
        name = "Specular Suffix"
    )
    suffix_opacity: bpy.props.StringProperty(
        default = "_Opacity",
        name = "Opacity Suffix"
    )
    filename_ext : bpy.props.EnumProperty(
        items = [
            ('.png','.png','*.png'),
            ('.jpg','.jpg','*.jpg')
            
        ],
        name = 'File Extension'
    )
    materialtype : bpy.props.EnumProperty(
        items = [
            ('Principle','Principle','Principle for cycles or Eevee'),
            ('gltf','gltf','gltf for babylon js')
        
        ],
        name = 'Material Type'
    )
    assigntype : bpy.props.EnumProperty(
        items = [
            ('All','All','Assign to all object'),
            ('Selected','Selected','Assign selected object only')
        
        ],
        name = 'Assign Type'
    )

class AutoPBRMapper_Actions(bpy.types.Operator):
    """ Actions """
    bl_label ="AutoPBRMapper Operator"
    bl_idname = "autopbrmapper.actions"

    button : bpy.props.StringProperty(default="")
    texturepath : bpy.props.StringProperty(default="")
    # texturepath : bpy.context.scene.AutoPBRMapper_setting.filepath

    def execute(self, context):
        button=self.button
        try:
            ## ObjectOperator
            if button=="AssignMaterial": 
                assignMaterial()
        
            else:
                print ('Not defined !')
        except Exception as e:
            print ('Execute Error:',e)
        
        return {"FINISHED"}

class AutoPBRMapper_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_idname = "AutoPBRMapper_PT_setup"
    bl_region_type = "UI"
    bl_category = "AutoPBRMapper"
    bl_label = "AutoPBRMapper"
    # bl_options = {"DEFAULT_CLOSED"}   

    
    def draw(self,context):

        layout = self.layout
        row = layout.row(align = True)
        #layout.label('Mesh Tools')
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "filepath")
        row = layout.row(align = True)
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "suffix_basecolor")
        row = layout.row(align = True)
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "suffix_normal")
        row = layout.row(align = True)
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "suffix_metallic")
        row = layout.row(align = True)
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "suffix_roughness")
        row = layout.row(align = True)
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "suffix_specular")
        row = layout.row(align = True)
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "suffix_opacity") 
        row = layout.row(align = True)
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "filename_ext", expand=True)        
        row = layout.row(align = True) 
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "materialtype", expand=True)        
        row = layout.row(align = True) 
        row.prop(bpy.context.scene.AutoPBRMapper_setting , "assigntype", expand=True)  
        row = layout.row(align = True) 
        row.operator('autopbrmapper.actions',text = 'Assign Materials').button = 'AssignMaterial'