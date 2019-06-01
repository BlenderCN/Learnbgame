import bpy


class PREV_MT_menu_insert_keyframe(bpy.types.Menu):
    bl_label = "Insert KeyFrame Menu"
    bl_idname = "VSE_MT_Insert_keyframe_Menu"

    def draw(self, context):
        types = []
        use_translations = []
        use_crops = []
        for strip in bpy.context.selected_sequences:
            types.append(strip.type)
            use_translations.append(strip.use_translation)
            use_crops.append(strip.use_crop)

        layout = self.layout

        if "TRANSFORM" in types:
            layout.operator("vse_transform_tools.insert_keyframe",
                            text="Location").ch = (1, 0, 0, 0, 0)

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="Rotation").ch = (0, 1, 0, 0, 0)

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="Scale").ch = (0, 0, 1, 0, 0)

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="LocRot").ch = (1, 1, 0, 0, 0)

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="LocScale").ch =(1, 0, 1, 0, 0)

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="RotScale").ch = (0, 1, 1, 0, 0)

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="LocRotScale").ch = (1, 1, 1, 0, 0)

            layout.separator()

            layout.operator("vse_transform_tools.insert_keyframe",
                        text="Crop").ch = (0, 0, 0, 0, 1)

            layout.separator()

        if not all(elem == "SOUND" for elem in types):
            if True in use_translations:
                layout.operator("vse_transform_tools.insert_keyframe",
                                text="Location").ch = (1, 0, 0, 0, 0)

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="Alpha").ch = (0, 0, 0, 1, 0)

            if True in use_crops:
                layout.operator("vse_transform_tools.insert_keyframe",
                                text="Crop").ch = (0, 0, 0, 0, 1)

        if "TRANSFORM" in types:
            layout.separator()

            layout.operator("vse_transform_tools.insert_keyframe",
                            text="All").ch = (1, 1, 1, 1, 1)
