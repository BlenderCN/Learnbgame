# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

import bpy, mathutils, random, operator, string #locale no longer needed!
from random import Random
from bpy.app.handlers import persistent

### Properties Classes:

# Object Properties:
class RandomiserObjectProps (bpy.types.PropertyGroup):
    use_randomise = bpy.props.BoolProperty(name = "Randomise")
    seed = bpy.props.IntProperty(name = "Seed", default  = 0)

    #Update Method Properties:
    update_method = bpy.props.EnumProperty(name = "Update Method", items = [
        ("freq","Frequency","Automatic Based on frame numbers"),
        ("man","Manual","Manual, based on a value that can be animated, driven, etc.")
        ])
    time = bpy.props.IntProperty(name = "Time")
    offset = bpy.props.IntProperty(name = "Offset")
    period = bpy.props.FloatProperty(name = "Frames per Update", default = 1.0, min = 0.01)

    #Generate Method Properties:
    generate_method = bpy.props.EnumProperty(name = "Generate Method", items = [("ordered","Ordered","ordered"),("random","Random","random")])
    source_group = bpy.props.StringProperty(name = "Group", description = "Name of the Group to use for Randomise.")

    #Previous choice for random choice selections to avoid repeats:
    previous_choice = bpy.props.StringProperty(name = "Previous Choice", description = "Stored value of previous random object choice")
    no_repeats = bpy.props.BoolProperty(name = "Avoid Repeats", default = False)
    
