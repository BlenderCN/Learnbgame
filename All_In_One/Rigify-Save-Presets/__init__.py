import bpy
import os
import re
from rigify.utils import write_metarig
from bpy.types import Operator, Menu
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bl_operators.presets import AddPresetBase

bl_info = {
    "name": "Rigify Save Presets",
    "version": (0, 0, 6),
    "author": "Rombout Versluijs",
    "blender": (2, 78, 0),
    "description": "Makes is easier to save rig presets to Rigify folder",
    "location": "Armature properties, Bone properties, View3d tools panel, Armature Add menu",
    "wiki_url": "https://github.com/schroef/rigify-save-presets",
    "category": "Learnbgame",
}


class RIGIFY_MT_SettingsPresetMenu(Menu):
    #bl_idname = "rigify.setting_preset_menu"
    bl_label = "Setting Presets"
    preset_subdir = "rigify"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


def write_rig_settings(obj, layers=False, func_name="create", groups=False):
    """
    Write a rig preset as a python script, this preset is to have all info needed for
    rig settings the real rig with rigify.
    """
    code = []

    code.append("import bpy")
    code.append("obj = bpy.context.object")
    code.append("arm = obj.data\n")

    arm = obj.data

    #First delete all old ones
    code.append("\nbpy.ops.armature.rigify_bone_group_remove_all()")

    # Rigify bone group colors info
    if groups and len(arm.rigify_colors) > 0:
        code.append("\nfor i in range(" + str(len(arm.rigify_colors)) + "):")
        code.append("   arm.rigify_colors.add()\n")
        ## add check to first delete all old layers, than add correct new amount

        for i in range(len(arm.rigify_colors)):
            name = arm.rigify_colors[i].name
            active = arm.rigify_colors[i].active
            normal = arm.rigify_colors[i].normal
            select = arm.rigify_colors[i].select
            standard_colors_lock = arm.rigify_colors[i].standard_colors_lock
            code.append('arm.rigify_colors[' + str(i) + '].name = "' + name + '"')
            code.append('arm.rigify_colors[' + str(i) + '].active = ' + str(active[:]))
            code.append('arm.rigify_colors[' + str(i) + '].normal = ' + str(normal[:]))
            code.append('arm.rigify_colors[' + str(i) + '].select = ' + str(select[:]))
            #code.append('arm.rigify_colors[' + str(i) + '].standard_colors_lock = ' + str(standard_colors_lock))

    # Rigify layer layout info
    if layers and len(arm.rigify_layers) > 0:

        for i in range(len(arm.rigify_layers)):
            name = arm.rigify_layers[i].name
            row = arm.rigify_layers[i].row
            set = arm.rigify_layers[i].set
            group = arm.rigify_layers[i].group
            code.append('arm.rigify_layers[' + str(i) + '].name = "' + name + '"')
            code.append('arm.rigify_layers[' + str(i) + '].row = ' + str(row))
            code.append('arm.rigify_layers[' + str(i) + '].set = ' + str(set))
            code.append('arm.rigify_layers[' + str(i) + '].group = ' + str(group))

    #print(code)
    return "\n".join(code)


