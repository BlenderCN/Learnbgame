"Niftools Vertex Correction"
"Dirty script to duplicate a nif and overwrite its vert colors"

import site
import bpy
from pyffi.formats.nif import NifFormat

class NifDataHolder:
    """ A python singleton """

    class __impl:
        """ Implementation of the singleton interface """
        def __init__(self):
            self.data = null
        
        def getinstancedata(self):
            return self.data
    
        def setinstancedata(self,data):
            self.data = data 

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton.__instance is None:
            # Create and remember instance
            Singleton.__instance = Singleton.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Singleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

class NifReader(bpy.types.Operator):
    "This is a dirty script used to change vert color"
    
    '''Bevels selected edges of the mesh'''
    bl_idname = "vertexcolor.nifread"
    bl_label = "Duplicate mesh and overwrite the vert color"
    
    def execute(self, context):
        filein = bpy.context.scene.vertexcolor.fileinput
        hexvalue = bpy.context.scene.vertexcolor.hexwidget
        
        # open file for binary reading
        print("Importing %s" % filein)
        niffile = open(filein, "rb")
        self.data = NifFormat.Data()
        
        # check if nif file is valid
        self.data.inspect(niffile)
        if self.data.version >= 0:
            # it is valid, so read the file
            print("NIF file version: 0x%08X" % self.data.version)
            print("Reading file")
            self.data.read(niffile)
        elif self.data.version == -1:
            print("Unsupported NIF version.")
        else:
            print("Not a NIF file.") 
        
        for root in self.data.roots:
            for block in root.tree():
                if isinstance(block, NifFormat.NiTriShape):
                    if(block.data.has_vertex_colors):
                        vertexcol = block.data.vertex_colors[0]
                        bpy.context.scene.vertexcolor.hexwidget = [vertexcol._items[0]._value,
                                                                   vertexcol._items[1]._value,
                                                                   vertexcol._items[2]._value]
                                
        if(bpy.context.scene.vertexcolor.fileoutput == ""):
            print("check run ok")
            input = bpy.context.scene.vertexcolor.fileinput
            bpy.context.scene.vertexcolor.fileoutput = input[ :-4] + "_copy.nif"
        
        niffile.close()
        print("Finished Reading file :D")
        
        nif = NifDataHolder()
        nif.setinstancedata(self.data)
        return{'FINISHED'}

class NifWriter(bpy.types.Operator):
    "This will write the loaded file"
    
    bl_idname = "vertexcolor.nifwrite"
    bl_label = "Output file with overwritten vert color"
    
    def execute(self, context):
        
        nif = NifDataHolder()
        if(nif.getinstancedata() == null):
            bpy.context.scene.vertexcolor.helpmsg
        else:
            self.data = nif.getinstancedata()
            for root in self.data.roots:
                for block in root.tree():
                    if isinstance(block, NifFormat.NiTriShape):
                        if(block.data.has_vertex_colors):
                            for vertexcol in block.data.vertex_colors:
                                vertexcol._items[0]._value = bpy.context.scene.vertexcolor.hexwidget[0]
                                vertexcol._items[1]._value = bpy.context.scene.vertexcolor.hexwidget[1]
                                vertexcol._items[2]._value = bpy.context.scene.vertexcolor.hexwidget[2]
                            print(block.data.vertex_colors)
            stream = open(bpy.context.scene.vertexcolor.fileoutput, "wb")
            try:
                self.data.write(stream)
                print("Writing File")
            finally:
                stream.close()
        
        return{'FINISHED'}
        
class Popup(bpy.types.Operator):
    bl_idname = "vertexcolor.helpmsg"
    bl_label = "Useful info messages"

    test = bpy.props.StringProperty(name="warning", default="Please load the nif before trying to save")
    
    def execute(self, context):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
