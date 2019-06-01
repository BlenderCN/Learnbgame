##\file
# the network builder file
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

## network builder class
#
# should act as a reference for other builders class.
#
# builders ui can use existing methods (operators, buttons, panels..)
# each builder class define its own field, depending of the needed parametrics. but some field are mandatory
#
#
class BC_networks(BC_elements,bpy.types.PropertyGroup) :
    bc_label = 'Network'
    bc_description = 'split a web like mesh into outline parts'
    bc_collection = 'networks'
    bc_element = 'network'

    #name = bpy.props.StringProperty()
    parent = bpy.props.StringProperty() #  name of the group it belongs to
    inherit = bpy.props.BoolProperty(default=False,update=updateBuild)
    floorNumber = bpy.props.IntProperty(
        default = 3,
        min=1,
        max=30,
        update=updateBuild
        )
    floorHeight = bpy.props.FloatProperty(
        default = 2.4,
        min=2.2,
        max=5.0,
        update=updateBuild
        )
    firstFloorHeight = bpy.props.FloatProperty(
        default = 3,
        min=2.2,
        max=5,
        update=updateBuild
        )
    firstFloor = bpy.props.BoolProperty(update=updateBuild)
    linesAsWall = bpy.props.BoolProperty(update=updateBuild)
    interFloorHeight = bpy.props.FloatProperty(
        default = 0.3,
        min=0.1,
        max=1.0,
        update=updateBuild
        )
    roofHeight = bpy.props.FloatProperty(
        default = 0.5,
        min=0.1,
        max=1.0,
        update=updateBuild
        )

    def build(self,data) :

        verts = []
        edges = []
        networks = []

        perimeters = data['perimeters']
        lines = data['lines']

        if len(perimeters) or len(lines) > 0 :

            if len(lines) > 0 :
                for line in lines :
                    verts = edgesEnlarge(line,1,'coord')
                    edges = edgesLoop(0,len(verts),False)
                    networks.append(['outline',verts, edges, [],  [] ])

            if len(perimeters) > 0 :
                for perimeter in perimeters :
                    verts = polyIn(perimeter,0.5,'coord')
                    edges = edgesLoop(0,len(verts),False)
                    
                    verts2 = polyIn(perimeter,-0.5,'coord')
                    edges2 = edgesLoop(len(verts),len(verts2),False)

                    verts.extend(verts2)
                    edges.extend(edges2)
                    networks.append(['outline',verts, edges, [],  [] ])

            return networks

        else :
            print('* cant build, no network in this outline')

    # returns the z coordinates of each level (ceilings, floors.. then roof)
    def heights(self,offset=0) :
        city = bpy.context.scene.city
        this = self
        while this.inherit == True :
            otl = this.Parent(True)
            print(this.name,this.inherit,otl.name)
            if otl.className() != this.className() : this.inherit = False 
            else : this = otl
        zs = [] # list of z coords of floors and ceilings
        for i in range( self.floorNumber ) :
            if i == 0 :
                zf = offset
                if self.firstFloor :
                    zc = offset + self.firstFloorHeight
                else :
                    zc = offset + this.floorHeight
            else :
                zf = zc + this.interFloorHeight
                zc = zf + this.floorHeight
            zs.append(zf)
            zs.append(zc)
        zs.append(zc + this.roofHeight) # roof

        return zs
 
    def height(self,offset=0) :
        return self.heights(offset)[-1]


## network builder user interface class
class BC_networks_panel(bpy.types.Panel) :
    bl_label = 'Networks'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'networks'


    @classmethod
    def poll(self,context) :
        return pollBuilders(context,'networks')


    def draw_header(self, context):
        drawHeader(self,'builders')


    def draw(self, context):
        city = bpy.context.scene.city
        scene  = bpy.context.scene
        ob = bpy.context.active_object

        # either the network or its outline is selected : lookup
        elm, grp, otl = city.elementGet('active',True)
        network = grp.asBuilder()

        layout  = self.layout
        layout.alignment  = 'CENTER'

        #  TABS
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(city.ui,'builder_tabs','builder')
        row.prop_enum(city.ui,'builder_tabs','materials')
        if city.ui.builder_tabs == 'builder' :

            row = layout.row()
            row.label(text = 'Name : %s / %s'%(network.objectName(),network.name))

            row = layout.row()
            #row.label(text = 'Floor Number:')
            #row.props_enum(bpy.data,'materials')
            #row.template_ID(ob, "active_material", new="material.new")

            row = layout.row()
            row.label(text = 'Floor Number:')
            row.prop(network,'floorNumber')

            row = layout.row()
            row.label(text = 'Build First Floor :')
            row.prop(network,'firstFloor')

            row = layout.row()
            row.label(text = 'Inherit Values :')
            row.prop(network,'inherit')

            if network.inherit : ena = False
            else : ena = True

            row = layout.row()
            row.active = ena
            row.label(text = 'Floor Height :')
            row.prop(network,'floorHeight')

            row = layout.row()
            row.active = network.firstFloor
            row.label(text = '1st Floor Height :')
            row.prop(network,'firstFloorHeight')

            row = layout.row()
            row.active = ena
            row.label(text = 'Inter Floor Height :')
            row.prop(network,'interFloorHeight')

            row = layout.row()
            row.active = ena
            row.label(text = 'Roof Height :')
            row.prop(network,'roofHeight')

            row = layout.row()
            row.active = True
            row.label(text = 'lines are walls :')
            row.prop(network,'linesAsWall')

        if city.ui.builder_tabs == 'materials' :
            drawBuilderMaterials(layout,network)

            
            
            
            