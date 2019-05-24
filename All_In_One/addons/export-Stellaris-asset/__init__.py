import bpy
from bpy.types import Panel, Operator

bl_info = {
    "name": "Stellaris .asset Exporter",
    "category": "Learnbgame",
    "author": "Dayshine, original by Oninoni (oninoni@oninoni.de)",
    "version": (0, 0, 3),
    "blender": (2, 73, 0),
    "support": "COMMUNITY"
}

def createLocator(object):
    data = "locator = {name=\"" + object.name + "\" "
    data += "position={"
    data += '%.10f' % object.location[0]
    data += " "
    data += '%.10f' % object.location[1]
    data += " "
    data += '%.10f' % object.location[2]
    data += "} rotation={"
    data += '%.10f' % object.rotation_euler[0]
    data += " "
    data += '%.10f' % object.rotation_euler[1]
    data += " "
    data += '%.10f' % object.rotation_euler[2]
    data += "}}"
    
    return data

def createAttach(object):
    return "attach = {" + object.name + "=\"YouNeedToAddTheMeshHere\"}"

def main(context, selectedonly, outputattach):
    selected = context.object
    others = context.visible_objects
    
    print("Main: \"" + selected.name + "\"")
    
    print(bpy.path.abspath("//") + "\STH_" + selected.name + ".asset")
    assetFile = open(bpy.path.abspath("//") + "STH_" + selected.name + ".asset","w")
    assetFile.write("# Created by the .asset-Creator v"+ ".".join([str(i) for i in bl_info["version"]]) + " written by Oninoni (oninoni@oninoni.de) and edited by Dayshine for Star Trek New Horizon\n\n")
    
    for object in others:
        print(object.type)
        if(object.type == 'MESH' or object.type == "EMPTY"):
            if(not selectedonly and selected == object):
                continue
            if(not selectedonly or object.select):
                print("Sub: \"" + object.name + "\"")
                print(createLocator(object))
                assetFile.write(createLocator(object) + "\n")
                if(outputattach):
                    print(createAttach(object))
                    assetFile.write(createAttach(object) + "\n\n")
                else:
                    assetFile.write("\n")
        
    assetFile.close()

class AssetExporterOperator(bpy.types.Operator):
    """Export"""
    bl_idname = "object.asset_export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}

    selected = bpy.props.BoolProperty(name="Only Selected")
    attach = bpy.props.BoolProperty(name="Output 'Attach'")

    def execute(self, context):
        main(context, self.selected, self.attach)
        return {'FINISHED'}


class ClausewitzAssetExporterPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Clausewitz Model Exporter'
    bl_context = 'objectmode'
    bl_category = 'Exporter'

    #Add UI elements here
    def draw(self, context):
        layout = self.layout
        layout.row().label('To export select the MAIN Object!')
        layout.row().label('Currently Selected: ' + context.object.name)
        
        layout.operator(AssetExporterOperator.bl_idname)

        

#Register
def register():
    bpy.utils.register_class(AssetExporterOperator)
    bpy.utils.register_class(ClausewitzAssetExporterPanel)
    

#Unregister
def unregister():
    bpy.utils.unregister_class(AssetExporterOperator)
    bpy.utils.unregister_class(ClausewitzAssetExporterPanel)

# Needed to run script in Text Editor
if __name__ == '__main__':
    register()