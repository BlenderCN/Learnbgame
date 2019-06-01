import bpy
from bpy.types import Header, Menu
from bpy.types import FILEBROWSER_HT_header as FILEBROWSER_HT_header_old


class FILEBROWSER_HT_header_new(Header):
    bl_space_type = 'FILE_BROWSER'

    def draw(self, context):
        layout = self.layout

        st = context.space_data

        row = layout.row()
        row.label(icon='FILESEL')
        # row.template_header()

        row = layout.row(align=True)
        row.operator("file.previous", text="", icon='BACK')
        row.operator("file.next", text="", icon='FORWARD')
        row.operator("file.parent", text="", icon='FILE_PARENT')
        row.operator("file.refresh", text="", icon='FILE_REFRESH')

        layout.separator()
        layout.operator_context = 'EXEC_DEFAULT'
        layout.operator("file.directory_new", icon='NEWFOLDER', text="")
        layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        params = st.params

        # can be None when save/reload with a file selector open
        if params:
            is_lib_browser = params.use_library_browsing

            layout.prop(params, "recursion_level", text="")

            layout.prop(params, "display_type", expand=True, text="")

            layout.prop(params, "display_size", text="")

            layout.prop(params, "sort_method", expand=True, text="")

            layout.prop(params, "show_hidden", text="", icon='FILE_HIDDEN')
            layout.prop(params, "use_filter", text="", icon='FILTER')

            row = layout.row(align=True)
            row.active = params.use_filter

            row.prop(params, "use_filter_folder", text="")

            if params.filter_glob:
                # if st.active_operator and hasattr(st.active_operator, "filter_glob"):
                #     row.prop(params, "filter_glob", text="")
                row.label(text=params.filter_glob)
            else:
                row.prop(params, "use_filter_blender", text="")
                row.prop(params, "use_filter_backup", text="")
                row.prop(params, "use_filter_image", text="")
                row.prop(params, "use_filter_movie", text="")
                row.prop(params, "use_filter_script", text="")
                row.prop(params, "use_filter_font", text="")
                row.prop(params, "use_filter_sound", text="")
                row.prop(params, "use_filter_text", text="")

            if is_lib_browser:
                row.prop(params, "use_filter_blendid", text="")
                if params.use_filter_blendid:
                    row.separator()
                    row.prop(params, "filter_id_category", text="")

            row.separator()
            row.prop(params, "filter_search", text="", icon='VIEWZOOM')

        layout.template_running_jobs()


classes_to_unregister = [
    FILEBROWSER_HT_header_old,
    ]


classes = [
    FILEBROWSER_HT_header_new,
]