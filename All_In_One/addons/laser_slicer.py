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
     "name": "Laser Slicer",
     "author": "Ryan Southall",
     "version": (0, 9, 2),
     "blender": (2, 80, 0),
     "location": "3D View > Tools Panel",
     "description": "Makes a series of cross-sections and exports an svg file for laser cutting",
     "warning": "",
     "wiki_url": "tba",
     "tracker_url": "https://github.com/rgsouthall/laser_slicer/issues",
     "category": "Learnbgame",
     }

import bpy, os, bmesh, numpy
from bpy.props import FloatProperty, BoolProperty, EnumProperty, IntProperty, StringProperty, FloatVectorProperty

def newrow(layout, s1, root, s2):
    row = layout.row()
    row.label(text = s1)
    row.prop(root, s2)
    
def slicer(settings):
    f_scale = 1000 * bpy.context.scene.unit_settings.scale_length
    aob = bpy.context.active_object
    bm = bmesh.new()
    tempmesh = aob.to_mesh(bpy.context.depsgraph, apply_modifiers = True, calc_undeformed=False)
    bm.from_mesh(tempmesh)
    omw = aob.matrix_world
    bm.transform(omw)
    bpy.data.meshes.remove(tempmesh)
    aob.select_set(False)
    mwidth = settings.laser_slicer_material_width
    mheight = settings.laser_slicer_material_height
    lt = settings.laser_slicer_material_thick/f_scale
    sepfile = settings.laser_slicer_separate_files
    minz = min([v.co[2] for v in bm.verts])
    maxz = max([v.co[2] for v in bm.verts])
    lh = minz + lt * 0.5
    accuracy = settings.laser_slicer_accuracy
    ct = settings.laser_slicer_cut_thickness/f_scale
    svgpos = settings.laser_slicer_svg_position
    dpi = settings.laser_slicer_dpi
    yrowpos = 0
    xmaxlast = 0
    ofile = settings.laser_slicer_ofile
    mm2pi = dpi/25.4
    scale = f_scale*mm2pi
    ydiff, rysize  = 0, 0
    lcol = settings.laser_slicer_cut_colour
    lthick = settings.laser_slicer_cut_line
       
    if not any([o.get('Slices') for o in bpy.context.scene.objects]):
        me = bpy.data.meshes.new('Slices')
        cob = bpy.data.objects.new('Slices', me)
        cob['Slices'] = 1
        cobexists = 0
    else:
        for o in bpy.context.scene.objects:
            if o.get('Slices'):
                bpy.context.view_layer.objects.active = o

                for vert in o.data.vertices:
                    vert.select = True
                    
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.delete(type = 'VERT')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                me = o.data
                cob = o
                cobexists = 1
                break 
            
    vlen, elen, vlenlist, elenlist = 0, 0, [0], [0]
    vpos = numpy.empty(0)
    vindex = numpy.empty(0)
    vtlist = []
    etlist = []
    vlist = []
    elist = []
    erem = []
    
    while lh < maxz:
        cbm = bm.copy()
        newgeo = bmesh.ops.bisect_plane(cbm, geom = cbm.edges[:] + cbm.faces[:], dist = 0, plane_co = (0.0, 0.0, lh), plane_no = (0.0, 0.0, 1), clear_outer = False, clear_inner = False)['geom_cut']
        newverts = [v for v in newgeo if isinstance(v, bmesh.types.BMVert)]        
        newedges = [e for e in newgeo if isinstance(e, bmesh.types.BMEdge)]        
        voffset = min([v.index for v in newverts])
        lvpos = [v.co for v in newverts]  
        vpos = numpy.append(vpos, numpy.array(lvpos).flatten())
        vtlist.append([(v.co - cob.location)[0:2] for v in newverts])           
        etlist.append([[(v.co - cob.location)[0:2] for v in e.verts] for e in newedges])
        vindex = numpy.append(vindex, numpy.array([[v.index  - voffset + vlen for v in e.verts] for e in newedges]).flatten())
        vlen += len(newverts)
        elen += len(newedges)
        vlenlist.append(len(newverts) + vlenlist[-1])
        elenlist.append(len(newedges) + elenlist[-1])
        lh += lt
        cbm.free()  
        
    bm.free()        
    me.vertices.add(vlen)
    me.vertices.foreach_set('co', vpos)
    me.edges.add(elen)
    me.edges.foreach_set('vertices', vindex)
    
    if accuracy:
        vranges = [(vlenlist[i], vlenlist[i+1], elenlist[i], elenlist[i+1]) for i in range(len(vlenlist) - 1)]
        vtlist = []
        etlist = []
        
        for vr in vranges:
            vlist, elist, erem = [], [], []
            sliceedges = me.edges[vr[2]:vr[3]]
            edgeverts = [ed.vertices[0] for ed in sliceedges] + [ed.vertices[1] for ed in sliceedges]
            edgesingleverts = [ev for ev in edgeverts if edgeverts.count(ev) == 1]
            
            for ed in sliceedges:
                if ed.vertices[0] in [ev for ev in edgeverts if edgeverts.count(ev) > 2] and ed.vertices[1] in [ev for ev in edgeverts if edgeverts.count(ev) > 2]:
                    erem.append(ed)
            for er in erem:
                sliceedges.remove(er)
       
            vlen = len(me.vertices)
            
            if edgesingleverts:
                e = [ed for ed in sliceedges if ed.vertices[0] in edgesingleverts or ed.vertices[1] in edgesingleverts][0]
                if e.vertices[0] in edgesingleverts:
                    vlist.append(e.vertices[0])
                    vlist.append(e.vertices[1])
                else:
                    vlist.append(e.vertices[1])
                    vlist.append(e.vertices[0])
                elist.append(e)
            else:   
                elist.append(sliceedges[0]) # Add this edge to the edge list
                vlist.append(elist[0].vertices[0]) # Add the edges vertices to the vertex list
                vlist.append(elist[0].vertices[1])
                
            while len(elist) < len(sliceedges):
                va = 0
                for e in [ed for ed  in sliceedges if ed not in elist]:
                     if e.vertices[0] not in vlist and e.vertices[1] == vlist[-1]: # If a new edge contains the last vertex in the vertex list, add the other edge vertex
                         va = 1
                         vlist.append(e.vertices[0])
                         elist.append(e)
                         
                         if len(elist) == len(sliceedges):
                            vlist.append(-2) 
                            
                     if e.vertices[1] not in vlist and e.vertices[0] == vlist[-1]:
                         va = 1
                         vlist.append(e.vertices[1])
                         elist.append(e)
                         
                         if len(elist) == len(sliceedges):
                            vlist.append(-2)
                            
                     elif e.vertices[1] in vlist and e.vertices[0] in vlist and e not in elist: # The last edge already has it's two vertices in the vertex list so just add the edge
                         elist.append(e)
                         va = 2
                                                                                
                if va in (0, 2):
                    vlist.append((-1, -2)[va == 0])
                    
                    if len(elist) < len(sliceedges):
                        try:
                            e1 = [ed for ed in sliceedges if ed not in elist and (ed.vertices[0] in edgesingleverts or ed.vertices[1] in edgesingleverts)][0]
                            if e1.vertices[0] in edgesingleverts:
                                vlist.append(e1.vertices[0])
                                vlist.append(e1.vertices[1])
                            else:
                                vlist.append(e1.vertices[1])
                                vlist.append(e1.vertices[0])
                                
                        except Exception as e:
                            e1 = [ed for ed in sliceedges if ed not in elist][0]
                            vlist.append(e1.vertices[0])
                            vlist.append(e1.vertices[1])
                        elist.append(e1)
    
            vtlist.append([(me.vertices[v].co, v)[v < 0]  for v in vlist])            
            etlist.append([elist]) 
    
    if not sepfile:
        filename = os.path.join(os.path.dirname(bpy.data.filepath), aob.name+'.svg') if not ofile else bpy.path.abspath(ofile)
    else:
        if not ofile:
            filenames = [os.path.join(os.path.dirname(bpy.path.abspath(bpy.data.filepath)), aob.name+'{}.svg'.format(i)) for i in range(len(vlenlist))]
        else:
            filenames = [os.path.join(os.path.dirname(bpy.path.abspath(ofile)), bpy.path.display_name_from_filepath(ofile) + '{}.svg'.format(i)) for i in range(len(vlenlist))]

    for vci, vclist in enumerate(vtlist):
        if sepfile or vci == 0:
            svgtext = ''
            
        xmax = max([vc[0] for vc in vclist if vc not in (-1, -2)])
        xmin = min([vc[0] for vc in vclist if vc not in (-1, -2)])
        ymax = max([vc[1] for vc in vclist if vc not in (-1, -2)])
        ymin = min([vc[1] for vc in vclist if vc not in (-1, -2)])
        cysize = ymax - ymin + ct
        cxsize = xmax - xmin + ct
                
        if (sepfile and svgpos == '0') or (sepfile and vci == 0 and svgpos == '1'):
            xdiff = -xmin + ct
            ydiff = -ymin + ct

        elif (sepfile and svgpos == '1') or not sepfile:            
            if f_scale * (xmaxlast + cxsize) <= mwidth:
                xdiff = xmaxlast - xmin + ct
                ydiff = yrowpos - ymin + ct
                
                if rysize < cysize:
                    rysize = cysize
                
                xmaxlast += cxsize
                                
            elif f_scale * cxsize > mwidth:
                xdiff = -xmin + ct
                ydiff = yrowpos - ymin + ct
                yrowpos += cysize
                if rysize < cysize:
                    rysize = cysize
                
                xmaxlast = cxsize
                rysize = cysize
    
            else:
                yrowpos += rysize
                xdiff = -xmin + ct
                ydiff = yrowpos - ymin + ct
                xmaxlast = cxsize
                rysize = cysize
    
        elif sepfile and svgpos == '2':
            xdiff = mwidth/(2 * f_scale) - (0.5 * cxsize) - xmin
            ydiff = mheight/(2 * f_scale) - (0.5 * cysize) - ymin
               
        if not accuracy:
            svgtext += '<g>\n'
            svgtext += "".join(['<line x1="{0[0][0]}" y1="{0[0][1]}" x2="{0[1][0]}" y2="{0[1][1]}" style="stroke:rgb({1[0]},{1[1]},{1[2]});stroke-width:{2}" />\n'.format([(scale * (xdiff + v[0]), scale * (ydiff + v[1])) for v in e], [int(255 * lc) for lc in lcol], lthick) for e in etlist[vci]])
            svgtext += '</g>\n'
        else:
            points = "{:.3f},{:.3f} {:.3f},{:.3f} ".format(scale*(xdiff+vclist[0][0]), scale*(ydiff+vclist[0][1]), scale*(xdiff+vclist[1][0]), scale*(ydiff+vclist[1][1]))
            svgtext += '<g>\n'
            
            for vco in vclist[2:]:
                if vco in (-1, -2):
                    polyend = 'gon' if vco == -1 else 'line'
                    svgtext += '<poly{0} points="{1}" style="fill:none;stroke:rgb({2[0]},{2[1]},{2[2]});stroke-width:{3}" />\n'.format(polyend, points, [int(255 * lc) for lc in lcol], lthick)
                    points = '' 
                else:
                    points += "{:.2f},{:.2f} ".format(scale*(xdiff+vco[0]), scale*(ydiff+vco[1]))
             
            if points:
                svgtext += '<polygon points="{0}" style="fill:none;stroke:rgb({1[0]},{1[1]},{1[2]});stroke-width:{2}" />\n'.format(points, [int(255 * lc) for lc in lcol], lthick)
             
            svgtext += '</g>\n'          

        if sepfile:
            svgtext += '</svg>\n' 
            
            with open(filenames[vci], 'w') as svgfile:
                svgfile.write('<?xml version="1.0"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n\
                <svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n    width="{0}"\n    height="{1}"\n    viewbox="0 0 {0} {1}">\n\
                <desc>Laser SVG Slices from Object: Sphere_net. Exported from Blender3D with the Laser Slicer Script</desc>\n\n'.format(mwidth*mm2pi, mheight*mm2pi))
                
                svgfile.write(svgtext)
        
    if not sepfile:
        with open(filename, 'w') as svgfile:
            svgfile.write('<?xml version="1.0"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n\
                <svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n    width="{0}"\n    height="{1}"\n    viewbox="0 0 {0} {1}">\n\
                <desc>Laser SVG Slices from Object: Sphere_net. Exported from Blender3D with the Laser Slicer Script</desc>\n\n'.format(mwidth*mm2pi, mheight*mm2pi))
            
            svgfile.write(svgtext)
            svgfile.write("</svg>\n")
            
    if not cobexists:
        bpy.context.scene.collection.objects.link(cob)
        
    bpy.context.view_layer.objects.active = cob
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    aob.select_set(True)
    bpy.context.view_layer.objects.active = aob
        
