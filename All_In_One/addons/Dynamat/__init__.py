bl_info = {
    "name": "DYNAMAT",
    "author": "Pratik Solanki - special thanks to Akash Hamirwasia, mont29, brita,jasper,and lots of other developers",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "View3D > Property",
    "description": "Create Materials in Single Click",
    "wiki_url": "http://www.dragoneex.com/dynamats.html",
    "category": "Material",
    }


import os
import bpy
import sys
import zipfile
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import AddonPreferences, WindowManager
import bpy.utils.previews

preview_collections = {}
items = []
enum_items = []
image_paths = []
sub_cate_index = []
def enum_previews_from_directory_items(self, context):
    pcoll = preview_collections.get("main")
    if not pcoll:
        return []

    if self.dynamats_preview_thumbs_dir == "":
        pass
    return pcoll.dynamats_preview_thumbs

def preview_dir_update(wm, context):
    """EnumProperty callback"""
    pic_in = "1"
    try:
        enum_items.clear()
        items.clear()
        image_paths.clear()
        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        register()
    except:
        pass

    if context is None:
        return enum_items

    wm = bpy.context.scene
    directory = wm.dynamats_preview_thumbs_dir

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory == pcoll.dynamats_preview_thumbs_dir:
        return pcoll.dynamats_preview_thumbs

    if directory and os.path.exists(directory):
        # Scan the directory for image files
        for fn in os.listdir(directory):
            if fn.lower().endswith(".jpg" or ".JPG" or ".jpeg" or ".PNG" or ".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            dot = name.rfind('.')
            name = name[:dot]
            if "_" in name:
                name = name.replace('_', " ")
            enum_items.append((pic_in, name, "", thumb.icon_id, i))
            pic_in = str(int(pic_in)+1)
            items.append(name)

    pcoll.dynamats_preview_thumbs = enum_items
    pcoll.dynamats_preview_thumbs_dir = directory
    return None

def preview_enum_update(wm, context):
    #Useful for later updates
    return None

def generate_cat(self, context):
    cate = []
    mat = 1
    for ca in os.listdir(os.path.dirname(__file__)):
        if str(ca) != "__init__.py" and str(ca) != "__pycache__" and str(ca) != "ui_mode.txt":
            if mat == 1:
                cate.append(("Dynamats", "Dynamats", ""))
            name = str(ca)
            name = name.title()
            if name != "Dynamats":
                cate.append((name, name, ""))
            mat = mat+1
    return cate

def generate_subcat(self, context):
    sub_cate = []
    sub_cate_index.clear()
    directory = bpy.context.scene.dynamats_MainCategory.lower()
    for sub in os.listdir(os.path.join(os.path.dirname(__file__), directory)):
        if os.path.isdir(os.path.join(os.path.dirname(__file__), directory, str(sub))):
            name2 = str(sub)
            name2 = name2.title()
            sub_cate.append((name2, name2, ""))
            sub_cate_index.append(name2)
    return sub_cate

def MainCat_Update(self, context):
    bpy.context.scene.dynamats_SubCategory = sub_cate_index[0]
    return None

def specify_thumb(self, context):
    cat = bpy.context.scene.dynamats_MainCategory.lower()
    sub = bpy.context.scene.dynamats_SubCategory.lower()
    try:
        bpy.context.scene.dynamats_preview_thumbs = "1"
    except:
        pass
    try:
        bpy.context.scene.dynamats_preview_thumbs_dir = os.path.join(os.path.dirname(__file__), cat, sub)
    except:
        pass
    return None

class RefreshMenu(bpy.types.Operator):
    """Refresh the Icon menu"""
    bl_idname="dynamats.refresh_menu"
    bl_label="Refresh"

    def execute(self, context):
        specify_thumb(self, context)
        return{'FINISHED'}

class DynaPropsPanel(bpy.types.Panel):
    bl_label = "Dynamat"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        DynamatUI(self, context)

class DynaToolsPanel(bpy.types.Panel):
    bl_label = "Dynamat"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = 'Dynamat'

    def draw(self, context):
        DynamatUI(self, context)

class DynaMatePanel(bpy.types.Panel):
    bl_label = "Dynamat"
    bl_space_type = "PROPERTIES"

    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_category = 'Dynamat'

    def draw(self, context):
        DynamatUI(self, context)

def DynamatUI(self, context):
    layout = self.layout

    layout.prop(bpy.context.scene, "dynamats_MainCategory")
    layout.prop(bpy.context.scene, "dynamats_SubCategory")
    if len(bpy.context.scene.dynamats_preview_thumbs) == 0:
        preview_dir_update(self, context)

    col2 = layout.column(align=True)
    row2 = col2.row(align=True)
    row2.scale_y = 20
    row2.scale_x = 5

    row = layout.row()
    col = row.column()
    if len(bpy.context.scene.dynamats_preview_thumbs) != 0:
        col.scale_y= 6
        col.operator(PreviousMat.bl_idname, icon="TRIA_LEFT",text="")
        col = row.column()
        col.template_icon_view(bpy.context.scene, "dynamats_preview_thumbs", show_labels=True, scale=5.2) #layout

        col = row.column()
        col.scale_y= 6
        col.operator(NextMat.bl_idname, text="", icon='TRIA_RIGHT')
    else:
        col.label()
        col.label("No Material(s) in", icon='UGLYPACKAGE')
        col.label("this category")
        col.label()

    row = layout.row()
    split = row.split(percentage=0.75)
    col = split.column(align=True)
    row = col.row(align=True)
    if len(bpy.context.scene.dynamats_preview_thumbs) != 0:
        row.scale_y = 1.2
        row.operator(Assign.bl_idname, text="Assign")
        col1 = split.column(align=True)
        row = col1.row(align=True)
        row.scale_y = 1.2
        row.operator('addmat.button' ,icon = 'ZOOMIN')
        row.operator('removemat.button' ,icon = 'ZOOMOUT')
    else:
        col3 = layout.column(align=True)
        row = col3.row(align=True)
        row.scale_y = 1.2
        row.scale_x = 5
        row.operator('addmat.button' ,icon = 'ZOOMIN', text="")
        row.operator('removemat.button' ,icon = 'ZOOMOUT', text="")

    """row = layout.row()
    row = layout.row()
    name = bpy.context.object.active_material.name
    ntree = bpy.data.node_groups[name]
    mat = bpy.context.object.active_material
    ntree2 = mat.node_tree
    node = ntree2.nodes.active
    for socket in node.inputs:
        layout.template_node_view(ntree2, node,socket)"""
class selno(bpy.types.Operator):
    bl_idname = 'selno.button'
    bl_label = 'Display'

    def execute(self, context):
        layout = self.layout
        #obj = bpy.context.active_object

        mat = bpy.context.object.active_material
        ntree2 = mat.node_tree
        node = ntree2.nodes.active
        for node in ntree2.nodes:
            node.select = True

        return{'FINISHED'}

class removemat(bpy.types.Operator):

    bl_idname = 'removemat.button'
    bl_label = ''

    def execute(self, context):
        cat = bpy.context.scene.dynamats_MainCategory.lower()
        sub = bpy.context.scene.dynamats_SubCategory.lower()
        matname = items[int(bpy.context.scene.dynamats_preview_thumbs)-1]
        fp = os.path.join(os.path.dirname(__file__), cat,sub, matname+'.jpg')
        bfp = os.path.join(os.path.dirname(__file__), cat, matname+'.blend')

        os.remove(fp)
        os.remove(bfp)

        bpy.context.scene.dynamats_SubCategory = bpy.context.scene.dynamats_SubCategory
        try:
            bpy.context.scene.dynamats_preview_thumbs = '1'
        except:
            pass
        return{'FINISHED'}

class addmat(bpy.types.Operator):
    bl_idname = 'addmat.button'
    bl_label = ''

    def execute(self, context):
        cat = bpy.context.scene.dynamats_MainCategory.lower()
        sub = bpy.context.scene.dynamats_SubCategory.lower()

        #blendpath = 'C:/Users/drago/Desktop/matsetup.blend'
        blendpath = os.path.join(os.path.dirname(__file__), cat,"matsetup.blend")
        matname = bpy.context.object.active_material.name
        mat = bpy.data.materials[matname]
        current_scene = bpy.context.scene
        if bpy.context.scene.render.engine == 'CYCLES':

            bpy.ops.scene.new(type='NEW')
            bpy.context.scene.name = "asd"
            bpy.context.window.screen.scene = bpy.data.scenes['asd']

            bpy.context.scene.render.engine = 'CYCLES'
            bpy.ops.world.new()

            link = False

            with bpy.data.libraries.load(blendpath,link=link) as (data_from, data_to):
                data_to.objects = data_from.objects

            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.scene.objects.link(obj)

            matcam = bpy.data.objects['matcam']
            bpy.context.scene.camera = matcam
            bpy.context.scene.render.resolution_x = 256
            bpy.context.scene.render.resolution_y = 256
            ob = bpy.data.objects['matsphere']
            ob.name = matname
            ob.data.materials.append(mat)
            bpy.data.scenes['asd'].render.image_settings.file_format = 'JPEG'
            #img = bpy.data.images[matname]
            bpy.data.scenes['asd'].render.filepath = os.path.join(os.path.dirname(__file__), cat,sub, matname+'.jpg')
            #os.path.join('//matsphere_' , matname + ".jpg")
            bpy.ops.render.render(write_still=True)

            blend = "mat2.blend"
            savepath = os.path.join(os.path.dirname(__file__), cat,matname+".blend")
            #savepath = os.path.join(os.path.dirname(__file__), cat, blend)

            # write all materials, textures and node groups to a library
            data_blocks = {bpy.data.materials[matname]}
            bpy.data.libraries.write(savepath, data_blocks, fake_user=True)

            bpy.ops.scene.delete()

        else:

            bpy.ops.scene.new(type='NEW')
            bpy.context.scene.name = "asd"
            bpy.context.window.screen.scene = bpy.data.scenes['asd']

            #bpy.context.scene.render.engine = 'CYCLES'
            link = False

            with bpy.data.libraries.load(blendpath,link=link) as (data_from, data_to):
                data_to.objects = data_from.objects

            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.scene.objects.link(obj)

            matcam = bpy.data.objects['matcam']
            a1 = bpy.data.lamps['a1']
            a2 = bpy.data.lamps['a2']
            a3 = bpy.data.lamps['a3']
            a4 = bpy.data.lamps['a4']
            a1.distance = 0.280
            a2.distance = 0.280
            a3.distance = 0.280
            a4.distance = 0.280

            bpy.context.scene.camera = matcam
            bpy.context.scene.render.resolution_x = 256
            bpy.context.scene.render.resolution_y = 256
            ob = bpy.data.objects['matsphere']
            ob.name = matname
            ob.data.materials.append(mat)
            bpy.data.scenes['asd'].render.image_settings.file_format = 'JPEG'
            #img = bpy.data.images[matname]
            bpy.data.scenes['asd'].render.filepath = os.path.join(os.path.dirname(__file__), cat,sub, matname+'.jpg')
            #os.path.join('//matsphere_' , matname + ".jpg")
            bpy.ops.render.render(write_still=True)

            blend = "mat2.blend"
            savepath = os.path.join(os.path.dirname(__file__), cat,matname+".blend")
            #savepath = os.path.join(os.path.dirname(__file__), cat, blend)

            # write all materials, textures and node groups to a library
            data_blocks = {bpy.data.materials[matname]}
            bpy.data.libraries.write(savepath, data_blocks, fake_user=True)

            bpy.ops.scene.delete()
        bpy.context.scene.dynamats_SubCategory = bpy.context.scene.dynamats_SubCategory
        try:
            bpy.context.scene.dynamats_preview_thumbs = '1'
        except:
            pass

        return{'FINISHED'}

class NextMat(bpy.types.Operator):
    """Select the Next Material from the Library"""
    bl_idname = 'dynamats.next_mat'
    bl_label = "Next"

    def execute(self, context):
        if int(bpy.context.scene.dynamats_preview_thumbs) == len(items):
            bpy.context.scene.dynamats_preview_thumbs = '1'
        else:
            bpy.context.scene.dynamats_preview_thumbs = str(int(bpy.context.scene.dynamats_preview_thumbs)+1)
        return{'FINISHED'}

class PreviousMat(bpy.types.Operator):
    """Select the Previous Material from the Library"""
    bl_idname = 'dynamats.prev_mat'
    bl_label = "Previous"

    def execute(self, context):
        if bpy.context.scene.dynamats_preview_thumbs == '1':
            bpy.context.scene.dynamats_preview_thumbs = str(len(items))
        else:
            bpy.context.scene.dynamats_preview_thumbs = str(int(bpy.context.scene.dynamats_preview_thumbs)-1)
        return{'FINISHED'}

class Assign(bpy.types.Operator):
    """Assign the Material to the Selected Object(s)"""
    bl_idname = 'dynamats.assign_mat'
    bl_label = 'Assign'

    def execute(self, context):
        cat = bpy.context.scene.dynamats_MainCategory.lower()
        mat_name = items[int(bpy.context.scene.dynamats_preview_thumbs)-1]
        if " " in mat_name:
            mat_name = mat_name.replace(" ", "_")
        #dot  = mat_name.rfind('.')
        #mat_name = mat_name[:dot]

        for obj in bpy.data.objects:
            if obj.select == True:

                ob = obj
                blend = mat_name+'.blend'
                path = os.path.join(os.path.dirname(__file__), cat, mat_name+".blend")

                """blend = ""
                if "-" in mat_name:
                    indi = mat_name.rfind("-")+1
                    blend = mat_name[indi:]+".blend"
                    mat_name = mat_name[:indi-1]
                else:
                    blend = "materials.blend"

                path = os.path.join(os.path.dirname(__file__), cat, 'materials.blend')"""

                with bpy.data.libraries.load(path) as (data_from, data_to):
                    if data_from.materials:
                        data_to.materials = [mat_name]

                for mat in data_to.materials:
                    if mat is not None:

                        if len(ob.material_slots) < 1:

                            ob.data.materials.append(mat)
                        else:

                            ob.material_slots[ob.active_material_index].material = mat

        return{'FINISHED'}


class CustomInstall(bpy.types.Operator, ImportHelper): #Importing Presets
    """Install Materials Pack .zip files"""
    bl_idname = "dynamats.custom_install"
    bl_label = "Install Materials Pack"

    filename_ext = ".zip"

    filter_glob = StringProperty(
            default="*.zip",
            options={'HIDDEN'},
            )

    def execute(self, context):
        try:
            zipref = zipfile.ZipFile(self.filepath, 'r')
            n = 0
            sl = 0
            for i in enumerate(self.filepath):
                sl = self.filepath.rfind(str(os.path.join("a", "")[1]))
                if n != 0:
                    break
                else:
                    n = n+1
            name = self.filepath[sl+1:]
            name = name.title()
            dot = name.rfind(".")
            name = name[:dot]
            path = os.path.dirname(__file__)
            if (path != ""):
                zipref.extractall(path) #Extract to the Dynamats add-on Folder
                zipref.close()
            specify_thumb(self, context)
            self.report({'INFO'}, name+" Pack Installed")
        except:
            pass
        return {'FINISHED'}

class DYNAMAT(AddonPreferences):  #Interface for Addon preferences
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col1 = box.column(align=True)
        col = box.column()
        row1 = col1.row()
        row1.alignment = "CENTER"
        row1.label("Install Material Packs")
        col1.label()
        row1 = col1.row()
        row1.alignment = "CENTER"
        row1.label("INSTRUCTIONS:")
        col1.label()
        col.label("1. Download the Material Packs in .zip format. DO NOT EXTRACT IT")
        col.label("2. Click on \"Install Materials Pack\" button below and navigate to the .zip file")
        col.label("   NOTE: ONLY 1 ZIP FILE SHOULD BE SELECTED AT A TIME")
        col.label("3. After Installing the .zip you should find the new materials in the menu")

        col.label()
        row = col.row()
        row.scale_y = 1.2
        row.label("")
        row.operator(CustomInstall.bl_idname, text='Install Materials Pack', icon='PACKAGE') #Install Materials button
        row.label("")
        col.label()

        row1 = col.row()
        row1.label("Dynamat Panel Location:")
        row1.prop(bpy.context.scene, "dynamats_PanelLoc", expand=True)
        col.label()

def set_dyna_loc(self, context):
    choice = bpy.context.scene.dynamats_PanelLoc
    try:
        if choice == '0':
            bpy.utils.register_class(DynaPropsPanel)
            try:
                bpy.utils.unregister_class(DynaMatePanel)
            except:
                pass
            bpy.utils.unregister_class(DynaToolsPanel)
        elif choice == '1':
            bpy.utils.register_class(DynaToolsPanel)
            try:
                bpy.utils.unregister_class(DynaPropsPanel)
            except:
                pass
            bpy.utils.unregister_class(DynaMatePanel)
        elif choice == '2':
            bpy.utils.register_class(DynaMatePanel)
            try:
                bpy.utils.unregister_class(DynaPropsPanel)
            except:
                pass
            bpy.utils.unregister_class(DynaToolsPanel)
    except:
        pass

    file_py = open(os.path.join(os.path.dirname(__file__), "ui_mode.txt"), 'w')

    path = os.path.join(os.path.dirname(__file__), "ui_mode.txt")
    f = open(path, 'w+')
    if choice == "0":
        f.write("0"+"\n")
    elif choice == "1":
        f.write("1"+"\n")
    elif choice == "2":
        f.write("2"+"\n")
    f.close()
    return None

def register():
    try:
        pcoll = bpy.utils.previews.new()
        pcoll.dynamats_preview_thumbs_dir = ""
        pcoll.dynamats_preview_thumbs = ()

        preview_collections["main"] = pcoll

        bpy.types.Scene.dynamats_preview_thumbs_dir = StringProperty(
                name="Folder Path",
                subtype='DIR_PATH',
                default=os.path.join(os.path.dirname(__file__), "dynamats", "basic"),
                update=preview_dir_update,
                )
        bpy.types.Scene.dynamats_preview_thumbs = EnumProperty(
                items=enum_previews_from_directory_items,
                update=preview_enum_update,
                )

    except:
        pass

    bpy.types.Scene.dynamats_MainCategory = EnumProperty(name="Category", description="Choose the Main Category of Materials", items=generate_cat, update=MainCat_Update)
    bpy.types.Scene.dynamats_SubCategory = EnumProperty(name="Type", description="Choose the Type of Material", items=generate_subcat, update=specify_thumb)
    #Assigning default Value during registration
    check = False
    val = ""
    try:
        f = open(os.path.join(os.path.dirname(__file__), "ui_mode.txt"), "r")
        val = f.readline()
        val = val[0]
        f.close()
        check = True
    except:
        check = False

    if check == True:
        bpy.types.Scene.dynamats_PanelLoc = EnumProperty(name="Panel Location", description="Choose the Location for the Dynamat Panel", items=(('0', 'Properties', 'Choose the Properties Panel'),
                                                                                                                                                ('1', 'Tools', 'Choose the Tools Panel'),
                                                                                                                                                ('2', 'Materials', 'Choose the Materials Panel')), default=val, update=set_dyna_loc)
    else:
        bpy.types.Scene.dynamats_PanelLoc = EnumProperty(name="Panel Location", description="Choose the Location for the Dynamat Panel", items=(('0', 'Properties', 'Choose the Properties Panel'),
                                                                                                                                                ('1', 'Tools', 'Choose the Tools Panel'),
                                                                                                                                                ('2', 'Materials', 'Choose the Materials Panel')), default='0', update=set_dyna_loc)

    bpy.utils.register_class(RefreshMenu)
    if val == '0':
        bpy.utils.register_class(DynaPropsPanel)
    elif val == '1':
        bpy.utils.register_class(DynaToolsPanel)
    elif val == '2':
        bpy.utils.register_class(DynaMatePanel)
    else:
        bpy.utils.register_class(DynaPropsPanel)

    bpy.utils.register_class(removemat)
    bpy.utils.register_class(selno)
    bpy.utils.register_class(addmat)
    bpy.utils.register_class(Assign)
    bpy.utils.register_class(CustomInstall)
    bpy.utils.register_class(DYNAMAT)
    bpy.utils.register_class(NextMat)
    bpy.utils.register_class(PreviousMat)

def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    items.clear()
    enum_items.clear()

    del bpy.types.Scene.dynamats_preview_thumbs
    del bpy.types.Scene.dynamats_preview_thumbs_dir
    del bpy.types.Scene.dynamats_MainCategory
    del bpy.types.Scene.dynamats_SubCategory
    del bpy.types.Scene.dynamats_PanelLoc

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
