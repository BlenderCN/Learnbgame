# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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

# Geometric Outlines Generator (W.I.P.)
# alpha 0.44
# Pablo Gentile 1/2019
# https://github.com/g3ntile/geometric-inklines

bl_info = {
    "name": "GEO INKlines",
    "category": "Learnbgame",
    "author": "Pablo Gentile",
    "version": (0, 0, 5),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf",
    "description": "Adds and administrates a combo of modifiers, vertex groups and materialas (TO DO) to generate geometric inverted hull outlines to objects that work in realtime",
    "warning": "Beta version. Handle with care.",
    "wiki_url": "https://github.com/g3ntile/geometric-inklines/wiki",
    "tracker_url": "https://github.com/g3ntile/geometric-inklines" ,
}

import bpy
import mathutils
from math import radians

# =================================== OPERATORS =======================
# ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷
# ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ ADD OUTLINE OPERATOR 

class genOutline(bpy.types.Operator):
    """Adds a Solidify modifier for making inverted hull outlines"""
    bl_idname = "object.geoink_outline"
    bl_label = "add Outline"

    C = bpy.context
    #obj = bpy.context.active_object
    #ob = obj

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        C = bpy.context
        # main(context)
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        C.object.modifiers[len(C.object.modifiers)-1].name = "Outline"
        C.object.modifiers["Outline"].material_offset = 16384
        C.object.modifiers["Outline"].use_flip_normals = 1
        C.object.modifiers["Outline"].thickness = -.01
        C.object.modifiers["Outline"].show_expanded = False
        C.object.modifiers["Outline"].thickness_vertex_group = 0.5
        C.object.modifiers["Outline"].vertex_group = "__thickness__"
        
        return {'FINISHED'}
    
# ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷  Remove Outline Operator
class genNoOutline(bpy.types.Operator):
    """Removes the inverted hull Outlines"""
    bl_idname = "object.geoink_no_outline"
    bl_label = "remove Outline"

    C = bpy.context
    #obj = bpy.context.active_object
    #ob = obj

    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        C = bpy.context
        C.object.modifiers.remove(C.object.modifiers.get("Outline"))
        
        return {'FINISHED'}
    
    
# ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ ADD INLINE OPERATOR 

class genInnerline(bpy.types.Operator):
    """Adds a Bevel modifier for making geometric inner lines"""
    bl_idname = "object.geoink_innerline"
    bl_label = "add inner lines"

    C = bpy.context
    #obj = bpy.context.active_object
    #ob = obj

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        C = bpy.context
        
        bpy.ops.object.modifier_add(type='BEVEL')
        C.object.modifiers[len(C.object.modifiers)-1].name = "InnerLine"
        C.object.modifiers["InnerLine"].material = 1
        C.object.modifiers["InnerLine"].width = .0025
        C.object.modifiers["InnerLine"].limit_method = 'ANGLE'
        C.object.modifiers["InnerLine"].show_expanded = False
        return {'FINISHED'}
    
# ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ Remove Inner line Operator
class genNoInnerline(bpy.types.Operator):
    """Removes the beveled innerlines"""
    bl_idname = "object.geoink_no_innerline"
    bl_label = "remove innerline"

    C = bpy.context
    #obj = bpy.context.active_object
    #ob = obj

    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        C = bpy.context
        C.object.modifiers.remove(C.object.modifiers.get("InnerLine"))
        
        return {'FINISHED'}
    
# ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ set up thickness maps 
class genNormals2Thickness(bpy.types.Operator):
    """Generates a normals based thickness map to control the stroke thickness variation of the outlines. Select only objects to generate vertical thickness maps, or include ONE light in the selection to make it relative to the light position."""
    bl_idname = "object.geoink_normals2thick"
    bl_label = "generate thickness map"

    C = bpy.context
    #obj = bpy.context.active_object
    #ob = obj

    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        groupName = "__thickness__"

        import mathutils
        from math import radians

        # Includes light if present 9
        myLamp = None
        hasLight = False
        myLightVector = mathutils.Vector((0,0,65535))
        if len(bpy.context.selected_objects) > 1 :
            print ("\n\n+++++++ 2! ")
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    # mesh
                    print ('mesh!')
                elif ob.type == 'LIGHT':
                    # light
                    # Lamp based normals
                    myLamp = ob
                    hasLight = True
                    if ob.data.type == 'SUN':
                        myLightVector = myLamp.rotation_euler
                        myLightIsSun = True
                    else:
                        myLightVector = myLamp.location
                        myLightIsSun = False
                    #myLamp = bpy.data.objects['Lamp']



        

        # Convierte la rotacion de la lampara en vector
        # not working yet
        def myLampToVector(lampObj):
            return( mathutils.Quaternion((
                # tries to flip the quaternion somehow to get the shadows right
                # i don't get at all what I'm doing here, this is just intuitive math 
                                    -lampObj.rotation_quaternion[0], 
                                    lampObj.rotation_quaternion[1], 
                                    lampObj.rotation_quaternion[2],
                                    lampObj.rotation_quaternion[3])) )

        # check if group exists and create it 
        if "__thickness__" in bpy.context.active_object.vertex_groups:
            print("yes! exists")
            myGroup = bpy.context.active_object.vertex_groups[groupName]
        else:
            print("nope :-( it doesn't" )
            myGroup = bpy.context.active_object.vertex_groups.new(name=groupName)
        

        # Store the mesh
        mesh = bpy.context.active_object.data
        print("==== object: ", mesh.name)

        # backup rotation mode OBJECT
        rotModeBKP_ob = bpy.context.active_object.rotation_mode

        if hasLight:
            # backup rotation mode LIGHT
            rotModeBKP_li = myLamp.rotation_mode
        
            if not myLightIsSun:
                print('\n\n\n Point!')
                #POINT lights, spot, area
                # Sets weight based on angle with light DOT version
                # take rotation into account:
                bpy.context.active_object.rotation_mode = 'XYZ'
                myCrossedNormals = [ bpy.context.active_object.rotation_euler.to_matrix() @ v.normal for v in mesh.vertices  ]

                myCrossedNormals = [ ((v.dot(myLightVector) * -1+1)/2) for v in myCrossedNormals ]
                myWeights = [ ((v)) for v in myCrossedNormals]
            else: 
                print('\n\n\n Sun!')
                # FOR SUN LIGHTS
                # ROTATE OBJ OPPOSITE TO LIGHT
                            #rotModeBKP_ob = bpy.context.active_object.rotation_mode
                            #rotModeBKP_li = myLamp.rotation_mode

                # change mode to quaternion to avoid glitches and locks and simplify math
                myLamp.rotation_mode = 'QUATERNION'
                bpy.context.active_object.rotation_mode = 'QUATERNION'
                rotationBackup = ((
                                    bpy.context.active_object.rotation_quaternion[0] , 
                                    bpy.context.active_object.rotation_quaternion[1] , 
                                    bpy.context.active_object.rotation_quaternion[2] ,
                                    bpy.context.active_object.rotation_quaternion[3]))

                
                # multiply the quaternion of the obj with some sort of flipped quaternion of the lamp
                # WIP
                bpy.context.active_object.rotation_quaternion =   myLampToVector(myLamp) @ bpy.context.active_object.rotation_quaternion #myLamp.rotation_quaternion #


                ########. vertex normals according to world::
                #Actually it is, when the scaling factors are not the same (as @mifth pointed out) :
                # for v in bpy.context.active_object.data.vertices:
                #     myCrossedNormals[v] = v.normal.to_4d()
                #     myCrossedNormals[v].w = 0
                #     myCrossedNormals[v] = (bpy.context.active_object.matrix_world @ myCrossedNormals).to_3d()

                # If you know they are all the same, you can use :
                bpy.context.active_object.rotation_mode = 'XYZ'
                myCrossedNormals = [ bpy.context.active_object.rotation_euler.to_matrix() @ v.normal for v in mesh.vertices  ]
                
                #print( "\n\nto matrix: " , myCrossedNormals)
                myWeights = [ ((-v[2]+1)/2 ) for v in myCrossedNormals]


                # Restore rotation 
                bpy.context.active_object.rotation_mode = 'QUATERNION'
                bpy.context.active_object.rotation_quaternion = rotationBackup
                bpy.context.active_object.rotation_mode = rotModeBKP_ob
                

                
            #restore rotation mode LIGHT
            myLamp.rotation_mode = rotModeBKP_li
        else: 
            
            print('\n\n\n No light!')
            
            # take rotation into account:
            bpy.context.active_object.rotation_mode = 'XYZ'
            myCrossedNormals = [ bpy.context.active_object.rotation_euler.to_matrix() @ v.normal for v in mesh.vertices  ]
            
            # Sets weight based on vertex z normal
            myWeights = [ ((-v[2]+1)/2) for v in myCrossedNormals]
            #myWeights = [ ((-v.normal[2]+1)/2) for v in mesh.vertices] 
        
        # restore rotations
        bpy.context.active_object.rotation_mode = rotModeBKP_ob
        ### myLamp.rotation_mode = rotModeBKP_li 
        
        # Get the index of the required group
        index = bpy.context.active_object.vertex_groups[groupName].index

        # Exit Edit mode or fails
        bpy.ops.object.mode_set(mode='OBJECT')

        # Sets the calculated weights to each vertex in the mesh
        for v in mesh.vertices:
            #print ("i = ", i)
            # print ("v = ", v)
            # print ("w = ", myWeights[v.index]) 
            #obj.vertex_groups[index].add([v], myWeights[v], 'REPLACE')
            myGroup.add([v.index], myWeights[v.index], 'REPLACE')

        # Assign the map to the Outline if it exists
        try:
            bpy.context.active_object.modifiers["Outline"].vertex_group = "__thickness__"
        except:
            pass
        # Update to show results  
        bpy.context.active_object.data.update()  
        return {'FINISHED'}

