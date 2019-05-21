bl_info = {
    "name": "Blender 3D Particles",
    "author": "Edgar Figueiras",
    "version": (4, 0),
    "blender": (2, 78, 0),
    "location": "Tools Panel -> Last tab",
    "description": "Blender Add-on",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
    }


import bpy
import time
import math
import random
import struct
import binascii
import os.path
import numpy as np
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )


class RenderProperties(Operator):
    ''' An example operator for addon '''
    bl_idname = "render.render_properties"
    bl_label  = "Render Properties"
    bl_options = {'REGISTER'}
    prop = bpy.props.BoolProperty(options={'HIDDEN'})

    folder_path = StringProperty(
        name="Data Folder",
        description="Folder with the simulation data.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    folder_path_export = StringProperty(
        name="Data Folder export initial conditions",
        description="Folder where initial conditions will be exported.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    path = StringProperty(
        name="Data File",
        description="File with the simulation data.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    image_path = StringProperty(
        name="Store Path",
        description="Path where renders will be stored, by default uses the path of the simulation data",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')
        
    objects_path = StringProperty(
        name="Store Path",
        description="Path where files will be stored, by default uses the path of the simulation data",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    total_states_info = IntProperty(
        name="Min :0  Max ", 
        description="Total number of states of the simulation",
        min = 0, max = 1000000,
        default = 0)

    int_box_particulas_Simulacion = IntProperty(
        name="Simulation particles", 
        description="Total number of particles for generating the matrix",
        min = 1000, max = 10000000,
        default = 100000)

    int_box_n_particulas = IntProperty(
        name="Particles to show ", 
        description="Total number of particles of the simulation",
        min = 1000, max = 10000000,
        default = 10000)

    int_box_granularity = IntProperty(
        name="Granularity ", 
        description="Modifies the granularity. Min = 1 , Max = 10",
        min = 1, max = 10,
        default = 5)

    int_box_saturation = IntProperty(
        name="Saturation ", 
        description="Modify the saturation. Min = 1, Max = 10",
        min = 1, max = 10,
        default = 5)

    int_box_state = IntProperty(
        name="State ", 
        description="Modify the State",
        min = 0, max = 9999,
        default = 0)

    int_box_offset = IntProperty(
        name="Offset ", 
        description="Modify the offset to show the projection",
        min = -1000, max = 1000,
        default = 50)

    bool_cut_box = BoolProperty(
        name="Cut box side",
        description="Enables the oposite cut plane view",
        default = True)  

    int_x_size = IntProperty(
        name="X Max Size", 
        description="X-window size",
        min = 0, max = 1000,
        default = 100)  

    int_y_size = IntProperty(
        name="Y Max Size", 
        description="Y-window size",
        min = 0, max = 1000,
        default = 100)   

    int_absorb_coeff = IntProperty(
        name="Absorb Coefficient", 
        description="Absorb Coefficient",
        min = 0, max = 100,
        default = 10) 

    x_ob_pos = IntProperty(
        name="X initial object position", 
        description="X initial object position",
        min = -1000, max = 1000,
        default = 0) 
    
    y_ob_pos = IntProperty(
        name="Y initial object position", 
        description="Y initial object position",
        min = -1000, max = 1000,
        default = 0) 
    
    z_ob_pos = IntProperty(
        name="Z initial object position", 
        description="Z initial object position",
        min = -1000, max = 1000,
        default = 0)

    zR_ob = IntProperty(
        name="Rayleigh range", 
        description="Rayleigh range object property value",
        min = -1000, max = 1000,
        default = 0) 

    zini_ob = IntProperty(
        name="zini value", 
        description="zini object property value",
        min = -100, max = 100,
        default = -5) 

    quini_ob = IntProperty(
        name="quini value", 
        description="quini object property value",
        min = 0, max = 100,
        default = 10) 

    int_box_frames = IntProperty(
        name="Frames per step", 
        description="Frames captured for each time step",
        min = 1, max = 10000000,
        default = 1)

    int_box_total_frames = IntProperty(
        name="Total frames", 
        description="Total of frames that will be rendered",
        min = 1, max = 1000000000,
        default = 1)

    int_box_particles_size = IntProperty(
        name="Particles size", 
        description="Value to scale the particles size",
        min = 1, max = 10000,
        default = 1000)

    def execute(self, context):
        obj = context.scene.objects.active
        # Do the rendering here
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        if context.object is not None:
            layout.prop(context.object, "name")
 

#############################################################################################################################################
#  ____                                  _             ____                           
# |  _ \  _ __  ___   _ __    ___  _ __ | |_  _   _   / ___| _ __  ___   _   _  _ __  
# | |_) || '__|/ _ \ | '_ \  / _ \| '__|| __|| | | | | |  _ | '__|/ _ \ | | | || '_ \ 
# |  __/ | |  | (_) || |_) ||  __/| |   | |_ | |_| | | |_| || |  | (_) || |_| || |_) |
# |_|    |_|   \___/ | .__/  \___||_|    \__| \__, |  \____||_|   \___/  \__,_|| .__/ 
#                    |_|                      |___/                            |_|   
############################################################################################################################################



class RenderPropertySettings(PropertyGroup): 
    
    folder_path = StringProperty(
        name="Data Folder",
        description="Folder with the simulation data.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    folder_path_export = StringProperty(
        name="Data Folder export initial conditions",
        description="Folder where initial conditions will be exported.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    path = StringProperty(
        name="Data File",
        description="File with the simulation data.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    image_path = StringProperty(
        name="Store Path",
        description="Path where renders will be stored, by default uses the path of the simulation data",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')
        
    objects_path = StringProperty(
        name="Store Path",
        description="Path where files will be stored, by default uses the path of the simulation data",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    total_states_info = IntProperty(
        name="Min :0  Max ", 
        description="Total number of states of the simulation",
        min = 0, max = 1000000,
        default = 0)

    int_box_particulas_Simulacion = IntProperty(
        name="Simulation particles", 
        description="Total number of particles for generating the matrix",
        min = 1000, max = 10000000,
        default = 100000)

    int_box_n_particulas = IntProperty(
        name="Particles to show ", 
        description="Total number of particles of the simulation",
        min = 1000, max = 10000000,
        default = 10000)

    int_box_granularity = IntProperty(
        name="Granularity ", 
        description="Modifies the granularity. Min = 1 , Max = 10",
        min = 1, max = 10,
        default = 5)

    int_box_saturation = IntProperty(
        name="Saturation ", 
        description="Modify the saturation. Min = 1, Max = 10",
        min = 1, max = 10,
        default = 5)

    int_box_state = IntProperty(
        name="State ", 
        description="Modify the State",
        min = 0, max = 9999,
        default = 0)

    int_box_offset = IntProperty(
        name="Offset ", 
        description="Modify the offset to show the projection",
        min = -1000, max = 1000,
        default = 50)

    bool_cut_box = BoolProperty(
        name="Cut box side",
        description="Enables the oposite cut plane view",
        default = True)  

    int_x_size = IntProperty(
        name="X Max Size", 
        description="X-window size",
        min = 0, max = 1000,
        default = 100)  

    int_y_size = IntProperty(
        name="Y Max Size", 
        description="Y-window size",
        min = 0, max = 1000,
        default = 100)   

    int_absorb_coeff = IntProperty(
        name="Absorb Coefficient", 
        description="Absorb Coefficient",
        min = 0, max = 100,
        default = 10) 

    x_ob_pos = IntProperty(
        name="X initial object position", 
        description="X initial object position",
        min = -1000, max = 1000,
        default = 0) 
    
    y_ob_pos = IntProperty(
        name="Y initial object position", 
        description="Y initial object position",
        min = -1000, max = 1000,
        default = 0) 
    
    z_ob_pos = IntProperty(
        name="Z initial object position", 
        description="Z initial object position",
        min = -1000, max = 1000,
        default = 0)

    zR_ob = IntProperty(
        name="Rayleigh range", 
        description="Rayleigh range object property value",
        min = -1000, max = 1000,
        default = 0) 

    zini_ob = IntProperty(
        name="zini value", 
        description="zini object property value",
        min = -100, max = 100,
        default = -5) 

    quini_ob = IntProperty(
        name="quini value", 
        description="quini object property value",
        min = 0, max = 100,
        default = 10) 

    int_box_frames = IntProperty(
        name="Frames per step", 
        description="Frames captured for each time step",
        min = 1, max = 10000000,
        default = 1)

    int_box_total_frames = IntProperty(
        name="Total frames", 
        description="Total of frames that will be rendered",
        min = 1, max = 1000000000,
        default = 1)

    int_box_particles_size = IntProperty(
        name="Particles size", 
        description="Value to scale the particles size",
        min = 1, max = 10000,
        default = 1000)


    image_format = EnumProperty(
        name="image_format",
        description="Select the type of cloud to create with material settings",
        items=[('BMP', 'BMP', ''),
                ('IRIS', 'IRIS', ''),
                ('PNG', 'PNG', ''),
                ('JPEG', 'JPEG', ''),
                ('JPEG2000', 'JPEG2000', ''),
                ('TARGA', 'TARGA', ''),
                ('TARGA_RAW', 'TARGA_RAW', ''), 
                ('CINEON', 'CINEON', ''),
                ('DPX', 'DPX', ''),
                ('OPEN_EXR_MULTILAYER', 'OPEN_EXR_MULTILAYER', ''),
                ('OPEN_EXR', 'OPEN_EXR', ''), 
                ('HDR', 'HDR', ''),
                ('TIFF', 'TIFF', ''),
              ],
        default='PNG') 

    
    video_format = EnumProperty(
        name="video_format",
        description="Select the type of cloud to create with material settings",
        items=[
                ('AVI_JPEG', 'AVI_JPEG', ''),
                ('AVI_RAW', 'AVI_RAW', ''), 
                ('FRAMESERVER', 'FRAMESERVER', ''), 
                ('H264', 'H264', ''),
                ('FFMPEG', 'FFMPEG', ''),
                ('THEORA', 'THEORA', ''),
              ],
        default='AVI_JPEG') 


    calculation_format = EnumProperty(
        name="calculation_format",
        description="Select the type of cloud to create with material settings",
        items=[
                ('2D', '2D', ''),
                ('3D', '3D', ''),
              ],
        default='2D') 


    planes_number = EnumProperty(
        name="planes_number",
        description="Select the type of cloud to create with material settings",
        items=[
                ('1P', '1P', ''),
                ('2P', '2P', ''),
              ],
        default='1P') 


    planes_project = EnumProperty(
        name="planes_project",
        description="Select the type of cloud to create with material settings",
        items=[
                ('X', 'X', ''),
                ('Y', 'Y', ''),
                ('XZ', 'XZ', ''),
                ('Z', 'Z', ''),
              ],
        default='X') 


    enum_items = EnumProperty(
        name="enum_items",
        description="Select the type of cloud to create with material settings",
        items=[
                ('FOO', 'Foo', ''),
                ('BAR', 'Bar', ''),
              ],
        default='FOO') 

    
    initial_objects = EnumProperty(
        name="initial_objects",
        description="Select the type of cloud to create with material settings",
        items=[
                ('GaussBeam', 'GaussBeam', ''),
                ('Vortex', 'Vortex', ''),
              ],
        default='GaussBeam') 


    color_schema = EnumProperty(
        name="color_schema",
        description="Select the type of cloud to create with material settings",
        items=[
                ('FullRange', 'FullRange', ''),
                ('MediumRange', 'MediumRange', ''),
                ('ColdRange', 'ColdRange', ''),
                ('HotRange', 'HotRange', ''),
              ],
        default='FullRange') 


############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

#     ______   __         ______    ______    ______   ________   ______     
#    /      \ |  \       /      \  /      \  /      \ |        \ /      \ 
#   |  $$$$$$\| $$      |  $$$$$$\|  $$$$$$\|  $$$$$$\| $$$$$$$$|  $$$$$$\
#   | $$   \$$| $$      | $$__| $$| $$___\$$| $$___\$$| $$__    | $$___\$$
#   | $$      | $$      | $$    $$ \$$    \  \$$    \ | $$  \    \$$    \ 
#   | $$   __ | $$      | $$$$$$$$ _\$$$$$$\ _\$$$$$$\| $$$$$    _\$$$$$$\
#   | $$__/  \| $$_____ | $$  | $$|  \__| $$|  \__| $$| $$_____ |  \__| $$
#   \$$    $$| $$     \| $$  | $$ \$$    $$ \$$    $$| $$     \ \$$    $$
#     \$$$$$$  \$$$$$$$$ \$$   \$$  \$$$$$$   \$$$$$$  \$$$$$$$$  \$$$$$$ 

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

class OBJECT_OT_AddColors(bpy.types.Operator):
    bl_idname = "add.colors"
    bl_label = "Add colors"
    country = bpy.props.StringProperty()

    def execute(self, context):

        #TODO Set the number of particles for each step reading the data from the original file, 
        #remember to set 10 steps using the 10% of the biggest probability value
        #also you will have to use the dupli_weights list of values to iterate over it when the key changes because te 
        #number of particles
        #Define an error message if occurs a problem during the run, is showed using a popup 
        def error_message(self, context):
            self.layout.label("Error opening the original array data")

        try:
            path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
       
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        particles_number = bpy.context.scene.iso_render.int_box_n_particulas

        #Use an auxiliar array to work with a variable number of points, 
        #allowing the user to make diferent points simulation with good results
        array_aux = np.zeros((particles_number, 4))
        #Fill the auxiliar array with the data of the original one 
        for point_number in range (0, particles_number):
            array_aux[point_number] = array_3d[0][point_number]

        #Sort the array to place first the particles with more probability
        array_aux = array_aux[np.argsort(array_aux[:,3])]


        #With the array sorted the last position is the particle with the biggest probability to appear
        actual_max_prob_value = array_aux[particles_number-1][3]
        #With the array sorted the first position is the particle with less probability to appear
        actual_min_prob_value = array_aux[0][3]

        general_maximum = actual_max_prob_value
        general_minimum = actual_min_prob_value

        for state_array in array_3d:
            maxi = np.max(state_array[:,3])
            mini = np.max(state_array[:,3])

            if (maxi > general_maximum):
                general_maximum = maxi
            if (mini < general_minimum):
                general_minimum = mini


        #Obtain an scalated step to distribute the points between the 10 scales of probability
        step_prob = (general_maximum-general_minimum)/10
        prob_using = step_prob

        steps = np.zeros(11)
        actual_step = 0

        for cont_particle in range(particles_number):
            if(array_aux[cont_particle][3] <= prob_using):
                steps[actual_step] += 1
            else:
                actual_step += 1
                prob_using += step_prob 

        #solves the problem with the extra particles not asigned to the last position
        steps[9] += steps[10]

        bpy.data.objects['Sphere'].select = True
        bpy.context.scene.objects.active = bpy.data.objects['Sphere']
        for cont_mat in range(10):
            material_value = bpy.data.objects['Sphere'].particle_systems['Drops'].settings.dupli_weights.get("Ico_"+str(9-cont_mat)+": 1")
            material_value.count = steps[cont_mat]

        return{'FINISHED'} 

class OBJECT_OT_ResetButton(bpy.types.Operator):
    bl_idname = "reset.image"
    bl_label = "Reiniciar entorno"
    country = bpy.props.StringProperty()

    def execute(self, context):

        def confirm_message(self, context):
            self.layout.label("The system environment was cleaned")

        nombreObjeto = "Sphere"  

        bpy.data.objects[nombreObjeto].hide = False

        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        bpy.context.scene.frame_current = 0

        bpy.context.scene.iso_render.int_box_state = -1
        bpy.context.window_manager.popup_menu(confirm_message, title="Reset", icon='VIEW3D_VEC')

        return{'FINISHED'} 



class OBJECT_OT_RenderButton(bpy.types.Operator):
    bl_idname = "render.image"
    bl_label = "RenderizarImagen"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.context.scene.iso_render.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Render. Try again with other path")


        try:    
            #Set the image format, PNG by default
            bpy.context.scene.render.image_settings.file_format = bpy.context.scene['ImageFormat']

        except:        
            bpy.context.scene.render.image_settings.file_format = 'PNG'

        try:

            #Sets the path where the file will be stored, by default the same as the datafile
            if dir_image_path == "":
                bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.iso_render.path + time.strftime("%c%s") + '.jpg'
                
                #Define a confirmation message to the default path            
                def confirm_message(self, context):
                    self.layout.label("Render image saved at: " + bpy.context.scene.iso_render.path )

            else:                
                bpy.data.scenes['Scene'].render.filepath = dir_image_path + time.strftime("%c%s") + '.jpg'
               
                #Define a confirmation message to the selected path 
                def confirm_message(self, context):
                    self.layout.label("Rendered image saved at: " + dir_image_path )   

            bpy.ops.render.render( write_still=True ) 


            bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        return{'FINISHED'} 


#Renders all objects one by one jumping between states
class OBJECT_OT_RenderAllButton(bpy.types.Operator):
    bl_idname = "render_all.image"
    bl_label = "RenderizarAllImagen"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.context.scene.iso_render.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Renders. Try again with other path")

        #Calculate the total of states
        #Calculate the total of states
        try:
            path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        for x in range(int(total_states)):

            try:    
                #Set the image format, PNG by default
                bpy.context.scene.render.image_settings.file_format = bpy.context.scene['ImageFormat']

            except:        
                bpy.context.scene.render.image_settings.file_format = 'PNG'

            try:

                #Sets the path where the file will be stored, by default the same as the datafile
                if dir_image_path == "":
                    bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.iso_render.path + str(x) + '.jpg'
                    
                    #Define a confirmation message to the default path            
                    def confirm_message(self, context):
                        self.layout.label("Render image saved at: " + bpy.context.scene.iso_render.path )

                else:                
                    bpy.data.scenes['Scene'].render.filepath = dir_image_path + str(x) + '.jpg'
                   
                    #Define a confirmation message to the selected path 
                    def confirm_message(self, context):
                        self.layout.label("Rendered image saved at: " + dir_image_path )   

                bpy.ops.render.render( write_still=True ) 

                bpy.ops.particle.forward()
                

            except:
                bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        return{'FINISHED'} 

#Renders all objects one by one jumping between states and do projections
class OBJECT_OT_RenderAllProjButton(bpy.types.Operator):
    bl_idname = "render_all_proj.image"
    bl_label = "RenderizarAllImagenProj"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.context.scene.iso_render.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Renders. Try again with other path")

        #Calculate the total of states
        #Calculate the total of states
        try:
            path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        for x in range(int(total_states)):

            try:    
                #Set the image format, PNG by default
                bpy.context.scene.render.image_settings.file_format = bpy.context.scene['ImageFormat']

            except:        
                bpy.context.scene.render.image_settings.file_format = 'PNG'

            try:

                #Sets the path where the file will be stored, by default the same as the datafile
                if dir_image_path == "":
                    bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.iso_render.path + str(x) + '.jpg'
                    
                    #Define a confirmation message to the default path            
                    def confirm_message(self, context):
                        self.layout.label("Render image saved at: " + bpy.context.scene.iso_render.path )

                else:                
                    bpy.data.scenes['Scene'].render.filepath = dir_image_path + str(x) + '.jpg'
                   
                    #Define a confirmation message to the selected path 
                    def confirm_message(self, context):
                        self.layout.label("Rendered image saved at: " + dir_image_path )   

                #Projections in X and Z axis using default values
                #bpy.context.scene.iso_render.planes_project = "XZ"
                bpy.ops.place.planeproject()
                bpy.ops.particle.projection()
                bpy.ops.delete.planeproject()

                bpy.ops.render.render( write_still=True ) 

                bpy.ops.particle.forward()
                

            except:
                bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        return{'FINISHED'} 

#Renders all objects one by one jumping between states and do cuts
class OBJECT_OT_RenderAllCutButton(bpy.types.Operator):
    bl_idname = "render_all_cut.image"
    bl_label = "RenderizarAllImagenCut"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.context.scene.iso_render.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Renders. Try again with other path")

        #Calculate the total of states
        #Calculate the total of states
        try:
            path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        for x in range(int(total_states)):

            try:    
                #Set the image format, PNG by default
                bpy.context.scene.render.image_settings.file_format = bpy.context.scene['ImageFormat']

            except:        
                bpy.context.scene.render.image_settings.file_format = 'PNG'

            try:

                #Sets the path where the file will be stored, by default the same as the datafile
                if dir_image_path == "":
                    bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.iso_render.path + str(x) + '.jpg'
                    
                    #Define a confirmation message to the default path            
                    def confirm_message(self, context):
                        self.layout.label("Render image saved at: " + bpy.context.scene.iso_render.path )

                else:                
                    bpy.data.scenes['Scene'].render.filepath = dir_image_path + str(x) + '.jpg'
                   
                    #Define a confirmation message to the selected path 
                    def confirm_message(self, context):
                        self.layout.label("Rendered image saved at: " + dir_image_path )   

                #Cut using 2 planes with default values
                bpy.context.scene.iso_render.planes_number = "2P"
                bpy.ops.place.plane()
                bpy.ops.particle.cut()
                bpy.ops.delete.plane()

                bpy.ops.render.render( write_still=True ) 

                bpy.ops.particle.forward()
                

            except:
                bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        return{'FINISHED'} 



#Renders all objects one by one jumping between states and do cuts
class OBJECT_OT_RenderAllFrame(bpy.types.Operator):
    bl_idname = "render_all_frame.image"
    bl_label = "RenderizarAllImagenFrame"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.context.scene.iso_render.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Renders. Try again with other path")

        try:
            frames_to_change = bpy.context.scene.iso_render.int_box_frames 
            total_frames = bpy.context.scene.iso_render.int_box_total_frames 

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        for x in range(int(total_frames)):

            try:    
                #Set the image format, PNG by default
                bpy.context.scene.render.image_settings.file_format = bpy.context.scene['ImageFormat']

            except:        
                bpy.context.scene.render.image_settings.file_format = 'PNG'

            try:

                #Sets the path where the file will be stored, by default the same as the datafile
                if dir_image_path == "":
                    bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.iso_render.path + str(x) + '.jpg'
                    
                    #Define a confirmation message to the default path            
                    def confirm_message(self, context):
                        self.layout.label("Render image saved at: " + bpy.context.scene.iso_render.path )

                else:                
                    bpy.data.scenes['Scene'].render.filepath = dir_image_path + str(x) + '.jpg'
                   
                    #Define a confirmation message to the selected path 
                    def confirm_message(self, context):
                        self.layout.label("Rendered image saved at: " + dir_image_path )   

                #Cut using 2 planes with default values
                #bpy.context.scene.iso_render.planes_number = "2P"
                #bpy.ops.place.plane()
                #bpy.ops.particle.cut()
                #bpy.ops.delete.plane()

                bpy.ops.render.render( write_still=True ) 

                frames_to_change -= 1

                if (frames_to_change == 0):
                    bpy.ops.particle.forward()
                    frames_to_change = bpy.context.scene.iso_render.int_box_frames

                else:
                    bpy.context.scene.frame_current += 1
 
                

            except:
                bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        return{'FINISHED'} 



class OBJECT_OT_RenderVideoButton(bpy.types.Operator):
    bl_idname = "render.video"
    bl_label = "RenderizarVideo"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.context.scene.iso_render.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Render. Try again with other path")


        try:    
            #Set the video format, AVI_JPEG by default            
            bpy.context.scene.render.image_settings.file_format = bpy.context.scene['VideoFormat'] 

        except:        
            bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG' 
        
        try:

            #Sets the path where the file will be stored, by default the same as the datafile
            if dir_image_path == "":
                bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.iso_render.path + time.strftime("%c%s") + '.avi'
                
                #Define a confirmation message to the default path            
                def confirm_message(self, context):
                    self.layout.label("Rendered video saved at: " + bpy.context.scene.iso_render.path )

            else:                
                bpy.data.scenes['Scene'].render.filepath = dir_image_path + time.strftime("%c%s") + '.avi'
               
                #Define a confirmation message to the selected path 
                def confirm_message(self, context):
                    self.layout.label("Rendered video saved at: " + dir_image_path )   

            bpy.ops.render.render(animation=True, write_still=True)


            bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        return{'FINISHED'}

class OBJECT_OT_CameraPlacement(bpy.types.Operator):
    bl_idname = "place.camera"
    bl_label = "Camera management"
    country = bpy.props.StringProperty()

    def execute(self, context):

        object_name = "Camera"  

        bpy.data.objects[object_name].location=(0,0,300)
        bpy.data.objects[object_name].rotation_euler=(0,0,0)
        bpy.data.objects[object_name].data.clip_end=1000


        return{'FINISHED'} 

class OBJECT_OT_CameraPlacement2(bpy.types.Operator):
    bl_idname = "place.camera2"
    bl_label = "Camera management2"
    country = bpy.props.StringProperty()

    def execute(self, context):

        object_name = "Camera"  

        bpy.data.objects[object_name].location=(0,-500,440)
        bpy.data.objects[object_name].rotation_euler=(0.872665,0,0)
        bpy.data.objects[object_name].data.clip_end=1000

        return{'FINISHED'} 

class OBJECT_OT_PlanePlacement(bpy.types.Operator):
    bl_idname = "place.plane"
    bl_label = "Plane management"
    country = bpy.props.StringProperty()

    def execute(self, context):

        bpy.ops.mesh.primitive_plane_add(radius=5, view_align=False, enter_editmode=False, location=(0, 0, 6), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        
        cut_plane_name = "Cut_plane"
        bpy.context.object.name = "Cut_plane"
        bpy.data.objects[cut_plane_name].rotation_euler=(0,1.5708,0)

        if (bpy.context.scene.iso_render.planes_number =="2P"):
            bpy.ops.mesh.primitive_plane_add(radius=5, view_align=False, enter_editmode=False, location=(5, 0, 1), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            cut_plane_name = "Cut_plane2"
            bpy.context.object.name = "Cut_plane2"
            bpy.data.objects[cut_plane_name].rotation_euler=(0,0,0)

        return{'FINISHED'} 

class OBJECT_OT_PlaneDelete(bpy.types.Operator):
    bl_idname = "delete.plane"
    bl_label = "Plane delete"
    country = bpy.props.StringProperty()

    def execute(self, context):

        bpy.context.object.select = 0

        if (bpy.context.scene.iso_render.planes_number =="1P"):
            bpy.data.objects["Cut_plane"].select = True
            bpy.ops.object.delete() 

        if (bpy.context.scene.iso_render.planes_number =="2P"):
            bpy.data.objects["Cut_plane"].select = True
            bpy.ops.object.delete() 
            bpy.data.objects["Cut_plane2"].select = True
            bpy.ops.object.delete() 

        return{'FINISHED'} 

class OBJECT_OT_PlanePlacementProject(bpy.types.Operator):
    bl_idname = "place.planeproject"
    bl_label = "Plane project management"
    country = bpy.props.StringProperty()

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')
        try:
            bpy.data.objects['Sphere_projections'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections'] 
            bpy.ops.object.delete()
            bpy.data.objects['Sphere'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Sphere'] 
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(297.861, -706.12, -1793.05), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
            bpy.context.object.name='Sphere_projections'
            bpy.data.objects['Sphere_projections'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections'] 
            if(bpy.context.scene.iso_render.planes_project == "XZ"):
                bpy.data.objects['Sphere_projections_2'].select = True
                bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections_2'] 
                bpy.ops.object.delete()
                bpy.data.objects['Sphere_projections'].select = True
                bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections'] 
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(297.861, -706.12, -1793.05), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                bpy.context.object.name='Sphere_projections_2'
                bpy.data.objects['Sphere_projections_2'].select = True
                bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections_2']
        except:
            bpy.data.objects['Sphere'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Sphere'] 
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(297.861, -706.12, -1793.05), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
            bpy.context.object.name='Sphere_projections'
            bpy.data.objects['Sphere_projections'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections']
            if(bpy.context.scene.iso_render.planes_project == "XZ"): 
                bpy.data.objects['Sphere_projections'].select = True
                bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections'] 
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(297.861, -706.12, -1793.05), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                bpy.context.object.name='Sphere_projections_2'
                bpy.data.objects['Sphere_projections_2'].select = True
                bpy.context.scene.objects.active = bpy.data.objects['Sphere_projections_2']



        bpy.ops.mesh.primitive_plane_add(radius=15, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        proj_plane_name1 = "Project_plane"
        bpy.context.object.name = "Project_plane"
        if(bpy.context.scene.iso_render.planes_project == "X"):
            bpy.data.objects[proj_plane_name1].rotation_euler=(0,1.5708,0)
        if(bpy.context.scene.iso_render.planes_project == "Y"):
            bpy.data.objects[proj_plane_name1].rotation_euler=(1.5708,0,0)
        if(bpy.context.scene.iso_render.planes_project == "Z"):
            bpy.data.objects[proj_plane_name1].rotation_euler=(0,0,0)
        if(bpy.context.scene.iso_render.planes_project == "XZ"):
            bpy.ops.mesh.primitive_plane_add(radius=15, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            proj_plane_name2 = "Project_plane_2"
            bpy.context.object.name = "Project_plane_2"
            bpy.data.objects[proj_plane_name1].rotation_euler=(0,1.5708,0)
            bpy.data.objects[proj_plane_name2].rotation_euler=(0,0,0)
        

        return{'FINISHED'} 

class OBJECT_OT_PlaneDeleteProject(bpy.types.Operator):
    bl_idname = "delete.planeproject"
    bl_label = "Plane project delete"
    country = bpy.props.StringProperty()

    def execute(self, context):

        bpy.context.object.select = 0

        bpy.data.objects["Project_plane"].select = True
        bpy.ops.object.delete() 
        try:
            bpy.data.objects["Project_plane_2"].select = True
            bpy.ops.object.delete() 
        except:
            return{'FINISHED'}

        return{'FINISHED'} 


class OBJECT_OT_Template_1(bpy.types.Operator):
    bl_idname = "template.1"
    bl_label = "Template 1"
    country = bpy.props.StringProperty()

    def execute(self, context):

        #Adds a grid with transpaces to the center
        mat_grid = bpy.data.materials.new('Grid_Material')
        mat_grid.diffuse_color = (0.34, 0.34, 0.34)
        mat_grid.type='WIRE'

        bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=8, radius=10, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.data.materials.append(mat_grid)


        return{'FINISHED'} 

class OBJECT_OT_Template_2(bpy.types.Operator):
    bl_idname = "template.2"
    bl_label = "Template 2"
    country = bpy.props.StringProperty()

    def execute(self, context):

        #Cut using 2 planes with default values
        bpy.context.scene.iso_render.planes_number = "2P"
        bpy.ops.place.plane()
        bpy.ops.particle.cut()
        bpy.ops.delete.plane()

        #Projections in X and Z axis using default values
        bpy.context.scene.iso_render.planes_project = "XZ"
        bpy.ops.place.planeproject()
        bpy.ops.particle.projection()
        bpy.ops.delete.planeproject()


        return{'FINISHED'} 

class OBJECT_OT_Template_3(bpy.types.Operator):
    bl_idname = "template.3"
    bl_label = "Template 3"
    country = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        
        #If dont exists a BezierCircle_Path 
        try:
            bpy.data.objects['BezierCircle_Path'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['BezierCircle_Path'] 
            bpy.ops.object.delete()
            bpy.ops.curve.primitive_bezier_circle_add(radius=100, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.name = 'BezierCircle_Path'
            bpy.data.objects['Camera'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Camera']

        #If already exist the BezierCircle_Path
        except:
            bpy.ops.curve.primitive_bezier_circle_add(radius=100, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.name = 'BezierCircle_Path'
            bpy.data.objects['Camera'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Camera']
            bpy.ops.object.constraint_add(type='FOLLOW_PATH')

        #Configure the camera settings to make the orbital path
        bpy.context.object.constraints["Follow Path"].target = bpy.data.objects["BezierCircle_Path"]
        bpy.context.object.constraints["Follow Path"].forward_axis = 'FORWARD_X'
        bpy.context.object.constraints["Follow Path"].use_curve_follow = True
        bpy.context.object.constraints["Follow Path"].up_axis = 'UP_Y'
        bpy.context.object.constraints["Follow Path"].offset = 1

        #Sets camera properties to look to the center
        bpy.data.objects['Camera'].data.clip_end=1000
        bpy.context.object.rotation_euler=(0,-3.14159,0)

        return{'FINISHED'} 

class OBJECT_OT_Template_4(bpy.types.Operator):
    bl_idname = "template.4"
    bl_label = "Template 4"
    country = bpy.props.StringProperty()

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')

        try:
            bpy.data.objects['Axis_XYZ'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Axis_XYZ'] 
            bpy.ops.object.delete()

        except:
            bpy.ops.object.select_all(action='DESELECT')

        size_axis = 40
        cone_size = 0.7
        cone_length = 1

        #Axis X
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Cone_X'
        bpy.context.object.scale=(cone_size,cone_size,cone_length)
        bpy.context.object.rotation_euler=(0,1.5708,0)
        bpy.context.object.location=(size_axis+cone_length,0,0)

        bpy.ops.mesh.primitive_cylinder_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Axis_X'
        bpy.context.object.rotation_euler=(0,1.5708,0)
        bpy.context.object.scale=(0.1,0.1,size_axis)

        bpy.data.objects['Cone_X'].select = True
        bpy.data.objects['Axis_X'].select = True
        bpy.ops.object.join()

        bpy.context.object.location=(size_axis,0,0)

        #Axis Y
        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Cone_Y'
        bpy.context.object.scale=(cone_size,cone_size,cone_length)
        bpy.context.object.rotation_euler=(-1.5708,0,0)
        bpy.context.object.location=(0,size_axis+cone_length,0)

        bpy.ops.mesh.primitive_cylinder_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Axis_Y'
        bpy.context.object.rotation_euler=(1.5708,0,0)
        bpy.context.object.scale=(0.1,0.1,size_axis)

        bpy.data.objects['Cone_Y'].select = True
        bpy.data.objects['Axis_Y'].select = True
        bpy.ops.object.join()

        bpy.context.object.location=(0,size_axis,0)

        #Axis Z
        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Cone_Z'
        bpy.context.object.scale=(cone_size,cone_size,cone_length)
        bpy.context.object.rotation_euler=(0,0,1.5708)
        bpy.context.object.location=(0,0,size_axis+cone_length)

        bpy.ops.mesh.primitive_cylinder_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Axis_XYZ'
        bpy.context.object.rotation_euler=(0,0,0)
        bpy.context.object.scale=(0.1,0.1,size_axis)

        bpy.data.objects['Cone_Z'].select = True
        bpy.data.objects['Axis_XYZ'].select = True
        bpy.ops.object.join()

        bpy.context.object.location=(0,0,size_axis)


        #Axis XYZ
        bpy.ops.object.select_all(action='DESELECT')

        bpy.data.objects['Axis_X'].select = True
        bpy.data.objects['Axis_Y'].select = True
        bpy.data.objects['Axis_XYZ'].select = True
        bpy.ops.object.join()

        #Axis space placement
        bpy.context.object.location=(-30,-30,0)

        #Adds a grid with transpaces to the center
        mat_grid = bpy.data.materials.new('Axis_Material')
        mat_grid.diffuse_color = (0.34, 0.34, 0.34)
        mat_grid.type='SURFACE'

        bpy.context.object.data.materials.append(mat_grid)

        return{'FINISHED'} 


#Initial conditions code

class OBJECT_OT_Split_Screen(bpy.types.Operator):
    bl_idname = "split.screen"
    bl_label = "Split Screen"
    country = bpy.props.StringProperty()

    def execute(self, context):
        start_areas = context.screen.areas[:]
        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.3)
        for area in context.screen.areas:
            if area not in start_areas:
                area.type = 'VIEW_3D'

        bpy.context.space_data.lock_camera_and_layers = False

        return{'FINISHED'}


class OBJECT_OT_Initial_Object(bpy.types.Operator):
    bl_idname = "initial.object"
    bl_label = "Initial Object"
    country = bpy.props.StringProperty()

    def execute(self, context):

        bpy.context.scene.layers[0]=True
        bpy.context.scene.layers[1]=False

        bpy.data.objects['Lamp'].data.type = 'POINT'
        bpy.data.objects['Lamp'].location = (0,0,10)
        bpy.data.objects['Lamp'].rotation_euler = (0,0,10)

        bpy.context.scene.world.horizon_color = (1, 1, 1)
        bpy.context.scene.world.light_settings.use_ambient_occlusion = True


        bpy.ops.object.select_all(action='DESELECT')

        try:
            bpy.data.objects['Origin_Cube'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Origin_Cube'] 
            bpy.ops.object.delete()
            bpy.data.objects['X_size_text'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['X_size_text'] 
            bpy.ops.object.delete()
            bpy.data.objects['Y_size_text'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Y_size_text'] 
            bpy.ops.object.delete()
            bpy.data.objects['Abs_coeff_text'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Abs_coeff_text'] 
            bpy.ops.object.delete()
            #Remove materials function, first parameter de material, second the unlink boolean 
            #remove(material, do_unlink=False by default)
            bpy.data.materials.remove(bpy.data.materials['Origin_Cube_Material'],True)
            bpy.data.materials.remove(bpy.data.materials['Text_Material'],True)
            bpy.ops.object.select_all(action='DESELECT')

        except:
            bpy.ops.object.select_all(action='DESELECT')


        #X-size and Y-size are stored in the X and Y sie values of the object
        #Absorb coeff is stored in the alpha color value of the material
        bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Origin_Cube'
        x_size= bpy.context.scene.iso_render.int_x_size / 10
        real_x_size = bpy.context.scene.iso_render.int_x_size
        y_size= bpy.context.scene.iso_render.int_y_size / 10
        real_y_size = bpy.context.scene.iso_render.int_y_size
        bpy.data.objects['Origin_Cube'].scale[0] = x_size
        bpy.data.objects['Origin_Cube'].scale[1] = y_size
        #Z axis size equal to (x+y)/2
        z_size = (x_size+y_size)/2
        bpy.data.objects['Origin_Cube'].scale[2] = z_size

        #Space cube Material
        origin_cube_mat = bpy.data.materials.new('Origin_Cube_Material')
        origin_cube_mat.diffuse_color = (0, 0, 0)
        origin_cube_mat.type='WIRE'
        origin_cube_mat.use_transparency = True
        density_mat_absorb_coeff = 1
        origin_cube_mat.alpha = density_mat_absorb_coeff
        bpy.data.objects['Origin_Cube'].data.materials.append(origin_cube_mat)

        #Adding text to referene properties
        text_scale=4

        bpy.ops.object.text_add(radius=text_scale, view_align=False, enter_editmode=False, location=(-1*x_size, -1*(y_size+text_scale), -1*(z_size+0.5)), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'X_size_text'
        bpy.context.object.rotation_euler[0] = 0.523599
        bpy.ops.object.editmode_toggle()
        bpy.ops.font.delete()
        bpy.ops.font.text_insert(text=" X: " + str(real_x_size) + " - Y: " + str(real_y_size))
        bpy.ops.object.editmode_toggle()

        bpy.ops.object.text_add(radius=text_scale, view_align=False, enter_editmode=False, location=(-1*x_size, -1*(y_size+text_scale*2.1), -1*(z_size+0.5)), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Abs_coeff_text'
        bpy.context.object.rotation_euler[0] = 0.523599
        bpy.ops.object.editmode_toggle()
        bpy.ops.font.delete()
        bpy.ops.font.text_insert(text=" Abs coeff: " + str(bpy.context.scene.iso_render.int_absorb_coeff))
        bpy.ops.object.editmode_toggle()

        bpy.ops.object.text_add(radius=text_scale, view_align=False, enter_editmode=False, location=(-1*(x_size + text_scale), y_size, -1*(z_size+0.5)), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.name = 'Y_size_text'
        bpy.context.object.rotation_euler[0] = 0.523599
        bpy.context.object.rotation_euler[2] = -1.5708
        bpy.ops.object.editmode_toggle()
        bpy.ops.font.delete()
        bpy.ops.font.text_insert(text=" Y: " + str(real_y_size))
        bpy.ops.object.editmode_toggle()



        #Texts material
        text_mat = bpy.data.materials.new('Text_Material')
        text_mat.diffuse_color = (0, 0, 0)
        text_mat.type='SURFACE'
        text_mat.use_transparency = True
        density_mat_absorb_coeff = 0.95
        text_mat.alpha = density_mat_absorb_coeff
        bpy.data.objects['X_size_text'].data.materials.append(text_mat)
        bpy.data.objects['Abs_coeff_text'].data.materials.append(text_mat)
        bpy.data.objects['Y_size_text'].data.materials.append(text_mat)

        return{'FINISHED'} 



class OBJECT_OT_Initial_Object2(bpy.types.Operator):
    bl_idname = "initial.object2"
    bl_label = "Initial Object2"
    country = bpy.props.StringProperty()

    def execute(self, context):

        bpy.context.scene.layers[0]=False
        bpy.context.scene.layers[1]=True

        bpy.context.space_data.lock_camera_and_layers = False


        bpy.data.objects['Lamp'].data.type = 'POINT'
        bpy.data.objects['Lamp'].location = (0,0,10)
        bpy.data.objects['Lamp'].rotation_euler = (0,0,10)

        bpy.context.scene.world.horizon_color = (1, 1, 1)
        bpy.context.scene.world.light_settings.use_ambient_occlusion = True


        bpy.ops.object.select_all(action='DESELECT')

        try:
            bpy.data.objects['Gauss_Sphere'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Gauss_Sphere'] 
            bpy.ops.object.delete()
            bpy.data.objects['Gauss_text'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Gauss_text'] 
            bpy.ops.object.delete()
            bpy.data.materials.remove(bpy.data.materials['Gauss_Sphere_Material'],True)
            bpy.data.materials.remove(bpy.data.materials['Text_Material_2'],True)

        except:
            bpy.ops.object.select_all(action='DESELECT')

        try:
            bpy.data.objects['Vortex'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Vortex'] 
            bpy.ops.object.delete()
            bpy.data.objects['Vortex_text'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Vortex_text'] 
            bpy.ops.object.delete()
            bpy.data.materials.remove(bpy.data.materials['Vortex_Material'],True)
            bpy.data.materials.remove(bpy.data.materials['Text_Material_2'],True)

        except:
            bpy.ops.object.select_all(action='DESELECT')



        if (bpy.context.scene.iso_render.initial_objects == "GaussBeam"):
            #Gaussian 

            x_gauss_pos = bpy.context.scene.iso_render.x_ob_pos / 10
            y_gauss_pos = bpy.context.scene.iso_render.y_ob_pos / 10
            z_gauss_pos = bpy.context.scene.iso_render.z_ob_pos / 10
            gauss_size = 2
            bpy.ops.mesh.primitive_uv_sphere_add(size=gauss_size, view_align=False, enter_editmode=False, location=(x_gauss_pos, y_gauss_pos, z_gauss_pos), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.name = 'Gauss_Sphere'

            #Gaussian Material, Absortion coeff will be represented by the volume density, transparency settings
            gauss_sphere_material = bpy.data.materials.new('Gauss_Sphere_Material')
            gauss_sphere_material.diffuse_color = (0.75, 0, 0)
            gauss_sphere_material.type='SURFACE'
            bpy.data.objects['Gauss_Sphere'].data.materials.append(gauss_sphere_material)

            #Objects text
            text_scale = 4
            bpy.ops.object.text_add(radius=text_scale, view_align=False, enter_editmode=False, location=(x_gauss_pos, y_gauss_pos-text_scale, z_gauss_pos-0.5), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.name = 'Gauss_text'
            bpy.context.object.rotation_euler[0] = 0.523599
            bpy.ops.object.editmode_toggle()
            bpy.ops.font.delete()
            zR=bpy.context.scene.iso_render.zR_ob 
            zini=bpy.context.scene.iso_render.zini_ob
            bpy.ops.font.text_insert(text=" G, zR:" + str(zR) + ",zini:" + str(zini))
            bpy.ops.object.editmode_toggle()


            #Texts material
            text_mat = bpy.data.materials.new('Text_Material_2')
            text_mat.diffuse_color = (0, 0, 0)
            text_mat.type='SURFACE'
            text_mat.use_transparency = True
            density_mat_absorb_coeff = 0.95
            text_mat.alpha = density_mat_absorb_coeff
            bpy.data.objects['Gauss_text'].data.materials.append(text_mat)

        if (bpy.context.scene.iso_render.initial_objects == "Vortex"):
            #Vortex
            x_vortex_pos = bpy.context.scene.iso_render.x_ob_pos / 10
            y_vortex_pos = bpy.context.scene.iso_render.y_ob_pos / 10
            z_vortex_pos = bpy.context.scene.iso_render.z_ob_pos / 10
            vortex_size = 2
            bpy.ops.mesh.primitive_torus_add(rotation=(0, 0, 0), view_align=False, location=(x_vortex_pos, y_vortex_pos, z_vortex_pos), minor_segments=22, mode='MAJOR_MINOR', major_radius=0.88, minor_radius=0.70, abso_major_rad=1.25, abso_minor_rad=0.75, layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.scale[2] = 1.92
            bpy.context.object.name = 'Vortex'
            

            #Vortex Material, Absortion coeff will be represented by the volume density, transparency settings
            vortex_material = bpy.data.materials.new('Vortex_Material')
            vortex_material.diffuse_color = (0, 0.5, 1)
            vortex_material.type='SURFACE'
            bpy.data.objects['Vortex'].data.materials.append(vortex_material)

            #Objects text
            text_scale = 4
            bpy.ops.object.text_add(radius=text_scale, view_align=False, enter_editmode=False, location=(x_vortex_pos, y_vortex_pos-text_scale, z_vortex_pos-0.5), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.name = 'Vortex_text'
            bpy.context.object.rotation_euler[0] = 0.523599
            bpy.ops.object.editmode_toggle()
            bpy.ops.font.delete()
            zR=bpy.context.scene.iso_render.zR_ob 
            zini=bpy.context.scene.iso_render.zini_ob
            bpy.ops.font.text_insert(text=" G, zR:" + str(zR) + ",zini:" + str(zini))
            bpy.ops.object.editmode_toggle()


            #Texts material
            text_mat = bpy.data.materials.new('Text_Material_2')
            text_mat.diffuse_color = (0, 0, 0)
            text_mat.type='SURFACE'
            text_mat.use_transparency = True
            density_mat_absorb_coeff = 0.95
            text_mat.alpha = density_mat_absorb_coeff
            bpy.data.objects['Vortex_text'].data.materials.append(text_mat)

        return{'FINISHED'} 

class OBJECT_OT_Export_Parameters(bpy.types.Operator):
    bl_idname = "export.parameters"
    bl_label = "Export Parameters"
    country = bpy.props.StringProperty()

    def execute(self, context):
        path = bpy.context.scene.iso_render.folder_path_export
        f = open(path + 'initial_conditions.py', 'w+')
        f.write("#Object type: " + bpy.context.scene.iso_render.initial_objects + "\r\n")
        f.write("\r\n")
        f.write("import numpy as np" + "\r\n")
        f.write("\r\n")
        f.write("Nx = 300" + "\r\n")
        f.write("Ny = Nx" + "\r\n")
        f.write("tmax = 10" + "\r\n")
        f.write("dt = 0.001" + "\r\n")
        f.write("xmax = " + str(bpy.context.scene.iso_render.int_x_size) + "\r\n")
        f.write("ymax = " + str(bpy.context.scene.iso_render.int_y_size) + "\r\n")
        f.write("\r\n")
        f.write("x_ob_pos = " + str(bpy.context.scene.iso_render.x_ob_pos) + "\r\n")
        f.write("y_ob_pos = " + str(bpy.context.scene.iso_render.y_ob_pos) + "\r\n")
        f.write("z_ob_pos = " + str(bpy.context.scene.iso_render.z_ob_pos) + "\r\n")
        f.write("\r\n")
        f.write("images = 100" + "\r\n")
        f.write("absorb_coeff = " + str(bpy.context.scene.iso_render.int_absorb_coeff) + "\r\n")
        if (bpy.context.scene.iso_render.initial_objects == "GaussBeam"):
            f.write("fixmaximum = 2/(4*np.pi)" + "\r\n") 
        if (bpy.context.scene.iso_render.initial_objects == "Vortex"):
            f.write("fixmaximum= 2/(4*np.pi*np.exp(1))" + "\r\n")
        f.write("\r\n") 
        f.write("\r\n")
        f.write("def psi_0(x,y):" + "\r\n") 
        f.write("\r\n")
        f.write("   zR = " + str(bpy.context.scene.iso_render.zR_ob) + "\r\n")
        f.write("   zR = " + str(bpy.context.scene.iso_render.zini_ob) + "\r\n")
        f.write("   qini = 2*1.j*zini+zR" + "\r\n")
        if (bpy.context.scene.iso_render.initial_objects == "Vortex"):
            f.write("   r=np.sqrt(x**2+y**2)" + "\r\n")
            f.write("   phase=np.exp(1.j*np.arctan2(y,x))" + "\r\n")
        f.write("   f = np.sqrt(2*zR/np.pi)/qini*np.exp(-(x**2+y**2)/qini)" + "\r\n")
        f.write("\r\n")
        f.write("   return f;" + "\r\n")
        f.write("\r\n") 
        f.write("\r\n")
        f.write("def V(x,y,t,psi):" + "\r\n")
        f.write("   V=0" + "\r\n")
        f.write("\r\n")
        f.write("   return V;" + "\r\n")
        f.close()

        return{'FINISHED'}


#Saves the actual template
class OBJECT_OT_SaveThisFiles(bpy.types.Operator):
    bl_idname = "save_this.files"
    bl_label = "SaveThisFiles"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):
    
        bpy.ops.particle.forward()
        bpy.ops.particle.backward()
        
        objs = bpy.data.objects

        if "Ico_9_extra" in objs:
            objs.remove(objs["Ico_9_extra"], True)        

        dir_image_path = bpy.context.scene.iso_render.objects_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Files. Try again with other path")

        try:
            #Sets the path where the files will be stored, by default the same as the datafile
            if dir_image_path == "":
                bpy.ops.wm.save_as_mainfile(filepath="/Users/edgarfigueiras/Desktop/template.blend")
                #Define a confirmation message to the default path            
                def confirm_message(self, context):
                    self.layout.label("Template file saved at: " + bpy.context.scene.iso_render.path )

            else:              
                bpy.ops.wm.save_as_mainfile(filepath = dir_image_path + "template.blend")
               
                #Define a confirmation message to the selected path 
                def confirm_message(self, context):
                    self.layout.label("Template file saved at: " + dir_image_path )  


            bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE') 

            bpy.ops.render.render( write_still=True )
                
        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        return{'FINISHED'} 

#Renders all objects one by one jumping between states
class OBJECT_OT_SaveAllFiles(bpy.types.Operator):
    bl_idname = "save_all.files"
    bl_label = "SaveAllFiles"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):
    
        bpy.ops.particle.forward()
        bpy.ops.particle.backward()
        
        objs = bpy.data.objects
        objs.remove(objs["Ico_9_extra"], True)

        dir_image_path = bpy.context.scene.iso_render.objects_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Files. Try again with other path")

        #Calculate the total of states
        try:
            path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        for x in range(int(total_states)):

            try:
                #Sets the path where the files will be stored, by default the same as the datafile
                if dir_image_path == "":
                    bpy.ops.wm.save_as_mainfile(filepath="/Users/edgarfigueiras/Desktop/" + str(x) + ".blend")
                    #Define a confirmation message to the default path            
                    def confirm_message(self, context):
                        self.layout.label("Template files saved at: " + bpy.context.scene.iso_render.path )

                else:                
                    bpy.ops.wm.save_as_mainfile(filepath = dir_image_path + str(x) + ".blend")
                   
                    #Define a confirmation message to the selected path 
                    def confirm_message(self, context):
                        self.layout.label("Template files saved at: " + dir_image_path )   

                bpy.ops.render.render( write_still=True )

                bpy.ops.particle.forward()
                

            except:
                bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        return{'FINISHED'} 

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
#
#    _______    ______   __    __  ________  __        ______  
#   |       \  /      \ |  \  |  \|        \|  \      /      \
#   | $$$$$$$\|  $$$$$$\| $$\ | $$| $$$$$$$$| $$     |  $$$$$$\
#   | $$__/ $$| $$__| $$| $$$\| $$| $$__    | $$     | $$___\$$
#   | $$    $$| $$    $$| $$$$\ $$| $$  \   | $$      \$$    \ 
#   | $$$$$$$ | $$$$$$$$| $$\$$ $$| $$$$$   | $$      _\$$$$$$\
#   | $$      | $$  | $$| $$ \$$$$| $$_____ | $$_____|  \__| $$
#   | $$      | $$  | $$| $$  \$$$| $$     \| $$     \\$$    $$
#    \$$       \$$   \$$ \$$   \$$ \$$$$$$$$ \$$$$$$$$ \$$$$$$ 
#
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################                                                   

class PanelStartingParameters(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Starting Parameters Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box = layout.box()


        box.label(text="INITIAL PARAMETERS")

        #box.operator("areatype.splitview", text="Split Screen")

        box.label(text="Environment", icon='META_CUBE')
       
        box.prop(scn.iso_render, "int_x_size")

        box.prop(scn.iso_render, "int_y_size")

        box.label(text="Absorb coeff, 0 = Periodic boundary")

        box.prop(scn.iso_render, "int_absorb_coeff")

        box.operator("initial.object", text="Create environment")

        box.label(text="Object", icon='META_BALL')

        box.label(text="Select object and properties")

        box.prop(scn.iso_render, "initial_objects", text="", icon='OBJECT_DATA' )

        box.prop(scn.iso_render, "x_ob_pos")

        box.prop(scn.iso_render, "y_ob_pos")

        box.prop(scn.iso_render, "z_ob_pos")

        box.prop(scn.iso_render, "zR_ob")

        box.prop(scn.iso_render, "zini_ob")

        box.operator("initial.object2", text="Create object")

        box.label(text="Select the folder where you will export the data", icon='FILE_FOLDER')

        box.prop(scn.iso_render, "folder_path_export", text="")

        box.operator("export.parameters", text="Export parameters")


class PanelDataSelection(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Data Selection Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box1 = layout.box()
        box2 = layout.box()


        box1.label(text="PARAMETERS")

        box1.label(text="Select the data file", icon='LIBRARY_DATA_DIRECT')

        box1.prop(scn.iso_render, "path", text="")

        box1.label(text="Select the number of particles to be shown by step", icon='PARTICLE_DATA')

        box1.prop(scn.iso_render, "int_box_n_particulas")


        box2.label(text="SIMULATION")

        box2.prop(scn.iso_render, "int_box_particles_size")

        box2.label(text="Select the colour range", icon='GROUP_VCOL')

        box2.prop(scn.iso_render, "color_schema", text="")

        box2.operator("particle.calculator", text="Place Particles")

        box2.operator("add.colors", text="Add Colors")

        box2.operator("reset.image", text="Reset Environment")


class PanelStates(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "States Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box22 = layout.box()


        #Box to move back and forward between states

        box22.label(text="STATES")

        col = box22.column(align = True)

        row = col.row(align = True)
        
        row.prop(scn.iso_render, "total_states_info")

        row.enabled = False 

        row_box = box22.row()

        row_box.prop(scn.iso_render, "int_box_state")

        row_box.enabled = True    

        row = box22.row()

        row.operator("particle.backward", text="Previous State", icon='BACK')

        row.operator("particle.forward", text="Next State", icon='FORWARD')



class PanelSaveFiles(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Objects template saver"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box1 = layout.box()

        box1.label(text="PARAMETERS")

        box1.label(text="Select the path to save the files", icon='LIBRARY_DATA_DIRECT')

        box1.prop(scn.iso_render, "objects_path", text="")

        box1.label(text="Save this file to be used as a template", icon='PARTICLE_DATA')

        box1.operator("save_this.files", text="Save this file")

        box1.label(text="Save all the files to be used as templates for generate models", icon='PARTICLE_DATA')

        box1.operator("save_all.files", text="Save all files")


class PanelTemplate(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Templates Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box = layout.box()


        #Box to move back and forward between states

        box.label(text="TEMPLATES")

        box.operator("template.1", text="Add a grid", icon='GRID')

        box.operator("template.2", text="Cut and Projections", icon='MOD_ARRAY')

        box.operator("template.3", text="Orbital camera", icon='OUTLINER_DATA_CAMERA')

        box.operator("template.4", text="3D Axis", icon='OUTLINER_DATA_EMPTY')


class PanelCut(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Cut Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box22 = layout.box()

        box22.label(text="CUTS")

        box22.label(text="Number of planes (1 by default)", icon='MOD_SOLIDIFY')

        box22.prop(scn.iso_render, "planes_number", text="")

        box22.label(text="Places the cut plane in the 3D view", icon='MOD_UVPROJECT')

        box22.operator("place.plane", text="Place plane")

        box22.operator("bool_cut_box", text="Place plane")

        box22.label(text="Makes a cut using the plane", icon='MOD_DECIM')

        box22.operator("particle.cut", text="Cut")

        box22.label(text="Delete planes", icon='FACESEL_HLT')

        box22.operator("delete.plane", text="Delete Planes")


class PanelProject(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Projection Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box22 = layout.box()

        box22.label(text="PROJECTIONS")

        box22.label(text="Axis of the projection", icon='MANIPUL')

        box22.prop(scn.iso_render, "planes_project", text="")

        box22.label(text="Places the projection plane in the 3D view", icon='MOD_UVPROJECT')

        box22.operator("place.planeproject", text="Place plane")

        box22.operator("bool_cut_box", text="Place plane")

        box22.label(text="Sets the offset of the projection respect the center", icon='MOD_UVPROJECT')

        box22.prop(scn.iso_render, "int_box_offset")

        box22.label(text="Makes the projection using the plane", icon='MOD_MIRROR')

        box22.operator("particle.projection", text="Projection")

        box22.label(text="Delete the projection plane", icon='FACESEL_HLT')

        box22.operator("delete.planeproject", text="Delete Plane")     



class PanelRenderData(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Rendering Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box23 = layout.box()
        box3 = layout.box()

        box23.label(text="CAMERA OPTIONS")

        box23.label(text="Camera predefs", icon='SCENE')

        box23.operator("place.camera", text="Sets camera to Top")

        box23.operator("place.camera2", text="Sets camera 50º angle")


        box3.label(text="RENDER")

        box3.label(text="Select the folder to store renders", icon='FILE_FOLDER')

        box3.prop(scn.iso_render, "image_path", text="")

        box3.label(text="Select the image format (PNG by default)", icon='RENDER_STILL')

        box3.prop(scn.iso_render, "image_format", text="")

        box3.operator("render.image", text="Save image")

        box3.operator("render_all.image", text="Save all images")

        box3.operator("render_all_proj.image", text="Save all images + projections")

        box3.operator("render_all_cut.image", text="Save all images + cuts")

        box3.label(text="Video frame by frame", icon='CAMERA_DATA')

        box3.prop(scn.iso_render, "int_box_frames")

        box3.prop(scn.iso_render, "int_box_total_frames")

        box3.operator("render_all_frame.image", text="Save all images as film")

        box3.label(text="Select the video format (AVI by default)", icon='RENDER_ANIMATION')

        box3.prop(scn.iso_render, "video_format", text="")

        box3.operator("render.video", text="Save video")


class PanelInfoShortcuts(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Information Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    bl_category = "QMBlender"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box4 = layout.box()

        box4.label(text="SHORTCUTS")

        box4.label(text="To switch view press SHIFT + Z", icon='INFO')

        box4.label(text="To start the animation press ALT + A", icon='INFO')

        box4.label(text="To modify grid values F6", icon='INFO')

        box4.label(text="Transform particles into objects using CRTL + SHIFT + A", icon='INFO')

        box4.label(text="Join all selected objects using CRTL + J", icon='INFO')
        



############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
#
#    ______   __       __        ________  __    __  __    __   ______  ________  ______   ______   __    __   ______  
#   /      \ |  \     /  \      |        \|  \  |  \|  \  |  \ /      \|        \|      \ /      \ |  \  |  \ /      \ 
#   |  $$$$$$\| $$\   /  $$      | $$$$$$$$| $$  | $$| $$\ | $$|  $$$$$$\\$$$$$$$$ \$$$$$$|  $$$$$$\| $$\ | $$|  $$$$$$\
#   | $$  | $$| $$$\ /  $$$      | $$__    | $$  | $$| $$$\| $$| $$   \$$  | $$     | $$  | $$  | $$| $$$\| $$| $$___\$$
#   | $$  | $$| $$$$\  $$$$      | $$  \   | $$  | $$| $$$$\ $$| $$        | $$     | $$  | $$  | $$| $$$$\ $$ \$$    \ 
#   | $$ _| $$| $$\$$ $$ $$      | $$$$$   | $$  | $$| $$\$$ $$| $$   __   | $$     | $$  | $$  | $$| $$\$$ $$ _\$$$$$$\
#   | $$/ \ $$| $$ \$$$| $$      | $$      | $$__/ $$| $$ \$$$$| $$__/  \  | $$    _| $$_ | $$__/ $$| $$ \$$$$|  \__| $$
#    \$$ $$ $$| $$  \$ | $$      | $$       \$$    $$| $$  \$$$ \$$    $$  | $$   |   $$ \ \$$    $$| $$  \$$$ \$$    $$
#    \$$$$$$\ \$$      \$$       \$$        \$$$$$$  \$$   \$$  \$$$$$$    \$$    \$$$$$$  \$$$$$$  \$$   \$$  \$$$$$$ 
#       \$$$  
#
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################


#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particle calculator                                                  #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticleCalculator(bpy.types.Operator):
    """My Object Moving Script"""                 # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.calculator"             # unique identifier for buttons and menu items to reference.
    bl_label = "Particle calculator"              # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}             # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
       
        def sphere_object(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.0' + str(x)]
            if (x >= 100) :
                emitter = bpy.data.objects['Sphere.' + str(x)]
            return emitter
            

        #Creating the Icospheres that will give the particles the color gradiations as an origin of the material
        #Takes as input the materials vector
        def ico_creation(materials_vector): 
            number_of_icos=10 #10 plus the extra
            #First Ico and Group creation
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, view_align=False, enter_editmode=False, location=(2, 2, -99), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.name = "Ico_0"
            bpy.ops.object.group_add()
            bpy.data.groups["Group"].name = "Ico"
            bpy.ops.object.group_link(group='Ico')
            bpy.context.object.scale = (0.0001, 0.0001, 0.0001)
            bpy.context.active_object.active_material=materials_vector[0]

            #Icos iterative creation
            for cont in range(1, number_of_icos):
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, view_align=False, enter_editmode=False, location=(2, 2, -100 + (-1*cont)), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.context.object.name = "Ico_" + str(cont)
                bpy.ops.object.group_link(group='Ico')
                bpy.context.object.scale = (0.0001, 0.0001, 0.0001)
                bpy.context.active_object.active_material=materials_vector[cont]

           #Extra Ico for ordenation purpouses 
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, view_align=False, enter_editmode=False, location=(2, 2, -111), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.context.object.name = "Ico_9_extra"
            bpy.ops.object.group_link(group='Ico')
            bpy.context.object.scale = (0.0001, 0.0001, 0.0001)

        #Define an error message if occurs a problem during the run, is showed using a popup 
        def error_message(self, context):
            self.layout.label("No datafile selected. Remember to select a compatible datafile")

        #Delete all the old materials    
        for material in bpy.data.materials:
            material.user_clear();
            bpy.data.materials.remove(material);

        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        bpy.context.scene.frame_current = 0    
        bpy.context.scene.iso_render.int_box_state = -1
        
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)   #Refresh the actual visualization with the new generator object placed  

        #Reading the data to generate the function who originated it
        #Read the data from te panel 
        path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
        
        try:
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        N = len(array_3d)   #Size of the matrix

        #Sets the maximum state avaliable
        bpy.context.scene.iso_render.total_states_info = N-1


        particles_number = bpy.context.scene.iso_render.int_box_n_particulas #Read from the panel 
        

        #Set the world color 
        bpy.context.scene.world.horizon_color = (0, 0, 0)
        #bpy.context.scene.world.horizon_color = (0.0041, 0.0087, 0.145)
        bpy.context.scene.world.light_settings.use_environment_light = True
        #Set the light propertyes
        bpy.data.objects['Lamp'].data.type = 'SUN'
        bpy.data.objects['Lamp'].location = (0,0,10)
        bpy.data.objects['Lamp'].rotation_euler = (0,0,10)

        #Emitter object, father of the particles
        ob = bpy.ops.mesh.primitive_uv_sphere_add(size=0.2, location=(0,0,-10000))
        bpy.context.object.scale = (0.0001, 0.0001, 0.0001)
        emitter = bpy.context.object

        bpy.ops.object.particle_system_add()    
        psys1 = emitter.particle_systems[-1]
                    
        psys1.name = 'Drops' 

        if (bpy.context.scene.iso_render.color_schema == "FullRange" or bpy.context.scene.iso_render.color_schema==""):
            #Create materialsx
            #Creating the 10 materials to make the degradation
            mat_bur = bpy.data.materials.new('Burdeaux')
            mat_bur.diffuse_color = (0.174563, 0.004221, 0.0208302)
            mat_bur.type='SURFACE'

            mat_red = bpy.data.materials.new('Red')
            mat_red.diffuse_color = (0.8, 0, 0.0414922)
            mat_red.type='SURFACE'

            mat_ora = bpy.data.materials.new('Orange')
            mat_ora.diffuse_color = (0.801, 0.0885, 0.0372)
            mat_ora.type='SURFACE'

            mat_pap = bpy.data.materials.new('Papaya')
            mat_pap.diffuse_color = (0.8, 0.40282, 0)
            mat_pap.type='SURFACE'

            mat_lim = bpy.data.materials.new('Lima')
            mat_lim.diffuse_color = (0.517173, 0.8, 0)
            mat_lim.type='SURFACE'

            mat_gre = bpy.data.materials.new('Green')
            mat_gre.diffuse_color = (0.188, 0.8, 0)
            mat_gre.type='SURFACE'

            mat_tur = bpy.data.materials.new('Turquoise')
            mat_tur.diffuse_color = (0.006, 0.8, 0.366286)
            mat_tur.type='SURFACE'

            mat_sky = bpy.data.materials.new('Skyline')
            mat_sky.diffuse_color = (0, 0.266361, 0.8)
            mat_sky.type='SURFACE'

            mat_blu = bpy.data.materials.new('Blue')
            mat_blu.diffuse_color = (0.001, 0.0521, 0.8)
            mat_blu.type='SURFACE'

            mat_dar = bpy.data.materials.new('DarkBlue')
            mat_dar.diffuse_color = (0.017, 0, 0.8)
            mat_dar.type='SURFACE'

            #materials_vector = ([mat_dar, mat_blu, mat_sky, mat_tur, mat_gre, mat_lim, mat_pap, mat_ora, mat_red, mat_bur])
            materials_vector = ([mat_bur, mat_red, mat_ora, mat_pap, mat_lim, mat_gre, mat_tur, mat_sky, mat_blu, mat_dar])
        
        if (bpy.context.scene.iso_render.color_schema == "MediumRange"):
            #Create materialsx
            #Creating the 10 materials to make the degradation

            mat_ora = bpy.data.materials.new('Orange')
            mat_ora.diffuse_color = (0.801, 0.0885, 0.0372)
            mat_ora.type='SURFACE'

            mat_lio = bpy.data.materials.new('LightOrange')
            mat_lio.diffuse_color = (0.8, 0.45282, 0.01)
            mat_lio.type='SURFACE'

            mat_pap = bpy.data.materials.new('Papaya')
            mat_pap.diffuse_color = (0.8, 0.40282, 0)
            mat_pap.type='SURFACE'

            mat_dye = bpy.data.materials.new('DarkYellow')
            mat_dye.diffuse_color = (0.8, 0.71, 0)
            mat_dye.type='SURFACE'

            mat_yel = bpy.data.materials.new('Yellow')
            mat_yel.diffuse_color = (0.8, 0.68, 0)
            mat_yel.type='SURFACE'

            mat_fli = bpy.data.materials.new('FluorLima')
            mat_fli.diffuse_color = (0.67, 0.8, 0)
            mat_fli.type='SURFACE'

            mat_lim = bpy.data.materials.new('Lima')
            mat_lim.diffuse_color = (0.517173, 0.8, 0)
            mat_lim.type='SURFACE'

            mat_gre = bpy.data.materials.new('Green')
            mat_gre.diffuse_color = (0.188, 0.8, 0)
            mat_gre.type='SURFACE'

            mat_tur = bpy.data.materials.new('Turquoise')
            mat_tur.diffuse_color = (0.006, 0.8, 0.366286)
            mat_tur.type='SURFACE'

            mat_sky = bpy.data.materials.new('Skyline')
            mat_sky.diffuse_color = (0, 0.266361, 0.8)
            mat_sky.type='SURFACE'


            #materials_vector = ([mat_dar, mat_blu, mat_sky, mat_tur, mat_gre, mat_lim, mat_pap, mat_ora, mat_red, mat_bur])
            materials_vector = ([mat_ora, mat_lio, mat_pap, mat_dye, mat_yel, mat_fli, mat_lim, mat_gre, mat_tur, mat_sky])

        if (bpy.context.scene.iso_render.color_schema == "ColdRange"):
            #Create materialsx
            #Creating the 10 materials to make the degradation   

            mat_yel = bpy.data.materials.new('Yellow')
            mat_yel.diffuse_color = (0.8, 0.68, 0)
            mat_yel.type='SURFACE'

            mat_fli = bpy.data.materials.new('FluorLima')
            mat_fli.diffuse_color = (0.67, 0.8, 0)
            mat_fli.type='SURFACE'

            mat_lim = bpy.data.materials.new('Lima')
            mat_lim.diffuse_color = (0.517173, 0.8, 0)
            mat_lim.type='SURFACE'

            mat_gre = bpy.data.materials.new('Green')
            mat_gre.diffuse_color = (0.188, 0.8, 0)
            mat_gre.type='SURFACE'

            mat_tur = bpy.data.materials.new('Turquoise')
            mat_tur.diffuse_color = (0.006, 0.8, 0.366286)
            mat_tur.type='SURFACE'

            mat_lbl = bpy.data.materials.new('LightBlue')
            mat_lbl.diffuse_color = (0.009, 0.75, 0.8)
            mat_lbl.type='SURFACE'

            mat_sky = bpy.data.materials.new('Skyline')
            mat_sky.diffuse_color = (0, 0.266361, 0.8)
            mat_sky.type='SURFACE'

            mat_cbl = bpy.data.materials.new('CoolBlue')
            mat_cbl.diffuse_color = (0.0075, 0.15, 0.8)
            mat_cbl.type='SURFACE'

            mat_blu = bpy.data.materials.new('Blue')
            mat_blu.diffuse_color = (0.001, 0.0521, 0.8)
            mat_blu.type='SURFACE'

            mat_dar = bpy.data.materials.new('DarkBlue')
            mat_dar.diffuse_color = (0.017, 0, 0.8)
            mat_dar.type='SURFACE'

            #materials_vector = ([mat_dar, mat_blu, mat_sky, mat_tur, mat_gre, mat_lim, mat_pap, mat_ora, mat_red, mat_bur])
            materials_vector = ([mat_yel, mat_fli, mat_lim, mat_gre, mat_tur, mat_lbl, mat_sky, mat_cbl, mat_blu, mat_dar])
        

        if (bpy.context.scene.iso_render.color_schema == "HotRange"):
            #Create materialsx
            #Creating the 10 materials to make the degradation
            mat_bur = bpy.data.materials.new('Burdeaux')
            mat_bur.diffuse_color = (0.174563, 0.004221, 0.0208302)
            mat_bur.type='SURFACE'

            mat_dre = bpy.data.materials.new('DarkRed')
            mat_dre.diffuse_color = (0.41, 0.007, 0.009)
            mat_dre.type='SURFACE'

            mat_red = bpy.data.materials.new('Red')
            mat_red.diffuse_color = (0.8, 0, 0.0414922)
            mat_red.type='SURFACE'

            mat_for = bpy.data.materials.new('FullOrange')
            mat_for.diffuse_color = (0.801, 0.0283, 0.042)
            mat_for.type='SURFACE'

            mat_ora = bpy.data.materials.new('Orange')
            mat_ora.diffuse_color = (0.801, 0.0885, 0.0372)
            mat_ora.type='SURFACE'

            mat_lio = bpy.data.materials.new('LightOrange')
            mat_lio.diffuse_color = (0.8, 0.45282, 0.01)
            mat_lio.type='SURFACE'

            mat_pap = bpy.data.materials.new('Papaya')
            mat_pap.diffuse_color = (0.8, 0.40282, 0)
            mat_pap.type='SURFACE'

            mat_dye = bpy.data.materials.new('DarkYellow')
            mat_dye.diffuse_color = (0.8, 0.71, 0)
            mat_dye.type='SURFACE'

            mat_lim = bpy.data.materials.new('Lima')
            mat_lim.diffuse_color = (0.517173, 0.8, 0)
            mat_lim.type='SURFACE'

            mat_gre = bpy.data.materials.new('Green')
            mat_gre.diffuse_color = (0.188, 0.8, 0)
            mat_gre.type='SURFACE'

            #materials_vector = ([mat_dar, mat_blu, mat_sky, mat_tur, mat_gre, mat_lim, mat_pap, mat_ora, mat_red, mat_bur])
            materials_vector = ([mat_bur, mat_dre, mat_red, mat_for, mat_ora, mat_lio, mat_pap, mat_dye, mat_lim, mat_gre])
  

        #Creating the Icospheres that will give the particles the color gradiations as an origin of the material
        ico_creation(materials_vector)

        psys1 = bpy.data.objects['Sphere'].particle_systems[-1]

        #Sets the configuration for the particle system of each emitter
        #configure_particles(psys1)
        psys1.settings.frame_start=bpy.context.scene.frame_current
        psys1.settings.frame_end=bpy.context.scene.frame_current+1
        psys1.settings.lifetime=1000
        psys1.settings.count = particles_number 

        psys1.settings.render_type='GROUP'
        psys1.settings.dupli_group=bpy.data.groups["Ico"]
        psys1.settings.use_group_count = True

        psys1.settings.normal_factor = 0.0
        psys1.settings.factor_random = 0.0
     
        # Physics
        psys1.settings.physics_type = 'NEWTON'
        psys1.settings.mass = 0
        #Takes from GUI the size to scale particles
        particles_selected_size = bpy.context.scene.iso_render.int_box_particles_size
        psys1.settings.particle_size = particles_selected_size #Remember the object scale 0.0001 of the icospheres to not be showed in the visualization
        psys1.settings.use_multiply_size_mass = False
     
        # Effector weights
        ew = psys1.settings.effector_weights
        ew.gravity = 0
        ew.wind = 0


        nombreMesh = "Figura" + str(0)
        me = bpy.data.meshes.new(nombreMesh)

        psys1 = emitter.particle_systems[-1] 

        x_pos = 0
        y_pos = 0
        z_pos = 0
        prob = 0
        cont = 0

        #Use an auxiliar array to work with a variable number of points, 
        #allowing the user to make diferent points simulation with good results
        array_aux = np.zeros((particles_number, 4))
        #Fill the auxiliar array with the data of the original one 
        for point_number in range (0, particles_number):
            array_aux[point_number] = array_3d[0][point_number]

        #Sort the array to place first the particles with more probability
        array_aux = array_aux[np.argsort(array_aux[:,3])]

        for pa in psys1.particles:
            #God´s particle solution
            #if pa.die_time < 500 :
            pa.die_time = 500
            pa.lifetime = 500
            pa.velocity = (0,0,0)
            #3D placement
            x_pos = array_aux[cont][0] 
            y_pos = array_aux[cont][1] 
            z_pos = array_aux[cont][2]
            pa.location = (x_pos,y_pos,z_pos)
            prob = array_aux[cont][3] 
            cont += 1 
        
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1   #Goes one frame forward to show particles clear at rendering MANDATORY


        file_with_binary_data.close()

        bpy.ops.particle.stabilizer()

        #bpy.ops.particle.generation() #Next step, go to particle generation

        return {'FINISHED'}            # this lets blender know the operator finished successfully.




#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles Stabilizer                                                 #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesStabilizer(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.stabilizer"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Stabilization"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Imposible to stabilize particles. Try to Run simulation again")

        #return the name of the emitter wich is asigned to this number by order
        def emitter_system(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            return emitter.particle_systems[-1] 

        path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
        try:
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        N = len(array_3d[0])   #Size of the matrix

        particles_number = bpy.context.scene.iso_render.int_box_n_particulas #Read from the panel 
        
        x_pos = 0
        y_pos = 0
        z_pos = 0
        prob = 0
        cont = 0

        actual_state = bpy.context.scene.iso_render.int_box_state 

        if (actual_state == -1):
            actual_state=0

        object_name = "Sphere"  
        emitter = bpy.data.objects[object_name]  
        psys1 = emitter.particle_systems[-1] 

        particles_number = bpy.context.scene.iso_render.int_box_n_particulas

        #Use an auxiliar array to work with a variable number of points, 
        #allowing the user to make diferent points simulation with good results
        array_aux = np.zeros((particles_number, 4))
        #Fill the auxiliar array with the data of the original one
        for point_number in range (0, particles_number):
            array_aux[point_number] = array_3d[actual_state][point_number]

        array_aux = array_aux[np.argsort(array_aux[:,3])]
        for pa in psys1.particles:
            #God´s particle solution
            #if pa.die_time < 500 :
            pa.die_time = 500
            pa.lifetime = 500
            pa.velocity = (0,0,0)
            #3D placement
            x_pos = array_aux[cont][0] 
            y_pos = array_aux[cont][1] 
            z_pos = array_aux[cont][2]
            pa.location = (x_pos,y_pos,z_pos)
            prob = array_aux[cont][3] 
            cont += 1 


        file_with_binary_data.close()


        #bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1
        return {'FINISHED'}            # this lets blender know the operator finished successfully.

    

#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles forward                                                    #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesForward(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.forward"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Forward"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
    #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Imposible to read from original file. Try to Run simulation again")

        def draw(self, context):
            self.layout.label("Returned to the origin state")

        def sphere_object(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.0' + str(x)]
            if (x >= 100) :
                emitter = bpy.data.objects['Sphere.' + str(x)]
            return emitter


        #Calculates the position of spheres in a state given
        def sphere_placement(state, array_3d):
            actual_state = state
            particles_number = bpy.context.scene.iso_render.int_box_n_particulas

            x_pos = 0
            y_pos = 0
            z_pos = 0

            prob = 0
            cont = 0

            object_name = "Sphere"  
            emitter = bpy.data.objects[object_name]  
            psys1 = emitter.particle_systems[-1]



            #Use an auxiliar array to work with a variable number of points, 
            #allowing the user to make diferent points simulation with good results
            array_aux = np.zeros((particles_number, 4))
            #Fill the auxiliar array with the data of the original one 
            for point_number in range (0, particles_number):
                array_aux[point_number] = array_3d[actual_state][point_number]

            #Sort the array to place first the particles with more probability
            array_aux = array_aux[np.argsort(array_aux[:,3])]

            #With the array sorted the last position is the particle with the biggest probability to appear
            actual_max_prob_value = array_aux[particles_number-1][3]
            #With the array sorted the first position is the particle with less probability to appear
            actual_min_prob_value = array_aux[0][3]

            general_maximum = actual_max_prob_value
            general_minimum = actual_min_prob_value

            for state_array in array_3d:
                maxi = np.max(state_array[:,3])
                mini = np.max(state_array[:,3])

                if (maxi > general_maximum):
                    general_maximum = maxi
                if (mini < general_minimum):
                    general_minimum = mini

            #Obtain an scalated step to distribute the points between the 10 scales of probability
            step_prob = (general_maximum-general_minimum)/10
            prob_using = step_prob

            steps = np.zeros(11)
            actual_step = 9

            for cont_particle in range(particles_number):
                if(array_aux[cont_particle][3] < prob_using):
                    steps[actual_step] += 1
                else:
                    actual_step -= 1
                    prob_using += step_prob 

            #solves the problem with the extra particles not asigned to the last position
            #steps[9] += steps[10]

            bpy.data.objects['Sphere'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Sphere']
            for cont_mat in range(10):
                #Avoid the Ico9_extra problem using "9-"
                bpy.data.objects['Sphere'].particle_systems['Drops'].settings.active_dupliweight_index = 9-cont_mat
                dupli_weights_name = bpy.data.objects['Sphere'].particle_systems['Drops'].settings.active_dupliweight.name
                material_value = bpy.data.objects['Sphere'].particle_systems['Drops'].settings.dupli_weights.get(dupli_weights_name)
                material_value.count = steps[cont_mat]

            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                pa.location = (x_pos,y_pos,z_pos)
                prob = array_aux[cont][3] 
                cont += 1 

            bpy.ops.particle.stabilizer()

        #Take the actual state
        actual_state = bpy.context.scene.iso_render.int_box_state
        
        #Calculate the total of states
        try:
            path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        #First time do this
        if(actual_state == -1):
            #Calculate the coordinates of each particle
            bpy.context.scene.iso_render.int_box_state = 1
            sphere_placement(1, array_3d)
            
        
        else:
            #If is not the last state
            if((actual_state+1) < int(total_states)):
                #Take the name of the Sphere to make the complete name and disable it
                bpy.context.scene.iso_render.int_box_state = actual_state + 1
                sphere_placement(actual_state+1, array_3d)
                
            #If its the last state 
            if((actual_state+1) >= int(total_states)):
                bpy.context.scene.iso_render.int_box_state = 0
                sphere_placement(0, array_3d)
                

        #Goes one frame forward
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1




        return {'FINISHED'}            # this lets blender know the operator finished successfully.



#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles backward                                                   #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesBackward(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.backward"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Backward"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
    #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Imposible to read from original file. Try to Run simulation again")

        def draw(self, context):
            self.layout.label("Returned to the origin state")

        def sphere_object(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.0' + str(x)]
            if (x >= 100) :
                emitter = bpy.data.objects['Sphere.' + str(x)]
            return emitter
 

        #Calculates the position of spheres in a state given
        def sphere_placement(state, array_3d):
            actual_state = state
            particles_number = bpy.context.scene.iso_render.int_box_n_particulas

            x_pos = 0
            y_pos = 0
            z_pos = 0

            prob = 0
            cont = 0

            object_name = "Sphere"  
            emitter = bpy.data.objects[object_name]  
            psys1 = emitter.particle_systems[-1]


            #Use an auxiliar array to work with a variable number of points, 
            #allowing the user to make diferent points simulation with good results
            array_aux = np.zeros((particles_number, 4))
            #Fill the auxiliar array with the data of the original one 
            for point_number in range (0, particles_number):
                array_aux[point_number] = array_3d[actual_state][point_number]

            #Sort the array to place first the particles with more probability
            array_aux = array_aux[np.argsort(array_aux[:,3])]

            #With the array sorted the last position is the particle with the biggest probability to appear
            actual_max_prob_value = array_aux[particles_number-1][3]
            #With the array sorted the first position is the particle with less probability to appear
            actual_min_prob_value = array_aux[0][3]

            general_maximum = actual_max_prob_value
            general_minimum = actual_min_prob_value

            for state_array in array_3d:
                maxi = np.max(state_array[:,3])
                mini = np.max(state_array[:,3])

                if (maxi > general_maximum):
                    general_maximum = maxi
                if (mini < general_minimum):
                    general_minimum = mini

            #Obtain an scalated step to distribute the points between the 10 scales of probability
            step_prob = (general_maximum-general_minimum)/10
            prob_using = step_prob

            steps = np.zeros(11)
            actual_step = 9

            for cont_particle in range(particles_number):
                if(array_aux[cont_particle][3] < prob_using):
                    steps[actual_step] += 1
                else:
                    actual_step -= 1
                    prob_using += step_prob 

            #solves the problem with the extra particles not asigned to the last position
            steps[9] += steps[10]

            bpy.data.objects['Sphere'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Sphere']
            for cont_mat in range(10):
                #Avoid the Ico9_extra problem using "9-"
                bpy.data.objects['Sphere'].particle_systems['Drops'].settings.active_dupliweight_index = 9-cont_mat
                dupli_weights_name = bpy.data.objects['Sphere'].particle_systems['Drops'].settings.active_dupliweight.name
                material_value = bpy.data.objects['Sphere'].particle_systems['Drops'].settings.dupli_weights.get(dupli_weights_name)
                material_value.count = steps[cont_mat]

            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                pa.location = (x_pos,y_pos,z_pos)
                prob = array_aux[cont][3] 
                cont += 1

            bpy.ops.particle.stabilizer()


        #Take the actual state
        actual_state = bpy.context.scene.iso_render.int_box_state
        
        #Calculate the total of states
        try:
            path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')



        #First time do this
        if(actual_state == -1):
            bpy.context.scene.iso_render.int_box_state = total_states - 1
            sphere_placement(total_states-1,array_3d)
            
        else:
            #If is not the last state
            if((actual_state-1) >= 0):
                bpy.context.scene.iso_render.int_box_state = actual_state - 1
                sphere_placement(actual_state-1,array_3d)

            #If its the last state
            if((actual_state-1) < 0):
                bpy.context.scene.iso_render.int_box_state = total_states - 1
                sphere_placement(total_states-1,array_3d)


        #Goes one frame forward
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1


        return {'FINISHED'}            # this lets blender know the operator finished successfully.



#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles calculation                                                #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesCalculation(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particles.calculation"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Calculation"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
        
        def error_message(self, context):
            self.layout.label("Imposible to read psi data from the selected folder.")

        #Set the calculation format, 2D by default
        calculation_format_final = bpy.data.scenes["Scene"].CalculationFormat
        if (calculation_format_final == ''):
            calculation_format_final = '2D'
        #Takes the data from the folder with all psi files
        try:
            path = bpy.context.scene.iso_render.folder_path #Origin from where the data will be readen, selected by the first option in the Panel
            
            psi_files_number=0

            if (calculation_format_final == '2D'):
                while (os.path.isfile(path+ str(psi_files_number) +"psi")):
                    psi_files_number += 1

            if (calculation_format_final == '3D'):
                while (os.path.isfile(path+ "psi_" + str(psi_files_number) + ".pkl")):
                    psi_files_number += 1
            


        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')
    
        #number of 3D points for each step
        number_of_points=bpy.context.scene.iso_render.int_box_particulas_Simulacion
        #3D matrix creation
        matrix_3d = np.zeros((160,number_of_points,4))

        #Data storage matrix
        array_aux = np.zeros((number_of_points, 4))
 

        path=bpy.context.scene.iso_render.folder_path


        #2D calculation    
        if (calculation_format_final == '2D'):
            for cont_file in range(0, 160):

                file_with_binary_data = open(path+ str(cont_file) +"psi", 'rb+') #File with binary data

                array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)

                #Matrix with the data of the 2D grid
                Z = array_with_all_data['arr_0'] 
                
                #cArray.matrix2Dprob(Z, array_aux)

                matrix_3d[cont_file]=array_aux

        #3D calculation 
        if (calculation_format_final == '3D'):
            for cont_file in range(0, 160):

                if (cont_file < 10) : 
                    cont_file_text = "00" + str(cont_file)
                elif (cont_file >= 10 and cont_file < 100) : 
                    cont_file_text = "0" + str(cont_file) 
                else:
                    cont_file_text = str(cont_file)

                file_with_binary_data = open(path+ "psi_" + cont_file_text + ".npz", 'rb+') #File with binary data

                array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)

                #Matrix with the data of the 3D grid
                Z = array_with_all_data['psi'] 

                #cArray.matrix3Dprob(Z, array_aux)

                matrix_3d[cont_file]=array_aux

        
        f = open(path + '3dData.3d', 'wb+')
        np.savez(f, matrix_3d)
        f.close()

        return {'FINISHED'}            # this lets blender know the operator finished successfully.



#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles Cut                                                        #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesCut(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.cut"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Cut"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Imposible to stabilize particles. Try to Run simulation again")

        #return the name of the emitter wich is asigned to this number by order
        def emitter_system(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            return emitter.particle_systems[-1] 

        path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
        try:
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        N = len(array_3d[0])   #Size of the matrix

        particles_number = bpy.context.scene.iso_render.int_box_n_particulas #Read from the panel 
        
        x_pos = 0
        y_pos = 0
        z_pos = 0
        prob = 0
        cont = 0

        actual_state = bpy.context.scene.iso_render.int_box_state 

        if (actual_state == -1):
            actual_state=0

        object_name = "Sphere"  
        emitter = bpy.data.objects[object_name]  
        psys1 = emitter.particle_systems[-1] 

        particles_number = bpy.context.scene.iso_render.int_box_n_particulas

        #Use an auxiliar array to work with a variable number of points, 
        #allowing the user to make diferent points simulation with good results
        array_aux = np.zeros((particles_number, 4))
        #Fill the auxiliar array with the data of the original one
        for point_number in range (0, particles_number):
            array_aux[point_number] = array_3d[actual_state][point_number]

        #Plane info
        #For just 1 plane
        if(bpy.context.scene.iso_render.planes_number == "1P"):
            cut_plane_1= "Cut_plane"
            plane_pos_1 = bpy.data.objects[cut_plane_1].location
            plane_size_1 = bpy.data.objects[cut_plane_1].dimensions

            array_aux = array_aux[np.argsort(array_aux[:,3])]
            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                bpy.context.scene.iso_render.bool_cut_box
                if(x_pos > (plane_pos_1[0])):
                    pa.location = (-10000,-10000,-10000)
                prob = array_aux[cont][3] 
                cont += 1

        #For 2 planes
        if(bpy.context.scene.iso_render.planes_number == "2P"):
            cut_plane_1= "Cut_plane"
            plane_pos_1 = bpy.data.objects[cut_plane_1].location
            plane_size_1 = bpy.data.objects[cut_plane_1].dimensions

            cut_plane_2= "Cut_plane2"
            plane_pos_2 = bpy.data.objects[cut_plane_2].location
            plane_size_2 = bpy.data.objects[cut_plane_2].dimensions

            array_aux = array_aux[np.argsort(array_aux[:,3])]
            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                if(x_pos > plane_pos_1[0] and z_pos > plane_pos_2[2]):
                    pa.location = (-10000,-10000,-10000)
                prob = array_aux[cont][3] 
                cont += 1 

        file_with_binary_data.close()


        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1
        return {'FINISHED'}            # this lets blender know the operator finished successfully.



#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles Projection                                                 #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesProjection(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.projection"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles projection"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Imposible to stabilize particles. Try to Run simulation again")

        #return the name of the emitter wich is asigned to this number by order
        def emitter_system(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            return emitter.particle_systems[-1] 

        path = bpy.context.scene.iso_render.path #Origin from where the data will be readen, selected by the first option in the Panel
        try:
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        N = len(array_3d[0])   #Size of the matrix

        particles_number = bpy.context.scene.iso_render.int_box_n_particulas #Read from the panel 
        
        actual_state = bpy.context.scene.iso_render.int_box_state 

        if (actual_state == -1):
            actual_state=0

        #Deselects all
        bpy.ops.object.select_all(action='DESELECT')

        bpy.data.objects['Sphere'].select = True
        bpy.context.scene.objects.active = bpy.data.objects['Sphere'] 

        emitter = bpy.data.objects['Sphere_projections']  
        psys1 = emitter.particle_systems[-1] 

        particles_number = bpy.context.scene.iso_render.int_box_n_particulas

        #Use an auxiliar array to work with a variable number of points, 
        #allowing the user to make diferent points simulation with good results
        array_aux = np.zeros((particles_number, 4))
        #Fill the auxiliar array with the data of the original one
        for point_number in range (0, particles_number):
            array_aux[point_number] = array_3d[actual_state][point_number]


        proj_plane_1= "Project_plane"
        plane_pos_1 = bpy.data.objects[proj_plane_1].location
        plane_size_1 = bpy.data.objects[proj_plane_1].dimensions

        array_aux = array_aux[np.argsort(array_aux[:,3])]

        bpy.ops.object.select_all(action='DESELECT')

        #Distance from the original object
        offset_xy = 0
        offset_z = 0

        try:
            bpy.data.objects['Axis_XYZ'].select = True
            bpy.context.scene.objects.active = bpy.data.objects['Axis_XYZ'] 
            #X and Y should be at the same spacial point, so the ofsett of any asis will be the same
            offset_xy = bpy.context.object.location[0]
            offset_z = -1 * (bpy.context.object.scale[2] + ( -1 * bpy.context.object.location[2]))

        except:
            offset_xy = -1 * bpy.context.scene.iso_render.int_box_offset
            offset_z = -1 * bpy.context.scene.iso_render.int_box_offset




        x_pos = 0
        y_pos = 0
        z_pos = 0
        prob = 0
        cont = 0

        if (bpy.context.scene.iso_render.planes_project == "X"):
            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                prob = array_aux[cont][3]
                if((x_pos > plane_pos_1[0] - 0.5) and (x_pos < plane_pos_1[0] + 0.5)):
                    pa.location = (offset_xy , y_pos, z_pos)
                else:
                    pa.location = (0,0,0)
                cont += 1 


        if (bpy.context.scene.iso_render.planes_project == "Y"):
            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                prob = array_aux[cont][3]
                if((y_pos > plane_pos_1[1] - 0.5) and (y_pos < plane_pos_1[1] + 0.5)):
                    pa.location = (x_pos, offset_xy, z_pos)
                else:
                    pa.location = (-10000,-10000,-10000)
                cont += 1 

        if (bpy.context.scene.iso_render.planes_project == "Z"):
            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                prob = array_aux[cont][3]
                if((z_pos > plane_pos_1[2] - 0.5) and (z_pos < plane_pos_1[2] + 0.5)):
                    pa.location = (x_pos, y_pos, offset_z)
                else:
                    pa.location = (-10000,-10000,-10000)
                cont += 1 

        if (bpy.context.scene.iso_render.planes_project == "XZ"):

            #X
            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                prob = array_aux[cont][3]
                if((x_pos > plane_pos_1[0] - 0.5) and (x_pos < plane_pos_1[0] + 0.5)):
                    pa.location = (offset_xy, y_pos, z_pos)
                else:
                    pa.location = (-10000,-10000,-10000)
                cont += 1 

            #Z
            proj_plane_2= "Project_plane_2"
            plane_pos_2 = bpy.data.objects[proj_plane_2].location
            plane_size_2 = bpy.data.objects[proj_plane_2].dimensions
            emitter = bpy.data.objects['Sphere_projections_2']  
            psys1 = emitter.particle_systems[-1] 
            cont = 0

            for pa in psys1.particles:
                #God´s particle solution
                #if pa.die_time < 500 :
                pa.die_time = 500
                pa.lifetime = 500
                pa.velocity = (0,0,0)
                #3D placement
                x_pos = array_aux[cont][0] 
                y_pos = array_aux[cont][1] 
                z_pos = array_aux[cont][2]
                prob = array_aux[cont][3]
                if((z_pos > plane_pos_2[2] - 0.5) and (z_pos < plane_pos_2[2] + 0.5)):
                    pa.location = (x_pos, y_pos, offset_z)
                else:
                    pa.location = (-10000,-10000,-10000)
                cont += 1 


        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1
        return {'FINISHED'}            # this lets blender know the operator finished successfully.




#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Split Screen code                                                    #
# ----------------------------------------------------------------------- #
#*************************************************************************# 


class AREATYPE_OT_split(bpy.types.Operator):
    bl_idname = "areatype.splitview"
    bl_label = "areatype.splitview"
    def execute(self,context):
        thisarea = context.area
        otherarea = None
        tgxvalue = thisarea.x + thisarea.width + 1
        thistype = context.area.type
        arealist = list(context.screen.areas)
        for area in context.screen.areas:
            if area == thisarea:
                continue
            elif area.x == tgxvalue and area.y == thisarea.y:
                otherarea = area
                break
        if otherarea:
            bpy.ops.screen.area_join(min_x=thisarea.x,min_y=thisarea.y,max_x=otherarea.x,max_y=otherarea.y)
            bpy.ops.screen.screen_full_area()
            bpy.ops.screen.screen_full_area()
            return {"FINISHED"}
        else:
            context.area.type = "VIEW_3D"
            areax = None
            bpy.ops.screen.area_split(direction="VERTICAL")
            bpy.ops.screen.area_split(direction="HORIZONTAL")
            for area in context.screen.areas:
                if area not in arealist:
                    areax = area
                    break
            if areax:
                areax.type = thistype
                return {"FINISHED"}
        return {"CANCELLED"}


    def viewdraw(self,context):
        layout = self.layout
        layout.operator("areatype.splitview",text="",icon="COLOR_BLUE")




############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
#
#    __    __  __    __          _______   ________   ______   ______   ______  ________  ________  _______  
#   |  \  |  \|  \  |  \        |       \ |        \ /      \ |      \ /      \|        \|        \|       \ 
#   | $$  | $$| $$\ | $$        | $$$$$$$\| $$$$$$$$|  $$$$$$\ \$$$$$$|  $$$$$$\\$$$$$$$$| $$$$$$$$| $$$$$$$\
#   | $$  | $$| $$$\| $$ ______ | $$__| $$| $$__    | $$ __\$$  | $$  | $$___\$$  | $$   | $$__    | $$__| $$
#   | $$  | $$| $$$$\ $$|      \| $$    $$| $$  \   | $$|    \  | $$   \$$    \   | $$   | $$  \   | $$    $$
#   | $$  | $$| $$\$$ $$ \$$$$$$| $$$$$$$\| $$$$$   | $$ \$$$$  | $$   _\$$$$$$\  | $$   | $$$$$   | $$$$$$$\
#   | $$__/ $$| $$ \$$$$        | $$  | $$| $$_____ | $$__| $$ _| $$_ |  \__| $$  | $$   | $$_____ | $$  | $$
#    \$$    $$| $$  \$$$        | $$  | $$| $$     \ \$$    $$|   $$ \ \$$    $$  | $$   | $$     \| $$  | $$
#     \$$$$$$  \$$   \$$         \$$   \$$ \$$$$$$$$  \$$$$$$  \$$$$$$  \$$$$$$    \$$    \$$$$$$$$ \$$   \$$
#   
#
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
 
def register():
    bpy.utils.register_class(RenderPropertySettings)
    bpy.types.Scene.iso_render = PointerProperty(type=RenderPropertySettings)
    bpy.utils.register_class(RenderProperties)

    #Panels
    bpy.utils.register_class(PanelStartingParameters)
    bpy.utils.register_class(PanelDataSelection)
    bpy.utils.register_class(PanelStates)
    bpy.utils.register_class(PanelSaveFiles)
    bpy.utils.register_class(PanelTemplate)
    bpy.utils.register_class(PanelCut)
    bpy.utils.register_class(PanelProject)
    bpy.utils.register_class(PanelRenderData)

    #Classes
    bpy.utils.register_class(OBJECT_OT_AddColors)
    bpy.utils.register_class(OBJECT_OT_ResetButton)
    bpy.utils.register_class(OBJECT_OT_RenderButton)
    bpy.utils.register_class(OBJECT_OT_RenderAllButton)
    bpy.utils.register_class(OBJECT_OT_RenderAllProjButton)
    bpy.utils.register_class(OBJECT_OT_RenderAllCutButton)
    bpy.utils.register_class(OBJECT_OT_RenderAllFrame)
    bpy.utils.register_class(OBJECT_OT_RenderVideoButton)
    bpy.utils.register_class(OBJECT_OT_CameraPlacement)
    bpy.utils.register_class(OBJECT_OT_CameraPlacement2)
    bpy.utils.register_class(OBJECT_OT_PlanePlacement)
    bpy.utils.register_class(OBJECT_OT_PlaneDelete)
    bpy.utils.register_class(OBJECT_OT_PlanePlacementProject)
    bpy.utils.register_class(OBJECT_OT_PlaneDeleteProject)
    bpy.utils.register_class(OBJECT_OT_Template_1)
    bpy.utils.register_class(OBJECT_OT_Template_2)
    bpy.utils.register_class(OBJECT_OT_Template_3)
    bpy.utils.register_class(OBJECT_OT_Template_4)
    bpy.utils.register_class(OBJECT_OT_Split_Screen)
    bpy.utils.register_class(OBJECT_OT_Initial_Object)
    bpy.utils.register_class(OBJECT_OT_Initial_Object2)
    bpy.utils.register_class(OBJECT_OT_Export_Parameters)
    bpy.utils.register_class(OBJECT_OT_SaveThisFiles)
    bpy.utils.register_class(OBJECT_OT_SaveAllFiles)

    #QMBlender base classes
    bpy.utils.register_class(ParticleCalculator)
    bpy.utils.register_class(ParticlesStabilizer)
    bpy.utils.register_class(ParticlesForward)
    bpy.utils.register_class(ParticlesBackward)
    bpy.utils.register_class(ParticlesCalculation)
    bpy.utils.register_class(ParticlesCut)
    bpy.utils.register_class(ParticlesProjection)
    bpy.utils.register_class(AREATYPE_OT_split)

 
def unregister():
    bpy.utils.unregister_class(RenderPropertySettings)
    bpy.utils.unregister_class(RenderProperties)

    #Panels
    bpy.utils.unregister_class(PanelStartingParameters)
    bpy.utils.unregister_class(PanelDataSelection)
    bpy.utils.unregister_class(PanelStates)
    bpy.utils.unregister_class(PanelSaveFiles)
    bpy.utils.unregister_class(PanelTemplate)   
    bpy.utils.unregister_class(PanelCut)
    bpy.utils.unregister_class(PanelProject)
    bpy.utils.unregister_class(PanelRenderData)

    #Classes
    bpy.utils.unregister_class(OBJECT_OT_AddColors)
    bpy.utils.unregister_class(OBJECT_OT_ResetButton)
    bpy.utils.unregister_class(OBJECT_OT_RenderButton)
    bpy.utils.unregister_class(OBJECT_OT_RenderAllButton)
    bpy.utils.unregister_class(OBJECT_OT_RenderAllProjButton)
    bpy.utils.unregister_class(OBJECT_OT_RenderAllCutButton)
    bpy.utils.unregister_class(OBJECT_OT_RenderAllFrame)
    bpy.utils.unregister_class(OBJECT_OT_RenderVideoButton)
    bpy.utils.unregister_class(OBJECT_OT_CameraPlacement)
    bpy.utils.unregister_class(OBJECT_OT_CameraPlacement2)
    bpy.utils.unregister_class(OBJECT_OT_PlanePlacement)
    bpy.utils.unregister_class(OBJECT_OT_PlaneDelete)
    bpy.utils.unregister_class(OBJECT_OT_PlanePlacementProject)
    bpy.utils.unregister_class(OBJECT_OT_PlaneDeleteProject)
    bpy.utils.unregister_class(OBJECT_OT_Template_1)
    bpy.utils.unregister_class(OBJECT_OT_Template_2)
    bpy.utils.unregister_class(OBJECT_OT_Template_3)
    bpy.utils.unregister_class(OBJECT_OT_Template_4)
    bpy.utils.unregister_class(OBJECT_OT_Split_Screen)
    bpy.utils.unregister_class(OBJECT_OT_Initial_Object)
    bpy.utils.unregister_class(OBJECT_OT_Initial_Object2)
    bpy.utils.unregister_class(OBJECT_OT_Export_Parameters)
    bpy.utils.unregister_class(OBJECT_OT_SaveThisFiles)
    bpy.utils.unregister_class(OBJECT_OT_SaveAllFiles)
    
    #QMBlender base classes
    bpy.utils.unregister_class(ParticleCalculator)
    bpy.utils.unregister_class(ParticlesStabilizer)
    bpy.utils.unregister_class(ParticlesForward)
    bpy.utils.unregister_class(ParticlesBackward)
    bpy.utils.unregister_class(ParticlesCalculation)
    bpy.utils.unregister_class(ParticlesCut)
    bpy.utils.unregister_class(ParticlesProjection)
    bpy.utils.unregister_class(AREATYPE_OT_split)
    


if __name__ == "__main__" :
    register()