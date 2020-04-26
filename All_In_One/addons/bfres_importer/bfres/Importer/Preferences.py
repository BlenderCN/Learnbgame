import logging; log = logging.getLogger(__name__)
import bpy


class BfresPreferences(bpy.types.AddonPreferences):
    bl_idname = "import_scene.nxbfres"

    def _onUpdate(self, context):
        print("BFRES _onUpdate", context)

    debugDumpFiles = bpy.props.BoolProperty(
        name="Dump debug info to files",
        description="Create `fres-SomeFile-dump.txt` files for debugging.",
        default=False,
        options={'ANIMATABLE'},
        subtype='NONE',
        update=_onUpdate,
    )

    def draw(self, context):
        print("BfresPreferences draw")
        self.layout.prop(self, "debugDumpFiles")
