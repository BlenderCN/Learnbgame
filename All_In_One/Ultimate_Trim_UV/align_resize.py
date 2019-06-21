# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

##################################
# Imports
##################################
import mathutils
import bpy

#Credit goes to Luca Carella for his UV Align Distribution Addon providing uv island selection functionality via the following imports
#https://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/UV/UV_Align_Distribution

from . import make_islands, templates, utils, operator_manager, global_def

##################################
# Alignment and Resize
##################################

#Aligns the top of UV islands to the top of a trim index
class UV_OT_align_top_index(templates.UvOperatorTemplate):
    """Align Top Index."""

    bl_idname = "uv.align_top_index"
    bl_label = "Align top margin Index"
    bl_options = {'REGISTER', 'UNDO'}
	
	##################################
    # Properties
    ##################################
    
    #Controls the exact location in 0-1 UV space where the top of a UV Trim index exists.
    uvIndex : bpy.props.FloatProperty(
        name = "UV Index",
        default = 1.0,
        description = "Exact position for start of UV Index on Y axis"
    )
	
    ##################################
    # Execution
    ##################################

    def execute(self, context):

        #Creates UV islands out of the selected elements
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        #Applies the needed UV index float property to a variable
        targetElement = self.uvIndex

        #Loops through selected islands and aligns the top of each island with the top of the trim index
        for island in selectedIslands:
            vector = mathutils.Vector(
                (0.0, targetElement - island.BBox().top()))
            island.move(vector)

        utils.update()
        return {'FINISHED'}

#Aligns the left edge of UV islands to the left edge of a trim index
class UV_OT_align_left_index(templates.UvOperatorTemplate):
    """Align left index."""

    bl_idname = "uv.align_left_index"
    bl_label = "Align left index"
    bl_options = {'REGISTER', 'UNDO'}

	##################################
    # Properties
    ##################################
    
    #Sets the location of the left side of UV space to 0 and allows for margin to be added later when this property is modified as an operator button
    uvIndex : bpy.props.FloatProperty(
        name = "UV Index",
        default = 0.0,
        description = "Exact position for start of UV Index on X axis"
    )

    ##################################
    # Execution
    ##################################
    def execute(self, context):
        
        #Creates UV islands out of the selected elements
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        #Applies the needed UV index float property to a variable
        targetElement = self.uvIndex

        #Loops through selected islands and aligns the left of each island with the left of the trim index
        for island in selectedIslands:
            vector = mathutils.Vector(
                (targetElement - island.BBox().left(), 0.0))
            island.move(vector)

        utils.update()
        return {'FINISHED'}

#Aligns the right edge of UV islands to the right edge of a trim index
class UV_OT_align_right_index(templates.UvOperatorTemplate):
    """Align right index."""

    bl_idname = "uv.align_right_index"
    bl_label = "Align right margin"
    bl_options = {'REGISTER', 'UNDO'}

	##################################
    # Properties
    ##################################
    
    #Sets the location of the right side of UV space to 1.0 and allows for margin to be subtracted later when this property is modified as an operator button
    uvIndex : bpy.props.FloatProperty(
        name = "UV Index",
        default = 1.0,
        description = "Exact position for end of UV Index on X axis"
    )
    
    ##################################
    # Execution
    ##################################
    def execute(self, context):
        
        #Creates UV islands out of the selected elements
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        #Applies the needed UV index float property to a variable
        targetElement = self.uvIndex

        #Loops through selected islands and aligns the right of each island with the right of the trim index
        for island in selectedIslands:
            vector = mathutils.Vector(
                (targetElement - island.BBox().right(), 0.0))
            island.move(vector)

        utils.update()
        return {'FINISHED'}

