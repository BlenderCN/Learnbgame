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

import bpy, random, string, time, os
from bpy.types import Panel, Operator, Menu
from bpy.app.handlers import persistent, frame_change_pre
from bpy.props import *
from math import *

# Add-on info
bl_info = {
    "name": "TextFX",
    "author": "Monaime Zaim (CodeOfArt.com)",
    "version": (1, 0, 1),
    "blender": (2, 7, 8),
    "location": "View3D > Tools > TextFX",
    "description": "Text animation tools", 
    "wiki_url": "http://codeofart.com/text-fx/",
    "tracker_url": "http://codeofart.com/text-fx/",      
    "category": "Learnbgame"
}


################################################
################# Functions ####################
################################################


####################### Easing formulas ###############################
# t: Time evaluation (increment)
# b: Start value
# c: End value (in my case = end value - start value)
# d: Duration
# for example if the animation will start at the frame 1 and end 
# at the frame 50 the duration will be 49 = (50-1) and "t" must
# increment from 0 to 49, or you can use a linear interpolation [0..1]
# i have used a linear interpolation, see the "wiggle" fuction

def easeInOutSine(t, b, c, d):
    return -c/2 * (cos(pi*t/d) - 1) + b        
    
def easeInQuart(t, b, c, d):
    t /= d
    return c*t*t*t*t + b

def easeInOutQuart(t, b, c, d):
    t /= d/2
    if t < 1:
        return c/2*t*t*t*t + b
    t -= 2
    return -c/2 * (t*t*t*t - 2) + b

linearTween = lambda t, b, c, d : c*t/d + b

def easeInOutCirc(t, b, c, d):
    t /= d/2
    if t < 1:
        return -c/2 * (sqrt(1 - t*t) - 1) + b
    t -= 2
    return c/2 * (sqrt(1 - t*t) + 1) + b

def easeOutElastic(t, b, c, d):
    ts=(t/d)*t
    tc=ts*t
    return b+c*(46*tc*ts + -155*ts*ts + 190*tc + -100*ts + 20*t)

def easeInElastic(t, b, c, d):
    ts=(t/d)*t
    tc=ts*t
    return b+c*(33*tc*ts + -59*ts*ts + 32*tc + -5*ts)

def easeInCubic(t, b, c, d):
    tc=(t/d)*t*t
    return b+c*(tc)

def easeOutQuintic(t, b, c, d):
    ts=(t/d)*t
    tc=ts*t
    return b+c*(tc*ts + -5*ts*ts + 10*tc + -10*ts + 5*t)

def easeOutBackQuartic(t, b, c, d):
    ts=(t/d)*t
    tc=ts*t
    return b+c*(-2*ts*ts + 10*tc + -15*ts + 8*t)

def easeInBackQuartic(t, b, c, d):
    ts=(t/d)*t
    tc=ts*t
    return b+c*(2*ts*ts + 2*tc + -3*ts)

def easeOutInCubic(t, b, c, d):
    ts=(t/d)*t
    tc=ts*t
    return b+c*(4*tc + -6*ts + 3*t)

def easeInOutElastic(t, b, c, d):
    ts=(t/d)*t
    tc=ts*t
    return b+c*(-74*tc*ts + 195*ts*ts + -170*tc + 50*ts)

# List of available easing formulas
def easing_list(self, context):
    ease_list = ['easeInOutSine', 'linearTween', 'easeInBackQuartic', 'easeInCubic', 
                 'easeInElastic', 'easeInOutCirc', 'easeInOutElastic', 'easeInOutQuart', 
                 'easeInQuart', 'easeOutBackQuartic', 'easeOutElastic', 'easeOutInCubic', 
                 'easeOutQuintic']
    return [(i, i, '') for i in ease_list]
                 

###########################################################################

####################### Fcurves effects (Kinetic) #######################

# Overshoot effect
def overshoot(t, velocity, amplitude, frequency, duration):
    if t > 0 and t < duration:
        dur = (t-1)/(duration - 2)
        decay = velocity * amplitude *(sin((pi/2)*(1+(t-1)/(1+frequency))) * (1-dur))      
    else:
        decay = 0    
    return decay

# Bounce effect
def bounce(t, velocity, amplitude, e, duration, g = -10):
    
    def set_bounce_parametrs(t, dur, e):
        x = 0
        segments = [0]
        n = dur/e
        int_time = 0
        elasticity = 0
        
        for i in range(5):    
            if x+round((n/(e**(i)))) < x+2:       
                x+=2
            else:
                x+= round(n/(e**(i)))
            if dur-x <= 2:
                x = dur    
            segments.append(x)      
        for j, s in enumerate(segments):
            if t > s and j < len(segments):
                if t <= max(segments):
                    start = s
                    end = segments[j+1]
                    int_time = (t-start)/(end-start)
                    elasticity = 1/(e**j)                   
        return (int_time, elasticity)
    
    decay=0 
    if t > 0:           
        v=10     
        t1, elasticity = set_bounce_parametrs(t, duration, e)                      
        decay = amplitude * (((g)*((t1)**2)) + (v*t1))
        if decay <= 0:
            decay = 0 
        decay*=elasticity      
    else: decay = 0           
    decay*=(-velocity)
    return decay

###########################################################################


# Get object name
def get_obj_name(name):
    if bpy.data.objects.get(name) is None:
        return name
    i = 1
    while bpy.data.objects.get(name + str(i)) is not None:
        i += 1
    return name + str(i)

# add a property
def add_prop(obj, name, value, min, max, description):
    obj[name] = value
    if '_RNA_UI' not in obj.keys():
        obj['_RNA_UI'] = {}
    obj['_RNA_UI'][name] = {"min": min, "max": max ,"description": description}
           
    
# add a property variable to the driver
def add_prop_var(driver, name, id_type, id, path):
    var = driver.driver.variables.new()
    var.name = name
    var.type = 'SINGLE_PROP'
    var.targets[0].id_type = id_type
    var.targets[0].id = id
    var.targets[0].data_path = path
      
# list of texts
def texts(self, context):
    return [(text.name, text.name, '') for text in bpy.data.texts]

# list of fonts
def fonts(self, context):
    return [(text.name, text.name, '') for text in bpy.data.fonts] 

# list of audio files
def sounds(self, context):
    scn = context.scene
    prefix = 'TextFX_Audio_'
    return [(s.replace(prefix, ''), s.replace(prefix, ''), '') for s in scn.keys() if prefix in s]  

# Setup the font (Simple text)
def setup_font():    
    bpy.ops.object.text_add()
    font = bpy.context.object
    font.name = get_obj_name('TFX_Simple')           
    add_prop(font, 'TEXTFX_FONT', 0.0, 0.0, 1.0, '')
    add_prop(font, 'start_frame', 1, 1, 1000000, 'First frame of the animation')    
    add_prop(font, 'typewriter_start_frame', 1, 1, 1000000, 'First frame of the animation')    
    add_prop(font, 'scramble_start_frame', 1, 1, 1000000, 'First frame of the animation')    
    add_prop(font, 'timer_start_frame', 1, 1, 1000000, 'First frame of the animation')    
    add_prop(font, 'read_lines_start_frame', 1, 1, 1000000, 'First frame of the animation')    
    add_prop(font, 'start_number', 0.0, -1000000.0, 1000000.0, 'Start number')
    add_prop(font, 'end_number', 100.0, -1000000.0, 1000000.0, 'End number')
    add_prop(font, 'speed', 3, 1, 100, 'Speed of the animation (in Frames)')
    add_prop(font, 'typewriter_speed', 3, 1, 100, 'Speed of the animation (in Frames)')
    add_prop(font, 'scramble_speed', 3, 1, 100, 'Speed of the animation (in Frames)')    
    add_prop(font, 'scramble_seed', 1, 1, 100000, 'Random seed')    
    add_prop(font, 'read_lines_speed', 3, 1, 100, 'Speed of the animation (in Frames)')
    add_prop(font, 'text', 'Text FX', 0.0, 1.0, 'Enter your text here')    
    add_prop(font, 'scramble_text', 'Text FX', 0.0, 1.0, 'Enter your text here')    
    add_prop(font, 'read_lines_text', '', 0.0, 1.0, 'Enter your text here')    
    add_prop(font, 'before', '', 0.0, 1.0, 'This text will apear before the number')    
    add_prop(font, 'after', '', 0.0, 1.0, 'This text will apear after the number')
    add_prop(font, 'increment_by', 1.0, -10000000.0, 10000000.0, 'Increment by')    
    add_prop(font, 'decimals', 0, 0, 5, 'Decimals')    
    add_prop(font, 'cursor', '|', 0.0, 1.0, 'Cursor')    
    add_prop(font, 'cursor_start_frame', 1, 1, 100000, 'First frame of the cursor animation')    
    add_prop(font, 'cursor_speed', 20, 0, 100, 'Speed of the cursor blinking, 0 = No blinking')    
    add_prop(font, 'seconds', 1, 0, 59, 'Seconds')  
    add_prop(font, 'minutes', 1, 0, 59, 'Minutes')  
    add_prop(font, 'hours', 1, 0, 23, 'Hours')  
    add_prop(font, 'timer_inc', 1, -1, 1, 'Incrementation, 0 = disabled')
    font.text_fx_enabled = True
    font.simple_effect = 'None'
    font.typewriting_affect = 'Letters'
    font.scramble_affect = 'Letters'
    font.timer_format = 'hh:mm:ss'    
    font.scramble_char_type = 'Same'
    
