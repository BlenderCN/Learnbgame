import bpy
import os

from . list.list_utils import get_hi_res_prop
from . list.list_data import HiObjListPropertyGroup, LowObjListPropertyGroup
from . draw import Draw
from bpy.props import StringProperty, PointerProperty, BoolProperty, \
                      IntProperty, EnumProperty, CollectionProperty
from bpy.types import PropertyGroup, Object, Mesh, Scene, WindowManager
from bpy.utils import register_class, unregister_class

class ObjIdPropertyGroup(PropertyGroup):
    id = StringProperty(name="id", default="Id")
    object = StringProperty(name="object name", default="Object")

class MeshPropertyGroup(PropertyGroup):
    mesh = PointerProperty(name="mesh", type=Mesh)

class ObjectPropertyGroup(PropertyGroup):
    object = PointerProperty(name="object", type=Object)

class ActivePropertyGroup(PropertyGroup):
    object = PointerProperty(type=Object)
    select = BoolProperty(default=False)

class TagEdgePropertyGroup(PropertyGroup):
    def get_tag(self, type):
        return bpy.context.scene.tool_settings.edge_path_mode == type

    def set_tag(self, value, type):
        bpy.context.scene.tool_settings.edge_path_mode = (type if value else 'SELECT')

    sharp = BoolProperty(default=False,
                                   get=lambda self: self.get_tag('SHARP'),
                                   set=lambda self, value: self.set_tag(value, 'SHARP'))
    seam = BoolProperty(default=False,
                                   get=lambda self: self.get_tag('SEAM'),
                                   set=lambda self, value: self.set_tag(value, 'SEAM'))

class SnapPropertyGroup(PropertyGroup):
    def get_snap(self, type):
        ts = bpy.context.scene.tool_settings
        ret = True
        if type == 'FACE':
            ret = ret and ts.snap_element == type
            ret = ret and ts.use_snap_project
            ret = ret and ts.use_snap_align_rotation
            ret = ret and not ts.use_snap_self
        if type == 'VERTEX':
            ret = ret and ts.snap_element == type
            ret = ret and not ts.use_snap_align_rotation
            ret = ret and not ts.use_snap_self

        return ret

    def set_snap(self, value, type):
        ts = bpy.context.scene.tool_settings
        if type == 'FACE':
            ts.snap_element = type
            ts.use_snap_project = True
            ts.use_snap_align_rotation = True
            ts.use_snap_self = False
        if type == 'VERTEX':
            ts.snap_element = type
            ts.use_snap_align_rotation = False
            ts.use_snap_self = False

    vertex = BoolProperty(default=False,
                                    description="Align rotation = False\nSnap onto itself = True",
                                    get=lambda self: self.get_snap('VERTEX'),
                                    set=lambda self, value: self.set_snap(value, 'VERTEX'))
    face = BoolProperty(default=False,
                                  description="Project individual elements = True\n" + \
                                              "Align rotation = True\n" + \
                                              "Snap onto itself = False",
                                  get=lambda self: self.get_snap('FACE'),
                                  set=lambda self, value: self.set_snap(value, 'FACE'))

class SwapPropertyGroup(PropertyGroup):
    def swap(self, objs, high):
        for o in objs:
            if high:
                o.object.data = o.object.Jet.high_mesh
            else:
                o.object.data = o.object.Jet.opt_mesh

    def update_model(self, context):
        j = context.scene.Jet
        j.high_res = (j.swap.model=='hi')
        self.swap(j.opt_high_objs, j.high_res)

    model = EnumProperty(default='proxy', items=[
                                    ('proxy', 'Proxy', 'Proxy'),
                                    ('hi', 'Hi-Res', 'Hi-Res')],
                                   update=lambda self, context: self.update_model(context))