#Centers UV islands in 0-1 UV space
class UV_OT_align_center_index(templates.UvOperatorTemplate):
    """Align center index."""

    bl_idname = "uv.align_center_index"
    bl_label = "Align center index"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #Creates UV islands out of the selected elements
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        #half of uvspace is always .5, this value doesn't need to be modified for margin
        targetElement = 0.5

        #Loops through selected islands and centers them in UV space
        for island in selectedIslands:
            vector = mathutils.Vector(
                (targetElement - island.BBox().center().x, 0.0))
            island.move(vector)

        utils.update()
        return {'FINISHED'}

#Uniformly scales UV islands to fit within the vertical space of a UV index (x and y are scaled the same amount to preserve island aspect ratio)
class UV_OT_equalize_index_scale(templates.UvOperatorTemplate):
    """Equalize the islands scale to the active one."""

    bl_idname = "uv.equalize_index_scale"
    bl_label = "Equalize Index Scale"
    bl_options = {'REGISTER', 'UNDO'}

	##################################
    # Properties
    ##################################
    
    #This value must match the amount of vertical texture space an index consumes
    ratio : bpy.props.FloatProperty(
        name = "Ratio",
        default = .03125,
        description = "Trim Index Size in 0-1 UV Space"
        )
    
    ##################################
    # Execution
    ##################################
    def execute(self, context):
        
        #Creates UV islands out of the selected elements
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()
        islandRatio = self.ratio	

        #Resizes islands to match size of uv index vertically
        #Horizontal island size is resized the same amount to preserve island aspect ratio
        for island in selectedIslands:
            size = island.size()
            scaleY = islandRatio / size.height
            scaleX = scaleY

            island.scale(scaleX, scaleY)

        utils.update()
        return {"FINISHED"}
        
###############################
# Index Button Operator Classes
###############################

class UV_OT_trim_left_id_1(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 1, Left"""
    bl_label = "Align left index 1"
    bl_idname = "uv.trim_left_id_1"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')
    
    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 1.0,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.03125,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        
        #Resizes the UV Island to match index size with margin
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        #Resizes a second time to prevent uv flipping on secondary button presses
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        
        #Aligns the top of the island to the top of the selected index
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        
        #Aligns the left side of the island to the left side of UV space
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}

class UV_OT_trim_center_id_1(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 1, Center"""
    bl_label = "Align center index 1"
    bl_idname = "uv.trim_center_id_1"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 1.0,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.03125,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()

        return {'FINISHED'}

class UV_OT_trim_right_id_1(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 1, Right"""
    bl_label = "Align right index 1"
    bl_idname = "uv.trim_right_id_1"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 1.0,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.03125,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )        
    
    def execute(self, context):
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        
        return {'FINISHED'}		

class UV_OT_trim_left_id_2(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 2, Left"""
    bl_label = "Align left index 2"
    bl_idname = "uv.trim_left_id_2"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.96875,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.0625,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - global_def.trimHeight['1']
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))

        return {'FINISHED'}		

class UV_OT_trim_center_id_2(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 2, Center"""
    bl_label = "Align center index 2"
    bl_idname = "uv.trim_center_id_2"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.96875,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.0625,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - global_def.trimHeight['1']
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_2(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 2, Right"""
    bl_label = "Align right index 2"
    bl_idname = "uv.trim_right_id_2"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.96875,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.0625,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - global_def.trimHeight['1']
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}			

