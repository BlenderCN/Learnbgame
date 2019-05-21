import bpy,json

from ...widgets import CheckBox
from ...functions import clear_layout
# Apply the pose or anim to the rig
def refresh_gp(self,action) :
    print('refresh_gp')
    '''
    ob = bpy.context.scene.objects.active
    if ob.type=='ARMATURE' and ob.mode == 'POSE' :
        read_anim(self.action,self.blend.value()*0.01,self.action_left.isChecked(),self.action_right.isChecked(),self.selected_only.isChecked(),self.mirror_pose.isChecked(),self.frame_current)
        '''


def load_grease_pencil(self,ThumbnailList,item_info,link=True):
    scene = bpy.context.scene
    ob = scene.objects.active

    clear_layout(self.toolBoxLayout)

    self.replace = CheckBox('Replace')
    self.replace.setChecked(True)

    self.toolBoxLayout.addWidget(self.replace)

    if bpy.context.scene.tool_settings.grease_pencil_source == 'OBJECT' and ob and ob.grease_pencil:
        dest_gp = ob.grease_pencil
    elif bpy.context.scene.grease_pencil :
        dest_gp = bpy.context.scene.grease_pencil
    else :
        dest_gp =bpy.data.grease_pencil.new('GPencil')

    gpencil_txt = item_info['path']

    with open(gpencil_txt) as gpencil_data :
        source_gp = json.load(gpencil_data)

    print(source_gp)

    # create missing palette
    palette = dest_gp.palettes.active
    for p_name,p_value in source_gp["palettes"].items():
        if not palette.colors.get(p_name) :
            p = palette.colors.new()
            p.name = p_name
            for attr in ['color','alpha','fill_color','fill_alpha'] :
                setattr(p,attr,p_value[attr])

    for source_layer in source_gp["layers"] :
        dest_layer = dest_gp.layers.get(source_layer['info'])
        if not dest_layer:
            dest_layer = dest_gp.layers.new(source_layer['info'])

            for attr in ["hide","line_change","opacity","matrix_inverse","parent_type","show_x_ray"] :
                setattr(dest_layer,attr,source_layer[attr])

            if source_layer["parent_type"]=='BONE' :
                dest_layer.parent_bone = source_layer['parent_bone']

        frames={}
        for i,f in enumerate(dest_layer.frames) :
            frames[f.frame_number]=i

        if not scene.frame_current in frames.keys():
            dest_frame = dest_layer.frames.new(scene.frame_current)
        else :
            dest_frame = dest_layer.frames[frames[scene.frame_current]]




        for source_stroke in source_layer["strokes"]:
            dest_stroke = dest_frame.strokes.new(source_stroke["palette"])

            for attr in ["line_width","draw_mode"] :
                setattr(dest_stroke,attr,source_stroke[attr])

            for i,source_point_values in enumerate(source_stroke["points"]):
                dest_stroke.points.add()
                dest_point = dest_stroke.points[i]

                for attr in ["co","pressure","strength"] :
                    setattr(dest_point,attr,source_point_values[attr])


    self.replace.stateChanged.connect(lambda : refresh_gp(self,'action_txt'))
