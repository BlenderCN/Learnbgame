import bpy

class Westwood3DMaterialPass(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Name")
    ambient = bpy.props.FloatVectorProperty(name="Ambient Color", subtype='COLOR', min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, default=(1.0, 1.0, 1.0))
    diffuse = bpy.props.FloatVectorProperty(name="Diffuse Color", subtype='COLOR', min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, default=(1.0, 1.0, 1.0))
    specular = bpy.props.FloatVectorProperty(name="Specular Color", subtype='COLOR', min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, default=(0.0, 0.0, 0.0))
    emissive = bpy.props.FloatVectorProperty(name="Emissive Color", subtype='COLOR', min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, default=(0.0, 0.0, 0.0))
    shininess = bpy.props.FloatProperty(name="Shininess", default=1.0, min=0.0, max=100.0, soft_min=0.0, soft_max=100.0)
    opacity = bpy.props.FloatProperty(name="Opacity", default=1.0, min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
    translucency = bpy.props.FloatProperty(name="Translucency", min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
    
    mapping0 = bpy.props.EnumProperty(name="",
    items=[
        ("0", "UV", ""),
        ("1", "Environment", ""),
        ("2", "Cheap Environment", ""),
        ("3", "Screen", ""),
        ("4", "Linear Offset", ""),
        ("5", "Silhouette", ""),
        ("6", "Scale", ""),
        ("7", "Grid", ""),
        ("8", "Rotate", ""),
        ("9", "Sine Linear Offset", ""),
        ("10", "Step Linear Offset", ""),
        ("11", "Zigzag Linear Offset", ""),
        ("12", "WS Classic Env", ""),
        ("13", "WS Environment", ""),
        ("14", "Grid Classic Env", ""),
        ("15", "Grid Environment", ""),
        ("16", "Random", ""),
        ("17", "Edge", ""),
        ("18", "Bump Environment", "")
    ], default='0')
    mapping1 = bpy.props.EnumProperty(name="",
    items=[
        ("0", "UV", ""),
        ("1", "Environment", ""),
        ("2", "Cheap Environment", ""),
        ("3", "Screen", ""),
        ("4", "Linear Offset", ""),
        ("5", "Silhouette", ""),
        ("6", "Scale", ""),
        ("7", "Grid", ""),
        ("8", "Rotate", ""),
        ("9", "Sine Linear Offset", ""),
        ("10", "Step Linear Offset", ""),
        ("11", "Zigzag Linear Offset", ""),
        ("12", "WS Classic Env", ""),
        ("13", "WS Environment", ""),
        ("14", "Grid Classic Env", ""),
        ("15", "Grid Environment", ""),
        ("16", "Random", ""),
        ("17", "Edge", ""),
        ("18", "Bump Environment", "")
    ], default='0')
    stage0 = bpy.props.StringProperty(name="")
    stage1 = bpy.props.StringProperty(name="")
    
    srcblend = bpy.props.StringProperty(name="Src Blend")
    destblend = bpy.props.StringProperty(name="Dest Blend")
    depthmask = bpy.props.BoolProperty(name="Write ZBuffer", default=True)
    alphatest = bpy.props.BoolProperty(name="Alpha Test", default=False)
    
    
    # blend = bpy.props.EnumProperty(name="Blend", description="Blend presets",
    # items=[
        # ("1", "Opaque", ""),
        # ("2", "Add", ""),
        # ("3", "Multiply", ""),
        # ("4", "Multiply and Add", ""),
        # ("5", "Screen", ""),
        # ("6", "Alpha Blend", ""),
        # ("7", "Alpha Test", ""),
        # ("8", "Alpha Test and Blend", ""),
        # ("0", "[Custom]", ""),
    # ], default='1')
    

class Westwood3DMaterial(bpy.types.PropertyGroup):
    def change_mpass_count(self, context):
        while len(self.mpass) < self.mpass_count:
            self.mpass.add()
        while len(self.mpass) > self.mpass_count:
            self.mpass.remove(len(self.mpass) - 1)
        self.change_mpass_index(context)
    
    def change_mpass_index(self, context):
        if len(self.mpass) > 0:
            if self.mpass_index > len(self.mpass):
                self.mpass_index = len(self.mpass)
        elif self.mpass_index != 1:
            self.mpass_index = 1
    
    mpass = bpy.props.CollectionProperty(type=Westwood3DMaterialPass)
    mpass_index = bpy.props.IntProperty(name="Pass", min=1, max=4, update=change_mpass_index)
    mpass_count = bpy.props.IntProperty(name="Pass Count", min=0, max=4, update=change_mpass_count)
    sort_level = bpy.props.IntProperty(name="Sort Level", min=0)
    surface_type = bpy.props.EnumProperty(name="Surface", description="Surface types cause a range of effects, e.g. tiberium hurts you and is crunchy.",
    items=[
        ("0", "Light Metal", ""),
        ("1", "Heavy Metal", ""),
        ("2", "Water", ""),
        ("3", "Sand", ""),
        ("4", "Dirt", ""),
        ("5", "Mud", ""),
        ("6", "Grass", ""),
        ("7", "Wood", ""),
        ("8", "Concrete", ""),
        ("9", "Flesh", ""),
        ("10", "Rock", ""),
        ("11", "Snow", ""),
        ("12", "Ice", ""),
        ("13", "Default", ""),
        ("14", "Glass", ""),
        ("15", "Cloth", ""),
        ("16", "Tiberium Field", ""),
        ("17", "Foliage Permeable", ""),
        ("18", "Glass Permeable", ""),
        ("19", "Ice Permeable", ""),
        ("20", "Cloth Permeable", ""),
        ("21", "Electrical", ""),
        ("22", "Flammable", ""),
        ("23", "Steam", ""),
        ("24", "Electrical Permeable", ""),
        ("25", "Flammable Permeable", ""),
        ("26", "Steam Permeable", ""),
        ("27", "Water Permeable", ""),
        ("28", "Tiberium Water", ""),
        ("29", "Tiberium Water Permeable", ""),
        ("30", "Underwater Dirt", ""),
        ("31", "Underwater Tiberium Dirt", ""),
    ], default='13')

class Westwood3DMaterialPassEdit(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "material.mpassadd"
    bl_label = "MaterialPassEdit"
    
    add = bpy.props.BoolProperty(default = True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        w3d = context.material.westwood3d
        w3d.mpass.add()
        return {'FINISHED'}


class MATERIAL_PT_westwood3d(bpy.types.Panel):
    """Creates a Panel in the Material properties window"""
    bl_label = 'Westwood3D'
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'material'
    
    @classmethod
    def poll(cls, context):
        return (context.material is not None)

    def draw(self, context):
        mat = context.material
        me = context.object.data
        w3d = mat.westwood3d
        
        layout = self.layout
        col = layout.column()
        
        col.prop(w3d, "surface_type")
        col.prop(w3d, "sort_level")
        col.separator()
        col.prop(w3d, "mpass_count")
        col.separator()
        
        if len(w3d.mpass) > 0:
            mpass = w3d.mpass[w3d.mpass_index - 1]
            box = col.box()
            box.prop(w3d, "mpass_index")
            
            box.prop(mpass, "name")
            #box.prop(mpass, "blend")
            split = box.split()
            col = split.column()
            col.prop(mpass, "diffuse")
            col.prop(mpass, "ambient")
            col = split.column()
            col.prop(mpass, "specular")
            col.prop(mpass, "emissive")
            
            box.prop(mpass, "opacity")
            box.prop(mpass, "translucency")
            box.prop(mpass, "shininess")
            
            stbox = box.box()
            stbox.prop(mpass, "srcblend")
            stbox.prop(mpass, "destblend")
            stbox.prop(mpass, "depthmask")
            stbox.prop(mpass, "alphatest")
            
            stbox = box.box()
            split = stbox.split()
            split.label("Stage 0")
            split.prop(mpass, "mapping0")
            stbox.prop_search(mpass, "stage0", bpy.data, "textures")
            stbox = box.box()
            split = stbox.split()
            split.label("Stage 1")
            split.prop(mpass, "mapping1")
            stbox.prop_search(mpass, "stage1", bpy.data, "textures")