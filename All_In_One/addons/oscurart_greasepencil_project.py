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
    "name": "Project Grease Pencil",
    "author": "Oscurart",
    "version": (1, 0),
    "blender": (2, 76, 2),
    "api": 40600,
    "location": "Search > Project Grease Pencil",
    "description": "Project selected vertices in a grease pencil draw.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
import bmesh
from mathutils.geometry import intersect_line_line
from mathutils import Vector

def main(context,vaxis,gpAxis):
    axisdict = {"X":0,"Y":1,"Z":2}
    mesh = bpy.context.object
    bm = bmesh.from_edit_mesh(mesh.data)
    axis = axisdict[vaxis]
    gpaxis = axisdict[gpAxis]
    for vertice in bm.verts:
        if vertice.select:
            imen = -1000
            imay = 1000
            punto = vertice.co + mesh.location
            jj= [point.co for point in bpy.context.object.grease_pencil.layers.active.frames[0].strokes[0].points]
            for point in bpy.context.object.grease_pencil.layers.active.frames[0].strokes[-1].points:
                if point.co[gpaxis] < punto[gpaxis] and point.co[gpaxis] > imen:
                    imen = point.co[gpaxis]
                    men = point.co
                if point.co[gpaxis] > punto[gpaxis] and point.co[gpaxis] < imay:
                    imay = point.co[gpaxis]
                    may = point.co                       
            try :
                may
                men
            except:
                print("wrong projection axis!")
                break
       
            if axis == 0:
                try:
                    vertice.co = (intersect_line_line(men,may,punto,(punto[0]+1,punto[1],punto[2]))[0][0] - mesh.location[0],
                        vertice.co.y,
                        vertice.co.z)   
                except:
                    pass        
            if axis == 1:
                try:
                    vertice.co = (vertice.co.x,
                        intersect_line_line(men,may,punto,(punto[0],punto[1]+1,punto[2]))[0][1] - mesh.location[1],
                        vertice.co.z)         
                except:
                    pass                                  
            if axis == 2:    
                try:                           
                    vertice.co = (vertice.co.x,
                        vertice.co.y,
                        intersect_line_line(men,may,punto,(punto[0],punto[1],punto[2]+1))[0][2] - mesh.location[2])     
                except:
                    pass              
    bmesh.update_edit_mesh(mesh.data)



class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.project_grease_pencil"
    bl_label = "Project Grease Pencil"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    gpAxis = bpy.props.EnumProperty(
            name="Grease Pencil:",
            description="Grease pencil Along Axis",
            items=(("X", "Along X", "Along X Axis"),
                   ("Y", "Along Y", "Along Y Axis"),
                   ("Z", "Along Z", "Along Z Axis")),
            default="Z",
            )

    Axis = bpy.props.EnumProperty(
            name="Vertices Axis:",
            description="Select axis for project vertices",
            items=(("X", "Along X", "Along X Axis"),
                   ("Y", "Along Y", "Along Y Axis"),
                   ("Z", "Along Z", "Along Z Axis")),
            default="X",
            )

    def execute(self, context):

        if bpy.context.object.grease_pencil == None:
            self.report({'ERROR'}, "You must set Grease Pencil!")
        else:    
            main(context,self.Axis,self.gpAxis)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SimpleOperator)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)


if __name__ == "__main__":
    register()

