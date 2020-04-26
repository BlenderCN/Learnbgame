import os
import bpy
from bpy.props import StringProperty
from .. utils.ui import popup_message
from .. utils.registration import reload_plug_libraries
from .. utils.append import append_group
from .. utils import MACHIN3 as m3


class InsertPlug(bpy.types.Operator):
    bl_idname = "machin3.insert_plug"
    bl_label = "Insert Plug"
    bl_description = "Insert Selected Plug"

    library = StringProperty()
    plug = StringProperty()


    def execute(self, context):
        group = insert_plug(self.library, self.plug)

        if group:
            handle = None
            empties = []
            for obj in group.objects:
                bpy.context.scene.objects.link(obj)
                if obj.MM.isplughandle:
                    handle = obj
                else:
                    obj.select = False

                    # xray the plug and subsets if it's toggled in prefs
                    if obj.MM.isplug or obj.MM.isplugsubset:
                        obj.show_x_ray = m3.MM_prefs().plugxraypreview

                    # always, xray the empties:
                    if obj.type == "EMPTY":
                        obj.show_x_ray = True
                        empties.append(obj)


            # remove the group
            bpy.data.groups.remove(group, do_unlink=True)

            if handle:
                m3.unselect_all("OBJECT")

                # also selects and makes active
                m3.move_to_cursor(handle, context.scene)

                # scale plug if the uuid can be found in the scene
                plugscales = context.scene.MM.plugscales

                if handle.MM.uuid in plugscales:
                    ps = plugscales[handle.MM.uuid]
                    handle.scale = ps.scale

                    # position the empties as well
                    for e in empties:
                        if e.MM.uuid in ps.empties:
                            e.location = ps.empties[e.MM.uuid].location


                # set up snapping
                settings = context.scene.tool_settings
                settings.snap_element = 'FACE'
                settings.use_snap_align_rotation = True
                settings.snap_target = 'MEDIAN'

                # it's weird, but only by translating and will some hook/empty plugs udpdate their location properly
                bpy.ops.transform.translate(value=(0, 0, 0))

                # data and scene update for good meassure, although it doensn't seem to be required here
                handle.data.update()
                context.scene.update()
            else:
                popup_message("The Imported Plug doesn not contain a valid Plug Handle.")

        return {"FINISHED"}


class RemovePlug(bpy.types.Operator):
    bl_idname = "machin3.remove_plug"
    bl_label = "Remove Plug"

    library = StringProperty()
    plug = StringProperty()

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.label("This removes the plug '%s' from library '%s'!" % (self.plug, self.library), icon='ERROR')
        layout.label("Removing a plug deletes it from the hard drive, this cannot be undone!")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        print("\nRemoving plug '%s' from library '%s'" % (self.plug, self.library))

        path = m3.MM_prefs().assetspath

        # get the icon and all blends of the plug(incl the blend1's, blend2's, etc)
        iconpath = os.path.join(path, self.library, "icons", self.plug + ".png")
        blendbasepath = os.path.join(path, self.library, "blends")
        blendpaths = [os.path.join(path, self.library, "blends", blend) for blend in sorted(os.listdir(blendbasepath)) if self.plug + ".blend" in blend]


        for path in blendpaths:
            print(" » Deleting plug blend '%s' from disk" % path)
            if os.path.exists(path):
                os.remove(path)

        print(" » Deleting plug icon '%s' from disk" % iconpath)
        if os.path.exists(iconpath):
            os.remove(iconpath)

        # update asset loader, so the just removed plug cant be inserted
        reload_plug_libraries(library=self.library)

        return {'FINISHED'}


def insert_plug(folder_name, plug_name):
    path = m3.MM_prefs().assetspath

    filepath = os.path.join(path, folder_name, "blends", plug_name + ".blend")

    try:
        group = append_group(filepath, plug_name)
        return group
    except NameError:
        popup_message("The Group '%s' does not exist in the plug blend file." % (plug_name))
        return
    except OSError:
        popup_message("The file does not exist: %s" % (filepath))
        return