# Materials creator
class genAddOutlineMaterial(bpy.types.Operator):
    """Adds a Material to make outlines"""
    bl_idname = "object.geoink_addoutlinemat"
    bl_label = "add outlines materials"

    C = bpy.context
    #obj = bpy.context.active_object
    #ob = obj
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        print('TO DO. Just a placeholder')

        ob = bpy.context.active_object

        # Get material
        outMat = bpy.data.materials.get("outline")
        if outMat is None:
            # create  outline material
            outMat = bpy.data.materials.new(name="outline")
            outMat.use_nodes = True
            # enable transparency
            outMat.blend_method = 'BLEND'
            # set vewport color
            outMat.diffuse_color = (0,0,0,1)
            # get the nodes
            nodes = outMat.node_tree.nodes
            print("\n\n === " , nodes)

            #start clean
            for node in nodes:
                nodes.remove(node)

            # create output node
            node_output = nodes.new(type='ShaderNodeOutputMaterial')   
            node_output.location = 400,0

            # create Mix node 1
            node_mix_1 = nodes.new(type='ShaderNodeMixShader')   
            node_mix_1.location = 0,0

            # create Mix node 2
            node_mix_2 = nodes.new(type='ShaderNodeMixShader')   
            node_mix_2.location = -200,50

            # create emission node
            node_emission = nodes.new(type='ShaderNodeEmission')
            node_emission.inputs[0].default_value = (0,0,0,1)  # black RGBA
            node_emission.inputs[1].default_value = 0 # strength
            node_emission.location = -400,220

            # create Geometry node
            node_geometry = nodes.new(type='ShaderNodeNewGeometry')   
            node_geometry.location = -400,110

            # create Transparent node
            node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')   
            node_transparent.location = -400,-420

            # create LightPath node
            node_lightpath = nodes.new(type='ShaderNodeLightPath')   
            node_lightpath.location = -400,-110




            # link nodes
            links = outMat.node_tree.links
            # MIX 1 -> OUTPUT
            link = links.new(node_mix_1.outputs[0], node_output.inputs[0])
            # MIX 2 -> MIX 1
            link = links.new(node_mix_2.outputs[0], node_mix_1.inputs[1])
            # EMISSION -> MIX 2
            link = links.new(node_emission.outputs[0], node_mix_2.inputs[1])
            # GEOMETRY -> MIX 2
            link = links.new(node_geometry.outputs[6], node_mix_2.inputs[0])
            # TRANSPARENT -> MIX 2
            link = links.new(node_transparent.outputs[0], node_mix_2.inputs[2])
            # TRANSPARENT -> MIX 1
            link = links.new(node_transparent.outputs[0], node_mix_1.inputs[1])
            # LIGHT PATH -> MIX 1
            link = links.new(node_lightpath.outputs[0], node_mix_1.inputs[0])
            # MIX 1 -> MIX 2
            link = links.new(node_mix_2.outputs[0], node_mix_1.inputs[2])



            

        # Assign it to object
        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials.append(outMat)
        else:
            # no slots
            # dummy main material:
            dummyMat = bpy.data.materials.new(name="Material")
            ob.data.materials.append(dummyMat)
            dummyMat.use_nodes = True
            ob.data.materials.append(outMat)

            #

        # SETS BACKFACE CULLING
        # bpy.data.screens["Layout"].shading.show_backface_culling = True

        return {'FINISHED'}




    ######################################
    ################# PANEL
    
