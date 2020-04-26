import bpy
import ctypes

from .bridge import BPB

class Panda3DEngine(bpy.types.RenderEngine):
    bl_idname = 'PANDA3D'
    bl_label = 'Panda3D'
    bl_use_preview = False

    def __init__(self, *args, **kwargs):
        bpy.types.RenderEngine.__init__(self, *args, **kwargs)

        self.bpb_context = BPB.initialize(ctypes.c_int(0))
        self.bpb_renderer = BPB.new_renderer(BPB.RT_gl_viewport, 0)

        self.objects = {}
        self.meshes = {}

    def update(self, data, scene):
        """ Blender calls this before render() to let us
        export the scene before actually rendering it. """

        print('update:', self, data, scene)

    def render(self, scene):
        """ Render the scene previously exported by update(). """
        print('render:', self, scene)

    def preview_update(self, context, id):
        print('preview_update:', self, context, id)

    def preview_render(self):
        print('preview_render:', self)

    def view_update(self, context):
        """ Called by Blender when the scene rendered by the
        viewport has changed. """

        print('view_update:', self, context)

        # Currently leaks.  Terribly.  Also ugly.  Clean this up soon.

        for object in context.visible_objects:
            obj = self.objects.get(object)
            if not obj:
                obj = BPB.new_object(self.bpb_context)
                self.objects[object] = obj
                #TODO: delete object

            BPB.object_update(obj, object.as_pointer())

            if object.type == 'MESH':
                mesh = self.meshes.get(object.data)
                if not mesh:
                    mesh = BPB.new_object_data(self.bpb_context, 0)
                    self.meshes[object.data] = mesh
                    #TODO: delete mesh

                BPB.object_data_update(mesh, object.data.as_pointer())
                BPB.object_set_data(obj, mesh)

    def view_draw(self, context):
        """ Called by Blender when the viewport should be redrawn. """

        print('view_draw:', self, context)

        window = context.window
        region = context.region

        desc = BPB.render_desc()
        desc.camera = self.objects[context.scene.camera]
        desc.world = None

        desc.width = window.width
        desc.height = window.height
        desc.region_x = region.x
        desc.region_y = region.y
        desc.region_width = region.width
        desc.region_height = region.height

        desc.file_name = None

        BPB.renderer_start(self.bpb_renderer, desc)
        BPB.renderer_finish(self.bpb_renderer)