class RandomiserTextProps (bpy.types.PropertyGroup):
    use_randomise = bpy.props.BoolProperty(name = "Randomise")
    seed = bpy.props.IntProperty(name = "Seed", default  = 0)
    
    #Update Method props:
    update_method = bpy.props.EnumProperty(name = "Update Method", items = [
        ("freq","Frequency","Automatic Based on frame numbers"),
        ("man","Manual","Manual, based on a value that can be animated, driven, etc.")
        ])
    offset = bpy.props.IntProperty(name = "Offset")
    time = bpy.props.IntProperty(name = "Time")
    period = bpy.props.FloatProperty(name = "Frames per Update", default = 1.0, min = 0.01)

    #Generate Method Props:
    generate_method = bpy.props.EnumProperty(name = "Generate Method", items = [
        ("ordered","Pick Ordered","ordered"),
        ("random","Pick Random","random"),
        ("grow","Typewriter","Grow sentence letter by letter."),
        ("ticker","Scrolling Text","Scrolling Text"),
        ("numeric", "Counting", "Count up or countdown."),
        ("clock", "Clock", "Gives a clock readout.")
        ])
    textsource = bpy.props.EnumProperty(name = "Text Source", items = [
        ("binary","Binary","binary digits"),
        ("digits","Digits","random digits"),
        ("characters","Characters","random characters"),
        ("alphanumeric","Alphanumeric","random letters"),
        ("tblines","Text File, Lines","Random lines from a text block."),
        ("tbchars","Text File, Characters","Random characters from a text block.")
        ])
    caps = bpy.props.EnumProperty(name = "Case", items = [
        ("lc","Lowercase","lowercase"),
        ("uc","Uppercase","uppercase"),
        ("ac","Both","both")
        ])
    textdata = bpy.props.StringProperty(name = "Text Datablock", description = "Name of Text datablock to use.")
    
    #Ticker Properties
    ticklength = bpy.props.IntProperty(name = "Scroll length", default = 10)
    group_digits = bpy.props.BoolProperty(name = "Group Digits", default = False)

    #Time Properties:
    clock_minutes = bpy.props.IntProperty(name = "Minutes Offset", default = 0, min = 0, max = 59)
    clock_hours = bpy.props.IntProperty(name = "Hours Offset", default = 0, min = 0, max = 23)
    clock_24hr = bpy.props.BoolProperty(name = "24 Hour Clock", default = True)

    #Previous choice for random choice selections to avoid repeats:
    previous_choice = bpy.props.StringProperty(name = "Previous Choice", description = "Stored value of previous randomiser character generated.")
    no_repeats = bpy.props.BoolProperty(name = "Avoid Repeats", default = False)
    
    #Leader Properties:
    leader = bpy.props.EnumProperty(name = "Leader",items = [
        ("none","None","none"),
        ("random","Noise","Taken from noise source."),
        ("underscore","Underscore","underscore"),
        ("flash","Underscore Flash","flash")
        ])
    leader_period = bpy.props.IntProperty(name = "Leader Period", default = 25)

    # Noise Properties:
    use_noise = bpy.props.BoolProperty(name = "Noise")

    #Update Properties:
    noise_update_method = bpy.props.EnumProperty(name = "Noise Update Method", items = [
        ('copy',"Automatic",'Updates at the same rate as the overall string'),
        ('man',"Manual",'Updates based on a value that can be animated.'),
        ('freq',"Frequency",'Updates every x number of frames.')
        ])
    noise_mask_update_method = bpy.props.EnumProperty(name = "Mask Update Method", items = [
        ('copy',"Automatic",'Updates at the same rate as the overall string'),
        ('man',"Manual",'Updates based on a value that can be animated.'),
        ('freq',"Frequency",'Updates every x number of frames.')
        ])
    noise_time  = bpy.props.IntProperty(name = "Time", default = 0)
    noise_period = bpy.props.FloatProperty(name = "Frames per Update", default = 1.0, min = 0.01)
    noise_mask_time  = bpy.props.IntProperty(name = "Time", default = 0)
    noise_mask_period = bpy.props.FloatProperty(name = "Frames per Update",default = 1.0, min = 0.01)

    noise_threshold = bpy.props.FloatProperty(name = "Noise Threshold", min = 0.0, max = 1.0)
    noise_mask = bpy.props.StringProperty(name = "Mask (comma delimited)")

    #Generate Properties:
    noise_method = bpy.props.EnumProperty(name = "Noise Generate Method", items = [
        ("mask","Mask","mask"),
        ("random","Random","random")
        ])
    noise_source = bpy.props.EnumProperty(name = "Noise Source", items = [
        ("digits","Digits","random digits"),
        ("characters","Characters","random letters"),
        ("alphanumeric","Alphanumeric","random letters and numbers"),
        ("binary", "Binary", "Zeroes and Ones"),
        ("tbchars", "Text Block, Characters", "Random characters from a text block.")
        ])

    noise_textdata = bpy.props.StringProperty(name = "Text Datablock", description = "Name of Text datablock to use for Noise.")
    noise_ignore_whitespace = bpy.props.BoolProperty(name = "Ignore WhiteSpace", default = True)
    noise_ignore_custom = bpy.props.StringProperty(name = "Ignore Custom", description = "Whitelist of characters not to replace with noise.")


# Functions:

def check_fcurve(data, frame, prop):
    if data.animation_data:
        ad = data.animation_data
        if ad.action:
            ac = ad.action
            curves = ac.fcurves
            for curve in curves:
                if curve.data_path == "randomiser." + prop:
                    return curve.evaluate(frame)
    return None

def check_for_update(data, frame, update_method, prop):
    randomise = data.randomiser
    if update_method == 'man':
        #Check that the prop value is different from the previous frame:
        prop_current = randomise.get(prop)
        prop_old = check_fcurve(data, frame - 1, prop)
        return not prop_current == prop_old
    elif update_method == 'freq':
        #Check that i is different from the previous frame:
        i_current = get_iter(data, 'update', 0, frame)
        i_old = get_iter(data, 'update', -1, frame)
        return not i_current == i_old

