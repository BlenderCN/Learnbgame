bl_info = {
    "name": "Move Render Layers",
    "author": "Ray Mairlot",
    "version": (1, 0, 1),
    "blender": (2, 78, 0),
    "location": "Properties Editor> Render Layers",
    "description": "Adds 'up' and 'down' arrows for moving render layers up or down the render layers list",
    "wiki_url": "",
    "category": "Render",
    }



import bpy



def freestyleToDict(renderLayer):
    
    freestyleDict = {}
            
    freestyleProperties = [property for property in bpy.types.FreestyleSettings.bl_rna.properties]
                
    for freestyleProp in freestyleProperties:
        
        if freestyleProp.identifier == 'linesets':
            
            linesets = []
            
            for lineset in renderLayer.freestyle_settings.linesets:
                
                linesetDict = {}
                
                linesetProperties = [property for property in bpy.types.FreestyleLineSet.bl_rna.properties if not property.is_readonly]
                                
                for linesetProp in linesetProperties:
                    
                    linesetDict[linesetProp.identifier] = getattr(lineset, linesetProp.identifier)
                
                linesets.append(linesetDict)
                
            freestyleDict[freestyleProp.identifier] = linesets
            
            for lineset in renderLayer.freestyle_settings.linesets:
                
                renderLayer.freestyle_settings.linesets.remove(lineset)   
        
        if not freestyleProp.is_readonly:
        
            freestyleDict[freestyleProp.identifier] = getattr(renderLayer.freestyle_settings, freestyleProp.identifier)

    return freestyleDict



def renderLayerToDict(renderLayer):

    properties = [property for property in bpy.types.SceneRenderLayer.bl_rna.properties]

    renderLayerDict = {}

    for prop in properties:
        
        #The '[:]' makes sure the data of a collection of values is copied instead of a reference to it        
        if prop.identifier in ['layers', 'layers_exclude', 'layers_zmask']:
            
            renderLayerDict[prop.identifier] = getattr(renderLayer, prop.identifier)[:]
        
        elif prop.identifier == 'freestyle_settings':
                            
            renderLayerDict[prop.identifier] = freestyleToDict(renderLayer)
        
        elif not prop.is_readonly:
            
            renderLayerDict[prop.identifier] = getattr(renderLayer, prop.identifier)

    return renderLayerDict



def dictToRenderLayer(renderLayer, renderLayerDict):
    
    for key, value in renderLayerDict.items():
        
        if key == 'freestyle_settings':
            
            for freestyleKey, freestyleValue in value.items():
                
                if freestyleKey == 'linesets':
                                        
                    for lineset in freestyleValue:

                        newLineSet = renderLayer.freestyle_settings.linesets.new(lineset['name'])
                        
                        linestyle = newLineSet.linestyle
                        
                        for linesetKey, linesetValue in lineset.items():
                            
                            setattr(newLineSet, linesetKey, linesetValue)
                            
                        #We're assigning the linestyle from the old lineset, meaning the linestyle created 
                        #when the new lineset is created is redundant and needs to be removed    
                        bpy.data.linestyles.remove(linestyle)
                        
                else:
                
                    setattr(renderLayer.freestyle_settings, freestyleKey, freestyleValue)
        
        else:
            
            setattr(renderLayer, key, value)
    
    

def getRenderLayersNodes(renderLayerName):
    
    renderLayerNodes = []
    
    for scene in bpy.data.scenes:
    
        if scene.node_tree:
        
            for node in scene.node_tree.nodes:
                
                if node.type == 'R_LAYERS':
                    
                    if node.layer == renderLayerName and node.scene == bpy.context.scene:
            
                        renderLayerNodes.append(node)

    return renderLayerNodes
    


def swapRenderLayerNodes(renderLayer1Name, renderLayer2Name):

    renderLayer1Nodes = getRenderLayersNodes(renderLayer1Name)
    renderLayer2Nodes = getRenderLayersNodes(renderLayer2Name)

    for node in renderLayer1Nodes:
            
        node.layer = renderLayer2Name
         
    for node in renderLayer2Nodes: 
                        
        node.layer = renderLayer1Name



def swapRenderLayers(renderLayer1Name, renderLayer2Name):
    
    layers = bpy.context.scene.render.layers
    
    renderLayer1 = layers[renderLayer1Name]
        
    renderLayer1Dict = renderLayerToDict(layers[renderLayer1Name])
    renderLayer2Dict = renderLayerToDict(layers[renderLayer2Name])

    dictToRenderLayer(layers[renderLayer1Name], renderLayer2Dict)
    dictToRenderLayer(layers[renderLayer2Name], renderLayer1Dict)

    renderLayer1.name = renderLayer2Name



def swapAnimationData(renderLayer1Name, renderLayer2Name, animationType):
    
    if animationType == "fcurves":
    
        animationData = bpy.context.scene.animation_data.action.fcurves    
        
    elif animationType == "drivers":
    
        animationData = bpy.context.scene.animation_data.drivers
        
    for data in animationData:
    
        dataParts = data.data_path.rpartition('.')
        dataRenderLayer = dataParts[0]
        dataProperty = dataParts[2]
                    
        if 'render.layers["' + renderLayer1Name + '"]' == dataRenderLayer:
            
            data.data_path = 'render.layers["' + renderLayer2Name + '"].' + dataProperty
            
        if 'render.layers["' + renderLayer2Name + '"]' == dataRenderLayer:
            
            data.data_path = 'render.layers["' + renderLayer1Name + '"].' + dataProperty



def moveRenderLayer(direction):
    
    layers = bpy.context.scene.render.layers
        
    if direction == "Up" and layers.active_index > 0:
        
        targetLayerIndex = layers.active_index - 1
        
    elif direction == "Up" and layers.active_index == 0:
        
        targetLayerIndex = len(layers) - 1
        
    elif direction == "Down" and layers.active_index < len(layers) - 1:
        
        targetLayerIndex = layers.active_index + 1
        
    elif direction == "Down" and layers.active_index == len(layers) - 1:

        targetLayerIndex = 0        
        
    swapRenderLayers(layers[targetLayerIndex].name, layers[layers.active_index].name)
    swapRenderLayerNodes(layers[targetLayerIndex].name, layers[layers.active_index].name)
    
    if bpy.context.scene.animation_data:    
    
        swapAnimationData(layers[targetLayerIndex].name, layers[layers.active_index].name, "fcurves")
        swapAnimationData(layers[targetLayerIndex].name, layers[layers.active_index].name, "drivers")
    
    layers.active_index = targetLayerIndex



class RenderLayerMove(bpy.types.Operator):
    """Move the current render layer up or down"""
    bl_idname = "scene.render_layer_move"
    bl_label = "Move render layer"

    direction = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return len(context.scene.render.layers) > 1

    def execute(self, context):
        moveRenderLayer(self.direction)
        return {'FINISHED'}



def RenderLayerMoveButtons(self, context):
                
    layout = self.layout
    row = layout.row(align=True)
    operator = row.operator("scene.render_layer_move", "", icon="TRIA_UP")
    operator.direction = "Up"
    operator = row.operator("scene.render_layer_move", "", icon="TRIA_DOWN")
    operator.direction = "Down"



def register():
    
    bpy.utils.register_class(RenderLayerMove)
    bpy.types.RENDERLAYER_PT_layers.prepend(RenderLayerMoveButtons)



def unregister():

    bpy.utils.unregister_class(RenderLayerMove)
    bpy.types.RENDERLAYER_PT_layers.remove(RenderLayerMoveButtons)
        


if __name__ == "__main__":
    register()
    