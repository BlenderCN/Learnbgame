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

bl_info = {
    "name": "LUT Editor",
    "description": "Edit 3d Lookup Tables",
    "author": "Björn Sonnenschein",
    "version": (0, 9),
    "blender": (2, 70, 0),
    "location": "Node Editor > UI panel, 3D View > UI Panel",
    "warning": "Experimental",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Learnbgame",
}


import bpy, os
from math import pow, radians
import mathutils

#TODO:

####Scene Properties
def setcursor(self, context):
    bpy.context.scene.cursor_location = (bpy.context.scene.lut_color[0],bpy.context.scene.lut_color[1],bpy.context.scene.lut_color[2])

bpy.types.Scene.lut_color = bpy.props.FloatVectorProperty(name="Color",
                                                          description="Show color as 3D Pointer",
                                                          subtype='COLOR', min=0,max=1,
                                                          update=setcursor)
bpy.types.Scene.lut_steps = bpy.props.IntProperty(name="Steps",
                                                          description="Show color as 3D Pointer", min=2, default=3)       
                                                          
bpy.types.Scene.lut_current = bpy.props.StringProperty(name="Curent Path",
                                                          description="Path of LUT in 3D View")                                                                                                         

class LUTPanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "3DLUT"

    def draw(self, context):
        if (bpy.context.active_node.type == 'APPLYLUT'):
            layout = self.layout
            row = layout.row()
            col = row.column()
            col.operator("lut.setup")
            row.operator("lut.update")
            row = layout.row()
            col = row.column()
            col.operator("lut.curves")
            row.prop(bpy.context.scene, "lut_steps")
            row = layout.row()
            col.operator("lut.selectdirectory")
            row.prop(bpy.context.scene, "lut_color")
            
            row = layout.row()
            col = row.column()
            row.operator("lut.iterate")
            col.operator("lut.save")
        
        
class ViewPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "3DLUT"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.operator("lut.reset")
        row.operator("lut.update")
        
        row = layout.row()
        col = row.column()
        col.operator("lut.modal_update")
        
        row = layout.row()
        row.prop(bpy.context.scene, "lut_color")
        
        
class saveOperator(bpy.types.Operator):
 
    bl_idname = "lut.save"
    bl_label = "Save"
        
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        node = bpy.context.active_node
        
        bpy.context.area.type = 'VIEW_3D'
        # get steps count
        steps = 0
        for i in bpy.context.visible_objects:
            if (i.hide_select == False):
                steps = steps + 1
                
        bpy.context.area.type = 'NODE_EDITOR'    
            
        steps = pow(steps, 1/3)
        stepsstr = str(int(round(steps, 0)))
        
        # Datei Öffnen (Später vom ausgewählten Node übernehmen!)        
        lut = open(self.filepath,"w")
        lut.write("LUT_3D_SIZE " + stepsstr + "\n")
        
        for i in reversed(bpy.context.visible_objects):
            if (i.hide_select == False):
                lut.write(str(i.location[0]) + ' ' + str(i.location[1]) + ' ' + str(i.location[2]) + "\n" )
                
                
        node.filepath = self.filepath 

        # Update the filepath of used lut in 3d View    
        bpy.context.scene.lut_current = node.filepath
        
        
        return {'FINISHED'}

    def invoke(self, context, event):
        if (bpy.context.active_node.type == 'APPLYLUT'):
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}       
        else:
            return{'FINISHED'}   
        
        
class updateOperator(bpy.types.Operator):
 
    bl_idname = "lut.update"
    bl_label = "update"
        
    def invoke(self, context, event ):

        # get steps count
        steps = 0
        for i in bpy.context.visible_objects:
            if (i.hide_select == False):
                steps = steps + 1
                
        steps = pow(steps, 1/3)
        stepsstr = str(int(round(steps, 0)))
        
        # Datei Öffnen (Später vom ausgewählten Node übernehmen!)   
        abspath = bpy.path.relpath(bpy.context.scene.lut_current)
        abspath = bpy.path.abspath(abspath)     
        lut = open(abspath,"w")
        lut.write("LUT_3D_SIZE " + stepsstr + "\n")
        
        for i in reversed(bpy.context.visible_objects):
            if (i.hide_select == False):
                lut.write(str(i.location[0]) + ' ' + str(i.location[1]) + ' ' + str(i.location[2]) + "\n" )
        currentframe = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = currentframe + 1
        bpy.context.scene.frame_current = currentframe
        return {'FINISHED'}
    
    
