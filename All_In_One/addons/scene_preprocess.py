bl_info = {
    'name': 'Scene Preprocess',
    'description': 'Preprocess utils',
    'author': 'StevenZhang(zhzhxtrrk@gmail.com)',
    'version': (0, 1),
    'blender': (2, 6, 0),
    'api': 39685,
    'tracker_url' : '',
    "category": "Learnbgame",
}

import bpy

class SceneProcess(bpy.types.Operator):
    bl_label = "Make all shadeless"
    bl_idname = "scene_preprocess.process"

    def invoke(self, context, event):
        for m in bpy.data.materials:
            m.use_shadeless = True
        return {"FINISHED"}
    

class DeSceneProcess(bpy.types.Operator):
    bl_label = "Make all shade"
    bl_idname = "scene_preprocess.deprocess"

    def invoke(self, context, event):
        for m in bpy.data.materials:
            m.use_shadeless = False
        return {"FINISHED"}

    
class IrrProcess(bpy.types.Operator):
    bl_label = "Disable irrlicht lighting"
    bl_idname = "scene_preprocess.irrlighting"
    
    def invoke(self, context, event):
        for m in bpy.data.materials:
            m.irrb_lighting = False
        return {"FINISHED"}


class DeIrrProcess(bpy.types.Operator):
    bl_label = "Enable irrlicht lighting"
    bl_idname = "scene_preprocess.deirrlighting"

    def invoke(self, context, event):
        for m in bpy.data.materials:
            m.irrb_lighting = True
        return {"FINISHED"}
    
    
class OriginProcess(bpy.types.Operator):
    bl_label = "Separate origin"
    bl_idname = "scene_preprocess.origin"
    
    def invoke(self, context, event):
        for o in context.scene.objects:
            o.select = True
            context.scene.objects.active = o
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
        return {"FINISHED"}


class AlphaProcess(bpy.types.Operator):
    bl_label = "Process transparency objects"
    bl_idname = "scene_preprocess.alpha"

    def invoke(self, context, event):
        for m in bpy.data.materials:
            if m.name.startswith("a_"):
                m.irrb_type = "EMT_TRANSPARENT_ALPHA_CHANNEL"
                m.irrb_zwrite_enable = context.scene.spp_allow_zwrite_on_transparent
                m.irrb_backcull = False
        return {"FINISHED"}
    
        
class ScenePreprocessPanel(bpy.types.Panel):
    bl_label = "Scene processor"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align = True)

        row = col.row(align = True)
        row.operator(SceneProcess.bl_idname)
        row.operator(DeSceneProcess.bl_idname)

        row = col.row(align = True)
        row.operator(IrrProcess.bl_idname)
        row.operator(DeIrrProcess.bl_idname)

        col.operator(OriginProcess.bl_idname)

        col = layout.column(align = True)
        col.prop(context.scene, "spp_allow_zwrite_on_transparent")
        col.operator(AlphaProcess.bl_idname)


def register():
    bpy.types.Scene.spp_allow_zwrite_on_transparent = bpy.props.BoolProperty(
        name = "Allow ZWrite", default = True)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
