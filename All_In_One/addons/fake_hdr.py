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

#
#  Author            : Tamir Lousky [ tlousky@gmail.com, tamir@pitchipoy.tv ]
#  Homepage(Wiki)    : http://bioblog3d.wordpress.com/
#  Studio (sponsor)  : PitchiPoy Animation Productions (PitchiPoy.tv)
#  Start of project  : 2013-11-08 by Tamir Lousky
#  Last modified     : 2013-13-09
#
#  Acknowledgements 
#  ================
#  PitchiPoy: Nathan Elias    (for suggesting the idea)
#             Dima Kondrashov (for feature suggestions and testing)
#  Zeffii @ StackExchange - for providing really useful insights and sample code 
#                           on how vertex colors can be matched with mesh verts.
#  Matan Harel from XLN.org.il: who helped me with the calculations related to
#                               converting from number of lamps to icosphere
#                               subdivisions.

bl_info = {    
    "name"        : "Fake HDR",
    "author"      : "Tamir Lousky",
    "version"     : (0, 0, 2),
    "blender"     : (2, 68, 0),
    "category"    : "Render",
    "location"    : "3D View >> Tools",
    "wiki_url"    : "https://github.com/Tlousky/production_scripts/wiki/Fake-HDR",
    "tracker_url" : "https://github.com/Tlousky/production_scripts/blob/master/fake_hdr.py",
    "description" : "Create an array of lamps that mimicks an HDR image"
}

import bpy, re, bmesh, math
from collections import defaultdict
from mathutils   import Color

def check_poll_conditions( context ):
    hdr_image_selected  = context.scene.fake_hdr_image
    render_engine_is_bi = context.scene.render.engine == 'BLENDER_RENDER'
    return hdr_image_selected and render_engine_is_bi

def change_light_intensity( obj, intensity ):
    """ Change the light intensity of a lamp. Uses the correct methods to 
    affect both cycles and BI lamps """
    if bpy.context.scene.render.engine == 'CYCLES':
        if not obj.data.use_nodes:
            obj.data.use_nodes = True
        strength = obj.data.node_tree.nodes['Emission'].inputs['Strength']
        strength.default_value = intensity
    else:
        obj.data.energy = intensity

def sort_by_value( colors, sorted_list, calls ):
    """ Recursive sorting algorithm meant to find the smallest to highest
        color values in a list of averaged vertex colors """
        
    # Find the indices that have not been sorted yet
    unsorted_indices = set( colors.keys() ).difference( set( sorted_list ) )
    
    min        = 4.0
    smallest_i = 0
    # Find current darkest vertex
    for i in unsorted_indices:
        val = sum( [ c for c in colors[i][:] ] )
        if val < min:
            smallest_i = i
            min        = val

    # Add it to the list of sorted verts
    sorted_list.append( smallest_i )

    # If we sorted all the verts, we can return them and exit the function. 
    # Otherwiese, call it again with the new (incomplete) sorted vert list.
    if len( sorted_list ) == len( colors ):
        return sorted_list
    else:
        return sort_by_value( colors, sorted_list, calls + 1 )
        
