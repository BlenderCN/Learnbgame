from freestyle.shaders import *
from freestyle.predicates import *
from freestyle.types import Operators, StrokeShader, StrokeVertex
from freestyle.chainingiterators import ChainSilhouetteIterator, ChainPredicateIterator
from freestyle.functions import *

import bpy
import bmesh
from bpy_extras import view3d_utils
import bpy_extras
from math import sqrt
import random
from mathutils import Vector, Matrix

from latk import *

bl_info = {
    "name": "Freestyle to Grease Pencil",
    "author": "Folkert de Vries and Nick Fox-Gieg",
    "version": (1, 0),
    "blender": (2, 74, 1),
    "location": "Properties > Render > Freestyle to Grease Pencil",
    "description": "Exports Freestyle's stylized to a Grease Pencil sketch",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
    }

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        )
import parameter_editor


# a tuple containing all strokes from the current render. should get replaced by freestyle.context at some point
def get_strokes():
    return tuple(map(Operators().get_stroke_from_index, range(Operators().get_strokes_size())))

# get the exact scene dimensions
def render_height(scene):
    return int(scene.render.resolution_y * scene.render.resolution_percentage / 100)

def render_width(scene):
    return int(scene.render.resolution_x * scene.render.resolution_percentage / 100)

def render_dimensions(scene):
    return render_width(scene), render_height(scene)

class FreestyleGPencil(bpy.types.PropertyGroup):
    """Implements the properties for the Freestyle to Grease Pencil exporter"""
    bl_idname = "RENDER_PT_gpencil_export"

    use_freestyle_gpencil_export = BoolProperty(
        name="Grease Pencil Export",
        description="Export Freestyle edges to Grease Pencil",
    )
    '''
    draw_mode = EnumProperty(
        name="Draw Mode",
        items=(
            # ('2DSPACE', "2D Space", "Export a single frame", 0),
            ('3DSPACE', "3D Space", "Export an animation", 1),
            # ('2DIMAGE', "2D Image", "", 2),
            ('SCREEN', "Screen", "", 3),
            ),
        default='3DSPACE',
    )
    '''
    use_fill = BoolProperty(
        name="Fill",
        description="Fill the contour with the object's material color",
        default=False,
    )
    use_connecting = BoolProperty(
        name="Connecting Strokes",
        description="Connect all vertices with strokes",
        default=False,
    )
    visible_only = BoolProperty(
        name="Visible Only",
        description="Only render visible lines",
        default=True,
    )
    use_overwrite = BoolProperty(
        name="Overwrite",
        description="Remove the GPencil strokes from previous renders before a new render",
        default=True,
    )
    vertexHitbox = FloatProperty(
        name="Vertex Hitbox",
        description="How close a GP stroke needs to be to a vertex",
        default=1.5,
    )
    numColPlaces = IntProperty(
        name="Color Places",
        description="How many decimal places used to find matching colors",
        default=5,
    )
    numMaxColors = IntProperty(
        name="Max Colors",
        description="How many colors are in the Grease Pencil palette",
        default=16,
    )
    doClearPalette = BoolProperty(
        name="Clear Palette",
        description="Delete palette before beginning a new render",
        default=False,
    )

class SVGExporterPanel(bpy.types.Panel):
    """Creates a Panel in the render context of the properties editor"""
    bl_idname = "RENDER_PT_FreestyleGPencilPanel"
    bl_space_type = 'PROPERTIES'
    bl_label = "Freestyle to Grease Pencil"
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw_header(self, context):
        self.layout.prop(context.scene.freestyle_gpencil_export, "use_freestyle_gpencil_export", text="")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        gp = scene.freestyle_gpencil_export
        freestyle = scene.render.layers.active.freestyle_settings

        layout.active = (gp.use_freestyle_gpencil_export and freestyle.mode != 'SCRIPT')

        #row = layout.row()
        #row.prop(gp, "draw_mode", expand=True)

        row = layout.row()
        row.prop(gp, "numColPlaces")
        row.prop(gp, "numMaxColors")

        row = layout.row()
        #row.prop(svg, "split_at_invisible")
        row.prop(gp, "use_fill")
        row.prop(gp, "use_overwrite")
        row.prop(gp, "doClearPalette")

        row = layout.row()
        row.prop(gp, "visible_only")
        row.prop(gp, "use_connecting")
        row.prop(gp, "vertexHitbox")

def render_visible_strokes():
    """Renders the scene, selects visible strokes and returns them as a tuple"""
    if (bpy.context.scene.freestyle_gpencil_export.visible_only == True):
        upred = QuantitativeInvisibilityUP1D(0) # visible lines only
    else:
        upred = TrueUP1D() # all lines
    Operators.select(upred)
    Operators.bidirectional_chain(ChainSilhouetteIterator(), NotUP1D(upred))
    Operators.create(TrueUP1D(), [])
    return get_strokes()