class genOutlinesPanel(bpy.types.Panel):
    """Creates a Panel in the N Panel"""
    bl_label = "GEO INKlines beta 0.5"
    bl_idname = "OBJECT_PT_GEOINKlines"
    #bl_space_type = 'PROPERTIES'
    #bl_region_type = 'WINDOW'
    #bl_context = "modifier"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "GEO Inklines"
    bl_options = {'DEFAULT_CLOSED'} 

    C = bpy.context
    #obj = bpy.context.active_object
    #ob = obj


    def draw(self, context):
        layout = self.layout

        obj = bpy.context.object
        C = bpy.context

        row = layout.row()
        row.label(text="https://github.com/g3ntile/geometric-inklines")

        # outline material generator
        row = layout.row() 
        row.operator("object.geoink_addoutlinemat")

        #row = layout.row()
        #row.prop_search(bpy.context.scene, "theChosenObject", bpy.context.scene, "objects")
        
        # thickness map generator
        ##row = layout.row()
        ##row.label(text="Variable thickness map generator")
        row = layout.row()
        # row.label(text="Generates a thickness map to control the stroke thickness\nvariation of the outlines.\nSelect only objects to generate vertical thickness maps,\nor include ONE light to make it relative to the light position.")

        row = layout.row() 
        row.operator("object.geoink_normals2thick" , text="1. generate thickness map")
       
        # add Buttons
        row = layout.row()
        # if not (C.object.modifiers['Outline']):
        
        # check if theres already an Outline
        myOperator = "object.geoink_outline"
        myLabel = "2. add Outline"
        hasOutline = False
        for modifier in C.object.modifiers:
            if modifier.name == "Outline":
                myOperator = "object.geoink_no_outline"
                myLabel = "remove Outline"
                hasOutline = True
                
        row.operator(myOperator, text = myLabel)
            
            
        # check if theres already an innerLine
        myOperator = "object.geoink_innerline"
        myLabel = "3. add Inner Line"
        hasInline = False
        for modifier in C.object.modifiers:
            if modifier.name == "InnerLine":
                hasInline = True
                myOperator = "object.geoink_no_innerline"
                myLabel = "remove Inner Line"
        
        row.operator(myOperator, text = myLabel)
        
        # edit buttons
        # --- thickness
        row = layout.row()
        if hasOutline:
            row.prop(C.object.modifiers['Outline'], "thickness", text="Outer thickness")
        if hasInline:
            row.prop(C.object.modifiers['InnerLine'], "width", text="Inner thickness")
        
        # --- contrast
        row = layout.row()
        try:
            row.prop(C.object.modifiers['Outline'], "thickness_vertex_group", text="Outline flatness")
        except Exception: 
            pass
        row = layout.row()
        try:
            row.prop(C.object.modifiers['InnerLine'], "angle_limit", text="inner lines angle")
        except Exception: 
            pass
        # --- offset
        row = layout.row()
        try:
            row.prop(C.object.modifiers['Outline'], "offset", text="Outline offset")
        except Exception: 
            pass

        row = layout.row()
        try:
            row.prop(C.object.modifiers['Outline'], "material_offset", text="Outline material offset")
        except Exception: 
            pass
        try:
            row.prop(C.object.modifiers['InnerLine'], "material", text="Inner line material offset")
        except Exception: 
            pass

        # row.prop(C.object.modifiers['Outline'], "vertex_group" )


# ################################################################

#                         R E G I S T E R 

# ################################################################
def register():
    bpy.utils.register_class(genOutline)
    bpy.utils.register_class(genInnerline)
    bpy.utils.register_class(genNoOutline)
    bpy.utils.register_class(genNoInnerline)
    bpy.utils.register_class(genNormals2Thickness)
    bpy.utils.register_class(genAddOutlineMaterial)

    bpy.utils.register_class(genOutlinesPanel)

def unregister():
    bpy.utils.unregister_class(genOutline)
    bpy.utils.unregister_class(genInnerline)
    bpy.utils.unregister_class(genNoOutline)
    bpy.utils.unregister_class(genNoInnerline)
    bpy.utils.unregister_class(genNormals2Thickness)
    bpy.utils.unregister_class(genAddOutlineMaterial)

    bpy.utils.unregister_class(genOutlinesPanel)

if __name__ == "__main__":
    register()

