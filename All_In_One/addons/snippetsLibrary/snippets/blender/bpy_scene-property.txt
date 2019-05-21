#propertyref:https://docs.blender.org/api/blender_python_api_2_77_0/bpy.props.html
bpy.types.Scene.variable_name = bpy.props.BoolProperty(name="use custom path")

#all type
bpy.types.Scene.Bool_variable_name = bpy.props.BoolProperty(name="", description="", default=False, options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None)
bpy.types.Scene.BoolVector_variable_name = bpy.props.BoolVectorProperty(name="", description="", default=(False, False, False), options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None, set=None)
bpy.types.Scene.Collection_variable_name = bpy.props.CollectionProperty(type=None, name="", description="", options={'ANIMATABLE'})
bpy.types.Scene.Enum_variable_name = bpy.props.EnumProperty(items, name="", description="", default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
bpy.types.Scene.Float_variable_name = bpy.props.FloatProperty(name="", description="", default=0.0, min=sys.float_info.min, max=sys.float_info.max, soft_min=sys.float_info.min, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, subtype='NONE', unit='NONE', update=None, get=None, set=None)
bpy.types.Scene.FloatVector_variable_name = bpy.props.FloatVectorProperty(name="", description="", default=(0.0, 0.0, 0.0), min=sys.float_info.min, max=sys.float_info.max, soft_min=sys.float_info.min, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, subtype='NONE', unit='NONE', size=3, update=None, get=None, set=None)
bpy.types.Scene.Int_variable_name = bpy.props.IntProperty(name="", description="", default=0, min=-2**31, max=2**31-1, soft_min=-2**31, soft_max=2**31-1, step=1, options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None)
bpy.types.Scene.IntVector_variable_name = bpy.props.IntVectorProperty(name="", description="", default=(0, 0, 0), min=-2**31, max=2**31-1, soft_min=-2**31, soft_max=2**31-1, step=1, options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None, set=None)
bpy.types.Scene.String_variable_name = bpy.props.StringProperty(name="", description="", default="", maxlen=0, options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None)
#usage exemple
## on top of execute function
bpy.types.Scene.bgref_to_camera = bpy.props.BoolProperty(name="In camera", description='set BG img to camera\n(All view if not)', default=True)

## in the Panel layout
layout.prop(context.scene, "bgref_to_camera")