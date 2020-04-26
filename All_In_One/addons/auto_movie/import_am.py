"""
TBD
"""


import bpy,os

current_channel = 1
current_frame = 1
scene = None
base_path = ""
cross_time = 12
def_image_length = 48
clip_list = []

def init_nle(filepath):
    global scene, current_channel, current_frame,base_path
    
    scene = bpy.context.scene   
    scene.sequence_editor_clear()  
    scene.sequence_editor_create()
    
    current_channel = 1
    current_frame = 1
    base_path = os.path.dirname(os.path.abspath(filepath))
    print(base_path)       

def toggle_channel():
    global current_channel
    current_channel +=2
    if current_channel > 3:
        current_channel = 1

def increment_current_frame(sequence):
    global current_frame
    current_frame += sequence.frame_final_duration - cross_time

def do_set_resolution(params):
    x_res = int(params[0])
    y_res = int(params[1])    
    print("Setting resolution to  %d x %d" % (x_res,y_res))
    print(scene)
    
    scene.render.resolution_x = x_res
    scene.render.resolution_y = y_res


def do_set_frame_rate(params):
    frame_rate = int(params[0])    
    print("Setting frame rate to %d" % (frame_rate))
    
    scene.render.fps = frame_rate
    scene.render.fps_base = 1

def do_set_cross_time(params):
    global cross_time
    cross_time = int(params[0])    
    print("Setting default crossfade time to %d" % (cross_time))

def do_insert_image(params):
    image_path = os.path.join(base_path,str(params[0]))
    
    image_length = def_image_length
    if len(params) >= 2:
        image_length = int(params[1])
       
    
    print("Insert image here" + str(image_path))
    
    image_seq = scene.sequence_editor.sequences.new_image(
                name=image_path,
                filepath=image_path,
                channel=current_channel, frame_start=current_frame)
    
    image_seq.frame_final_duration = image_length
    
    
    clip_list.append(image_seq)
    toggle_channel()
    increment_current_frame(image_seq) 
                
    
def do_insert_video(params):    
    clip_path = os.path.join(base_path,str(params[0]))
    
    offset_start = 0
    if len(params) >= 2:
        offset_start = int(params[1])
    
    offset_end = 0
    if len(params) >= 3:
        offset_end = int(params[2])    
    
    print("Insert video here" + str(clip_path))
        
    vid_seq = scene.sequence_editor.sequences.new_movie(
        name=clip_path,
        filepath=clip_path,
        channel=current_channel, frame_start=current_frame)
    
    #original_type = bpy.context.area.type
    #bpy.context.area.type = "SEQUENCE_EDITOR"
    #scene.frame_current = current_frame
    #bpy.ops.sequencer.movie_strip_add(filepath=clip_path,relative_path=False, channel=current_channel, frame_start=current_frame)	
    #bpy.context.area.type = original_type                
    #vid_seq = scene.sequence_editor.active_strip   
    #print ("vid seq is:" + str(vid_seq))        
		
    vid_seq.animation_offset_start=offset_start
    vid_seq.animation_offset_end=offset_end
    vid_seq.update()
    
    try:
        snd_seq = scene.sequence_editor.sequences.new_sound(
            name=clip_path,
            filepath=clip_path,
            channel=current_channel, frame_start=current_frame)
        snd_seq.animation_offset_start=offset_start
        snd_seq.animation_offset_end=offset_end    
    except:
        pass    
    
    clip_list.append(vid_seq)
    toggle_channel()
    increment_current_frame(vid_seq)    


def do_cmd(command):
    instr = command[0]    
    print ("Executing command %s" % instr)
    
    if not instr or instr[0] == '#':
        return
    
    if instr == "res":
        do_set_resolution(command[1:])
    else:
        if instr == "frt":
            do_set_frame_rate(command[1:])
        else:
            if instr == "ctm":
                do_set_cross_time(command[1:])
            else:
                if instr == "img":
                    do_insert_image(command[1:])
                else:
                    if instr == "vid":
                        do_insert_video(command[1:])
                    else:
                        print("Error! Unknown command")
    
def add_cross_fades():
    
    prev_clip = None
    
    for sequence in clip_list:
        print (sequence.name)
        if prev_clip:
            print("cross fading %s to %s" % (prev_clip.name,sequence.name))
            
            start =  sequence.frame_start
            end = start + cross_time
            
            #print("\t start: %d  end: %d" %(start,end)) 
            
            cross = scene.sequence_editor.sequences.new_effect(
                    name="cross",
                    type='CROSS',		
                    channel=5,frame_start=start,frame_end=end,seq1=prev_clip,seq2=sequence)       
            
            cross.update()        
                    
        prev_clip = sequence   
                

def read(filepath):
    init_nle(filepath)    
    
        
    print("loading file " + filepath)     
    
    filehandle = open(filepath, "r")
    for line in filehandle.readlines():
        do_cmd(line.strip().split("\t"))
        
    add_cross_fades()    
        
    scene.frame_end = current_frame
    bpy.context.window.screen = bpy.data.screens["Video Editing"]    

if __name__ == "__main__":
    read("/tmp/auto-movietest/test.am")