def render_external_contour():
    """Renders the scene, selects visible strokes of the Contour nature and returns them as a tuple"""
    upred = AndUP1D(QuantitativeInvisibilityUP1D(0), ContourUP1D())
    Operators.select(upred)
    # chain when the same shape and visible
    bpred = SameShapeIdBP1D()
    Operators.bidirectional_chain(ChainPredicateIterator(upred, bpred), NotUP1D(upred))
    Operators.create(TrueUP1D(), [])
    return get_strokes()


def create_gpencil_layer(scene, name, color, alpha, fill_color, fill_alpha):
    """Creates a new GPencil layer (if needed) to store the Freestyle result"""
    gp = bpy.data.grease_pencil.get("FreestyleGPencil", False) or bpy.data.grease_pencil.new(name="FreestyleGPencil")
    scene.grease_pencil = gp
    layer = gp.layers.get(name, False)
    if not layer:
        print("making new GPencil layer")
        layer = gp.layers.new(name=name, set_active=True)
        # set defaults
        '''
        layer.fill_color = fill_color
        layer.fill_alpha = fill_alpha
        layer.alpha = alpha 
        layer.color = color
        '''
    elif scene.freestyle_gpencil_export.use_overwrite:
        # empty the current strokes from the gp layer
        layer.clear()

    # can this be done more neatly? layer.frames.get(..., ...) doesn't seem to work
    frame = frame_from_frame_number(layer, scene.frame_current) or layer.frames.new(scene.frame_current)
    return layer, frame 

def frame_from_frame_number(layer, current_frame):
    """Get a reference to the current frame if it exists, else False"""
    return next((frame for frame in layer.frames if frame.frame_number == current_frame), False)

def freestyle_to_gpencil_strokes(strokes, frame, pressure=1, draw_mode="3DSPACE"):
    scene = bpy.context.scene
    if (scene.freestyle_gpencil_export.doClearPalette == True):
        clearPalette()
    """Actually creates the GPencil structure from a collection of strokes"""
    mat = scene.camera.matrix_local.copy()
    #~ 
    obj = scene.objects.active #bpy.context.edit_object
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me) #from_edit_mesh(me)
    #~
    # this speeds things up considerably
    images = getUvImages()
    #~
    uv_layer = bm.loops.layers.uv.active
    #~
    #~ 
    strokeCounter = 0;
    
    firstRun = True
    allPoints = []
    strokesToRemove = []
    allPointsCounter = 1
    lastActiveColor = None

    for fstroke in strokes:
        # *** fstroke contains coordinates of original vertices ***
        #~
        sampleVertRaw = (0,0,0)
        sampleVert = (0,0,0)
        #~
        fstrokeCounter = 0
        for svert in fstroke:
            fstrokeCounter += 1
        for i, svert in enumerate(fstroke):
            if (i == int(fstrokeCounter/2)):
            #if (i == fstrokeCounter-1):
                sampleVertRaw = mat * svert.point_3d
                break
        '''
        for svert in fstroke:
            sampleVertRaw = mat * svert.point_3d
            break
        '''
        sampleVert = (sampleVertRaw[0], sampleVertRaw[1], sampleVertRaw[2])
        #~
        pixel = (1,0,1)
        lastPixel = getActiveColor().color
        # TODO better hit detection method needed
        # possibly sort original verts by distance?
        # http://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list
        # X.sort(key=dict(zip(X, Y)).get)
        distances = []
        sortedVerts = bm.verts
        for v in bm.verts:
            distances.append(getDistance(obj.matrix_world * v.co, sampleVert))
        sortedVerts.sort(key=dict(zip(sortedVerts, distances)).get)
        #~ ~ ~ ~ ~ ~ ~ ~ ~ 
        if (scene.freestyle_gpencil_export.use_connecting == True):
            if (firstRun == True):
                for svert in sortedVerts:
                    allPoints.append(svert)
                firstRun = False

            if (lastActiveColor != None):
                points = []
                for i in range(allPointsCounter, len(allPoints)):
                    if (getDistance(allPoints[i].co, allPoints[i-1].co) < scene.freestyle_gpencil_export.vertexHitbox):
                        points.append(allPoints[i-1])
                    else:
                        allPointsCounter = i
                        break
                if (scene.freestyle_gpencil_export.use_fill):
                    lastActiveColor.fill_color = lastActiveColor.color
                    lastActiveColor.fill_alpha = 0.9
                gpstroke = frame.strokes.new(lastActiveColor.name)
                gpstroke.draw_mode = "3DSPACE"
                gpstroke.points.add(count=len(points))  
                for i in range(0, len(points)):
                    gpstroke.points[i].co = obj.matrix_world * points[i].co
                    gpstroke.points[i].select = True
                    gpstroke.points[i].strength = 1
                    gpstroke.points[i].pressure = pressure
        #~ ~ ~ ~ ~ ~ ~ ~ ~
        targetVert = None
        for v in sortedVerts:
            targetVert = v
            break
        #~
            #if (compareTuple(obj.matrix_world * v.co, obj.matrix_world * v.co, numPlaces=1) == True):
            #if (hitDetect3D(obj.matrix_world * v.co, sampleVert, hitbox=bpy.context.scene.freestyle_gpencil_export.vertexHitbox) == True):
            #if (getDistance(obj.matrix_world * v.co, sampleVert) <= 0.5):
        try:
            uv_first = uv_from_vert_first(uv_layer, targetVert)
            #uv_average = uv_from_vert_average(uv_layer, v)
            #print("Vertex: %r, uv_first=%r, uv_average=%r" % (v, uv_first, uv_average))
            #~
            pixelRaw = getPixelFromUvArray(images[obj.active_material.texture_slots[0].texture.image.name], uv_first[0], uv_first[1])
            #pixelRaw = getPixelFromUv(obj.active_material.texture_slots[0].texture.image, uv_first[0], uv_first[1])
            #pixelRaw = getPixelFromUv(obj.active_material.texture_slots[0].texture.image, uv_average[0], uv_average[1])
            pixel = (pixelRaw[0], pixelRaw[1], pixelRaw[2])
            #break
            #print("Pixel: " + str(pixel))    
        except:
            pixel = lastPixel   
        #~ 
        palette = getActivePalette()
        if (len(palette.colors) < scene.freestyle_gpencil_export.numMaxColors):
            createColorWithPalette(pixel, scene.freestyle_gpencil_export.numColPlaces, scene.freestyle_gpencil_export.numMaxColors)
        else:
            matchColorToPalette(pixel)
        lastActiveColor = getActiveColor()
        if (scene.freestyle_gpencil_export.use_fill):
            lastActiveColor.fill_color = lastActiveColor.color
            lastActiveColor.fill_alpha = 0.9
        gpstroke = frame.strokes.new(lastActiveColor.name)
        # enum in ('SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE')
        gpstroke.draw_mode = "3DSPACE"
        gpstroke.points.add(count=len(fstroke))

        #if draw_mode == '3DSPACE':
        for svert, point in zip(fstroke, gpstroke.points):
            # svert.attribute.color = (1, 0, 0) # confirms that this callback runs earlier than the shading
            point.co = mat * svert.point_3d
            point.select = True
            point.strength = 1
            point.pressure = pressure
        '''
        elif draw_mode == 'SCREEN':
            width, height = render_dimensions(bpy.context.scene)
            for svert, point in zip(fstroke, gpstroke.points):
                x, y = svert.point
                point.co = Vector((abs(x / width), abs(y / height), 0.0)) * 100
                point.select = True
                point.strength = 1
                point.pressure = 1
        else:
            raise NotImplementedError()
        '''
        