# Create the parent (controller) for advanced text
def add_parent():
    bpy.context.scene['TextFX_Audio_None'] = 0.0
    bpy.ops.object.empty_add(type='SPHERE', radius = 0.25)
    parent = bpy.context.object
    parent.name = get_obj_name('TFX_Controller')
    parent['Advanced_Font_FX'] = 0    
    parent['Advanced_Font_Offset'] = 0    
    add_prop(parent, 'Text', 'Text FX', 0.0, 1.0, 'Text')    
    add_prop(parent, 'spacing', 0.07, -10.0, 10.0, 'Space between characters')
    add_prop(parent, 'offset_source', '', 0.0, 1.0, 'Source object for the animation offset')
    add_prop(parent, 'offset_speed', 3, 0, 100, 'Speed of the offset (0 = no offset)')    
    add_prop(parent, 'wave_speed', 2.0, 0.5, 20.0, 'Speed of the wave')
    add_prop(parent, 'wave_amplitude', 1.0, 0.0, 10.0, 'Factor, 0 = No effect')
    add_prop(parent, 'wave_frequency', 0.5, -5.0, 1.0, 'Length of the wave.')
    add_prop(parent, 'wave_audio_influence', 1.0, 0.0, 100.0, 'Influence of the audio amplitude')
    add_prop(parent, 'wave_audio_min', 0.0, 0.0, 10.0, 'Minimum value for the amplitude of the audio')
    add_prop(parent, 'wiggle_speed', 2, 1, 200, 'Wiggle speed')    
    add_prop(parent, 'wiggle_factor', 0.05, 0.0, 20.0, 'Factor, 0 = No effect')
    add_prop(parent, 'wiggle_seed', 1, 1, 100000, 'Random seed')
    add_prop(parent, 'wiggle_audio_influence', 1.0, 0.0, 100.0, 'Influence of the audio amplitude')
    add_prop(parent, 'wiggle_audio_min', 0.0, 0.0, 10.0, 'Minimum value for the amplitude of the audio')
    add_prop(parent, 'copy_factor', 1.0, 0.0, 10.0, 'Factor, 0 = No effect')
    add_prop(parent, 'copy_looping_offset', 2, 1, 100.0, 'Delay between iterations, (in Frames)')
    add_prop(parent, 'copy_audio_influence', 1.0, 0.0, 100.0, 'Influence of the audio amplitude')
    add_prop(parent, 'copy_audio_min', 0.0, 0.0, 10.0, 'Minimum value for the amplitude of the audio')
    add_prop(parent, 'copy_start', 1, 1, 100000, 'Start frame of the effect')
    add_prop(parent, 'seed', 1, 1, 10000, 'Random seed')
    add_prop(parent, 'bake_start_frame', 1, 0, 1000000, 'Start frame for baking')
    add_prop(parent, 'bake_end_frame', 250, 1, 1000000, 'End frame for baking')
    add_prop(parent, 'low_frequency', 0.0, 0.0, 100000.0, 'Cutoff frequency of a high-pass filter that is applied to the audio data')
    add_prop(parent, 'high_frequency', 100000.0, 0.0, 100000.0, 'Cutoff frequency of a low-pass filter that is applied to the audio data')
    parent.offset_order = 'Left'
    parent.wave_axis = (False, False, False)
    parent.wiggle_axis = (False, False, False)
    parent.text_layers = parent.layers
    parent.advanced_text_fx_enabled = False
    parent.wave_use_audio = False    
    parent.copy_use_audio = False        
    parent.wiggle_use_audio = False
    parent.wiggle_ease = 'linearTween'
    parent.copy_kinetic = 'None'
    parent.sounds = 'None'
    add_prop(parent, 'offset', 0.0, -1.0, 1.0, 'Offset the curve to adjust the width of a text')
    add_prop(parent, 'extrude', 0.0, 0.0, 1000.0, 'Amount of curve extrusion when not using a bevel object')
    add_prop(parent, 'depth', 0.0, 0.0, 1000.0, 'Bevel depth when not using a bevel object')
    add_prop(parent, 'resolution', 0, 0, 32, 'Bevel resolution when depth is non-zero and no specific bevel object has been defined')
    add_prop(parent, 'shear', 0.0, -1.0, 1.0, 'Italic angle of the characters')
    add_prop(parent, 'overshoot_amp', 1.0, 1.0, 100.0, 'Amplitude of the overshoot effect.')
    add_prop(parent, 'overshoot_freq', 0.6, 0.0, 20.0, 'Increase or decrease the number of bounces.')
    add_prop(parent, 'overshoot_dur', 24, 6, 240, 'Duration of the effect.')
    
    add_prop(parent, 'bounce_amp', 1.0, 1.0, 100.0, 'Amplitude of the bounce effect.')
    add_prop(parent, 'bounce_ela', 2.0, 1.0, 5.0, 'Increase or decrease the number of bounces.')
    add_prop(parent, 'bounce_dur', 24, 6, 240, 'Duration of the effect.')
    return parent

# Create a letter for the advanced text
def add_char(parent):
    bpy.ops.object.text_add()
    char = bpy.context.object
    char.name = get_obj_name('TFX_Char')
    char['TextFX'] = ''
    add_prop(char, 'x', 0.0, -50.0, 50.0, '')
    add_prop(char, 'y', 0.0, -50.0, 50.0, '')
    
    driver = char.data.driver_add('offset')
    add_prop_var(driver, 'offset', 'OBJECT', parent, '["offset"]')
    driver.driver.expression = 'offset'
    
    driver = char.data.driver_add('extrude')
    add_prop_var(driver, 'extrude', 'OBJECT', parent, '["extrude"]')
    driver.driver.expression = 'extrude'
            
    driver = char.data.driver_add('bevel_depth')
    add_prop_var(driver, 'depth', 'OBJECT', parent, '["depth"]')
    driver.driver.expression = 'depth'
    
    driver = char.data.driver_add('bevel_resolution')
    add_prop_var(driver, 'res', 'OBJECT', parent, '["resolution"]')
    driver.driver.expression = 'res'
    
    driver = char.data.driver_add('shear')
    add_prop_var(driver, 'shear', 'OBJECT', parent, '["shear"]')
    driver.driver.expression = 'shear'
    
    return char
 
# Setup advanced Text     
def setup_advanced_font(text = 'Text FX', action = 'Create'):
    if text == '':
        text = 'Text FX'
    scn = bpy.context.scene
    obj = scn.objects
    cursor_location = (scn.cursor_location.x, scn.cursor_location.y, scn.cursor_location.z)    
    if action == 'Update':
        parent = bpy.context.object
        scn.cursor_location = obj.active.location
        delete_text('update')
    else: parent = add_parent()        
        
    text2 = text.replace(' ', '-')        
    loc = 0   
    
    for t, t2, i in zip(text, text2, range(len(text))):        
        ob = add_char(parent)
        ob.data.body = t2
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        ob.data.offset_y = 0.0
        bpy.ops.object.empty_add(type='CUBE', radius=0.00)
        empty = bpy.context.object
        empty['TextFX'] = ''
        empty.hide = True         
        empty.hide_select = True         
        ob.parent = empty
        ob.location = (0.0,0.0,0.0)
        empty.parent = parent    
        empty.location = (0.0,0.0,0.0)
        driver = empty.driver_add('location', 0)
        add_prop_var(driver, 'spacing', 'OBJECT', parent, '["spacing"]')        
        driver.driver.expression = str(loc + (ob.dimensions.x/2)) + '+ spacing * ' + str(i)
        loc+= ob.dimensions.x
        ob.data.body = t
        ob['x'] = ob.data.offset_x
    for ob in obj:
        ob.select = False
    parent.select = True
    parent.offs_x = 0.0
    parent.offs_y = 0.0     
    obj.active = parent
    parent['Text'] = text    
    scn.cursor_location = cursor_location
    
        