class InfoPropertyGroup(PropertyGroup):
    drawing = Draw()
    do_update = BoolProperty(default=True)

    retopology_text = "After you have a high resolution model, you need to create a lower resolution one that mimics its shape." \
                "\n\nYou do this by creating a new topology that adapts to the high resolution model's shape using snapping tools, " \
                "\nand this process is called 'Retopology' or 'Retopo'." \
                "\n\n(Press the button for more info.)"

    optimization_text = "When working for videogames, you usually have a 'polygon budget'." \
                        "\n\nIn the optimization process you'll take the model resulting from 'Retopo', and reduce polygons " \
                        "\nas necessary until you have the appropriate number of polygons." \
                        "\n\n(Press the button for more info.)"

    smooth_sharp_text = "Not all edges are equal, and especially when you're dealing with low resolution models, smoothing " \
                        "\ncan create some weird gradients in the surface." \
                        "\n\nTo avoid that, the sharpest corners of your model should be marked as sharp." \
                        "\n\n(Press the button for more info.)"

    uvs_text = "This is the part of the process in which you have to define how textures will be projected onto your model. " \
               "\n\nIn order to do that, you must unwrap and unfold it so you can turn a 2D image into a 3D model later." \
               "\n\n(Press the button for more info.)"

    model_prep_text = "Once you have your high and low resolution models, you'll need to bake the details from the high " \
                      "\nresolution onto the low resolution's UVs. " \
                      "\n\nBut before you set everything up, it's a good idea to prepare your models for easing the next stage " \
                      "\n(especially if you're working with extremely high polygon models). " \
                      "\n\n(Press the button for more info.)"

    bake_sets_creation_text = "Each low resolution object typically encompasses several smaller high resolution models." \
                              "\n\nCreate bake sets to assign a series of high resolution objects to a low resolution one," \
                              "\nand then you'll be able to control them easily during the bake setup." \
                              "\n\n(Press the button for more info.)"

    def reset_others(self, origin):
        self.do_update = False
        if origin!="retopology":
            self.retopology = False
        if origin != "optimization":
            self.optimization = False
        if origin != "smoothing_sharpening":
            self.smoothing_sharpening = False
        if origin != "uvs":
            self.uvs = False
        if origin != "model_preparation":
            self.model_preparation = False
        if origin != "bake_sets_creation":
            self.bake_sets_creation = False
        self.do_update = True

    def get_text(self, origin):
        loc = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), "info"))
        file = open(os.path.join(loc, origin), 'r')
        return file.read()

    def update(self, context, origin):
        if not self.do_update:
            return

        self.reset_others(origin)

        value = getattr(self, origin)
        if value:
            self.drawing.hide_info(context)
            text = self.get_text(origin)
            self.drawing.display_info(context, text)
        else:
            self.drawing.hide_info(context)

    retopology = BoolProperty(default=False,
        description=retopology_text,
        update=lambda self, context: self.update(context, "retopology"))
    optimization = BoolProperty(default=False,
        description=optimization_text,
        update=lambda self, context: self.update(context, "optimization"))
    smoothing_sharpening = BoolProperty(default=False,
        description=smooth_sharp_text,
        update=lambda self, context: self.update(context, "smoothing_sharpening"))
    uvs = BoolProperty(default=False,
        description=uvs_text,
        update=lambda self, context: self.update(context, "uvs"))
    model_preparation = BoolProperty(default=False,
        description=model_prep_text,
        update=lambda self, context: self.update(context, "model_preparation"))
    bake_sets_creation = BoolProperty(default=False,
        description=bake_sets_creation_text,
        update=lambda self, context: self.update(context, "bake_sets_creation"))

#Scene
class ScnJetPropertyGroup(PropertyGroup):
    list_low_res = PointerProperty(type=LowObjListPropertyGroup)

    high_res_file = StringProperty(name="", default="")
    optimized_res_file = StringProperty(name="", default="")

    opt_high_objs = CollectionProperty(type=ObjectPropertyGroup)
    opt_meshes = CollectionProperty(type=MeshPropertyGroup)
    high_meshes = CollectionProperty(type=MeshPropertyGroup)

    high_res = BoolProperty(options={'HIDDEN'}, default=False)
    remove_subsurf = BoolProperty(options={'HIDDEN'}, default=True)

    autosmooth = IntProperty(default=180, max=180, min=0)
    decimate_ratio = IntProperty(default=10, max=100, min=0)
    subdivisions = IntProperty(default=2, max=10, min=0)

    mesh_objs = IntProperty(default=0)

    tag = PointerProperty(type=TagEdgePropertyGroup)
    snap = PointerProperty(type=SnapPropertyGroup)
    swap = PointerProperty(type=SwapPropertyGroup)
    info = PointerProperty(type=InfoPropertyGroup)
    active = PointerProperty(type=ActivePropertyGroup)

#Object
class ObjJetPropertyGroup(PropertyGroup):
    opt_mesh = PointerProperty(type=Mesh)
    high_mesh = PointerProperty(type=Mesh)

class WMJetPropertyGroup(PropertyGroup):
    timer = BoolProperty(default=False)

def register():
    register_class(WMJetPropertyGroup)
    register_class(SnapPropertyGroup)
    register_class(InfoPropertyGroup)
    register_class(SwapPropertyGroup)
    register_class(TagEdgePropertyGroup)
    register_class(MeshPropertyGroup)
    register_class(ObjectPropertyGroup)
    register_class(ActivePropertyGroup)
    register_class(ObjIdPropertyGroup)
    register_class(ObjJetPropertyGroup)
    register_class(ScnJetPropertyGroup)

    Scene.Jet = PointerProperty(options={'HIDDEN'}, type=ScnJetPropertyGroup)
    Object.Jet = PointerProperty(options={'HIDDEN'}, type=ObjJetPropertyGroup)
    WindowManager.Jet = PointerProperty(options={'HIDDEN'}, type=WMJetPropertyGroup)

def unregister():
    del Scene.Jet
    del Object.Jet

    unregister_class(ScnJetPropertyGroup)
    unregister_class(ObjJetPropertyGroup)
    unregister_class(ObjIdPropertyGroup)
    unregister_class(MeshPropertyGroup)
    unregister_class(ActivePropertyGroup)
    unregister_class(ObjectPropertyGroup)
    unregister_class(TagEdgePropertyGroup)
    unregister_class(SwapPropertyGroup)
    unregister_class(InfoPropertyGroup)
    unregister_class(SnapPropertyGroup)
    unregister_class(WMJetPropertyGroup)


