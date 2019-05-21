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
    'name': '3D View: Toggle Views',
    'author': 'Evgen Zaitsev',
    'version': ( 0, 1 ),
    'blender': ( 2, 6, 3 ),
    'location': 'View3D > Alt Q',
    'description': 'toggle Camera from PERSP view to SIDE view and back (depends of camera vector)',
    'wiki_url': 'http://evgeniyzaitsev.com/2012/05/29/3d-view-toggle-views/',
    'tracker_url': 'None',
    'category': '3D View'}

import bpy
import mathutils
import copy
import math 

global m_toggleViewsCounter
global m_distance
global m_location
global m_rotation
m_toggleViewsCounter = 0

def findMaximum( m_list ):
    '''     find maximum value in a list     '''
    m_max = m_list[0]
    m_max_index = 0
    for m_ind in range( len( m_list ) ):
        if m_list[ m_ind ] > m_max:
            m_max       = m_list[ m_ind ] 
            m_max_index = m_ind
    return m_max_index 

def perspToOrtho():
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            break  
    m_region3D = area.spaces.active.region_3d
    # toggle to 'ORTHO'
    m_region3D.view_perspective = 'ORTHO' 
    # look rotation when it goes into side view 
    m_region3D.lock_rotation = True
    # Save viewport camera settings
    global m_distance
    global m_location
    global m_rotation    
    m_distance    = copy.deepcopy( m_region3D.view_distance  )
    m_location    = copy.deepcopy( m_region3D.view_location  )
    m_rotation    = copy.deepcopy( m_region3D.view_rotation  )
    # find camera vector
    m_matrix = area.spaces.active.region_3d.perspective_matrix     
    m_Xvec = mathutils.Vector( ( 1, 0, 0 ) )
    m_Yvec = mathutils.Vector( ( 0, 1, 0 ) )
    m_Zvec = mathutils.Vector( ( 0, 0, 1 ) )
    m_LookAtVector =  mathutils.Vector( ( m_matrix[2][0], m_matrix[2][1], m_matrix[2][2] ) ) 
    m_VdotX = m_LookAtVector.dot( m_Xvec )
    m_VdotY = m_LookAtVector.dot( m_Yvec ) 
    m_VdotZ = m_LookAtVector.dot( m_Zvec )
    m_index = findMaximum( [ math.fabs( m_VdotX ), math.fabs( m_VdotY ), math.fabs( m_VdotZ ) ] )  
    if   0 == m_index:
        if ( m_VdotX > 0 ):
            m_region3D.view_rotation = mathutils.Quaternion( ( 0.5, 0.5, -0.5, -0.5 ) ) 
            #print ( 'LEFT' )
            #bpy.ops.view3d.viewnumpad( type = 'LEFT' )
        else: 
            m_region3D.view_rotation = mathutils.Quaternion( ( 0.5, 0.5, 0.5, 0.5 ) ) 
            #print ( 'RIGHT' )
            #bpy.ops.view3d.viewnumpad( type = 'RIGHT' )   
    elif 1 == m_index:
        if ( m_VdotY > 0 ):            
            m_region3D.view_rotation = mathutils.Quaternion( ( 1.0, 0.0, 0.0), math.radians( 90.0 ) )
            #print ( 'FRONT' )
            #bpy.ops.view3d.viewnumpad( type = 'FRONT' )
        else:  
            m_region3D.view_rotation = mathutils.Quaternion( ( 0.0, 0.0, 0.7071, 0.7071 ) ) 
            #print ( 'BACK' )
            #bpy.ops.view3d.viewnumpad( type = 'BACK' )  
    elif 2 == m_index:
        if ( m_VdotZ > 0 ):            
            m_view_quat = veiw_rotation( m_view_quaternion = m_region3D.view_rotation, type = 'BOTTOM' )
            m_region3D.view_rotation = m_view_quat
            #print ( 'BOTTOM' )
            #bpy.ops.view3d.viewnumpad( type = 'BOTTOM' )
        else:
            m_view_quat = veiw_rotation( m_view_quaternion = m_region3D.view_rotation, type = 'TOP' )
            m_region3D.view_rotation = m_view_quat
            #print ( 'TOP' )
            #bpy.ops.view3d.viewnumpad( type = 'TOP' )            
    return