# Delete advanced text
def delete_text(action = 'delete'):
    parent = bpy.context.object
    empties = parent.children
    scn = bpy.context.scene
    obj = scn.objects
    if len(empties) >0:
        for empty in empties:
            texts = empty.children
            for text in texts:
                obj.unlink(text)
                bpy.data.objects.remove(text)
            obj.unlink(empty) 
            bpy.data.objects.remove(empty)
    if action == 'delete':
        obj.unlink(parent)
        bpy.data.objects.remove(parent)
    
# calculate spacing
def calculate_spacing():
    parent = bpy.context.object
    scn = bpy.context.scene
    obj = scn.objects
    space = False    
    x = 0
    if parent.scale.x >0:
        if len(parent.children) >0:   
            for i, e in enumerate(parent.children) :
                if 'TextFX' in e.keys():
                    if e.children[0].type == 'FONT' and 'TextFX' in e.children[0].keys():
                        e.children[0].data.font = bpy.data.fonts[scn.fonts]
                        if e.children[0].data.body == ' ':
                            e.children[0].data.body ='-'
                            space = True            
                        x += e.children[0].dimensions.x/2 / parent.scale.x
                        e.animation_data.drivers[0].driver.expression = str(x) + '+spacing*'+str(i)
                        obj.active = e.children[0]
                        for ob in obj:
                            ob.select = False
                        e.children[0].select = True        
                        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') 
                        e.children[0].location = (0,0,0)
                        x+= e.children[0].dimensions.x/2/ parent.scale.x
                        e.children[0].data.offset_y = 0.0
                        e.children[0]['y'] = 0.0
                        e.children[0]['x'] = e.children[0].data.offset_x
                        if space:
                            e.children[0].data.body = ' '
                        space = False    
                    obj.active = parent
                    for ob in obj:
                        ob.select = False
                    parent.select = True
                    parent.offs_x = 0.0
                    parent.offs_y = 0.0                
    else:
        print('Scale of the controller must be greater than zero to perform this operation') 
        
# Get available fcurves (loc, rot, scale)
def avail_fcurves(OBname):
    scn = bpy.context.scene
    obj = scn.objects
    ob = obj[OBname]
    fcs = []
    index = []
    if hasattr(ob.animation_data, 'action'):
        if hasattr(ob.animation_data.action, 'fcurves'):                    
            fc = ob.animation_data.action.fcurves            
            for i in range(len(fc)):
                if fc[i].data_path in ['location', 'rotation_euler', 'scale']:
                    fcs.append(fc[i].data_path + str(fc[i].array_index))
                    index.append(i)
    return (fcs, index)

# get the list of keyframe points -- return the frame and correspanding value
def get_keyframes(obj, fc_index):    
    kf = []
    v = []
    fc = obj.animation_data.action.fcurves    
    for k in fc[fc_index].keyframe_points:
        kf.append(k.co[0])
        v.append(k.co[1])
        
    return (kf, v) 

# get the last active keyframe
def get_last_active_frame(OBname, fc_index, frame):
    kf, v = get_keyframes(OBname, fc_index)    
    last_kf = max(kf)    
    if len(kf) > 1:        
        if frame > kf[1] and frame <= max(kf):
            for k in range(1,len(kf)):
                if frame > kf[k] :
                    last_kf = kf[k]                   
    return last_kf                         

# get the type of a letter
def char_type(char):
    type = ''
    if char.islower():
        type = string.ascii_lowercase
    elif char.isupper():
        type = string.ascii_uppercase
    elif char.isdigit():
        type = string.digits
    elif char.isspace():
        type = ' '            
    else : type = string.punctuation
    
    return type    

# generate random text 
def random_chars(text, type, seed):
    random.seed(seed)
    i = ''    
    if type == 'Same':
        random_slice = i.join(random.choice(char_type(i)) for i in text)
    elif type == 'Digits':
        random_slice = i.join(random.choice(string.digits) for i in text)
    elif type == 'Letters':
        random_slice = i.join(random.choice(string.ascii_letters) for i in text)    
    elif type == 'Lower case':
        random_slice = i.join(random.choice(string.ascii_lowercase) for i in text)
    elif type == 'Upper case':
        random_slice = i.join(random.choice(string.ascii_uppercase) for i in text)
    elif type == 'Punctuation':
        random_slice = i.join(random.choice(string.punctuation) for i in text)
    else:
        random_slice = i.join(random.choice(string.printable[0:68]+string.printable[69:94]) for i in text)                           
    return random_slice

# combine a list of lines into one string
def combine_lines(list):
    text = ''
    for line in list:
        text += (line+'\n')
    return text  

# increment effect (numbers animation) 
def increment(start_frame, start_number, end_number, before, after, speed, inc, dec, cur_frame):
    body = ''   
    if cur_frame > start_frame:
        slice = (cur_frame-start_frame)//speed
        if dec >0:
            decimals = '%.' + str(dec) + 'f' 
            body = before + (str(decimals % end_number) if (
            (((slice*inc)+(start_number) > end_number) and (inc > 0)) or (((slice*inc)+(start_number) < end_number) and (inc < 0))
            ) else str(decimals % ((slice*inc)+(start_number)))) + after        
        else: body = before + (str(int(end_number)) if (
              (((slice*inc)+(start_number) > end_number) and (inc > 0)) or (((slice*inc)+(start_number) < end_number) and (inc < 0))
              ) else str(int((slice*inc)+(start_number)))) + after              
            
    elif cur_frame == start_frame:
        if dec >0:
            decimals = '%.' + str(dec) + 'f' 
            body = before + str(decimals % start_number) + after        
        else:
            body = before + str(int(start_number)) + after         
    
    return body

# typewriting effect
def typewriter(start, speed, text, affect, cursor, cursor_start_frame, cursor_speed, cur_frame): 
    count = len(text)
    string = ''
    body = ''
    cur = ''     
    if cur_frame > start:
        slice = (cur_frame-start)//speed
        if affect == 'Letters':            
            string = text[0:min(slice, count)]
        elif affect == 'Lines':
            lines = text.splitlines()
            if slice <= len(lines):
                string = combine_lines(lines[0:slice])
            else:
                string = text            
    if cursor_speed  == 0:
        cur= cursor        
    else:
        if cur_frame > cursor_start_frame:
            if (cur_frame-start) % cursor_speed > cursor_speed/2:
                cur  = cursor
                
    body = string+cur
    return body

# scrambling effect
def scramble(text, start, affect, speed, char_type, seed, cur_frame):    
    
    body = ''
    ran = ''
    
    count = len(text)    
    
    if cur_frame > start:
        if affect == 'Letters':
            slice = (cur_frame-start)//speed
            if slice != count:
                ran =  random_chars(text[slice:count], char_type, cur_frame+seed)
            else:
                ran = ''    
            body = text[0:min(slice, count)] + ran 
             
        elif affect == 'Words': 
            words = text.split()
            count_w = len(words) 
            slice = (cur_frame-start)//speed
            w = ''
            if slice <= count_w:            
                for i in range(slice):
                    w += words[i] + ' '
                ran =  random_chars(text[len(w):count], char_type, cur_frame+seed)
            else:
                ran = text
            body = text[0:min(len(w), count)] + ran
            
        elif affect == 'Line': 
            body = text      
    
    else:
        body = random_chars(text, char_type, cur_frame+seed)                 
    return body


# timer effect
def timer(start, sec, min, hou, inc, format, fps, cur_frame):    
    """
    # get local time (useless)
    time = time.strftime("%H:%M:%S", time.localtime())
    """
    seconds = sec + (min * 60) + (hou*3600)
    if cur_frame - start > fps:
        fac = (cur_frame - start) // fps
        seconds += fac * inc
        
    if format == 'ss':
        body = time.strftime("%S", time.gmtime(seconds))
    elif format == 'mm:ss':
        body = time.strftime("%M:%S", time.gmtime(seconds))
    elif format == 'hh:mm':
        body = time.strftime("%H:%M", time.gmtime(seconds))  
    else:
        body = time.strftime("%H:%M:%S", time.gmtime(seconds))
    
    return body