class fake_hdr(bpy.types.Panel):
    bl_idname      = "FakeHDR"
    bl_label       = "Fake HDR"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'objectmode'

    @classmethod
    def poll( self, context ):
        return True
        # return context.scene.render.engine == 'BLENDER_RENDER'

    def draw( self, context) :
        # hdr_image = context.scene.fake_hdr_image
        props     = context.scene.fake_hdr_props

        layout = self.layout
        col    = layout.column()

        col.prop_search(          
            context.scene, "fake_hdr_image",  # Pick HDR image 
            bpy.data, "images"                # From list of images in scene
        )

        col.prop( props, 'num_of_lamps' )
        col.prop( props, 'shadow_casting_lamps' )

        layout.operator( 'render.create_hdr_sphere', icon = 'MAT_SPHERE_SKY' )

        if 'FakeHDR.LightArray.Control' in context.scene.objects:
            lbl = layout.label( "Update lamp properties" )
            box = layout.box()
            col = box.column()

            col.prop( context.scene.fake_hdr_props, 'lamp_type' )

            row = col.row()
            row.prop( 
                context.scene.fake_hdr_props, 
                'lamp_intensity', 
                text = 'Intensity' 
            )
            row.prop( 
                context.scene.fake_hdr_props, 'lamp_distance', text = 'Distance'  
            )
            row.prop( context.scene.fake_hdr_props, 'lamp_use_specular' )
            
            if props.lamp_shadow_type == 'RAY_SHADOW':
                col.prop( context.scene.fake_hdr_props, 'lamp_ray_samples' )

            col.prop( context.scene.fake_hdr_props, 'lamp_size' )

            col.separator()
            if props.lamp_type == 'SPOT':
                col.prop( 
                    context.scene.fake_hdr_props, 'spot_shadow_type'
                )
                
                row = col.row()
                row.prop( 
                    context.scene.fake_hdr_props, 'spot_size', text = 'Size' 
                )

                row.prop( 
                    context.scene.fake_hdr_props, 
                    'spot_blend', 
                    text = 'Blend',
                    slider = True 
                )

                if props.spot_shadow_type == 'BUFFER_SHADOW':
                    col.separator()
                    col.prop( context.scene.fake_hdr_props, 'buffer_type' )
                    col.prop( context.scene.fake_hdr_props, 'filter_type' )

                    row = col.row()
                    row.prop( context.scene.fake_hdr_props, 'sample_buffers'  )
                    row.prop( context.scene.fake_hdr_props, 'buffer_softness' )
                    row.prop( context.scene.fake_hdr_props, 'buffer_size'     )

                    row = col.row()
                    row.prop( context.scene.fake_hdr_props, 'buffer_bias'    )
                    row.prop( context.scene.fake_hdr_props, 'buffer_samples' )
                
            else:
                col.prop( 
                    context.scene.fake_hdr_props, 
                    'lamp_shadow_type',
                    expand = True
                )
            
            layout.separator()
            lbl = layout.label( "Make sun lamp of strongest light" )
            box = layout.box()
            col = box.column()
            
            col.prop( context.scene.fake_hdr_props, 'use_sun' )
            if context.scene.fake_hdr_props.use_sun:
                col.prop( context.scene.fake_hdr_props, 'sun_intensity' )
        