def get_iter(data, mode, shift, frame): #New version of get iter that doesn't use frame_current, which is messy.
    # Mode should be one of the following:
    # "update" : Returns iter based on the time property.
    # "noise1" : Returns a random iter with time and noise_update_period as a seed.
    # "noise2" : Returns a random iter, no seed.
    # "mask"   : Returns a random iter with time and noise_pick_period as a seed. 
    randomise = data.randomiser
    integer = 0
    offset = randomise.offset

    if mode == "update":
        if randomise.update_method == 'man':
            integer = randomise.time - randomise.offset + shift
        elif randomise.update_method == 'freq':
            period = randomise.period
            integer = int(round((frame - offset + shift) / period))
    elif mode == 'noise1':
        if randomise.noise_update_method == 'copy':
            integer = get_iter(data,'upate',shift,frame)
        elif randomise.noise_update_method == 'man':
            integer = randomise.noise_time - randomise.offset + shift
        elif randomise.noise_update_method == 'freq':
            period = randomise.noise_period
            integer = int(round((frame - offset + shift) / period))
    elif mode == 'noise2':
        integer = random.randint(1000)
    elif mode == "mask":
        if randomise.noise_mask_update_method == 'copy':
            integer = get_iter(data,'update',shift,frame)
        elif randomise.noise_mask_update_method == 'man':
            integer = randomise.noise_mask_time - randomise.offset + shift
        elif randomise.noise_mask_update_method == 'freq':
            period = randomise.noise_mask_period
            integer = int(round((frame - offset + shift) / period))
    return integer


def custom_rand(data, method, noisemode, shift, frame, *args): 
    # Custom randomise method that uses current frame as seed and initialises each frame to stay predictable.
    # Args:
    #   object: Input data to operate on: either object or text data.
    #   method: Method in random to call (see docs for random)
    #   *args: required args for the method chosen, given as a list []
    x = Random(get_iter(data, noisemode, shift, frame) + data.randomiser.seed)
    methodtocall = getattr(x,method)
    #print(args)
    result = methodtocall(*args)
    return result

def time_to_clock(time):
    #Takes a time in seconds and returns a clock readout in h:m:s.
    m, s = divmod(time, 60)
    h, m = divmod(m, 60) 
    return h, m, s



# Operators:

class RandomiseSpreadSeeds(bpy.types.Operator):
    bl_idname = 'object.randomise_spread_seeds'
    bl_label = "Spread Randomiser Seeds"
    text = bpy.props.BoolProperty(name  = "Text", default = False)

    @classmethod
    def poll(cls,context):
        return context.object is not None

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        objects = bpy.context.selected_objects
        count = 0
        for ob in objects:
            if self.text:
                if ob.type == 'FONT':
                    try:
                        ob.data.randomiser.seed = count
                    except AttributeError:
                        print("Couldn't find a seed value for object: " + ob.name)
                        pass
            else:
                try:
                    ob.randomiser.seed = count
                except AttributeError:
                    print("Couldn't find a seed value for object: " + ob.name)
                    pass
            count += 1000
        return {'FINISHED'}

class RandomiseCopySettings(bpy.types.Operator):
    bl_idname = 'object.randomise_copy_settings'
    bl_label = 'Copy Randomiser Settings from Active'
    text = bpy.props.BoolProperty(name = "Text", default = False)

    @classmethod
    def poll(cls,context):
        return context.object is not None

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        for ob in objects:
            if self.text:
                if ob.type == 'FONT':
                    try:
                        ob.data.randomiser.seed = active.data.randomiser.seed
                    except AttributeError:
                        print("Couldn't find a seed value for object: " + ob.name +  " or: " + active.name)
                        pass
            else:
                try:
                    ob.randomiser.seed = active.randomiser.seed
                except AttributeError:
                    ("Couldn't find a seed value for object: " + ob.name  + " or: " + active.name)
                    pass
        return {'FINISHED'}