# Read Lines effect
def read_lines(text, start, speed, cur_frame):            
    body = ''    
    if text in bpy.data.texts.keys():
        text = bpy.data.texts[text]        
        if cur_frame >= start + speed:
            time = (cur_frame - start) // speed
            if time in range(len(text.lines)):
                body = text.lines[time-1].body
            else:
                body = text.lines[len(text.lines)-1].body
                
    return body

# Sine wave animation   
def wave(speed, frequency, amplitude, index, axis, sound, frame):
    x = (amplitude+sound)*(sin((frame/speed)+index*(1-frequency))) if axis[0] else 0
    y = (amplitude+sound)*(sin((frame/speed)+index*(1-frequency))) if axis[1] else 0
    z = (amplitude+sound)*(sin((frame/speed)+index*(1-frequency))) if axis[2] else 0
    
    # Triangle wave (It works but needs more polishing)    
    # y = (2*amplitude/pi)*asin(sin((2*pi/frequency)*((frame/(speed*5))+index))) if axis[1] else 0  
    
    return (x, y, z)

# Wiggle animation
def wiggle(speed, factor, index, axis, seed, sync, ease, sound, frame):
    
    x, y, z = (0, 0, 0)
    if not sync:
        frame += index
    
    start_frame = frame - (frame%speed)
    end_frame = start_frame + speed
    random.seed(start_frame+index+seed)
    loc_x = random.uniform(-factor - sound, factor + sound)
    random.seed(end_frame+index+seed)
    loc_x_1 = random.uniform(-factor - sound, factor + sound)    
    random.seed(start_frame+index+seed+1)
    loc_y = random.uniform(-factor - sound, factor + sound)
    random.seed(end_frame+index+seed+1)
    loc_y_1 = random.uniform(-factor - sound, factor + sound)    
    random.seed(start_frame+index+seed+2)
    loc_z = random.uniform(-factor - sound, factor + sound)
    random.seed(end_frame+index+seed+2)
    loc_z_1 = random.uniform(-factor - sound, factor + sound)
    
    # Linear interpolation
    t= (frame - start_frame) / (end_frame-start_frame)
    
    # Easing                    
    x = eval(ease + '(t, loc_x, loc_x_1 - loc_x, 1.0) if axis[0] else 0')
    y = eval(ease + '(t, loc_y, loc_y_1 - loc_y, 1.0) if axis[1] else 0')
    z = eval(ease + '(t, loc_z, loc_z_1 - loc_z, 1.0) if axis[2] else 0')
    
    # Quadric Bezier interpolation (don't work well with the current method)
    #x = ((1-t)*(1-t)*loc_x) + (2*(1-t)*t*((loc_x_1+factor)))+(t*t*loc_x_1)
    #y = ((1-t)*(1-t)*loc_y) + (2*(1-t)*t*((loc_y_1+factor)))+(t*t*loc_y_1)
    #z = ((1-t)*(1-t)*loc_z) + (2*(1-t)*t*((loc_z_1-loc_z)/2))+(t*t*loc_z_1)
    
    # Linear (this one work well, but Easing is much better)
    #x = (1-t)*loc_x + t*loc_x_1 if axis[0] else 0
    #y = (1-t)*loc_y + t*loc_y_1 if axis[1] else 0
    #z = (1-t)*loc_z + t*loc_z_1 if axis[2] else 0        
    
    return (x, y, z)

# Copy animation with offset.
def copy_offset(source, speed, order, factor, loop, loop_offset, count, sound, kinetic, over_amp, over_freq, over_dur, bounce_amp, bounce_ela, bounce_dur, i, frame):
    scn = bpy.context.scene
    obj = scn.objects
    location = [0.0 ,0.0 ,0.0]    
    rotation_euler = [0.0 ,0.0 ,0.0]       
    scale = [1.0 ,1.0 ,1.0]      
         
    if factor >0 or sound>0:
        if obj.get(source) is not None:
            src = obj[source]
            fcs, index = avail_fcurves(source)            
            if fcs != []:
                action = src.animation_data.action                                             
                for fc, ind in zip(fcs, index):                                    
                    if loop:
                        start = action.frame_range[0]
                        end = action.frame_range[1]
                        frame_range = end - start+loop_offset
                        duration = frame_range + (speed*count)                        
                        inc = frame // duration
                        evaluate = start-1+(frame-inc*duration)-(i*speed)                                 
                    else:                        
                        evaluate = frame-(i*speed)
                    if kinetic != 'None':
                        cur = action.fcurves[ind].evaluate(evaluate)
                        prev = action.fcurves[ind].evaluate(evaluate-1)
                        if cur == prev:
                            active_frame = get_last_active_frame(src, ind, evaluate)
                            t = evaluate - active_frame
                            cur = action.fcurves[ind].evaluate(active_frame)
                            prev = action.fcurves[ind].evaluate(active_frame-1)
                            velocity = cur - prev
                            if kinetic == 'Bounce':
                                decay = bounce(t, velocity, bounce_amp, bounce_ela, bounce_dur)
                            elif kinetic == 'Overshoot':
                                decay = overshoot(t, velocity, over_amp, over_freq, over_dur)
                        else: decay = 0.0        
                    else:
                        decay = 0.0                                                  
                    if 'location' in fc:                        
                        location[int(fc[-1:])] = (action.fcurves[ind].evaluate(evaluate) * (factor+sound)) + decay
                    elif 'rotation_euler' in fc:
                        rotation_euler[int(fc[-1:])] = (action.fcurves[ind].evaluate(evaluate) * (factor+sound)) + decay
                    elif 'scale' in fc:
                        scale[int(fc[-1:])] = (action.fcurves[ind].evaluate(evaluate) * max(1.0, (factor + sound))) + decay
    return (tuple(location), tuple(rotation_euler), tuple(scale))



