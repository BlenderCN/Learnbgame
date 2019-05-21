import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper    # help with file browser
from .img_texturizer import ImgTexturizer

class ImgTexturesPanel (bpy.types.Panel):
    bl_label = 'Import Textures as One Plane'
    bl_idname = 'material.texbatch_panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'texture'
    update_existing = BoolProperty(name="Add to this object", default=True)

    def draw (self, ctx):
        self.update_existing = True
        # selection to allow for create vs update
        try:
            curr_mat = bpy.context.scene.objects.active.active_material
        except:
            curr_mat = None
        if curr_mat is not None:
            self.layout.operator('material.texbatch_import', text='Add Texs to Object').update_existing = True
            if curr_mat.texture_slots.items()[0][1].texture.type == 'IMAGE':
                self.layout.operator('material.toggle_transparency', text='Toggle Transparency')
        # /!\ Returns error - see create img as plane method in main class /!\
        else:
            self.layout.operator('material.texbatch_import', text='Create New Plane').update_existing = False

class ImgTexturesToggleTransparency (bpy.types.Operator):
    bl_idname = 'material.toggle_transparency'
    bl_label = 'Toggle All Textures Transparent'
    def execute (self, ctx):
        mat = bpy.context.scene.objects.active.active_material
        toggle_imgmat_transparency(mat)
        return {'FINISHED'}

class ImgTexturesImport (bpy.types.Operator, ImportHelper):
    bl_idname = 'material.texbatch_import'
    bl_label = 'Import Texs to Single Plane'
    # file browser info and settings
    filepath = StringProperty (name='File Path')
    files = CollectionProperty(name='File Names', type=bpy.types.OperatorFileListElement)
    directory = StringProperty(maxlen=1024, subtype='DIR_PATH',options={'HIDDEN'})
    filter_image = BoolProperty(default=True, options={'HIDDEN'})
    filter_folder = BoolProperty(default=True, options={'HIDDEN'})
    filter_glob = StringProperty(default="", options={'HIDDEN'})
    # img alpha setting to pass to batch texturizer
    use_transparency = BoolProperty (default=True, name="Use transparency")
    replace_current = BoolProperty (default=False, name="Replace current textures")
    update_existing = BoolProperty (options={'HIDDEN'})

    def store_files (self, files):
        img_filenames = []
        for f in files:
            img_filenames.append (f.name)
        return img_filenames

    def store_directory (self, path):
        return path

    def execute (self, ctx):
        # store files in array and add them to material as textures
        img_filenames = self.store_files(self.files)
        img_dir = self.store_directory(self.directory)

        # add textures to plane
        texBatchAdder = ImgTexturizer(img_filenames, img_dir)
        texBatchAdder.setup(self.replace_current, self.update_existing, self.use_transparency)
        return {'FINISHED'}

    def invoke (self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