def freestyle_to_fill(scene):
    default = dict(color=(0, 0, 0), alpha=1, fill_color=(0, 1, 0), fill_alpha=1)
    layer, frame = create_gpencil_layer(scene, "freestyle fill", **default)
    # render the external contour 
    strokes = render_external_contour()
    freestyle_to_gpencil_strokes(strokes, frame, draw_mode="3DSPACE")#scene.freestyle_gpencil_export.draw_mode)

def freestyle_to_strokes(scene):
    default = dict(color=(0, 0, 0), alpha=1, fill_color=(0, 1, 0), fill_alpha=0)
    layer, frame = create_gpencil_layer(scene, "freestyle stroke", **default)
    # render the normal strokes 
    #strokes = render_visible_strokes()
    strokes = get_strokes()
    freestyle_to_gpencil_strokes(strokes, frame, draw_mode="3DSPACE")#scene.freestyle_gpencil_export.draw_mode)


classes = (
    FreestyleGPencil,
    SVGExporterPanel,
    )

def export_stroke(scene, _, x):
    # create stroke layer
    freestyle_to_strokes(scene)

def export_fill(scene, layer, lineset):
    # Doesn't work for 3D due to concave edges
    return

    #if not scene.freestyle_gpencil_export.use_freestyle_gpencil_export:
    #    return 

    #if scene.freestyle_gpencil_export.use_fill:
    #    # create the fill layer
    #    freestyle_to_fill(scene)
    #    # delete these strokes
    #    Operators.reset(delete_strokes=True)



def register():

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.freestyle_gpencil_export = PointerProperty(type=FreestyleGPencil)

    parameter_editor.callbacks_lineset_pre.append(export_fill)
    parameter_editor.callbacks_lineset_post.append(export_stroke)
    # bpy.app.handlers.render_post.append(export_stroke)
    print("anew")

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.freestyle_gpencil_export

    parameter_editor.callbacks_lineset_pre.remove(export_fill)
    parameter_editor.callbacks_lineset_post.remove(export_stroke)


if __name__ == '__main__':
    register()