# Update text
@persistent 
def text_fx_font_animation_update(scn):
    """ Function for updating the effects when the scene update """    
    cur_frame = scn.frame_current
    
    # Update simple text
    for ob in scn.objects:
        if ob.text_fx_enabled and 'TEXTFX_FONT' in ob.keys():            
            fps = scn.render.fps                      
            start = ob["start_frame"]
            typewriter_start = ob["typewriter_start_frame"]
            scramble_start = ob["scramble_start_frame"]
            timer_start = ob["timer_start_frame"]
            read_lines_start = ob["read_lines_start_frame"]
            start_number = ob["start_number"]
            end_number = ob["end_number"]
            before = ob['before']
            after = ob['after']
            speed = ob["speed"]
            typewriter_speed = ob["typewriter_speed"]
            scramble_speed = ob["scramble_speed"]            
            read_lines_speed = ob["read_lines_speed"]
            numbers_inc = ob['increment_by']
            dec = ob['decimals']
            text = ob["text"]
            scramble_text = ob["scramble_text"]
            scramble_seed = ob["scramble_seed"]
            read_lines_text = ob["read_lines_text"]
            typewriting_affect = ob.typewriting_affect
            cursor = ob["cursor"]
            cursor_start = ob["cursor_start_frame"]
            cursor_speed = ob["cursor_speed"]
            scrambling_affect = ob.scramble_affect
            speed = ob["speed"]
            sec = ob["seconds"]
            min = ob["minutes"]
            hou = ob["hours"]
            timer_inc = ob['timer_inc']
            format = ob.timer_format
            char_type = ob.scramble_char_type
            
            if ob.simple_effect == 'Increment':
                if start_number > end_number and numbers_inc >0:
                    ob['increment_by']  = -numbers_inc
                elif start_number < end_number and numbers_inc < 0:
                    ob['increment_by']  = -numbers_inc                                        
                ob.data.body = increment(start, start_number, end_number, before, after, speed, numbers_inc, dec, cur_frame)
            elif ob.simple_effect == 'Typewriter':
                ob.data.body = typewriter(typewriter_start, typewriter_speed, text, typewriting_affect, cursor, cursor_start, cursor_speed, cur_frame)
            elif ob.simple_effect == 'Scramble':
                ob.data.body = scramble(scramble_text, scramble_start, scrambling_affect, scramble_speed, char_type, scramble_seed, cur_frame)
            elif ob.simple_effect == 'Timer':
                ob.data.body = timer(timer_start, sec, min, hou, timer_inc, format, fps, cur_frame)
            elif ob.simple_effect == 'Read Lines':
                ob.data.body = read_lines(read_lines_text, read_lines_start, read_lines_speed, cur_frame)
                
        # Update advanced text        
        elif ob.type == 'EMPTY' and 'Advanced_Font_FX' in ob.keys():
            if ob.advanced_text_fx_enabled and len(ob.children) >0:
                sound = ob.sounds            
                wave_speed = ob['wave_speed']
                wave_frequency = ob['wave_frequency']
                wave_amplitude = ob['wave_amplitude']
                wave_audio_influence = ob['wave_audio_influence']
                min_wave = ob['wave_audio_min']
                wave_use_audio = ob.wave_use_audio                
                wave_axis = ob.wave_axis
                wave_sound = 0                
                wiggle_speed = ob['wiggle_speed']            
                wiggle_factor = ob['wiggle_factor']
                wiggle_seed = ob['wiggle_seed']
                wiggle_audio_influence = ob['wiggle_audio_influence']
                min_wiggle = ob['wiggle_audio_min']
                wiggle_use_audio = ob.wiggle_use_audio
                wiggle_axis = ob.wiggle_axis
                wiggle_sync = ob.wiggle_synchronize
                wiggle_ease = ob.wiggle_ease
                wiggle_sound = 0
                
                source = ob['offset_source']
                offset_speed = ob['offset_speed']
                order = ob.offset_order
                copy_use_audio = ob.copy_use_audio
                copy_factor = ob['copy_factor']
                loop_offset = ob['copy_looping_offset']
                copy_audio_influence = ob['copy_audio_influence']
                min_copy = ob['copy_audio_min']
                start = ob['copy_start']
                seed = ob['seed']
                over_amp = ob['overshoot_amp']
                over_freq = ob['overshoot_freq']
                over_dur = ob['overshoot_dur']
                bounce_amp = ob['bounce_amp']
                bounce_ela = ob['bounce_ela']
                bounce_dur = ob['bounce_dur']
                loop = ob.copy_loop                
                kinetic = ob.copy_kinetic                
                copy_sound = 0
                frame = 1                            
                children = list(ob.children)
                for i, child in enumerate(children):
                    ch = child.children[0]
                    if sound != '' and sound != 'None':
                        aud = scn['TextFX_Audio_' + sound]
                        if wave_use_audio:                            
                            wave_sound = wave_audio_influence * aud if aud > min_wave else 0
                        if wiggle_use_audio:
                            wiggle_sound = wiggle_audio_influence * aud if aud > min_wiggle else 0 
                        if copy_use_audio:
                            copy_sound = copy_audio_influence * aud if aud > min_copy else 0             
                    wav = wave(wave_speed, wave_frequency, wave_amplitude, i, wave_axis, wave_sound, cur_frame)                
                    wig = wiggle(wiggle_speed, wiggle_factor, i, wiggle_axis, wiggle_seed, wiggle_sync, wiggle_ease, wiggle_sound, cur_frame)                
                    if cur_frame > start:
                        frame = cur_frame - start + 1
                    if order == 'Right':
                        copy = copy_offset(source, offset_speed, order, copy_factor, loop, loop_offset, len(children)-1, copy_sound, kinetic, over_amp, over_freq, over_dur, bounce_amp, bounce_ela, bounce_dur, len(children)-1-i, frame)
                    elif order == 'Random':
                        random.seed(seed)
                        ran_children = list(range(len(children)))                    
                        random.shuffle(ran_children)                      
                        copy = copy_offset(source, offset_speed, order, copy_factor, loop, loop_offset, len(children)-1, copy_sound, kinetic, over_amp, over_freq, over_dur, bounce_amp, bounce_ela, bounce_dur, ran_children[i], frame)    
                    else: copy = copy_offset(source, offset_speed, order, copy_factor, loop, loop_offset, len(children)-1, copy_sound, kinetic, over_amp, over_freq, over_dur, bounce_amp, bounce_ela, bounce_dur, i, frame)    
                    ch.delta_location = tuple(map(lambda x, y, z: x + y + z, wav, wig, copy[0]))                
                    ch.delta_rotation_euler = copy[1]                
                    ch.delta_scale = copy[2]            
            
                   
# update text list
def upd_txt_lst(self, context):
    scn = bpy.context.scene
    act = bpy.context.object
    if act.simple_effect == 'Typewriter':
        act['text'] = bpy.data.texts[scn.texts].as_string()
    elif act.simple_effect == 'Read Lines':
        act['read_lines_text'] = bpy.data.texts[scn.texts].name    
    return None

# update font list
def upd_font_lst(self, context):
    scn = bpy.context.scene
    act = bpy.context.object
    
    if len(act.children) > 0:    
        for e in act.children:
            if 'TextFX' in e.keys():
                if e.children[0].type == 'FONT' and 'TextFX' in e.children[0].keys():
                    e.children[0].data.font = bpy.data.fonts[scn.fonts]
        calculate_spacing() 
    return None

# update text layers
def upd_font_layers(self, context):
    scn = bpy.context.scene
    act = bpy.context.object
    layers = act.text_layers
    act.layers = layers
    if len(act.children) > 0:        
        for e in act.children:
            if 'TextFX' in e.keys():
                e.layers = layers
                if e.children[0].type == 'FONT' and 'TextFX' in e.children[0].keys():
                    e.children[0].layers = layers    
    return None

# update chars offset for the X axis
def upd_text_offset_x(self, context):    
    act = bpy.context.object    
    if len(act.children)>0:
        x = act.offs_x        
        for e in act.children:
            if 'TextFX' in e.keys() and len(e.children) >0:            
                offsx = e.children[0]['x']
                e.children[0].data.offset_x = offsx + x               
    return None

# update chars offset for the Y axis
def upd_text_offset_y(self, context):    
    act = bpy.context.object    
    if len(act.children)>0:
        y = act.offs_y                    
        for e in act.children:
            if 'TextFX' in e.keys() and len(e.children) >0:            
                offsy = e.children[0]['y']
                e.children[0].data.offset_y = offsy + y                
    return None

# Load audio as keyframes
def load_audio(file_path):
    scn = bpy.context.scene
    ob = bpy.context.object
    low_frequency = ob['low_frequency']
    high_frequency = ob['high_frequency']
    scn.frame_current = 1
    file_name = os.path.basename(file_path)
    prop_name = 'TextFX_Audio_' + file_name + ' (' + str(int(low_frequency)) + '-' + str(int(high_frequency))  + ')' 
    if prop_name not in scn.keys():
        add_prop(scn, prop_name, 0.0, 0.0, 100.0, 'Audio file amplitude')
        scn.keyframe_insert('["'+prop_name + '"]')
    else:        
        if not hasattr(scn.animation_data, 'action'):
            scn.keyframe_insert('["'+prop_name + '"]')
        else:
            ready = False
            if hasattr(scn.animation_data.action, 'fcurves'):
                fcs = scn.animation_data.action.fcurves
                for f in fcs:
                    if f.data_path == '["'+prop_name + '"]':
                        ready = True
                if not ready:
                    scn.keyframe_insert('["'+prop_name + '"]')      
                             
    act_area = bpy.context.area.spaces.active.type
    fcs = scn.animation_data.action.fcurves
    for f in fcs:
        if f.data_path != '["'+prop_name + '"]':
            f.select = False
        else: f.select = True 
    for area in bpy.context.screen.areas:
        if area.type == act_area:
            try:                
                area.type = 'GRAPH_EDITOR'
                bpy.ops.graph.sound_bake(filepath = file_path, low = low_frequency, high = high_frequency)            
            except Exception as error:
                print(error)
            finally:
                area.type = act_area             
            break    
    

        
###############################################################
######################### Operators ###########################    
###############################################################

# Setup the font
class TextFX(Operator):
    bl_idname = "textfx.setup_font"
    bl_label = "Simple"
    bl_description = "Add simple text."

    def execute(self, context):
        setup_font()
        return {'FINISHED'}
    
# Setup Advanced font
class AdvancedTextFX(Operator):
    bl_idname = "textfx.setup_advanced_font"
    bl_label = "Advanced"
    bl_description = "Add advanced text."

    def execute(self, context):
        setup_advanced_font()
        return {'FINISHED'}
      
# Delete advanced text
class Delete_ADV_OP(Operator):
    bl_idname = "textfx.delete_advanced_text"
    bl_label = "Delete text"
    bl_description = "Delete text."

    def execute(self, context):
        delete_text('delete')
        return {'FINISHED'} 
    
# Select text
class Select_ADV_OP(Operator):
    bl_idname = "textfx.advanced_text_select"
    bl_label = "Select"
    bl_description = "Select all the characters."

    def execute(self, context):
        ob = context.object
        for e in ob.children:
            if 'TextFX' in e.keys():
                if e.children[0].type == 'FONT' and 'TextFX' in e.children[0].keys():
                    e.children[0].select = True
        ob.select = False         
        return {'FINISHED'}
    