class RandomiseCopySeed(bpy.types.Operator):
    bl_idname = 'object.randomise_copy_seed'
    bl_label = "Copy Randomiser Seed from Active"
    text = bpy.props.BoolProperty(name = "Text", default = False)

    @classmethod
    def poll(cls,context):
        return context.object is not None

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        objects = bpy.context.selected_objects
        active = bpy.context.active_object

        for ob in objects:
            if self.text:
                if ob.type == 'FONT':
                    try:
                        ob.data.randomiser.seed = active.data.randomiser.seed
                    except AttributeError:
                        print("Couldn't find a seed value for object: " + ob.name +  " or: " + active.name)
                        pass
            else:
                try:
                    ob.randomiser.seed = active.randomiser.seed
                except AttributeError:
                    ("Couldn't find a seed value for object: " + ob.name  + " or: " + active.name)
                    pass
        return {'FINISHED'}

class RandomiseObjectData (bpy.types.Operator):
    bl_idname = 'object.randomise_data'
    bl_label = "Randomise Object Data"
    object_string = bpy.props.StringProperty()
    frame = bpy.props.IntProperty()

    def randomise_data(self, object):
        randomise = object.randomiser
        generate_method = randomise.generate_method
        group_name = randomise.source_group
        group = bpy.data.groups[group_name]

        #Get data source and do sanity check:
        #print("Source Group name give is: " + group_name)
        data_source = [bpy.data.objects[name] for name in sorted(group.objects.keys()) if bpy.data.objects[name].type == object.type] #Sorted and cleaned list of objects in source group
        if len(data_source) == 0:
            print("Data source list is empty. Skipping.")
            return
        else:
            if generate_method == 'ordered':
                object.data = data_source[get_iter(object, 'update', 0, self.frame) % len(data_source)].data
            elif generate_method == 'random':
                previous = randomise.previous_choice #Name of previous choices object data.
                no_repeats = randomise.no_repeats
                if no_repeats:
                    #Cleaned List of choices.
                    list_clean = []
                    for x in data_source:
                        if x not in list_clean:
                            list_clean.append(x)
                    #Check if update is required.
                    if check_for_update(object, self.frame, randomise.update_method, "time"):
                        previous = object.data.name
                        randomise.previous_choice = previous
                    #Now remove previous from list_clean:
                    #Check that none of the group members have previous as their object data and if so remove them too.
                    for ob in list_clean:
                        if ob.data.name == previous:
                            list_clean.remove(ob)
                    #Choose a new value:
                    object.data = custom_rand(object, 'choice','update', 0, self.frame, list_clean).data
                else:
                    object.data = custom_rand(object, 'choice','update', 0, self.frame, data_source).data
            return

    def execute(self, context):
        try:
            object = bpy.data.objects[self.object_string]
        except TypeError:
            print("Couldnt find object :" + self.object_string)
        self.randomise_data(object)
        return {'FINISHED'}