class RIGIFY_OT_AddSettingsPreset(Operator):
    '''Add or remove Rigify settings preset'''
    bl_idname = "rigify.add_settings_presets"
    bl_label = "Save Rigify Settings as preset"
    preset_menu = "RIGIFY_MT_SettingsPresetMenu"

    name = StringProperty(
            name="Name",
            description="Name of the preset, used to make the path name",
            maxlen=64,
            options={'SKIP_SAVE'},
            )
    remove_active = BoolProperty(
            default=False,
            options={'HIDDEN', 'SKIP_SAVE'},
            )

    # needed for mix-ins
    order = [
        "name",
        "remove_active",
        ]

    preset_subdir = "rigify"

    @staticmethod
    def as_filename(name):  # could reuse for other presets

        # lazy init maketrans
        def maketrans_init():
            cls = AddPresetBase
            attr = "_as_filename_trans"

            trans = getattr(cls, attr, None)
            if trans is None:
                trans = str.maketrans({char: "_" for char in " !@#$%^&*(){}:\";'[]<>,.\\/?"})
                setattr(cls, attr, trans)
            return trans

        name = name.lower().strip()
        name = bpy.path.display_name_to_filepath(name)
        trans = maketrans_init()
        return name.translate(trans)

    def execute(self, context):
        ext = ".py"

        preset_menu_class = getattr(bpy.types, self.preset_menu)

        if not self.remove_active:
            name = self.name.strip()
            if not name:
                return {'FINISHED'}

            filename = self.as_filename(name)

            target_path = os.path.join("presets", self.preset_subdir)
            target_path = bpy.utils.user_resource('SCRIPTS',
                                                  target_path,
                                                  create=True)

            if not target_path:
                self.report({'WARNING'}, "Failed to create presets path")
                return {'CANCELLED'}

            filepath = os.path.join(target_path, filename) + ext

            if hasattr(self, "add"):
                self.add(context, filepath)
            else:
                code = write_rig_settings(context.active_object, layers=True, func_name="create", groups=True)

                file_preset = open(filepath, 'w', encoding="utf-8")

                if code:
                    file_preset.write("%s\n" % code)
                    file_preset.write("\n")
                    file_preset.close()

        else:
            preset_active = preset_menu_class.bl_label
            # fairly sloppy but convenient.
            filepath = bpy.utils.preset_find(preset_active,
                                             self.preset_subdir,
                                             ext=ext)

            #print("## filepath: %s" % filepath)
            if not filepath:
                filepath = bpy.utils.preset_find(preset_active,
                                                 self.preset_subdir,
                                                 display_name=True,
                                                 ext=ext)

            if not filepath:
                return {'CANCELLED'}

            try:
                if hasattr(self, "remove"):
                    self.remove(context, filepath)
                else:
                    os.remove(filepath)
            except Exception as e:
                self.report({'ERROR'}, "Unable to remove preset: %r" % e)
                import traceback
                traceback.print_exc()
                return {'CANCELLED'}

        return {'FINISHED'}

    def check(self, context):
        self.name = self.as_filename(self.name.strip())

    def invoke(self, context, event):
        if not self.remove_active:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)


#Get preset folders
def PresetFolders():
    """Return paths for both local and user preset folders"""

    for path in bpy.utils.script_paths():
        if os.path.isdir(os.path.join(path,"addons","rigify")):
            directory = os.path.dirname(path)
            localDir = os.path.join(directory,"scripts","addons","rigify", "metarigs")

    return localDir


def RigFolderItems(self, context):
    rigFolderItems = []
    rigFolderItems.append(("0", "Preset location", PresetFolders()))
    for folder in os.listdir(PresetFolders()):
        if os.path.isdir(PresetFolders()+"/"+folder):
            path = os.path.abspath(os.path.abspath(folder))
            rigFolderItems.append((folder, folder, path))

    return rigFolderItems


## NEW PRESET SECTION
IDStore = bpy.types.WindowManager
IDStore.rigify_preset = bpy.props.EnumProperty(
                        name="Rigify Save Presets",
                        description="'Save presets for rigify settings and rig presets.",
                        items=(('Setting Presets', 'Setting Presets', 'Save Rigify settings'),
                             ('Rig Presets', 'Rig Presets', 'Save Rig presets')))

IDStore.rigify_presetsEnabled = bpy.props.BoolProperty(
                        name="Rigify Presets",
                        description="Save/load Rigify rig presets",
                        default=False)

IDStore.rigify_addfolder = bpy.props.BoolProperty(
                        name="Add Folder",
                        description="Adds new folder in preset folder",
                        default=False)

IDStore.rigify_presetName = bpy.props.StringProperty(
                        name='Preset Name',
                        description='Name of the preset to be saved. Use lowercase only, don\'t use special characters, dashes or spaces, numbers. All of these will be striped or replaced by underscore.',
                        default='',
                        subtype='FILE_NAME')

IDStore.rigify_presetFolder = bpy.props.StringProperty(
                        name='New Folder',
                        description='Name new folder to be added in presets folder',
                        default='')

IDStore.rigify_overwrite = bpy.props.BoolProperty(
                        name='Overwrite',
                        description='When checked, overwrite existing preset files when saving',
                        default=False)


IDStore.rigify_folders = bpy.props.EnumProperty(
                       items=RigFolderItems,
                       name="Rigify Preset Folders",
                       description="Choose folder to add preset")


