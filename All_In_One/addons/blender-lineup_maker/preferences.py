import bpy
import os

preferences_tabs = [("GENERAL", "General", ""),
                    ("ABOUT", "About", "")]

links = [("tilapiatsu.fr", "http://tilapiatsu.fr/", "WORLD"),
         ("Twitter", "https://twitter.com/tilapiatsu", "NONE"),
         ("", "", ""),
         ("", "", ""),
         ("Artstation", "https://www.artstation.com/tilapiatsu", "NONE"),
         ("", "", ""),
         ]

def get_path():
    return os.path.dirname(os.path.realpath(__file__))

def get_name():
    return os.path.basename(get_path())

def get_prefs():
    return bpy.context.preferences.addons[get_name()].preferences



class LM_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    textureSet_albedo_keyword: bpy.props.StringProperty(name="Albedo", default='Albedo')
    textureSet_normal_keyword: bpy.props.StringProperty(name="Normal", default="Normal")
    textureSet_roughness_keyword: bpy.props.StringProperty(name="Roughness", default="Roughness")
    textureSet_metalic_keyword: bpy.props.StringProperty(name="Metalic", default="Metalic")


    # HIDDEN
    tabs: bpy.props.EnumProperty(name="Tabs", items=preferences_tabs, default="GENERAL")

    def draw(self, context):
        layout=self.layout


        # TAB BAR

        column = layout.column(align=True)
        row = column.row()
        row.prop(self, "tabs", expand=True)
        box = column.box()
        if self.tabs == "GENERAL":
            self.draw_general(box)

        # elif self.tabs == "KEYMAPS":
        #     self.draw_keymaps(box)

        elif self.tabs == "ABOUT":
            self.draw_about(box)

    def draw_general(self, box):
        split = box.split()

        # LEFT

        b = split.box()
        b.label(text="Texture Sets")

        column = b.column()

        column.label(text="TextureSets Keywords")

        column.prop(self, "textureSet_albedo_keyword")
        column.prop(self, "textureSet_normal_keyword")
        column.prop(self, "textureSet_roughness_keyword")
        column.prop(self, "textureSet_metalic_keyword")
    
    def draw_about(self, box):
        column = box.column()

        for idx, (text, url, icon) in enumerate(links):
            if idx % 2 == 0:
                row = column.row()
                if text == "":
                    row.separator()
                else:
                    row.operator("wm.url_open", text=text, icon=icon).url = url
            else:
                if text == "":
                    row.separator()
                else:
                    row.operator("wm.url_open", text=text, icon=icon).url = url