class RandomiseTextData (bpy.types.Operator):
    bl_idname = 'object.randomise_text'
    bl_label = 'Randomises an objects text data.'
    data_string = bpy.props.StringProperty()
    frame = bpy.props.IntProperty()

    def get_textsource(self, source, generate_method, caps, text_block):
        text_data = ""
        #Returns a string for randomiser to sample from.

        if generate_method == 'grow':
            #Check that text block is not None. If it is it can't be picked from.
            if text_block is None:
                #print("ERROR: Method: Grow - No text block given as source. Check your settings.")
                text_data = "ERROR -  Text block not found. See console."     
            else:
                for line in text_block.lines:
                    text_data += line.body
                    text_data += "\n"
            return text_data

        elif generate_method == 'ticker':
            #Check that text block is not None. If it is it can't be picked from.
            if text_block is None:
                #print("ERROR: Method: Ticker - No text block given as source. Check your settings.")
                text_data = "ERROR -  Text block not found. See console."     
            else:
                for line in text_block.lines:
                    text_data += line.body
            return text_data

        elif generate_method == 'numeric':
            #print("Nothing to generate, skipping.")
            text_data = ""
            return text_data

        else:
            if source == "binary":
                text_data = ["0","1"]
                return text_data

            elif source == "digits":
                text_data = [x for x in string.digits]
                return text_data
                
            elif source == "characters":
                if caps == "ac":
                    text_data = [x for x in string.ascii_letters]
                elif caps == "uc":
                    text_data = [x for x in string.ascii_uppercase]
                elif caps == "lc":
                    text_data = [x for x in string.ascii_lowercase]
                return text_data
                    
            elif source == "alphanumeric":
                if caps == "ac":
                    text_data = [x for x in (string.ascii_letters + string.digits)]
                elif caps == "uc":
                    text_data = [x for x in (string.ascii_uppercase + string.digits)]
                elif caps == "lc":
                    text_data = [x for x in (string.ascii_lowercase + string.digits)]
                return text_data
            
            elif source in ['tblines', 'tbchars']:
                #Check that text block is not None. If it is it can't be picked from.
                if text_block is None:
                    #print("ERROR: Method: Text Block Characters/Lines - No text block given as source. Check your settings.")
                    text_data = "ERROR -  Text block not found. See console."
                else:         
                    if source == "tblines":
                        text_data = [line.body + " " for line in text_block.lines]
                        
                    elif source == "tbchars":
                        for line in text_block.lines:
                            for char in line.body:
                                if char != " ":
                                    text_data += char
                return text_data

            else:
                print("Hmm, something should have returned by now, return None so as to give you a useful error...")
                return None             


    def addnoise(self, string, data):
        #noise info:
        randomise = data.randomiser
        source = randomise.noise_source
        mask_string = randomise.noise_mask
        noise_method = randomise.noise_method
        threshold = randomise.noise_threshold
        ignore_whitespace = randomise.noise_ignore_whitespace

        try:
            noise_text_datablock = bpy.data.texts[randomise.noise_textdata]
        except KeyError:
            #print("No text block found for noise.")
            noise_text_datablock = None
        noise_data = self.get_textsource(source, "random", randomise.caps, noise_text_datablock)

        if noise_method == 'mask':
            #Create noise at certain positions based on mask list:
            if len(mask_string) > 0:
                noise_mask = [int(a) for a in mask_string.split(",")]
            else:
                noise_mask = []
            #truncate noise mask to length of string:
            noise_mask = noise_mask[:len(string)]
            for x in noise_mask:
                #only add noise if that character is visible:
                if len(string) > 0:
                    if x < 0:
                        if abs(x) > len(string):
                            x = len(string) - (x % len(string)) 
                        else:
                            x = len(string) + x
                    text_working = string
                    try:
                        ignore_list = ["\n", ""]
                        if ignore_whitespace:
                            ignore_list.append(" ")
                        if string[x] in ignore_list:
                            pass
                        else:
                            if randomise.noise_update_method == 'copy':
                                iter_noise = 'update'
                            else:
                                iter_noise = 'noise1'
                            text_working = string[0:x] + custom_rand(data, "choice", iter_noise, x*13, self.frame, noise_data) + string[x+1:]
                    except (KeyError, IndexError):
                        pass
                    string = text_working
                    #This seems to get messed up sometimes, and end up with string getting much longer...
                    

        elif noise_method == 'random':
            #Create random noise at a certain percentage of indices.
            mask_length = int((threshold) * len(string))
            string_length = len(string)
            if randomise.noise_mask_update_method == 'copy':
                iter_noise = 'update'
            else:
                iter_noise = 'mask'
            noise_mask = custom_rand(data,"sample", iter_noise, 0, self.frame, range(0,string_length),mask_length)

            for x in noise_mask:
                text_working = string
                ignore_list = ["\n", ""]
                if ignore_whitespace:
                    ignore_list.append(" ")
                ignore_list += randomise.noise_ignore_custom
                if string[x] in ignore_list:
                    pass
                else:
                    if randomise.noise_update_method  == 'copy':
                        iter_noise = 'update'
                    else:
                        iter_noise = 'noise1'
                    text_working = string[0:x] + custom_rand(data,"choice", iter_noise, x*13, self.frame, noise_data) + string[x+1:]    
                string = text_working

        return string


    def randomise_text(self, data):
        randomise = data.randomiser
        generate_method = randomise.generate_method
        caps = randomise.caps
        text_new = ""

        #text_block is only applicable if the source requires it. Otherwise it might not even be given and will cause errors.
        source  = randomise.textsource
        try:
            if generate_method in ['random', 'ordered']:
                if source in ['tblines', 'tbchars']:
                    text_block = bpy.data.texts[randomise.textdata]
                else:
                    #print("Source doesn't require text block.")
                    text_block = None
            elif generate_method in ['grow','ticker']:
                source = 'tbchars'
                text_block = bpy.data.texts[randomise.textdata]
            else:
                #print("Generate method doesn't require text block.")
                text_block = None
        except KeyError:
            if randomise.textdata == "":
                print("ERROR: No name given for text block.")
            else:
                print("ERROR: Cannot find text block with name: " + randomise.textdata)
            print("Tip: The Text Block should contain the name of a text block in the Text Editor, NOT a text object.")    
            text_block = None

        # First get the source text from which to generate new string from:
        #print("Text Data Inputs: \n Source: " + source + " \n Generate Method: " + generate_method + "\n Caps: " + caps + "\n Text_block: " + str(text_block))
        text_data = self.get_textsource(source, generate_method, caps, text_block)
        #print("Text Data for sampling:" + text_data)
        noise_data = self.get_textsource(randomise.noise_source, "random", "ac", text_block)
        i = get_iter(data, 'update', 0, self.frame)

        # Get a new string for the text:
        if generate_method == 'grow':
            if get_iter(data, 'update', 0, self.frame) != 0:
                #Dont allow a negative index, end should be > 0.
                end = 0
                if i > 0:
                    end = i
                text_new = text_data[:end]

        elif generate_method == 'ticker':
            #Sanity check that input text isn't empty:
            if text_data == "":
                text_data = " "
            #create repeated string in case original isn't long enough:
            ticker_length = randomise.ticklength
            text_length = len(text_data)
            if ticker_length < text_length:
                ticker_source  = text_data * 2
            else:
                repeats = int(ticker_length/text_length) + 1
                ticker_source = text_data * repeats
            ticker_startpos = i % len(text_data)
            ticker_endpos = ticker_startpos + ticker_length
            text_new = ticker_source[ticker_startpos:ticker_endpos]

        elif generate_method == 'numeric':
            if data.randomiser.group_digits:
                text_new = format(i, ',d') #locale.format("%d", i, grouping = data.randomiser.group_digits)
            else:
                text_new = str(i)
            #print("Text New:" + text_new)

        elif generate_method == 'clock':
            #Treat time as a number in seconds.
            h, m, s = time_to_clock(i + (randomise.clock_minutes*60) + (randomise.clock_hours) * 3600)
            if randomise.clock_24hr:
                h = h % 24
            else:
                h = h % 12
            string = str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)
            text_new = string

        elif generate_method == "ordered":
            text_new = text_data[i % len(text_data)]

        elif generate_method == 'random':
            previous = randomise.previous_choice
            no_repeats = randomise.no_repeats
            text_data = list(text_data)
            if no_repeats:
                #Cleaned list of choices 
                list_clean = []
                for x in text_data:
                    if x not in list_clean:
                        list_clean.append(x)
                #Check if an update is needed:
                if check_for_update(data, self.frame, randomise.update_method, "time"):
                    #Update previous to current:
                    previous = data.body
                    randomise.previous_choice = previous
                #Now remove previous from list_clean:
                if previous in list_clean:
                    list_clean.remove(previous)
                text_new = custom_rand(data,'choice','update',0, self.frame, list_clean)
            else:
                text_new = custom_rand(data,'choice','update',0, self.frame, text_data)

        # Add noise to text_new:
        if randomise.use_noise:
            text_new = self.addnoise(text_new, data)

        # Add leader to text_new if on grow:
        if generate_method == "grow":
            leader = data.randomiser.leader
            leader_period = data.randomiser.leader_period
            if leader == "random":
                text_new = text_new + custom_rand(data, "choice", 'update', 0, self.frame, noise_data)
            elif leader == "underscore":
                text_new  = text_new + "_"
            elif leader == 'flash':
                flash = [" ", "_"]
                flash_int = int(i / leader_period) % 2
                flash_choice = flash[flash_int]
                text_new = text_new + flash_choice

        # Apply new string:
        data.body = text_new

        return

    def execute(self, context):
        #try:
        data = bpy.data.curves[self.data_string]
        self.randomise_text(data)
        return {'FINISHED'}
        #except KeyError:
        #    print("Couldnt find data :" + self.data_string)
        #    return{'FINISHED'}

