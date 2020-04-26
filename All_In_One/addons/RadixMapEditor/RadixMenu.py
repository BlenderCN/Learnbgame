import bpy

class RadixMenu(object):
    """
    Class for adding the radix menu.
    """

    def getExportMenuOperator(self, blender ,context):
        blender.layout.operator("radix.export", text="Radix Map (.xml)")

    def getImportMenuOperator(self, blender, context):
        blender.layout.operator("radix.import", text="Radix Map (.xml)")

    def addMainMenu(self, blender, context):
        layout = blender.layout

        layout.menu("radixMenu.main", icon='WORLD')
        layout.separator()