def orthoToPersp():
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            break  
    m_region3D = area.spaces.active.region_3d 
    # toggle to 'PERSP'
    m_region3D.view_perspective = 'PERSP'
    m_region3D.lock_rotation = False   
    # Resotre viewport
    m_region3D.view_distance    = m_distance
    m_region3D.view_location    = m_location
    m_region3D.view_rotation    = m_rotation    
    return

def veiw_rotation( m_view_quaternion, type = 'TOP'):
    if  ( 'TOP' == type ):
        m_dot   = m_view_quaternion.w
        m_a     = m_view_quaternion.w
        m_b     = m_view_quaternion.z 
    elif( 'BOTTOM' == type ):
        m_dot   = m_view_quaternion.y
        m_a     = m_view_quaternion.x
        m_b     = m_view_quaternion.y 
    if   ( 0.92387 < math.fabs( m_dot ) ):
        #print( "+Y" )
        if ( 'TOP' == type ):             
            return mathutils.Quaternion( ( 1.0, 0.0, 0.0, 0.0 ) ) 
        elif( 'BOTTOM' == type ):
            return mathutils.Quaternion( ( 0.0, 0.0, -1.0, 0.0 ) ) 
    elif ( 0.38268 >= math.fabs( m_dot ) ):
        #print( "-Y" ) 
        if ( 'TOP' == type ):             
            return mathutils.Quaternion( ( 0.0, 0.0, 0.0, 1.0 ) ) 
        elif( 'BOTTOM' == type ):
            return mathutils.Quaternion( ( 0.0, 1.0, 0.0, 0.0 ) ) 
    elif ( 0.38268 < math.fabs( m_dot ) <= 0.92387 ):
        if ( ( 0 < m_a and  0 < m_b ) or ( 0 > m_a and 0 > m_b ) ):
            if ( 'TOP' == type ):
                #print( "-X" )
                return mathutils.Quaternion( ( 0.7071, 0.0, 0.0, 0.7071 ) ) 
            elif( 'BOTTOM' == type ):
                #print( "+X" )
                return mathutils.Quaternion( ( 0.0, 0.7071, 0.7071, 0.0 ) )  
        else:
            if ( 'TOP' == type ):
                #print( "+X" )
                return mathutils.Quaternion( ( -0.7071, 0.0, 0.0, 0.7071 ) )
            elif( 'BOTTOM' == type ):
                #print( "-X" )
                return mathutils.Quaternion( ( 0.0, 0.7071, -0.7071, 0.0 ) )
    
class toggleViewsOp( bpy.types.Operator ):
    bl_idname  = "view3d.toggle_views_op"
    bl_label   = "Toggle Views"
    bl_options = {'REGISTER'}
    
    def execute( self, context ):
        global m_toggleViewsCounter
        m_toggleViewsCounter += 1
        if ( m_toggleViewsCounter % 2 ):
            perspToOrtho()
        else:
            orthoToPersp()
        return {'FINISHED'}

def register():
    bpy.utils.register_module( __name__ )
    
    wm  = bpy.context.window_manager
    km  = wm.keyconfigs.addon.keymaps.new( name='3D View Generic', space_type='VIEW_3D' )
    #kmi = km.keymap_items.new( idname = 'view3d.toggle_views_op', type = 'ACCENT_GRAVE', value = 'PRESS', alt=True)
    kmi = km.keymap_items.new( idname = 'view3d.toggle_views_op', type = 'Q', value = 'PRESS', alt=True)

def unregister():        
    bpy.utils.unregister_module( __name__ ) 
       
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps[ '3D View Generic' ]
    for kmi in km.keymap_items:
        if kmi.idname == 'view3d.toggle_views_op':
            km.keymap_items.remove( kmi )
            break

if __name__ == "__main__":
    register()