# Handlers:
@persistent
def randomise_handler(dummy):
    #Randomise Objects and Texts in Current Scene:
    # Randomise Objects
    to_randomise = []
    scene = bpy.context.scene
    current_frame = bpy.context.scene.frame_current
    subframe = bpy.context.scene.frame_subframe
    for object in scene.objects:
        try:
            if object.randomiser.use_randomise == True:
                try:
                    if object.randomiser.source_group in bpy.data.groups.keys():
                        to_randomise.append((object, current_frame + subframe))
                except (KeyError, AttributeError): #Key error for key not found. Attr Error for key not given.
                    print("ERROR:Group not found for object to pick random data from.")
                    pass
        except AttributeError:
            pass

    for x in to_randomise:
        object = x[0]
        frame = x[1]
        bpy.ops.object.randomise_data(object_string = object.name, frame = frame)

    # Randomise Texts:
    to_randomise = []
    for text in [ob.data for ob in scene.objects if ob.type == 'FONT']:
        try:
            if text.randomiser.use_randomise == True:
                to_randomise.append((text,current_frame + subframe))
        except AttributeError:
            pass
    
    for x in to_randomise:
        text = x[0]
        frame = x[1]
        bpy.ops.object.randomise_text(data_string = text.name, frame = frame)


    #Randomise Objects and Texts in Sequencer Scenes:
    if scene.render.use_sequencer:
        #Randomise Objects:
        to_randomise = []
        try:
            seqs = [seq for seq in bpy.context.scene.sequence_editor.sequences_all if seq.type == 'SCENE' and seq.frame_final_start <= current_frame < seq.frame_final_end and seq.scene != bpy.context.scene]
            for seq in seqs:
                frame_scene = current_frame - seq.frame_start + seq.scene.frame_start + subframe
                for object in seq.scene.objects:
                    try:
                        if object.randomiser.use_randomise == True:
                            try:
                                if object.randomiser.source_group in bpy.data.groups.keys():
                                    to_randomise.append((object, frame_scene))
                            except (KeyError, AttributeError): #Key error for key not found. Attr Error for key not given.
                                print("ERROR:Group not found for object to pick random data from.")
                                pass
                    except AttributeError:
                        pass
        except AttributeError:
            pass

        for x in to_randomise:
            object = x[0]
            frame = x[1]
            bpy.ops.object.randomise_data(object_string = object.name, frame = frame)
        
        #Randomise Texts:
        to_randomise = []
        try:
            seqs = [seq for seq in bpy.context.scene.sequence_editor.sequences_all if seq.type == 'SCENE' and seq.frame_final_start <= current_frame < seq.frame_final_end  and seq.scene != bpy.context.scene]
            for seq in seqs:
                frame_scene = current_frame - seq.frame_start + seq.scene.frame_start + subframe
                for text in [ob.data for ob in seq.scene.objects if ob.type == 'FONT']:
                    try:
                        if text.randomiser.use_randomise == True:
                            to_randomise.append((text,frame_scene))
                    except AttributeError:
                        pass
        except AttributeError:
            pass

        for x in to_randomise:
            text = x[0]
            frame = x[1]
            bpy.ops.object.randomise_text(data_string = text.name, frame = frame)
    
    return
