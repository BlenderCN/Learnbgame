import bpy
import functools
import subprocess
from bpy.app.handlers import persistent

bl_info = {
    "name": "GraLL 2",
    "description": "Blender plugins for GraLL 2 development",
    "author": "Nikhilesh Sigatapu",
    "version": (1, 0),
    "blender": (2, 63, 0),
    "location": "File > Export",
    "warning": "", # used for warning icon and text in addons panel
    "category": "Import-Export"
}

#class GraLL2Panel(bpy.types.Panel):
#    bl_label = "GraLL 2"
#    bl_idname = "grall2_panel"
#    bl_space_type = "VIEW_3D"
#    bl_region_type = "TOOLS"
#
#    @classmethod
#    def poll(cls, context):
#        return True
#
#    def draw(self, context):
#        layout = self.layout

# select script for selected object
# 'makeNew' is whether to make a new one if it doesn't exist
def selectScript(obj, makeNew = False):
    # if the 'script' property exists, figure out the text name
    # else add a new 'script' property

    props = obj.game.properties

    if 'script' in props.keys():
        str = props['script'].value
        if str.startswith('refText ') and len(str) > 8:
            textname = str[8:]
        else:
            return {'FINISHED'}
    elif makeNew: # add script property if it doesn't exist
        bpy.ops.object.game_property_new(type='STRING', name='script')
        props['script'].value = 'refText ' + obj.name
        textname = obj.name
    else:
        return {'FINISHED'}

    # if the text object exists, use it, else create one and set
    # its name

    texts = bpy.data.texts
    if textname in texts.keys():
        text = texts[textname]
    elif makeNew:
        oldNames = set(bpy.data.texts.keys())
        bpy.ops.text.new()
        newNames = set(bpy.data.texts.keys())
        diff = newNames - oldNames
        if len(diff) == 1:
            text = texts[diff.pop()]
            text.name = textname
            text.from_string('import Ngf\nimport GraLL2\n\n')
        else:
            return {'CANCELLED'}
    else:
        return {'FINISHED'}

    # finally, focus the text object in the first text editor
    # space found (if any)

    try:
        textarea = next(area for area in
                bpy.context.screen.areas if area.type == 'TEXT_EDITOR')
        textarea.spaces[0].text = text
    except StopIteration:
        pass

prevSelect = None
@persistent
def handler(dummy):
    obj = bpy.context.object
    global prevSelect
    if obj != prevSelect:
        selectScript(obj, False)
        prevSelect = obj
bpy.app.handlers.scene_update_pre.append(handler)

class GraLL2OpenScript(bpy.types.Operator):
    bl_idname = "grall2.open_script"
    bl_label = "Open (or create) GameObject Python script"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        selectScript(context.object, True)
        return {'FINISHED'}

class GraLL2Menu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_grall2"
    bl_label = "GraLL 2"

    def draw(self, context):
        layout = self.layout

        layout.operator("grall2.export", text="Level export")
        layout.operator("grall2.export_with_meshes", text="Mesh export")
        layout.operator("grall2.run", text="Run")
        layout.operator("grall2.open_script", text="Script")

GRALL2_COMMAND='/home/nikki/Development/Projects/grall2/bin/release/GraLL2'
GRALL2_CWD='/home/nikki/Development/Projects/grall2/bin/release/'
class GraLL2RunGame(bpy.types.Operator):
    bl_idname = "grall2.run"
    bl_label = "Run GraLL 2 Level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        subprocess.Popen([GRALL2_COMMAND, context.scene.name],
                cwd = GRALL2_CWD)
        return {'FINISHED'}

class GraLL2OgreMeshes(bpy.types.Operator):
    bl_idname = "grall2.export_with_meshes"
    bl_label = "Export GraLL 2 Level and run Ogre Mesh Exporter"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.grall2.export()
        #bpy.ops.ogre3d.export() # doesn't work at the moment

        return {'FINISHED'}