class selectDirectoryOperator(bpy.types.Operator):
    bl_idname = "lut.selectdirectory"
    bl_label = "File"

    def invoke(self, context, event):

        node = bpy.context.active_node
        path = node.filepath
        path = bpy.path.relpath(path)
        path = bpy.path.abspath(path)
        
        print (path)
        print (path)
        return {'FINISHED'}    
    
    
class modalUpdateOperator(bpy.types.Operator):
    bl_idname = "lut.modal_update"
    bl_label = "Update the LUT dynamically"
    
    def __init__(self):
        print("Start watching for updates")
 
    def __del__(self):
        print("Finished")
    
    def execute(self, context):
        updateOperator.invoke(self, context, 0)

    def modal(self, context, event):
        if (((event.type == 'LEFTMOUSE' or event.type == 'RIGHTMOUSE') and event.value == 'RELEASE') or event.type == 'RET' or event.type == 'MIDDLEMOUSE') :  # Apply
            ## TODO: Kontext Checken (muss 3d view sein...)
            self.execute(context)
            return {'PASS_THROUGH'}
        elif event.type == 'ESC':  # Confirm
            return {'FINISHED'}
        else: 
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.execute(context)
        return {'RUNNING_MODAL'}
        
        
class resetOperator(bpy.types.Operator):
 
    bl_idname = "lut.reset"
    bl_label = "reset"
        
    def invoke(self, context, event ):
        for i in bpy.context.selected_objects:
            coordinates = i.name.split(',')
            i.location = (float(coordinates[0]),float(coordinates[1]),float(coordinates[2]))
        return {'FINISHED'}


class iterateOperator(bpy.types.Operator):
 
    bl_idname = "lut.iterate"
    bl_label = "iterate"
        
    def invoke(self, context, event ):
        scene = bpy.context.scene
        tree = scene.node_tree

        # check if there is an applylutnode
        
        node = bpy.context.active_node

        updateOperator.invoke(self, context, 0)
        
        try:
            lut = open(bpy.context.scene.lut_current,"r")

        except:
            print("No LUT Present.")
            return {'FINISHED'}
        
        steps = int((lut.readline()).split()[1])
        
        if (node.type == 'APPLYLUT' and steps != bpy.context.scene.lut_steps):

            matrix = [ [], [], []]
            
            steps_new = bpy.context.scene.lut_steps

            for B in range(1, steps + 1):
                for G in range(1, steps + 1):
                    for R in range (1, steps + 1):
                        values = (lut.readline()).split()
                        matrix[0].append(float(values[0]))
                        matrix[1].append(float(values[1]))
                        matrix[2].append(float(values[2]))
            lut.close()
            
            #print (matrix)
            
            lut = open(bpy.context.scene.lut_current,"w")   
            lut.write("LUT_3D_SIZE " + str(steps_new) + "\n")
            for B in range(1, steps_new + 1):
                for G in range(1, steps_new + 1):
                    for R in range (1, steps_new + 1):
                        
                        Coord = [0,0,0]
                        Rvalue = (R - 1) / (steps_new - 1)
                        Gvalue = (G - 1) / (steps_new - 1)
                        Bvalue = (B - 1) / (steps_new - 1)
                        
                        #print(str(Rvalue) + " " + str(Gvalue) + " " + str(Bvalue) + "\n")
                        
                        count = 0
                        for Bo in range(1, steps + 1):
                            for Go in range(1, steps + 1):
                                for Ro in range (1, steps + 1):     
                                    
                                    RvalueOld = (Ro - 1) / (steps - 1)
                                    GvalueOld = (Go - 1) / (steps - 1)
                                    BvalueOld = (Bo - 1) / (steps - 1)
                                    
                                    dR = abs(RvalueOld - Rvalue)
                                    dG = abs(GvalueOld - Gvalue)
                                    dB = abs(BvalueOld - Bvalue)
                                    
                                    if ( dR < 1/(steps - 1) and dG < 1/(steps - 1) and dB < 1/(steps - 1)):

                                        weight = ( 1 - dR * (steps - 1) ) * ( 1 - dG * (steps - 1) ) * ( 1 - dB * (steps - 1) )
                                        Coord[0] = Coord[0] + matrix[0][count] * weight
                                        Coord[1] = Coord[1] + matrix[1][count] * weight
                                        Coord[2] = Coord[2] + matrix[2][count] * weight

                                    count = count + 1
         
                        lut.write(str(Coord[0]) + " " + str(Coord[1]) + " " + str(Coord[2]) + "\n")
                                
                       
            lut.close()
            
            node.filepath = bpy.context.scene.lut_current
            setupOperator.invoke(self, context, 0)
            
        return {'FINISHED'}