class create_hdr_sphere( bpy.types.Operator ):
    """ Create a file output node for each pass in each renderlayer """
    bl_idname      = "render.create_hdr_sphere"
    bl_label       = "Create light array"
    bl_description = "Create a light array corresponding to an HDR sphere"
    bl_options     = {'REGISTER', 'UNDO' }

    @classmethod
    def poll( self, context ):
        return check_poll_conditions( context )

    def create_sphere( self, context, n ):
        bm = bmesh.new()
        
        # Calculate sphere subdivisions
        # The relationship between vert count and subdivisions is as follows:
        # subdivisions = log( ( vert_count - 2 ) / 2.5, base4 )
        # The subdivisions are rounded up to the num of verts > num of lights
        subd = math.ceil( math.log( (n - 2) / 2.5, 4 ) )

        # Create new icosphere mesh
        sphere_verts = bmesh.ops.create_icosphere( 
            bm, 
            subdivisions = subd,
            diameter     = 1
         )

        # Create new mesh from bmesh
        me = bpy.data.meshes.new("LightSphere")
        bm.to_mesh(me)
        bm.free()

        # Link new object to scene
        obj = bpy.data.objects.new("LightSphere", me)
        context.scene.objects.link( obj )
        
        return obj

    def map_hdr_to_sphere( self, context, obj ):
        # Select and make active
        context.scene.objects.active = obj
        obj.select = True

        # Go to edit mode
        bpy.ops.object.mode_set(mode ='EDIT')

        # Create spherical UV map
        bpy.ops.mesh.select_all( action = 'SELECT' )
        bpy.ops.uv.sphere_project()

        # Return to object mode
        bpy.ops.object.mode_set(mode ='OBJECT')

        # Add material slot to object
        bpy.ops.object.material_slot_add()

        # Create a new material and set it up
        bpy.ops.material.new()
        mat               = bpy.data.materials[-1]
        mat.name          = 'FakeHDR.Material'
        mat.use_shadeless = True

        # Set material as active on object
        context.object.material_slots[0].material = mat
        
        # Create a new texture and set it up
        tex = bpy.data.textures.new( name = 'FakeHDR.Texture', type = 'IMAGE' )
        tex.image = bpy.data.images[ context.scene.fake_hdr_image ]

        # Add material texture slot and set it up
        mat.texture_slots.add()
        mat.texture_slots[0].texture_coords = 'UV'      # Map texture to UVs
        mat.texture_slots[0].texture        = tex

    def bake_textures_to_verts( self, context, obj ):
        # Select and make active
        context.scene.objects.active = obj
        obj.select = True

        # Set up bake textures to vert colors
        context.scene.render.use_bake_to_vertex_color = True
        context.scene.render.bake_type                = 'TEXTURE'

        # Add vertex color map
        bpy.ops.mesh.vertex_color_add()

        # Bake
        bpy.ops.object.bake_image()
        
        # Make sphere unrendereable
        obj.hide_render = True

    def get_vcolors( self, context, obj, n ):
        vcolor_dict = defaultdict(list)
        mesh        = obj.data
        color_layer = obj.data.vertex_colors[0]

        i = 0
        for poly in mesh.polygons:
            for idx in poly.loop_indices:
                loop  = mesh.loops[idx]
                color = color_layer.data[i].color
                vcolor_dict[loop.vertex_index].append(color)
                i += 1

        avg_vcolors = {}
        for v in vcolor_dict:
            avg_vcolors[ v ] = Color( (
                sum( [ c.r for c in vcolor_dict[v] ] ) / len( vcolor_dict[v] ),
                sum( [ c.g for c in vcolor_dict[v] ] ) / len( vcolor_dict[v] ),
                sum( [ c.b for c in vcolor_dict[v] ] ) / len( vcolor_dict[v] )
            ) )

        # Sort verts by value
        verts_sorted_by_value = sort_by_value( avg_vcolors, [], 1 )

        start = len( avg_vcolors ) - n
        culled_vert_list = verts_sorted_by_value[ start: ]
        
        vcolors = { v : avg_vcolors[v] for v in culled_vert_list }
        
        return vcolors
        
    def create_lamps( self, context, obj ):
        # Create empty which will act as the lamps' parent object
        bpy.ops.object.empty_add( type = 'SPHERE' )

        empty      = context.scene.objects[ context.object.name ]
        empty.name = 'FakeHDR.LightArray.Control' 

        # Set empty as the sphere's parent
        obj.parent = empty

        n       = context.scene.fake_hdr_props.num_of_lamps
        lamps   = []
        verts   = obj.data.vertices
        vcolors = self.get_vcolors( context, obj, n )
        
        for i,v in enumerate( vcolors.keys() ):
            bpy.ops.object.lamp_add( type = 'POINT' )

            # Reference lamp (which is now the selected and active object
            lamp      = context.scene.objects[ context.object.name ]
            lamp.name = 'fake_hdr_lamp'
            lamps.append( lamp.name )

            # Parent lamp to empty, and:
            # Create damped track constraint from lamp to empty to make sure
            # spots and sun always look in the direction of the empty
            lamp.parent      = empty 
            const            = lamp.constraints.new( type = 'DAMPED_TRACK' )
            const.target     = empty
            const.track_axis = 'TRACK_NEGATIVE_Z'

            # Set lamp location
            lamp.location = verts[v].co
            
            # Set lamp color
            lamp.data.color = vcolors[v]
            
            # Set all default parameters
            props = context.scene.fake_hdr_props
            lamp.data.distance           = props.lamp_distance
            lamp.data.shadow_ray_samples = props.lamp_ray_samples
            lamp.data.shadow_soft_size   = props.lamp_size
            lamp.data.use_specular       = props.lamp_use_specular
            
            # make the strongest lamp a sun if option is turned on
            if context.scene.fake_hdr_props.use_sun and i == len( vcolors ) - 1:
                lamp.data.type = 'SUN'
                value = context.scene.fake_hdr_props.sun_intensity
                change_light_intensity( lamp, value )

        return lamps

    def execute( self, context ):
        n   = context.scene.fake_hdr_props.num_of_lamps
        obj = self.create_sphere( context, n )
        self.map_hdr_to_sphere( context, obj )
        self.bake_textures_to_verts( context, obj )
        lamps = self.create_lamps( context, obj )
        
        return {'FINISHED'}