class GraLL2Exporter(bpy.types.Operator):
    bl_idname = "grall2.export"
    bl_label = "Export GraLL 2 Level"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def __init__(self):
        filepath = ''

    @classmethod
    def poll(cls, context):
        return True

    # called when the exporter is invoked
    def invoke(self, context, event):
        return self.execute(context)

    # called by the file selection dialog
    def execute(self, context):
        cfg = bpy.data.texts.get('NGFExport.cfg')
        if cfg:
            self.save_ngf(cfg.lines[0].body)
        elif self.filepath != '':
            self.save_ngf(self.filepath)
            self.filepath = ''
        else:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        return {'FINISHED'}

    # actually write the file
    def save_ngf(self, filename):
        out = open(filename, "w")

        # each scene becomes one NGF level
        for scene in bpy.data.scenes:
            out.write("ngflevel %s\n{\n" % (scene.name))

            # brush counter
            brushIndex = 0

            for obj in scene.objects:
                # deselect now, reselect later if brush
                obj.select = False

                # get position, orientation, game properties
                obj.rotation_mode = 'QUATERNION'
                pos = obj.location
                rot = obj.rotation_quaternion
                props = obj.game.properties

                # write basic game properties and position, orientation
                out.write("\tobject\n\t{\n")
                out.write("\t\ttype %s\n" % props['type'].value)
                out.write("\t\tname %s\n" % props['name'].value)
                out.write("\t\tposition %f %f %f\n" % (pos[0], pos[2], -pos[1]))
                out.write("\t\trotation %f %f %f %f\n" % (rot[0], rot[1], rot[3], -rot[2]))

                # write special properties
                haveProps = False # whether there are any properties - initially no
                propStr = "\n\t\tproperties\n\t\t{\n"

                # (GRALL 2 MODIFICATION: write dimension value corresponding to obj.layers boolean vector)
                propStr += "\t\t\tdimensions %d\n" % (functools.reduce(
                    lambda p, b: (p[0] + 1, (b << p[0]) | p[1]), obj.layers, (0, 0))[1])

                for prop in props:
                    # (GRALL 2 MODIFICATION: don't write 'dimensions', ... )
                    if prop.name not in ['type', 'name', 'dimensions', 'dimension1', 'dimension2']:
                        haveProps = True
                        name = prop.name
                        value = ''

                        # check if brush and save relevant info
                        if name == 'isBrush':
                            # update name to follow naming convention
                            brushName = "%s_b%d" % (scene.name, brushIndex)
                            obj.name = brushName       #object name
                            obj.data.name = brushName  #mesh name

                            # rename materials to follow naming convention
                            for matIndex, mat in enumerate([slot.material for slot in obj.material_slots]):
                                mat.name = '%s_m%d' % (brushName, matIndex)

                            # store mesh name in property
                            name = "brushMeshFile"
                            value = obj.data.name + ".mesh"
                            brushIndex += 1

                            # select for subsequent Ogre .mesh export
                            obj.select = True

                        # check for refText - reference to Blender text object (useful for scripts etc.)
                        elif prop.type == 'STRING' and prop.value.startswith('refText'):
                            print(obj.name)
                            lines = [line.body for line in bpy.data.texts[prop.value[8:]].lines]

                            # first line is simple
                            value = ": " + lines[0]

                            # indent other lines
                            lineFormat = "\n\t\t\t" + (" " * len(name)) + " : %s"
                            for line in lines[1:]:
                                value += lineFormat % line

                        # else simply convert to string
                        else:
                            value = str(prop.value)

                        # write name, value pair
                        propStr += "\t\t\t%s %s\n" % (name, value)

                if haveProps:
                    out.write(propStr + "\t\t}\n")

                out.write("\t}\n")

            # (GRALL 2 MODIFICATION: enable all layers)
            scene.layers = [True] * len(scene.layers)

            # end of scene
            out.write("}\n\n")

        # save filename
        cfg = bpy.data.texts.get('NGFExport.cfg')
        if cfg:
            bpy.data.texts.remove(cfg)
        cfg = bpy.data.texts.new('NGFExport.cfg')
        cfg.write(filename)

        # we're done!
        out.close()

# Blender registration
def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(GraLL2Exporter.bl_idname, text='GraLL 2 Level (.ngf)')
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
