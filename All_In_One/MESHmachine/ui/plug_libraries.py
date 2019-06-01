import bpy
from ..utils import MACHIN3 as m3


class MESHmachinePlugLibraries(bpy.types.Menu):
    bl_idname = "machin3.mesh_machine_plug_libraries"
    bl_label = "Plug Libraries"

    def draw(self, context):
        libraryscale = m3.DM_prefs().libraryscale
        plugsinlibraryscale = m3.DM_prefs().plugsinlibraryscale

        plugmode = m3.MM_prefs().plugmode

        pluglibsCOL = m3.DM_prefs().pluglibsCOL
        show_names = m3.DM_prefs().showplugnames
        show_count = m3.DM_prefs().showplugcount
        show_button = m3.DM_prefs().showplugbutton
        show_button_name = m3.DM_prefs().showplugbuttonname

        wm = context.window_manager
        wmt = bpy.types.WindowManager

        # get visible pluglibs
        pluglibs = [lib.name for lib in pluglibsCOL if lib.isvisible]

        # remove toggle
        if pluglibs:
            layout = self.layout

            # remove toggle
            column = self.layout.column()
            # column.scale_x = 0.5

            column.prop(m3.DM_prefs(), "plugremovemode", text="Remove Plugs")

            # libraries
            column = layout.column_flow(len(pluglibs))

            for library in pluglibs:
                # stretch the lib name to at least 4 letters, otherwise the icon will be shrunk down
                libname = library.center(4, " ") if len(library) < 4 else library

                # get the active's plug name in a library
                plugname = getattr(bpy.context.window_manager, "pluglib_" + library)

                column.separator()

                # show the libname
                if show_count:
                    plugcount = len(getattr(wmt, "pluglib_" + library)[1]['items'])
                    liblabel = "%s, %d" % (libname, plugcount)
                else:
                    liblabel = libname

                column.label(liblabel)

                # show plug icon / asset loader

                r = column.row()
                r.scale_y = libraryscale
                r.template_icon_view(wm, "pluglib_" + library, show_labels=show_names, scale=plugsinlibraryscale)

                # show insert button below library icons
                if show_button:
                    r = column.row()

                    if plugmode == "INSERT":
                        if show_button_name:
                            button = plugname
                        else:
                            button = "+"

                        op = r.operator("machin3.insert_plug", text=button.center(len(liblabel), " "))  # NOTE: this is not a regular space, it's wider, it's a figure space U+2007, see https://www.brunildo.org/test/space-chars.html

                    elif plugmode == "REMOVE":
                        op = r.operator("machin3.remove_plug", text="X".center(len(liblabel), " "))  # NOTE: this is not a regular space, it's wider, it's a figure space U+2007, see https://www.brunildo.org/test/space-chars.html

                    op.library = library
                    op.plug = plugname