class setupOperator(bpy.types.Operator):
 
    bl_idname = "lut.setup"
    bl_label = "setup"
        
    def invoke(self, context, event ):
        scene = bpy.context.scene
        tree = scene.node_tree

        ## Delete old 
        bpy.context.area.type = 'VIEW_3D'
        for i in bpy.context.visible_objects:
            i.hide_select = False
            i.select = True
        bpy.ops.view3d.select_or_deselect_all(deselect=False)
        bpy.ops.object.delete()
        
        #setup material
        material = bpy.data.materials.new('LUTmaterial')
        material.use_shadeless = True
        material.use_object_color = True
        
        bpy.context.area.type = 'NODE_EDITOR'
        
        # check if there is an applylutnode
        
        node = bpy.context.active_node
        
        if (node.type == 'APPLYLUT'):
            
            lutexists = True
            
            path = node.filepath
            if (path != ""):
                abspath = bpy.path.relpath(path)
                abspath = bpy.path.abspath(abspath)
                
                try:
                    lut = open(abspath,"r")
            
                except:
                    lutexists = False
                
                
            else:
                try:
                    abspath = bpy.path.relpath(bpy.context.scene.lut_current)
                    abspath = bpy.path.abspath(abspath)
                    lutexists = False
                except:
                    print("No LUT present.")
                    return {'FINISHED'}

            #Setup LUT File -> hinterher mode a und werte übernehmen.
            if (lutexists == False):
                steps = scene.lut_steps
                if (path == ""):
                    try:
                        lut = open(abspath,"w")
                        node.filepath = bpy.context.scene.lut_current
                        path = node.filepath
                    except:
                        print("No LUT present.")
                        return {'FINISHED'}
                else: 
                    lut = open(abspath,"w")
                    
                lut.write("LUT_3D_SIZE " + str(steps) + "\n")
                
            else:
                steps = int((lut.readline()).split()[1])
            
            print(steps)
            # Update the filepath of used lut in 3d View    
            bpy.context.scene.lut_current = path
            
            #Rotation for the spheres
            rot = [35*0.0174533, 0, -45*0.0174533]
            ssize = (1/(steps*10))
            csize = (1/(steps*25))
            
            bpy.context.area.type = 'VIEW_3D'
            
            for B in range(1, steps + 1):
                for G in range(1, steps + 1):
                    for R in range (1, steps + 1):
                        
                        #Different Values for spheres and boxes                        
                        RvalueR = (R - 1) / (steps - 1)
                        GvalueR = (G - 1) / (steps - 1)
                        BvalueR = (B - 1) / (steps - 1)    
                        
                        color = [pow(RvalueR, 1/2.2), pow(GvalueR, 1/2.2), pow(BvalueR, 1/2.2), 1.0]
                            
                        if (lutexists == False):
                            Rvalue = RvalueR
                            Gvalue = GvalueR
                            Bvalue = BvalueR
                        else:
                            values = (lut.readline()).split()
                            Rvalue = float(values[0])
                            Gvalue = float(values[1])
                            Bvalue = float(values[2])
                        
                        if (lutexists == False):
                            lut.write(str(Rvalue) + " " + str(Gvalue) + " " + str(Bvalue) + "\n")
                        
                        ## 3d stuff
                        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, size=ssize,location=(Rvalue,Gvalue,Bvalue), rotation=rot)
                        sphere = bpy.context.selected_objects[0]
                        sphere.name = str(Rvalue) + ',' + str(Gvalue) + ',' + str(Bvalue) + ',' + 'unique' ##Namen!
                        bpy.ops.object.constraint_add(type='CHILD_OF')    
                        sphere.constraints[0].influence = 0    
                        sphere.lock_rotation = (True,True,True) 
                        sphere.lock_scale = (True,True,True) 
                        sphere.color = (color)
                        sphere.data.materials.append(material)

                        bpy.ops.mesh.primitive_cube_add(radius=csize,location=(RvalueR,GvalueR,BvalueR))
                        staticsphere = bpy.context.selected_objects[0]
                        staticsphere.name = str(Rvalue) + ',' + str(Gvalue) + ',' + str(Bvalue) + ',' + 'static'
                        staticsphere.lock_location = (True,True,True) 
                        staticsphere.lock_rotation = (True,True,True) 
                        staticsphere.lock_scale = (True,True,True) 
                        staticsphere.hide_select = True
                        staticsphere.color = (color)
                        staticsphere.data.materials.append(material)
                        sphere.constraints[0].target = staticsphere
  
            bpy.context.area.type = 'NODE_EDITOR'
            lut.close()
        
        return {'FINISHED'}