class UV_OT_trim_left_id_3(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 3, Left"""
    bl_label = "Align left index 3"
    bl_idname = "uv.trim_left_id_3"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.90625,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.0625,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_3(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 3, Center"""
    bl_label = "Align center index 3"
    bl_idname = "uv.trim_center_id_3"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.90625,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.125,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_3(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 3, Right"""
    bl_label = "Align right index 3"
    bl_idname = "uv.trim_right_id_3"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.90625,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.125,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}			
		
class UV_OT_trim_left_id_4(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 4, Left"""
    bl_label = "Align left index 4"
    bl_idname = "uv.trim_left_id_4"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.78125,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.25,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
         
        return {'FINISHED'}		

class UV_OT_trim_center_id_4(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 4, Center"""
    bl_label = "Align center index 4"
    bl_idname = "uv.trim_center_id_4"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.78125,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.25,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_4(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 4, Right"""
    bl_label = "Align right index 4"
    bl_idname = "uv.trim_right_id_4"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.78125,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.25,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_left_id_5(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 5, Left"""
    bl_label = "Align left index 5"
    bl_idname = "uv.trim_left_id_5"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.53125,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.4375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_5(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 5, Center"""
    bl_label = "Align center index 5"
    bl_idname = "uv.trim_center_id_5"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.53125,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.4375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_5(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 5, Right"""
    bl_label = "Align right index 5"
    bl_idname = "uv.trim_right_id_5"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.53125,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.4375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_left_id_6(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 6, Left"""
    bl_label = "Align left index 6"
    bl_idname = "uv.trim_left_id_6"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_6(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 6, Center"""
    bl_label = "Align center index 6"
    bl_idname = "uv.trim_center_id_6"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_6(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 6, Right"""
    bl_label = "Align right index 6"
    bl_idname = "uv.trim_right_id_6"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}	

class UV_OT_trim_left_id_7(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 7, Left"""
    bl_label = "Align left index 7"
    bl_idname = "uv.trim_left_id_7"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
 
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_7(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 7, Center"""
    bl_label = "Align center index 7"
    bl_idname = "uv.trim_center_id_7"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_7(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 7, Right"""
    bl_label = "Align right index 7"
    bl_idname = "uv.trim_right_id_7"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}	

class UV_OT_trim_left_id_8(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 8, Left"""
    bl_label = "Align left index 8"
    bl_idname = "uv.trim_left_id_8"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_8(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 8, Center"""
    bl_label = "Align center index 8"
    bl_idname = "uv.trim_center_id_8"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_8(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 8, Right"""
    bl_label = "Align right index 8"
    bl_idname = "uv.trim_right_id_8"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}	

class UV_OT_trim_left_id_9(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 9, Left"""
    bl_label = "Align left index 9"
    bl_idname = "uv.trim_left_id_9"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_9(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 9, Center"""
    bl_label = "Align center index 9"
    bl_idname = "uv.trim_center_id_9"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_9(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 9, Right"""
    bl_label = "Align right index 9"
    bl_idname = "uv.trim_right_id_9"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}	

class UV_OT_trim_left_id_10(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 10, Left"""
    bl_label = "Align left index 10"
    bl_idname = "uv.trim_left_id_10"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_10(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 10, Center"""
    bl_label = "Align center index 10"
    bl_idname = "uv.trim_center_id_10"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_10(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 10, Right"""
    bl_label = "Align right index 10"
    bl_idname = "uv.trim_right_id_10"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}	

class UV_OT_trim_left_id_11(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 11, Left"""
    bl_label = "Align left index 11"
    bl_idname = "uv.trim_left_id_11"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
 
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'] + global_def.trimHeight['10'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_11(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 11, Center"""
    bl_label = "Align center index 11"
    bl_idname = "uv.trim_center_id_11"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'] + global_def.trimHeight['10'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_11(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 11, Right"""
    bl_label = "Align right index 11"
    bl_idname = "uv.trim_right_id_11"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'] + global_def.trimHeight['10'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}	

class UV_OT_trim_left_id_12(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 12, Left"""
    bl_label = "Align left index 12"
    bl_idname = "uv.trim_left_id_12"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'] + global_def.trimHeight['10'] + global_def.trimHeight['11'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_left_index(uvIndex = 0 + ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}		

class UV_OT_trim_center_id_12(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 12, Center"""
    bl_label = "Align center index 12"
    bl_idname = "uv.trim_center_id_12"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'] + global_def.trimHeight['10'] + global_def.trimHeight['11'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_center_index()
        
        return {'FINISHED'}		

class UV_OT_trim_right_id_12(bpy.types.Operator):
    """Aligns selected UV Island(s) to Trim Index 12, Right"""
    bl_label = "Align right index 12"
    bl_idname = "uv.trim_right_id_12"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    ##################################
    # Properties
    ##################################
    uvMargin : bpy.props.FloatProperty(
        name = "UV Padding Multiplier",
        default = 3,
        description = "Multiplier for adding Mipmap padding"
    )    
    
    locateIndex : bpy.props.FloatProperty(
        name = "Index Location",
        default = 0.09375,
        description = "Exact position for start of UV Index on Y axis",
        precision = 5,
        options={'HIDDEN'}
    )

    sizeRatio : bpy.props.FloatProperty(
        name = "Index Size",
        default = 0.09375,
        description = "Size of UV index in percent of 0-1 UV space",
        precision = 5,
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        self.locateIndex = 1.0 - (global_def.trimHeight['1'] + global_def.trimHeight['2'] + global_def.trimHeight['3'] + global_def.trimHeight['4'] + global_def.trimHeight['5'] +
            global_def.trimHeight['6'] + global_def.trimHeight['7'] + global_def.trimHeight['8'] + global_def.trimHeight['9'] + global_def.trimHeight['10'] + global_def.trimHeight['11'])
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.equalize_index_scale(ratio = self.sizeRatio - (.001 * self.uvMargin))
        bpy.ops.uv.align_top_index(uvIndex = self.locateIndex - ((.001 * self.uvMargin) / 2))
        bpy.ops.uv.align_right_index(uvIndex = 1 - ((.001 * self.uvMargin) / 2))
        
        return {'FINISHED'}	


#################################
# REGISTRATION
#################################
_om = operator_manager.om

#Registers resize classes in blender
_om.addOperator(UV_OT_align_top_index)
_om.addOperator(UV_OT_align_left_index)
_om.addOperator(UV_OT_align_right_index)
_om.addOperator(UV_OT_align_center_index)
_om.addOperator(UV_OT_equalize_index_scale)

#Registers button classes in blender
_om.addOperator(UV_OT_trim_left_id_1)
_om.addOperator(UV_OT_trim_center_id_1)
_om.addOperator(UV_OT_trim_right_id_1)
_om.addOperator(UV_OT_trim_left_id_2)
_om.addOperator(UV_OT_trim_center_id_2)
_om.addOperator(UV_OT_trim_right_id_2)
_om.addOperator(UV_OT_trim_left_id_3)
_om.addOperator(UV_OT_trim_center_id_3)
_om.addOperator(UV_OT_trim_right_id_3)
_om.addOperator(UV_OT_trim_left_id_4)
_om.addOperator(UV_OT_trim_center_id_4)
_om.addOperator(UV_OT_trim_right_id_4)
_om.addOperator(UV_OT_trim_left_id_5)
_om.addOperator(UV_OT_trim_center_id_5)
_om.addOperator(UV_OT_trim_right_id_5)
_om.addOperator(UV_OT_trim_left_id_6)
_om.addOperator(UV_OT_trim_center_id_6)
_om.addOperator(UV_OT_trim_right_id_6)
_om.addOperator(UV_OT_trim_left_id_7)
_om.addOperator(UV_OT_trim_center_id_7)
_om.addOperator(UV_OT_trim_right_id_7)
_om.addOperator(UV_OT_trim_left_id_8)
_om.addOperator(UV_OT_trim_center_id_8)
_om.addOperator(UV_OT_trim_right_id_8)
_om.addOperator(UV_OT_trim_left_id_9)
_om.addOperator(UV_OT_trim_center_id_9)
_om.addOperator(UV_OT_trim_right_id_9)
_om.addOperator(UV_OT_trim_left_id_10)
_om.addOperator(UV_OT_trim_center_id_10)
_om.addOperator(UV_OT_trim_right_id_10)
_om.addOperator(UV_OT_trim_left_id_11)
_om.addOperator(UV_OT_trim_center_id_11)
_om.addOperator(UV_OT_trim_right_id_11)
_om.addOperator(UV_OT_trim_left_id_12)
_om.addOperator(UV_OT_trim_center_id_12)
_om.addOperator(UV_OT_trim_right_id_12)