class OBJECT_OT_Laser_Slicer(bpy.types.Operator):
    ''''''
    bl_idname = "object.laser_slicer"
    bl_label = "Laser Slicer"

    def execute(self, context):
        slicer(context.scene.slicer_settings)
        return {'FINISHED'}

class OBJECT_OT_Laser_Slicer_Panel(bpy.types.Panel):
    bl_label = "Laser Slicer Panel"
    bl_idname = "object.laser_slicer_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Laser"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row()
        row.label(text = "Material dimensions:")
        newrow(layout, "Thickness (mm):", scene.slicer_settings, 'laser_slicer_material_thick')
        newrow(layout, "Width (mm):", scene.slicer_settings, 'laser_slicer_material_width')
        newrow(layout, "Height (mm):", scene.slicer_settings, 'laser_slicer_material_height')
        row = layout.row()
        row.label(text = "Cut settings:")
        newrow(layout, "DPI:", scene.slicer_settings, 'laser_slicer_dpi')
        newrow(layout, "Line colour:", scene.slicer_settings, 'laser_slicer_cut_colour')
        newrow(layout, "Thickness (pixels):", scene.slicer_settings, 'laser_slicer_cut_line')
        newrow(layout, "Separate files:", scene.slicer_settings, 'laser_slicer_separate_files')

        if scene.slicer_settings.laser_slicer_separate_files:
            newrow(layout, "Cut position:", scene.slicer_settings, 'laser_slicer_svg_position')

        newrow(layout, "Cut spacing (mm):", scene.slicer_settings, 'laser_slicer_cut_thickness')
        newrow(layout, "SVG polygons:", scene.slicer_settings, 'laser_slicer_accuracy')
        newrow(layout, "Export file(s):", scene.slicer_settings, 'laser_slicer_ofile')

        if context.active_object and context.active_object.select_get() and context.active_object.type == 'MESH' and context.active_object.data.polygons:
            row = layout.row()
            row.label(text = 'No. of slices : {:.0f}'.format(context.active_object.dimensions[2] * 1000 * context.scene.unit_settings.scale_length/scene.slicer_settings.laser_slicer_material_thick))
            
            if bpy.data.filepath or context.scene.slicer_settings.laser_slicer_ofile:
                split = layout.split()
                col = split.column()
                col.operator("object.laser_slicer", text="Slice the object")

