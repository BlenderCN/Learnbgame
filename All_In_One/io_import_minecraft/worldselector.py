import bpy

class MinecraftWorldSelector(bpy.types.Operator):
    """An operator defining a dialogue for displaying the in-system Minecraft worlds.
    This supplants the need to call the file selector, since Minecraft worlds require
    a given folder structure and multiple files and cannot be selected singly."""
    
    bl_idname = "mcraft.selectworld"
    bl_label = "Minecraft Select World"
    
    #bl_space_type = "PROPERTIES"
    #Possible placements for these:
    bl_region_type = "WINDOW"

    #filepath = bpy.props.StringProperty(subtype="DIR_PATH", name="World name")
    #my_float = bpy.props.FloatProperty(name="Float")
    #my_bool = bpy.props.BoolProperty(name="Toggle Option")
    #my_string = bpy.props.StringProperty(name="String Value")
    
    loadAtCursor = bpy.props.BoolProperty(name='Load at 3D Cursor', description='If true, the regions loaded will be around where you place the cursor in 3D View (relative to 0,0,0). Otherwise, loads at the saved player location.', default=False)

    #loadRadius intproperty... range etc. description="Be careful!"
    #superoptimiser algorithm

    omitStone = bpy.props.BoolProperty(name='Omit Stone', description='Check this to not load stone blocks (block id 1). Speeds up loading and viewport massively', default=True)
    
    showSlimeSpawns = bpy.props.BoolProperty(name='Slime Spawns', description='Check this to display chunk outlines which, based on your world seed, indicate where slimes will spawn', default=False)
    
    #surfaceOnly ==> only load surface, discard underground areas. Doesn't count for nether.
    
    # Load Nether (only available if selected world has nether)
    
    
    #When specifying a property of type EnumProperty, ensure you call the constructing method correctly.
    #Note that items is a set of (identifier, value, description) triples, and default is a string unless you switch on options=ENUM_FLAG in which case make default a set of 1 string.
    #Need a better way to handle this variable: (possibly set it as a screen property)
    #MCPATH = ""
	

    my_worldlist = bpy.props.EnumProperty(items=[("0", "A", "The A'th item"), ("2", 'B', "Bth item"), ('2', 'C', "Cth item"), ('3', 'D', "dth item"), ('4', 'E', 'Eth item')][::-1], default='2', name="World", description="Which Minecraft save should be loaded?")
    #my_worldlist = bpy.props.EnumProperty(items=[("0", "A", "The A'th item"), ("2", 'B', "Bth item"), ('2', 'C', "Cth item"), ('3', 'D', "dth item"), ('4', 'E', 'Eth item')][::-1], default={'2'}, name="Enum Value", description="bar", options={'ENUM_FLAG'})
    
    #want to define some buttons, damn it! Btn group? Or just several OK buttons....

    def execute(self, context): 
        print()
        #print(self.my_float)
        self.report( "INFO", "I got value: " + str(self.my_worldlist))
        
		from . import mineregion
		mineregion.readMinecraftChunk(self,context)
        #run minecraftLoadChunks
        
        return {'FINISHED'}

    def invoke(self, context, event):
        #update list of Minecraft worlds here.
        
        
        #context.window_manager.invoke_props_popup(self, event) # does nothing...?
        #context.window_manager.invoke_confirm(self, event)  # <-- Successfully asks 'OK?'
        #context.window_manager.invoke_popup(self, 200, 150) # self, width, height. WOOHOO! This could work! It's not quite what I'd like, though.
        #or invoke_popup()
        context.window_manager.invoke_props_dialog(self, width=340,height=250)
        #or invoke_props_dialog()
        # props_popup(self) #required parameter 'event' not specified
        # serach_popup
        
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout    #grab layout so we can add to it
        col = layout.column()
        col.label(text="Adam was here. I am the walrus, I am the eggman, ...!")

        row = col.row()
        row.prop(self, "loadAtCursor")
        row.prop(self, "omitStone")
        row.prop(self, "showSlimeSpawns")

        col.prop(self, "my_string") #defining the UI works by setting custom properties like this, on the column.
        
        
        
        
        #row = layout.row()
        #row.label(text="Labelling all around")
        row = layout.row()
        row.prop(self, "my_worldlist")
        col = layout.column()
        #col.prop(self, "my_worldlist")
        #col.label("fin")
        #spacer? Divider?
        
        #col.prop(self, 

bpy.utils.register_class(MinecraftWorldSelector)
#bpy.utils.unregister_class(MinecraftWorldSelector)


# test call
def io_minecraft_filemenu_func(self, context):
    #bpy.ops.object.custom_draw('INVOKE_DEFAULT')
    bpy.ops.mcraft.selectworld('INVOKE_DEFAULT')    # can't do this from here? render/draw apparently?
    
    
bpy.types.INFO_MT_file_import.append(io_minecraft_filemenu_func)