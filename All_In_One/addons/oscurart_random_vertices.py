bl_info = {
    "name": "Random Vertices",
    "author": "Oscurart, Greg",
    "version": (1, 0),
    "blender": (2, 5, 5),
    "api": 3900,
    "location": "Object > Transform > Random Vertices",
    "description": "Randomize selected components of active object.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


import bpy , random




def add_object(self, context, VALMIN, VALMAX, FACTOR, VGFILTER):
    
    ## DISCRIMINA EN LA OPCION CON MAPA DE PESO O NO
    
    if VGFILTER == True:
            
        ## GENERO VARIABLES
        MODE=bpy.context.active_object.mode
        OBJACT=bpy.context.active_object
        LISTVER=[]
        
        ## PASO A MODO OBJECT
        bpy.ops.object.mode_set(mode='OBJECT')
        
        ## SI EL VERTICE ESTA SELECCIONADO LO SUMA A UNA LISTA
        for vertice in OBJACT.data.vertices:
            if vertice.select:
                LISTVER.append(vertice.index)
    
        ## SI EL VALOR MINIMO ES MAYOR AL MAXIMO, LE SUMA UN VALOR AL MAXIMO
        if VALMIN[0] >= VALMAX[0]:
            VALMAX[0] = VALMIN[0] + 1
            
        if VALMIN[1] >= VALMAX[1]:
            VALMAX[1] = VALMIN[1] + 1
            
        if VALMIN[2] >= VALMAX[2]:
            VALMAX[2] = VALMIN[2] + 1                
            
        for vertice in LISTVER:
            if OBJACT.data.vertices[vertice].select:
                VERTEXWEIGHT = OBJACT.data.vertices[vertice].groups[0].weight
                OBJACT.data.vertices[vertice].co=(
                    (((random.randrange(VALMIN[0],VALMAX[0],1))*VERTEXWEIGHT*FACTOR)/1000)+OBJACT.data.vertices[vertice].co[0],
                    (((random.randrange(VALMIN[1],VALMAX[1],1))*VERTEXWEIGHT*FACTOR)/1000)+OBJACT.data.vertices[vertice].co[1],
                    (((random.randrange(VALMIN[2],VALMAX[2],1))*VERTEXWEIGHT*FACTOR)/1000)+OBJACT.data.vertices[vertice].co[2]
                )
        ## RECUPERO EL MODO DE EDICION
        bpy.ops.object.mode_set(mode=MODE)

    else:
    
        if VGFILTER == False:
                
            ## GENERO VARIABLES
            MODE=bpy.context.active_object.mode
            OBJACT=bpy.context.active_object
            LISTVER=[]
            
            ## PASO A MODO OBJECT
            bpy.ops.object.mode_set(mode='OBJECT')
            
            ## SI EL VERTICE ESTA SELECCIONADO LO SUMA A UNA LISTA
            for vertice in OBJACT.data.vertices:
                if vertice.select:
                    LISTVER.append(vertice.index)
        
            ## SI EL VALOR MINIMO ES MAYOR AL MAXIMO, LE SUMA UN VALOR AL MAXIMO
            if VALMIN[0] >= VALMAX[0]:
                VALMAX[0] = VALMIN[0] + 1
                
            if VALMIN[1] >= VALMAX[1]:
                VALMAX[1] = VALMIN[1] + 1
                
            if VALMIN[2] >= VALMAX[2]:
                VALMAX[2] = VALMIN[2] + 1                
                
            for vertice in LISTVER:
                if OBJACT.data.vertices[vertice].select:
                    OBJACT.data.vertices[vertice].co=(
                        (((random.randrange(VALMIN[0],VALMAX[0],1))*FACTOR)/1000)+OBJACT.data.vertices[vertice].co[0],
                        (((random.randrange(VALMIN[1],VALMAX[1],1))*FACTOR)/1000)+OBJACT.data.vertices[vertice].co[1],
                        (((random.randrange(VALMIN[2],VALMAX[2],1))*FACTOR)/1000)+OBJACT.data.vertices[vertice].co[2]
                    )
            ## RECUPERO EL MODO DE EDICION
            bpy.ops.object.mode_set(mode=MODE)
    
        	         
    
class OBJECT_OT_add_object(bpy.types.Operator):
    """Add a Mesh Object"""
    bl_idname = "mesh.random_vertices"
    bl_label = "Random Vertices"
    bl_description = "Random Vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    VGFILTER=bpy.props.BoolProperty(name="Vertex Group", default=False)
    FACTOR=bpy.props.FloatProperty(name="Factor", default=1)
    VALMIN = bpy.props.IntVectorProperty(name="Min XYZ",default=(0,0,0))
    VALMAX = bpy.props.IntVectorProperty(name="Max XYZ",default=(1,1,1))
    def execute(self, context):

        add_object(self, context, self.VALMIN, self.VALMAX, self.FACTOR, self.VGFILTER)

        return {'FINISHED'}


# Registration

def add_oscRandVerts_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Random Vertices",
        icon="PLUGIN")


def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_transform.append(add_oscRandVerts_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_transform.remove(add_oscRandVerts_button)


if __name__ == '__main__':
    register()