# Update Advanced font
class UpdateTextFX(Operator):
    bl_idname = "textfx.update_advanced_font"
    bl_label = "Update"
    bl_description = "Update the text."

    def execute(self, context):
        ob = bpy.context.object
        text = ob['Text']
        setup_advanced_font(text = text, action = 'Update')
        return {'FINISHED'}
    
# calculate_spacing
class Calc_spacing_ADV_OP(Operator):
    bl_idname = "textfx.calculate_spacing"
    bl_label = "Calculate"
    bl_description = "Recalculate the spacing between the characters."

    def execute(self, context):
        calculate_spacing()
        return {'FINISHED'}
    
# Enable autorun Python Scripts
class EnableAutoRun(Operator):
    bl_idname = "textfx.enable_auto_run_scripts"
    bl_label = "Enable Python Scripts"
    bl_description = "Enable autorun Python Scripts."

    def execute(self, context):
        context.user_preferences.system.use_scripts_auto_execute = True
        calculate_spacing()
        return {'FINISHED'}         
    
# Load Font 
class LoadFont(Operator):
    bl_idname = "textfx.load_font"
    bl_label = "Load a font"
    bl_description = "Load a new font from a file."     
    filepath = StringProperty(subtype="FILE_PATH")
        
    def execute(self, context):
        scn = context.scene
        ob = context.object        
        
        filename, file_extension = os.path.splitext(self.filepath)
        extensions = ['.ttf', '.otf']
        if file_extension.lower() not in extensions:
            self.report({'WARNING'}, os.path.basename(self.filepath) + ' : ' + 'Is not a Font file.')
        
        else:
            font = bpy.data.fonts.load(filepath = self.filepath)            
            for e in ob.children:
                if 'TextFX' in e.keys():
                    if e.children[0].type == 'FONT' and 'TextFX' in e.children[0].keys():
                        scn.fonts = font.name
            calculate_spacing()              
            
        return {'FINISHED'}
    
    def invoke(self, context, event):        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
# Load Audio as keyframes
class LoadAudio(Operator):
    bl_idname = "textfx.load_audio"
    bl_label = "Load audio"
    bl_description = "Load an audio file as keyframes."     
    filepath = StringProperty(subtype="FILE_PATH")
        
    def execute(self, context):       
        filename, file_extension = os.path.splitext(self.filepath)
        file_name = os.path.basename(self.filepath)
        extensions = ['.mp3', '.wav', '.ogg', '.wma']
        if file_extension.lower() not in extensions:
            self.report({'WARNING'}, os.path.basename(self.filepath) + ' : ' + 'Is not an audio file.')
        elif len(file_name) > 34:
            self.report({'WARNING'}, 'Name of the file is too long.')            
        else:
            load_audio(self.filepath)           
        return {'FINISHED'}
    
    def invoke(self, context, event):        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
# Bake to keyframes
class Bake_ADV_OP(Operator):
    bl_idname = "textfx.bake_action"
    bl_label = "Bake"
    bl_description = "Bake animation to keyframes."

    def execute(self, context):
        scn = bpy.context.scene
        obj = scn.objects
        parent = bpy.context.object
        start = parent['bake_start_frame'] 
        end = parent['bake_end_frame']
        if end > start:       
            source = parent['offset_source']            
            ref = ''        
            if len(parent.children) > 0:
                if parent.advanced_text_fx_enabled:
                    try:
                        if source != '':
                            if obj.get(source) is not None:                    
                                if obj[source].type == 'FONT' and 'TextFX' in obj[source].keys():                            
                                    bpy.ops.object.empty_add(location = (0,0,0))
                                    refrence = bpy.context.object
                                    refrence.name = 'refrence'
                                    refrence.animation_data_create()
                                    refrence.animation_data.action = obj[source].animation_data.action
                                    parent['offset_source'] = refrence.name
                                    ref = refrence.name
                        wm = bpy.context.window_manager                
                        wm.progress_begin(0, 100)                                  
                        for i, e in enumerate(parent.children):
                            if 'TextFX' in e.keys():
                                if e.children[0].type == 'FONT' and 'TextFX' in e.children[0].keys():
                                    for ob in obj:
                                        ob.select = False
                                    obj.active = e.children[0]
                                    e.children[0].select = True
                                    bpy.ops.nla.bake(frame_start=start, frame_end=end, bake_types={'OBJECT'})
                                    wm.progress_update(int((i*100)/len(parent.children)-1))
                        wm.progress_end()  
                    except Exception as error:
                        self.report({'WARNING'}, str(error))
                    else:
                        self.report({'INFO'}, 'Animation Baked successfully !')    
                    finally:                                
                        if ref != '' and 'refrence' in parent['offset_source']:                
                            parent['offset_source'] = ''
                            obj.unlink(obj[ref])                                      
                        for ob in obj:
                            ob.select = False
                        obj.active = parent
                        parent.select = True                  
                else: self.report({'WARNING'}, 'The effects are disabled')    
        else: self.report({'WARNING'}, 'Start frame must be greater than the end frame')            
        return {'FINISHED'}   
    
                                          
    
###############################################################
#########################  The UI  ############################    
###############################################################     

# Add font menu
class AddFont(Menu):
    bl_idname = "textfx.add_font"
    bl_label = "Add a text"
    bl_description = "Add a text."

    def draw(self, context):
        layout = self.layout                       
        layout.operator("textfx.setup_font", icon = 'FONT_DATA')
        layout.operator("textfx.setup_advanced_font", icon = 'OUTLINER_OB_FONT')
                