class curvesOperator(bpy.types.Operator):
 
    bl_idname = "lut.curves"
    bl_label = "Curves"
        
    def invoke(self, context, event ):
        scene = bpy.context.scene
        tree = scene.node_tree
        node = bpy.context.selected_nodes
        
        if (len(node) > 1):
        
            if (node[0].type == 'APPLYLUT' and node[1].type == 'CURVE_RGB'):

                lutexists = True
                steps = scene.lut_steps
                path = node[0].filepath
                if (path != ""):
                    abspath = bpy.path.relpath(path)
                    abspath = bpy.path.abspath(abspath)

                else: 
                    try:
                        abspath = bpy.path.relpath(bpy.context.scene.lut_current)
                        abspath = bpy.path.abspath(abspath)
                        
                    except:
                        print("No LUT present.")
                        return {'FINISHED'}
                

                if (path == ""):
                    try:
                        lut = open(abspath,"w")
                        node[0].filepath = bpy.context.scene.lut_current
                        path = node[0].filepath
                    except:
                        print("No LUT present.")
                        return {'FINISHED'}
                else:
                    lut = open(abspath,"w")

                lut.write("LUT_3D_SIZE " + str(steps) + "\n")
                
                # Update the filepath of used lut in 3d View    

                bpy.context.scene.lut_current = path
                
                for B in range(1, steps + 1):
                    for G in range(1, steps + 1):
                        for R in range (1, steps + 1):
                            
                            RvalueR = (R - 1) / (steps - 1)
                            GvalueR = (G - 1) / (steps - 1)
                            BvalueR = (B - 1) / (steps - 1)  
                            
                            node[1].mapping.initialize()                        
                            Rvalue = node[1].mapping.curves[3].evaluate(node[1].mapping.curves[0].evaluate((R - 1) / (steps - 1)))
                            Gvalue = node[1].mapping.curves[3].evaluate(node[1].mapping.curves[1].evaluate((G - 1) / (steps - 1)))
                            Bvalue = node[1].mapping.curves[3].evaluate(node[1].mapping.curves[2].evaluate((B - 1) / (steps - 1)))

                            lut.write(str(Rvalue) + " " + str(Gvalue) + " " + str(Bvalue) + "\n")
                lut.close()
            
                setupOperator.invoke(self, context, 0)       
        
        return {'FINISHED'}
    
    
def register():
    bpy.utils.register_class( iterateOperator )
    bpy.utils.register_class( curvesOperator )
    bpy.utils.register_class( saveOperator )
    bpy.utils.register_class( selectDirectoryOperator )
    bpy.utils.register_class( modalUpdateOperator )
    bpy.utils.register_class( setupOperator )
    bpy.utils.register_class( LUTPanel )
    bpy.utils.register_class( updateOperator ) 
    bpy.utils.register_class( resetOperator ) 
    bpy.utils.register_class( ViewPanel ) 
    
    
def unregister():
    bpy.utils.unregister_class( iterateOperator )
    bpy.utils.unregister_class( curvesOperator )
    bpy.utils.unregister_class( saveOperator )
    bpy.utils.unregister_class( selectDirectoryOperator ) 
    bpy.utils.unregister_class( modalUpdateOperator )    
    bpy.utils.unregister_class( setupOperator )
    bpy.utils.unregister_class( LUTPanel )    
    bpy.utils.unregister_class( updateOperator )
    bpy.utils.unregister_class( resetOperator )     
    bpy.utils.unregister_class( ViewPanel ) 
if __name__ == "__main__":
    register()