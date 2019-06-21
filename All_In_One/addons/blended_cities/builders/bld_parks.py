##\file
# the park builder file
#
# should act as a reference for other builders files.
#
# builders ui can use existing methods (operators, buttons, panels..)
# 
import bpy
import mathutils
from mathutils import *
from blended_cities.core.class_main import *
from blended_cities.utils.meshes_io import *
from blended_cities.core.ui import *
from blended_cities.utils import library

## park builder class
#
# should act as a reference for other builders class.
#
# builders ui can use existing methods (operators, buttons, panels..)
# each builder class define its own field, depending of the needed parametrics. but some field are mandatory
#
#
class BC_parks(BC_elements,bpy.types.PropertyGroup) :
    bc_label = 'Parks'
    bc_description = 'a simple park. dots as trees and perimeters as lawns'
    bc_collection = 'parks'
    bc_element = 'park'

    parent = bpy.props.StringProperty() #  name of the group it belongs to

    inherit = bpy.props.BoolProperty(default=False,update=updateBuild)
    refresh = bpy.props.BoolProperty(
        update=updateBuild
        )

    def build(self,data) :

        mat_grass = 0
        mat_wall = 1

        verts = []
        faces = []
        mats  = []
        elements = []

        perimeters = data['perimeters']
        lines = data['lines']
        dots = data['dots']

        if len(perimeters) or len(dots) > 0 :

            fof = 0
            if len(perimeters) > 0 :
                    for perimeter in perimeters :
                        fpf = len(perimeter)
                        #  small walls around a lawn
                        verts.extend(perimeter)
                        for c in perimeter :
                            verts.append( Vector(( c[0],c[1],c[2] + 1 )) )
                            faces.extend(facesLoop(fof,fpf))
                            mats.extend( mat_wall for i in range(fpf) )
                        fof += fpf * 2
                        #  a lawn. this needs to know the nb of verts added after adding faces
                        #verts.extend(perimeter)
                        #    lawn = fill(verts[-fpf:],fof)
                        #    mats.extend( mat_grass for i in range(len(lawn)) )
                        #    faces.extend( lawn )
                        #fof += fpf * 2
                    elements.append( [verts,[],faces,mats] )

            if len(dots) > 0 :
                    for dot in dots :
                        elements.append( ['comtree_1',dot] )

            return elements

        else :
            return []



## park builder user interface class
class BC_parks_panel(bpy.types.Panel) :
    bl_label = 'Objects'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'parks'


    @classmethod
    def poll(self,context) :
        return pollBuilders(context,'parks')


    def draw_header(self, context):
        drawHeader(self,'builders')


    def draw(self, context):
        city = bpy.context.scene.city
        scene  = bpy.context.scene

        # either the park or its outline is selected : lookup
        #park, otl = city.elementGet(bpy.context.active_object)
        elm, grp, otl = city.elementGet('active',True)
        park = grp.asBuilder()

        layout  = self.layout
        layout.alignment  = 'CENTER'

        drawElementSelector(layout,otl)

        row = layout.row()
        row.label(text = 'Name : %s / %s'%(park.objectName(),park.name))

        row = layout.row()
        row.label(text = 'Refresh:')
        row.prop(park,'refresh')