class AddRigPreset(bpy.types.Operator):
    """ Creates Python code that will generate the selected metarig.
    """
    bl_idname = "armature.rigify_add_rig_preset"
    bl_label = "Add Rig Preset"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        C = context
        id_store = C.window_manager

        filename = id_store.rigify_presetName
        filename = re.sub(' ', '_', filename)
        filename = re.sub('-', '_', filename)
        filename = filename.lower()
        filename = re.sub('[^0a-z_]+', '', filename)
        print("## filename: %s" % filename)
        if id_store.rigify_addfolder:
            subf = "/"+id_store.rigify_presetFolder
            makeDir = PresetFolders()+"/"+subf
            print("## check dir: %s" % os.path.isdir(makeDir))
            if os.path.isdir(makeDir):
                pass
            else:
                os.makedirs(makeDir)
        else:
            if id_store.rigify_folders == "0":
                subf = ""
            else:
                subf = "/"+id_store.rigify_folders

        fpath = os.path.join(PresetFolders()+subf, filename + '.py')

        if (filename == "") or (id_store.rigify_addfolder and (id_store.rigify_presetFolder=="")):
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'ERROR'}, 'No name set')
            return {'CANCELLED'}
        elif (not os.path.exists(fpath)) or (os.path.exists(fpath) and id_store.rigify_overwrite):
            data = write_metarig(context.active_object, layers=True, func_name="create", groups=True)
            #text_block.write(text)
            #f = open(os.path.join(PresetFolders(), subf, filename + '.py'), 'w')
            f = open(os.path.join(fpath), 'w')
            f.write(data)
            f.close()
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        else:
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'ERROR_INVALID_INPUT'}, 'Preset Already Exists')
            return {'CANCELLED'}



# Draw into an existing panel
def panel_func(self, context):
    layout = self.layout
    C = context
    id_store = C.window_manager

    if id_store.rigify_presetsEnabled:
        icon="DISCLOSURE_TRI_DOWN"
    else:
        icon="DISCLOSURE_TRI_RIGHT"

    layout.prop(id_store, "rigify_presetsEnabled", toggle=True, icon=icon)

    if id_store.rigify_presetsEnabled:
        #getattr(scene, "thea_settingsMenu") in ("addon"):
        row = layout.row(align=True)
        row.prop(id_store, "rigify_preset", expand=True)
        if id_store.rigify_preset == 'Setting Presets':
            settingsBox = layout.row()
            split = settingsBox.split(percentage=0.3)
            split.label(text="Presets:")
            sub = split.row(align=True)
            sub.menu(RIGIFY_MT_SettingsPresetMenu.__name__, text=RIGIFY_MT_SettingsPresetMenu.bl_label)
            sub.operator(RIGIFY_OT_AddSettingsPreset.bl_idname, text="", icon='ZOOMIN') #preset_values = context
            sub.operator(RIGIFY_OT_AddSettingsPreset.bl_idname, text="", icon='ZOOMOUT').remove_active = True
            layout.separator()

        if id_store.rigify_preset == 'Rig Presets':
            settingsBox = layout.row()
            split = settingsBox.split(percentage=0.3)
            split.label(text="Preset name:")
            sub = split.row(align=True)
            sub.prop(id_store, "rigify_presetName", text="")

            settingsBox = layout.row()
            split = settingsBox.split(percentage=0.3)
            split.label(text="Folder:")
            sub = split.row(align=True)
            sub.prop(id_store, "rigify_folders", text="")
            sub.prop(id_store, "rigify_addfolder", text="", icon='NEWFOLDER')

            if id_store.rigify_addfolder:
                setattr(id_store,'rigify_folders', "0")
                settingsBox = layout.row()
                split = layout.split(percentage=0.3)
                split.label("Preset Folder:")
                subs = split.row(align=True)
                subs.prop(id_store, "rigify_presetFolder", text="")
                subs.active =  id_store.rigify_addfolder == True

            settingsBox = layout.row()
            split = settingsBox.split(percentage=0.3)
            #split.label("")
            #sub = split.row(align=True)
            split.prop(id_store, "rigify_overwrite")
            #settingsBox = layout.row()

            #split = settingsBox.split(percentage=0.3)
            #split.label("")
            sub = split.row(align=True)
            sub.scale_y = 1.5
            sub.operator('armature.rigify_add_rig_preset')


classes = (
    RIGIFY_MT_SettingsPresetMenu,
    RIGIFY_OT_AddSettingsPreset,
    AddRigPreset,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.DATA_PT_rigify_buttons.append(panel_func)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.DATA_PT_rigify_buttons.remove(panel_func)


if __name__ == "__main__":
    register()