class fake_HDR_props( bpy.types.PropertyGroup ):
    def find_lamps( self, context ):
        empty = context.scene.objects['FakeHDR.LightArray.Control']
        objs  = context.scene.objects

        # Reference lamps by name to create a persisten reference list
        all_lamps = [ 
            objs[c.name] for c in empty.children if c.type == 'LAMP'
        ]

        lamp_indices_and_colors = { 
            i : all_lamps[i].data.color for i in range( len( all_lamps ) )
        }

        # Sort and return list of lamps sorted by color value (brightness)
        sorted_indices = sort_by_value( lamp_indices_and_colors, [], 1 )

        return [ all_lamps[i] for i in sorted_indices ]

    def update_intensity( self, context ):
        value  = context.scene.fake_hdr_props.lamp_intensity
        svalue = context.scene.fake_hdr_props.sun_intensity
        for l in self.find_lamps(context):
            if l.data.type != 'SUN':
                change_light_intensity( l, value )
            else:
                change_light_intensity( l, svalue )

    def update_size( self, context ):
        for l in self.find_lamps(context):
            l.data.shadow_soft_size = context.scene.fake_hdr_props.lamp_size

    def update_type( self, context ):
        for l in self.find_lamps(context):
            if l.data.type != 'SUN':
                l.data.type = context.scene.fake_hdr_props.lamp_type

    def update_distance( self, context ):
        for l in self.find_lamps(context):
            l.data.distance = context.scene.fake_hdr_props.lamp_distance

    def update_use_specular( self, context ):
        for l in self.find_lamps(context):
            l.data.use_specular = context.scene.fake_hdr_props.lamp_use_specular

    def update_shadow_type( self, context ):
        n     = context.scene.fake_hdr_props.shadow_casting_lamps
        t     = context.scene.fake_hdr_props.lamp_type
        stype = context.scene.fake_hdr_props.lamp_shadow_type

        if t == 'SPOT':
            stype = context.scene.fake_hdr_props.spot_shadow_type

        lamps = self.find_lamps( context )

        # Make sure only the number of lamps indicated by user will cast shadows
        for i,l in enumerate( lamps ):
            if i >= len( lamps ) - n:
                l.data.shadow_method = stype
            else:
                l.data.shadow_method = 'NOSHADOW'

    def update_ray_samples( self, context ):
        value = context.scene.fake_hdr_props.lamp_ray_samples
        for l in self.find_lamps(context):
            l.data.shadow_ray_samples = value

    def update_use_sun( self, context ):
        lamps      = self.find_lamps(context)
        sun_exists = 'SUN' in [ l.data.type for l in lamps ]
        use_sun    = context.scene.fake_hdr_props.use_sun

        if not use_sun:
            if sun_exists:
                default_type = context.scene.fake_hdr_props.lamp_type
                default_int  = context.scene.fake_hdr_props.lamp_intensity

                for l in lamps:
                    if l.data.type == 'SUN':
                        l.data.type = default_type
                        change_light_intensity( l, default_int )

        else:
            intensities = {          # Summarize rgb to get intensity
                l : sum( [ c for c in l.data.color ] ) for l in lamps
            }
        
            max_lightint = max( intensities.values() ) # Find highest intensity

            for l,i in intensities.items():
                if i == max_lightint:
                    l.data.type = 'SUN'

                    value = context.scene.fake_hdr_props.sun_intensity
                    change_light_intensity( l, value )

                    break # Make sure than no more than one sun exists

    def update_spot_size( self, context ):
        value = context.scene.fake_hdr_props.spot_size
        for l in self.find_lamps(context):
            l.data.shadow_spot_size = value
        
    def update_spot_blend( self, context ):
        value = context.scene.fake_hdr_props.spot_blend
        for l in self.find_lamps(context):
            l.data.shadow_spot_blend = value

        
    def update_buffer_type( self, context ):
        value = context.scene.fake_hdr_props.buffer_type
        for l in self.find_lamps(context):
            l.data.shadow_buffer_type = value
        
    def update_buffer_filter_type( self, context ):
        value = context.scene.fake_hdr_props.filter_type
        for l in self.find_lamps(context):
            l.data.shadow_filter_type = value
        
    def update_sample_buffers( self, context ):
        value = context.scene.fake_hdr_props.sample_buffers
        for l in self.find_lamps(context):
            l.data.shadow_sample_buffers = value

    def update_buffer_softness( self, context ):
        value = context.scene.fake_hdr_props.buffer_softness
        for l in self.find_lamps(context):
            l.data.shadow_buffer_soft = value
        
    def update_buffer_size( self, context ):
        value = context.scene.fake_hdr_props.buffer_size
        for l in self.find_lamps(context):
            l.data.shadow_buffer_size = value
        
    def update_buffer_bias( self, context ):
        value = context.scene.fake_hdr_props.buffer_bias
        for l in self.find_lamps(context):
            l.data.shadow_buffer_bias = value

    def update_buffer_samples( self, context ):
        value = context.scene.fake_hdr_props.buffer_samples
        for l in self.find_lamps(context):
            l.data.shadow_buffer_samples = value

    num_of_lamps = bpy.props.IntProperty(
        description = "Number of Lamps in scene",
        name        = "Number of Lamps",
        default     = 50,
        min         = 12,
        max         = 2500
    )

    shadow_casting_lamps = bpy.props.IntProperty(
        description = "Number of Shadow Casting Lamps in Scene",
        name        = "Shadow Casting Lamps",
        default     = 1,
        min         = 0,
        max         = 2500
    )
    
    types = [('POINT', 'point', ''), ('SPOT', 'spot', '')]
    lamp_type = bpy.props.EnumProperty(
        name    = "Lamp Type",
        items   = types, 
        default = 'SPOT',
        update  = update_type
    )

    lamp_intensity = bpy.props.FloatProperty(
        name        = "Lamp light intensity",
        description = "Size (and softness of shadows) of the array's lamps",
        default     = 1.0,
        update      = update_intensity
    )

    lamp_size = bpy.props.FloatProperty(
        name        = "Lamp shadow size",
        description = "Size (and softness of shadows) of the array's lamps",
        default     = 1.0,
        update      = update_size
    )

    lamp_distance = bpy.props.FloatProperty(
        name        = "Lamp distance",
        description = "Distance (affects intensity due to falloff)",
        default     = 25.0,
        update      = update_distance
    )

    lamp_use_specular = bpy.props.BoolProperty(
        name        = "Use specular",
        description = "If true - lamps create specular highlights",
        default     = True,
        update      = update_use_specular
    )

    shadow_types = [
        ('NOSHADOW',      'No Shadow',     ''), 
        ('RAY_SHADOW',    'Ray Shadow',    ''),
        ('BUFFER_SHADOW', 'Buffer Shadow', '')
    ]

    lamp_shadow_type = bpy.props.EnumProperty(
        name    = "Shadow type",
        items   = shadow_types[:-1], 
        default = 'NOSHADOW',
        update  = update_shadow_type
    )

    lamp_ray_samples = bpy.props.IntProperty(
        name        = "Ray shadow samples",
        description = "Number of ray shadow samples (i.e. quality)",
        default     = 5,
        update      = update_ray_samples
    )

    use_sun = bpy.props.BoolProperty(
        name        = "Create sun",
        description = "Make strongest light a sun lamp",
        default     = True,
        update      = update_use_sun
    )

    sun_intensity = bpy.props.FloatProperty(
        name        = "Sun intensity",
        description = "The intensity of the sun lamp",
        default     = 5.0,
        update      = update_intensity
    )
    
    # Spot lamp properties
    spot_shadow_type = bpy.props.EnumProperty(
        name    = "Shadow type",
        items   = shadow_types,
        default = 'NOSHADOW',
        update  = update_shadow_type
    )
    
    spot_size = bpy.props.FloatProperty(
        name        = "Spot Size (cone angle)",
        description = "The cone angle of the spot lamp",
        default     = math.radians(45.0),
        min         = math.radians(1.0),
        max         = math.radians(180.0),
        update      = update_spot_size
    )
    
    spot_blend = bpy.props.FloatProperty(
        name        = "Spot Size (cone angle)",
        description = "The cone angle of the spot lamp",
        default     = 0.15,
        min         = 0.0,
        max         = 1.0,
        update      = update_spot_blend
    )
    
    # Spot buffer shadow properties
    buffer_types = [
        ('REGULAR',   'Classical',         ''), 
        ('HALFWAY',   'Classical-Halfway', ''),
        ('IRREGULAR', 'Irregular',         ''),
        ('DEEP',      'Deep',              '')
    ]

    buffer_filter_types = [
        ('BOX', 'Box', ''), ('TENT', 'Tent', ''), ('GAUSS', 'Gauss', '')
    ]

    buffer_samples = [ ( '1', '1', '' ), ( '4', '4', '' ), ( '9', '9', '' ) ]
    
    buffer_type = bpy.props.EnumProperty(
        name    = "Buffer type",
        items   = buffer_types,
        default = 'HALFWAY',
        update  = update_buffer_type
    )
    
    filter_type = bpy.props.EnumProperty(
        name    = "Filter type",
        items   = buffer_filter_types,
        default = 'BOX',
        update  = update_buffer_filter_type
    )
    
    sample_buffers = bpy.props.EnumProperty(
        name        = "Sample Buffers",
        description = "Number of Anti Aliasing Samples",
        items       = buffer_samples,
        default     = '1',
        update      = update_buffer_samples
    )

    buffer_softness = bpy.props.FloatProperty(
        name        = "Buffer Shadow Softness",
        description = "Buffer shadow's softness",
        default     = 3.0,
        min         = 0.0,
        max         = 100.0,
        update      = update_buffer_softness
    )

    buffer_size = bpy.props.IntProperty(
        name        = "Buffer shadow size",
        description = "Buffer shadow's resolution",
        default     = 512,
        min         = 0,
        update      = update_buffer_size
    )
    
    buffer_bias = bpy.props.FloatProperty(
        name        = "Buffer Shadow Bias",
        description = "Buffer shadow's bias",
        default     = 3.0,
        min         = 0.0,
        max         = 100.0,
        update      = update_buffer_bias
    )

    buffer_samples = bpy.props.IntProperty(
        name        = "Samples",
        description = "Buffer shadow samples",
        default     = 3,
        min         = 1,
        max         = 16,
        update      = update_buffer_samples
    )

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.fake_hdr_props = bpy.props.PointerProperty( 
        type = fake_HDR_props
    )
    bpy.types.Scene.fake_hdr_image = bpy.props.StringProperty()
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.Scene.fake_hdr_image = None