class Slicer_Settings(bpy.types.PropertyGroup):   
    laser_slicer_material_thick: FloatProperty(
         name="", description="Thickness of the cutting material in mm",
             min=0.1, max=50, default=2)
    laser_slicer_material_width: FloatProperty(
         name="", description="Width of the cutting material in mm",
             min=1, max=5000, default=450)
    laser_slicer_material_height: FloatProperty(
         name="", description="Height of the cutting material in mm",
             min=1, max=5000, default=450)
    laser_slicer_dpi: IntProperty(
         name="", description="DPI of the laser cutter computer",
             min=50, max=500, default=96)
    laser_slicer_separate_files: BoolProperty(name = "", description = "Write out seperate SVG files", default = 0)
    laser_slicer_svg_position: EnumProperty(items = [('0', 'Top left', 'Keep top  left position'), ('1', 'Staggered', 'Staggered position'), ('2', 'Centre', 'Apply centre position')], name = "", description = "Control the position of the SVG slice", default = '0')
    laser_slicer_cut_thickness: FloatProperty(
         name="", description="Expected thickness of the laser cut (mm)",
             min=0, max=5, default=1)
    laser_slicer_ofile: StringProperty(name="", description="Location of the exported file", default="", subtype="FILE_PATH")
    laser_slicer_accuracy: BoolProperty(name = "", description = "Control the speed and accuracy of the slicing", default = False)
    laser_slicer_cut_colour: FloatVectorProperty(size = 3, name = "", attr = "Lini colour", default = [1.0, 0.0, 0.0], subtype ='COLOR', min = 0, max = 1)
    laser_slicer_cut_line: FloatProperty(name="", description="Thickness of the svg line (pixels)", min=0, max=5, default=1)

classes = (OBJECT_OT_Laser_Slicer_Panel, OBJECT_OT_Laser_Slicer, Slicer_Settings)

def register():
    for cl in classes:
        bpy.utils.register_class(cl)

    bpy.types.Scene.slicer_settings = bpy.props.PointerProperty(type=Slicer_Settings)

def unregister():
    bpy.types.Scene.slicer_settings
    
    for cl in classes:
        bpy.utils.unregister_class(cl)