##################### The Panel ########################
class TextFX_UI(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Text FX"
    bl_label = "Text FX"
    bl_context = "objectmode"
    
        
    def draw(self, context):
        scn = context.scene
        act = context.object
        layout = self.layout
        row = layout.row()
        row.menu("textfx.add_font", icon = 'ZOOMIN')
        
        if act != None:                            
            if act.type == 'FONT':
                if 'TEXTFX_FONT' in act.keys():                    
                    col = layout.column()                                      
                    box = layout.box()
                    col = box.column()
                    col.prop(act, 'text_fx_enabled',
                              icon = 'VISIBLE_IPO_ON' if act.text_fx_enabled else 'VISIBLE_IPO_OFF',
                               text = 'Disable effects' if act.text_fx_enabled else 'Enable effects')                    
                    col.separator()    
                    col.prop(act, 'simple_effect', text = '', icon = 'OUTLINER_DATA_FONT')                                                        
                    if act.simple_effect == 'Typewriter':                                     
                        col = box.column()                                     
                        col.separator()
                        col.separator()
                        row = col.row()
                        row.prop(act, 'typewriting_affect', expand = True)                 
                        row = col.row(align = True)                        
                        row.prop(scn, 'texts', text = '', icon = 'TEXT', icon_only=True)
                        row.prop(act, '["text"]', text = "")                  
                        col.prop(act, '["typewriter_start_frame"]', text = "Start Frame")
                        col.prop(act, '["typewriter_speed"]', text = "Speed")
                        col.separator()
                        col.separator()
                        col.prop(act, '["cursor"]', text = "Cursor")
                        col.prop(act, '["cursor_start_frame"]', text = "Cursor start frame")
                        col.prop(act, '["cursor_speed"]', text = "Cursor speed")
                    elif act.simple_effect == 'Increment':                        
                        col = box.column()                        
                        col.separator()
                        col.separator()                    
                        col.prop(act, '["before"]', text = "Before")
                        col.prop(act, '["after"]', text = "After")
                        col.prop(act, '["start_frame"]', text = "Start Frame")
                        col.prop(act, '["start_number"]', text = "Start Number")
                        col.prop(act, '["end_number"]', text = "End Number")
                        col.prop(act, '["speed"]', text = "Speed")    
                        col.prop(act, '["increment_by"]', text = "Increment by")    
                        col.prop(act, '["decimals"]', text = "Decimals")
                    elif act.simple_effect == 'Scramble':                        
                        col = box.column()                        
                        col.separator()
                        col.separator()
                        row = col.row()                                                                   
                        row.prop(act, 'scramble_affect', expand = True)                                     
                        col.separator()
                        col.prop(act, 'scramble_char_type')                                     
                        col.separator()
                        col.prop(act, '["scramble_text"]', text = "")
                        col.prop(act, '["scramble_start_frame"]', text = "Start Frame")
                        col.prop(act, '["scramble_speed"]', text = "Speed")
                        col.prop(act, '["scramble_seed"]', text = "Random seed")
                    elif act.simple_effect == 'Timer':                        
                        col = box.column()                        
                        col.separator()
                        col.separator()
                        row = col.row()
                        row.prop(act, 'timer_format', expand = True)                     
                        col = box.column(align = True)                           
                        col.prop(act, '["seconds"]', text = "Seconds")
                        col.prop(act, '["minutes"]', text = "Minutes")
                        col.prop(act, '["hours"]', text = "Hours")
                        col = box.column()
                        col.prop(act, '["timer_start_frame"]', text = "Start frame")                        
                        col.prop(act, '["timer_inc"]', text = "Increment")
                    elif act.simple_effect == 'Read Lines':                        
                        col = box.column()                        
                        col.separator()
                        row = col.row(align = True)                        
                        row.prop(scn, 'texts', text = '', icon = 'TEXT', icon_only=True)                                                
                        row.prop(act, '["read_lines_text"]', text = "")
                        if act['read_lines_text'] == '':
                            col.label(text = 'Please select a text.', icon = 'INFO')                  
                        elif act['read_lines_text'] not in bpy.data.texts:    
                            col.label(text = 'Text: "' + act['read_lines_text'] + '" Not found.', icon = 'ERROR')                  
                        col.prop(act, '["read_lines_start_frame"]', text = "Start Frame")
                        col.prop(act, '["read_lines_speed"]', text = "Speed")
            elif act.type == 'EMPTY' and 'Advanced_Font_FX' in act.keys():
                if context.user_preferences.system.use_scripts_auto_execute:                                    
                    row = layout.row()
                    row.prop(act, 'advanced_text_menu', expand = True)
                    col = layout.column()
                    row = col.row(align = True)
                    row.operator('textfx.advanced_text_select', text = '', icon = 'RESTRICT_SELECT_OFF')
                    row.prop(act, '["Text"]', text = "")
                    row.operator('textfx.update_advanced_font', text = '', icon = 'FILE_REFRESH')
                    if len(act.children) > 0:
                        
                        if act.advanced_text_menu == 'Text':
                            col = layout.column()
                            
                            col.separator()
                            row = col.row(align = True)
                            row.prop(scn, 'fonts', icon = 'FILE_FONT', icon_only = True)
                            if act.children[0] is not None: 
                                e = act.children[0]
                                if e.children[0] is not None and e.children[0].type == 'FONT': 
                                    row.prop(e.children[0].data.font, 'name', text = '')
                            row.operator('textfx.load_font', icon = 'FILESEL', text ='')
                            
                            row = col.row(align = True)
                            row.prop(act, '["spacing"]', text = "Spacing")
                            row.operator('textfx.calculate_spacing', text= '', icon = 'ARROW_LEFTRIGHT')
                            col.prop(act, '["shear"]', text = "Shear")
                            
                            col.label(text = 'Offset:')                    
                            row = col.row(align = True)
                            row.prop(act, 'offs_x', text = 'X')
                            row.prop(act, 'offs_y', text = 'Y')
                            
                            col.label(text = 'Modification:')
                            row = col.row(align = True)                    
                            row.prop(act, '["offset"]', text = "Offset")
                            row.prop(act, '["extrude"]', text = "Extrude")
                            
                            col.label(text = 'Bevel:')
                            row = col.row(align = True) 
                            row.prop(act, '["depth"]', text = "Bevel depth")
                            row.prop(act, '["resolution"]', text = "Bevel resolution")             
                            row = layout.row()                    
                            row.alignment = 'LEFT'
                            row.label(text ='Layers: ')
                            row.template_layers(act, "text_layers", act, "layers", 0)                                  
                        elif act.advanced_text_menu == 'Audio':
                            col = layout.column()
                            col.separator()
                            col.prop(act, 'sounds', icon = 'SOUND', text = '') 
                            col.separator()
                            box = col.box()
                            col1 = box.column()
                            col1.label(text = 'Load audio', icon = 'SPEAKER')                                           
                            col1.separator()
                            col1.prop(act, '["low_frequency"]', text = 'Lowest frequency')
                            col1.prop(act, '["high_frequency"]', text = 'Highest frequency')
                            col1.separator()
                            col1.operator('textfx.load_audio', icon = 'FILE_SOUND')
                            col.separator()
                        elif act.advanced_text_menu == 'Bake':                   
                            col = layout.column()
                            col.separator()                            
                            box = col.box()
                            col1 = box.column()
                            col1.label(text = 'Bake to keyframes', icon = 'KEY_HLT')                                           
                            col1.separator()                            
                            col1.prop(act, '["bake_start_frame"]', text = "Start frame")
                            col1.prop(act, '["bake_end_frame"]', text = "End frame")
                            col1.separator()
                            col1.operator('textfx.bake_action', icon = 'KEYINGSET')                   
                            col.separator()
                    else:
                        col = layout.column()
                        col.label(text = 'The text is empty!', icon = 'INFO')        
                        col.label(text = '     Type your text then press the update button.')        
                    col = layout.column()
                    col.scale_y = 1.7                
                    col.operator('textfx.delete_advanced_text', icon = 'CANCEL')     
                else:
                    col = layout.column()                
                    col.label(text = 'Python scripts are disabled', icon = 'ERROR')
                    col.operator('textfx.enable_auto_run_scripts', icon = 'SCRIPT')
                    
                    
                
# Panel for the advanced text's effects                
class TextFX_Effects_UI(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Text FX"
    bl_label = "Effects"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(self, context):
        scn = context.scene
        act = context.object
        vis = False
        if act is not None:
            if act.type == 'EMPTY' and 'Advanced_Font_FX' in act.keys():
                if len(act.children) > 0:
                    vis = True
        return vis       
    
        
    def draw(self, context):
        scn = context.scene
        obj = scn.objects
        act = context.object
        layout = self.layout
        if act is not None:
            if act.type == 'EMPTY' and 'Advanced_Font_FX' in act.keys():
                col = layout.column()
                col.prop(act, 'advanced_text_fx_enabled',
                              icon = 'VISIBLE_IPO_ON' if act.advanced_text_fx_enabled else 'VISIBLE_IPO_OFF',
                               text = 'Disable effects' if act.advanced_text_fx_enabled else 'Enable effects')
                if act.advanced_text_fx_enabled:          
                    box = layout.box()
                    row = box.row()
                    row.prop(scn, "expand_wave_menu",
                    icon="TRIA_DOWN" if scn.expand_wave_menu else "TRIA_RIGHT",
                    icon_only=True, emboss = False)
                    row.label(text='Wave', icon = 'MOD_WAVE')
                    if scn.expand_wave_menu:
                        row = box.row()
                        row.prop(act, 'wave_axis', text = 'XYZ')
                        col = box.column()                    
                        col.prop(act,'["wave_amplitude"]', text = 'Amplitude')     
                        col.prop(act,'["wave_frequency"]', text = 'Frequency')     
                        col.prop(act,'["wave_speed"]', text = 'Speed')
                        col = box.column()  
                        col.prop(act,"wave_use_audio", text = 'Use audio', icon = 'SPEAKER')
                        col = box.column(align = True)
                        if act.wave_use_audio:
                            col.prop(act, '["wave_audio_influence"]', text = 'Influence')
                            col.prop(act, '["wave_audio_min"]', text = 'Min')
                            
                        
                    box = layout.box()
                    row = box.row()
                    row.prop(scn, "expand_wiggle_menu",
                    icon="TRIA_DOWN" if scn.expand_wiggle_menu else "TRIA_RIGHT",
                    icon_only=True, emboss = False)
                    row.label(text='Wiggle', icon = 'MOD_PARTICLES')
                    if scn.expand_wiggle_menu:
                        row = box.row()
                        row.prop(act, 'wiggle_axis', text = 'XYZ')
                        col = box.column()                                            
                        col.prop(act,'wiggle_synchronize', text = 'Synchronize', icon = 'TIME')     
                        col.separator()
                        col.prop(act,'wiggle_ease', text = 'Easing')     
                        col.separator()
                        col.prop(act,'["wiggle_factor"]', text = 'Factor')     
                        col.prop(act,'["wiggle_seed"]', text = 'Random seed')     
                        col.prop(act,'["wiggle_speed"]', text = 'Speed')
                        col = box.column()  
                        col.prop(act,"wiggle_use_audio", text = 'Use audio', icon = 'SPEAKER')
                        col = box.column(align = True)
                        if act.wiggle_use_audio:
                            col.prop(act, '["wiggle_audio_influence"]', text = 'Influence')
                            col.prop(act, '["wiggle_audio_min"]', text = 'Min')
                        
                    box = layout.box()
                    row = box.row()
                    row.prop(scn, "expand_copy_menu",
                    icon="TRIA_DOWN" if scn.expand_copy_menu else "TRIA_RIGHT",
                    icon_only=True, emboss = False)
                    row.label(text='Copy animation', icon = 'MOD_MIRROR')
                    if scn.expand_copy_menu:
                        if act["offset_source"] != '' and obj.get(act["offset_source"]) is not None:
                            col = box.column()
                            col.prop(act, '["copy_factor"]', text = 'Factor')
                            col.prop(act, 'copy_loop', text = 'Repeat')
                            if act.copy_loop:
                                col.prop(act, '["copy_looping_offset"]', text = 'Delay')                    
                            row = box.row()
                            row.prop(act, 'offset_order', expand = True)
                            col = box.column()                            
                            col.prop_search(act, '["offset_source"]', scn, "objects", text = 'Source')
                            col.prop(act, '["copy_start"]', text = 'Start frame')
                            if act.offset_order == 'Random':
                                col.prop(act, '["seed"]', text = 'Random seed')
                            col.prop(act, '["offset_speed"]', text = "Speed")
                            col = box.column()
                            box1 = col.box()
                            col1 = box1.column()
                            col1.prop(act, 'copy_kinetic')
                            if act.copy_kinetic == 'Overshoot':
                                col1.prop(act, '["overshoot_amp"]', text = 'Amplitude')
                                col1.prop(act, '["overshoot_freq"]', text = 'Frequency')
                                col1.prop(act, '["overshoot_dur"]', text = 'Duration')
                            elif act.copy_kinetic == 'Bounce':
                                col1.prop(act, '["bounce_amp"]', text = 'Amplitude')
                                col1.prop(act, '["bounce_ela"]', text = 'Elasticity')
                                col1.prop(act, '["bounce_dur"]', text = 'Duration')   
                            col = box.column()  
                            col.prop(act,"copy_use_audio", text = 'Use audio', icon = 'SPEAKER')
                            col = box.column(align = True)
                            if act.copy_use_audio:
                                col.prop(act, '["copy_audio_influence"]', text = 'Influence')
                                col.prop(act, '["copy_audio_min"]', text = 'Min')                  
                        else:
                            col = box.column()
                            col.label(text = 'A Keyframed object is required to', icon = 'INFO')
                            col.label(text = '     copy its (Loction, Rotation, Scale)')
                            col.prop_search(act, '["offset_source"]', scn, "objects", text = 'Source')
                            
###################### Register ###########################                         
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.texts = EnumProperty(name = 'Available Texts', items = texts, update = upd_txt_lst,
                                         description = 'Available Texts.')       
    bpy.types.Scene.fonts = EnumProperty(name = 'Available Fonts', items = fonts, update = upd_font_lst, description = 'Available Fonts.')                                     
    bpy.types.Object.sounds = EnumProperty(name = 'Available Sounds', items = sounds, description = 'Available Sounds.')                                     
    bpy.types.Object.offset_order = EnumProperty(name = 'Offset order',
                                                 items = (('Left','Left',''),('Right','Right',''),('Random','Random','')),
                                                 description = 'Offset order')
    bpy.types.Object.copy_kinetic = EnumProperty(name = 'Kinetic',
                                                 items = (('Overshoot','Overshoot',''),
                                                          ('Bounce','Bounce',''),
                                                          ('None','None','')),
                                                 description = 'kinetic')                                                
    bpy.types.Object.advanced_text_menu = EnumProperty(name = 'Menu',
                                                 items = (('Text','Text',''),
                                                          ('Audio','Audio',''),
                                                          ('Bake','Bake','')),
                                                 description = 'Options for')   
    bpy.types.Object.simple_effect = EnumProperty(name = 'Choose an effect',
                                                  items = (('Increment','Increment',''),
                                                           ('Typewriter','Typewriter',''),('Scramble','Scramble',''),
                                                           ('Timer','Timer',''), ('Read Lines','Read Lines',''),
                                                           ('None','None','')),
                                                 description = 'Effects')                                                                                        
    bpy.types.Object.typewriting_affect = EnumProperty(name = 'Affect',
                                                       items = (('Letters','Letters',''),('Lines','Lines','')),
                                                       description = 'Typewriter affect')
    bpy.types.Object.scramble_affect = EnumProperty(name = 'Affect',
                                                    items = (('Letters','Letters',''),('Words','Words',''),('Line','Line','')),
                                                    description = 'Scrambling Affect')
    bpy.types.Object.timer_format = EnumProperty(name = 'format',
                                                 items = (('ss','ss',''), ('mm:ss','mm:ss',''), ('hh:mm:ss','hh:mm:ss',''), ('hh:mm','hh:mm','')),
                                                 description = 'Timer format')  
    bpy.types.Object.scramble_char_type = EnumProperty(name = 'Char type',
                                                       items = (('Same','Same',''), ('Digits','Digits',''), ('Lower case','Lower case',''), ('Upper case','Upper case',''), ('Punctuation','Punctuation',''), ('Letters','Letters',''), ('Random','Random','')),
                                                       description = 'Char type')
    bpy.types.Object.wiggle_ease = EnumProperty(name = 'Easing', items = easing_list, description = 'Easing')
    bpy.types.Object.text_fx_enabled = BoolProperty(description = 'Enable or disable effects.')       
    bpy.types.Object.advanced_text_fx_enabled = BoolProperty(description = 'Enable or disable effects.')       
    bpy.types.Object.wiggle_synchronize = BoolProperty(default = True, description = 'Synchronize the movement of all the characters.')       
    bpy.types.Object.wiggle_axis = BoolVectorProperty(name="Wiggle axis", description="Apply Wiggle effect to this axis")
    bpy.types.Object.wave_axis = BoolVectorProperty(name="Wave axis", description="Apply Wave effect to this axis")
    bpy.types.Object.copy_loop = BoolProperty(default = False, description = 'Repeat in a loop.')       
    bpy.types.Object.offs_x = FloatProperty(min = -50.0, max = 50.0, update = upd_text_offset_x, description = 'Horizontal offset from the object origin.')       
    bpy.types.Object.offs_y = FloatProperty(min = -50.0, max = 50.0, update = upd_text_offset_y, description = 'Vertical offset from the object origin.')       
    bpy.types.Scene.expand_wave_menu = BoolProperty(default = False)       
    bpy.types.Scene.expand_wiggle_menu = BoolProperty(default = False)       
    bpy.types.Scene.expand_copy_menu = BoolProperty(default = False)    
    bpy.types.Object.wave_use_audio = BoolProperty(default = False, description = 'Use audio to influence the wave amplitude')       
    bpy.types.Object.wiggle_use_audio = BoolProperty(default = False, description = 'Use audio to influence the wiggle factor')       
    bpy.types.Object.copy_use_audio = BoolProperty(default = False, description = 'Use audio to influence the effect factor')       
    bpy.types.Object.text_layers = BoolVectorProperty(size = 20, update = upd_font_layers, description = 'Move the text to this layer')       
        
    frame_change_pre.append(text_fx_font_animation_update)      

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.texts
    del bpy.types.Object.offset_order
    del bpy.types.Object.advanced_text_menu
    del bpy.types.Object.simple_effect
    del bpy.types.Object.typewriting_affect
    del bpy.types.Object.scramble_affect
    del bpy.types.Object.timer_format
    del bpy.types.Object.scramble_char_type
    del bpy.types.Object.wiggle_ease
    del bpy.types.Scene.fonts
    del bpy.types.Object.sounds
    del bpy.types.Object.text_fx_enabled
    del bpy.types.Object.advanced_text_fx_enabled
    del bpy.types.Object.wiggle_synchronize
    del bpy.types.Object.wiggle_axis
    del bpy.types.Object.wave_axis
    del bpy.types.Object.copy_loop
    del bpy.types.Object.offs_x
    del bpy.types.Object.offs_y
    del bpy.types.Scene.expand_wave_menu
    del bpy.types.Scene.expand_wiggle_menu
    del bpy.types.Scene.expand_copy_menu    
    del bpy.types.Object.wave_use_audio
    del bpy.types.Object.wiggle_use_audio
    del bpy.types.Object.copy_use_audio
    del bpy.types.Object.text_layers
    frame_change_pre.remove(text_fx_font_animation_update)    
              
if __name__ == "__main__":
    register()