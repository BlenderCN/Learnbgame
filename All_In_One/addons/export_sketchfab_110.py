bl_info = {
    "name": "Sketchfab export",
    "author": "Bart Crouch",
    "version": (1, 1, 0),
    "blender": (2, 6, 3),
    "location": "View3D > Properties panel",
    "description": "Upload your model to Sketchfab",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


import base64
import bpy
import json
import os
import threading
import time
import urllib.request
from bpy.app.handlers import persistent


test = False     # if True, no contact is made with the webserver


# save an openGL render as thumbnail
def create_thumbnail():
    # saving old settings
    old_path = bpy.context.scene.render.filepath
    old_fileformat = bpy.context.scene.render.image_settings.file_format
    old_extension = bpy.context.scene.render.use_file_extension
    old_x = bpy.context.scene.render.resolution_x
    old_y = bpy.context.scene.render.resolution_y
    old_percentage = bpy.context.scene.render.resolution_percentage
    old_aspect_x = bpy.context.scene.render.pixel_aspect_x
    old_aspect_y = bpy.context.scene.render.pixel_aspect_y
    old_perspective = bpy.context.region_data.view_perspective
    old_distance = bpy.context.region_data.view_distance
    old_location = bpy.context.region_data.view_location[:]
    old_rotation = bpy.context.region_data.view_rotation[:]
    
    # setting up render settings
    filepath = bpy.data.filepath
    filename_pos = len(bpy.path.basename(bpy.data.filepath))
    filepath = filepath[:-filename_pos]
    filename = time.strftime("Sketchfab_%Y_%m_%d_%H_%M_%S",
        time.localtime(time.time()))
    filepath += filename
    bpy.context.scene.render.filepath = filepath
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.use_file_extension = True
    bpy.context.scene.render.resolution_x = 448
    bpy.context.scene.render.resolution_y = 280
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.pixel_aspect_x = 1.0
    bpy.context.scene.render.pixel_aspect_y = 1.0
    if bpy.context.scene.camera:
        bpy.context.region_data.view_perspective = 'CAMERA'
    
    # render
    bpy.ops.render.opengl(write_still=True, view_context=True)
    
    # restore old settings
    bpy.context.scene.render.filepath = old_path
    bpy.context.scene.render.image_settings.file_format = old_fileformat
    bpy.context.scene.render.use_file_extension = old_extension
    bpy.context.scene.render.resolution_x = old_x
    bpy.context.scene.render.resolution_y = old_y
    bpy.context.scene.render.resolution_percentage = old_percentage
    bpy.context.scene.render.pixel_aspect_x = old_aspect_x
    bpy.context.scene.render.pixel_aspect_y = old_aspect_y
    bpy.context.region_data.view_perspective = old_perspective
    bpy.context.region_data.view_distance = old_distance
    bpy.context.region_data.view_location = old_location
    bpy.context.region_data.view_rotation = old_rotation

    # return values
    filepath += ".png"
    size = os.path.getsize(filepath)

    return(filepath, size)


# change a bytes int into a properly formatted string
def format_size(size):
    size /= 1024
    size_suffix = "kB"
    if size > 1024:
        size /= 1024
        size_suffix = "mB"
    if size >= 100:
        size = str(int(size))
    else:
        size = "%.1f"%size
    size += " " + size_suffix
    
    return(size)


# attempt to load token from presets
@persistent
def load_token(dummy=False):
    filepath = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets",
        "sketchfab.txt")
    try:
        file = open(filepath, 'r')
    except:
        return
    try:
        token = file.readline()
    except:
        token = ""
    file.close()
    bpy.context.window_manager.sketchfab.token = token
    

# change visibility statuses and pack images
def prepare_assets():
    props = bpy.context.window_manager.sketchfab
    
    hidden = []
    images = []
    if props.models == 'selection' or props.lamps != 'all':
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                for mat_slot in ob.material_slots:
                    if not mat_slot.material:
                        continue
                    for tex_slot in mat_slot.material.texture_slots:
                        if not tex_slot:
                            continue
                        if tex_slot.texture.type == 'IMAGE':
                            images.append(tex_slot.texture.image)
            if (props.models == 'selection' and ob.type == 'MESH') or \
            (props.lamps == 'selection' and ob.type == 'LAMP'):
                if not ob.select and not ob.hide:
                    ob.hide = True
                    hidden.append(ob)
            elif props.lamps == 'none' and ob.type == 'LAMP':
                if not ob.hide:
                    ob.hide = True
                    hidden.append(ob)
    
    packed = []
    for img in images:
        if not img.packed_file:
            img.pack()
            packed.append(img)
    
    return(hidden, packed)


# restore original situation
def restore(hidden, packed):
    for ob in hidden:
        ob.hide = False
    for img in packed:
        img.unpack(method='USE_ORIGINAL')


# save a copy of the current blendfile
def save_blend_copy():
    filepath = bpy.data.filepath
    filename_pos = len(bpy.path.basename(bpy.data.filepath))
    filepath = filepath[:-filename_pos]
    filename = time.strftime("Sketchfab_%Y_%m_%d_%H_%M_%S.blend",
        time.localtime(time.time()))
    filepath += filename
    
    bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=True,
        copy=True)
    size = os.path.getsize(filepath)
    
    return(filepath, filename, size)


# remove file copy
def terminate(filepath, thumbnail, thumbnail_path):
    os.remove(filepath)
    if thumbnail:
        os.remove(thumbnail_path)


# save token to file
def update_token(self, context):
    token = context.window_manager.sketchfab.token
    path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets")
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path, "sketchfab.txt")
    file = open(filepath, 'w+')
    file.write(token)
    file.close()


# upload the blend-file to sketchfab
def upload(filepath, filename, thumbnail_path):
    props = bpy.context.window_manager.sketchfab
    url="https://api.sketchfab.com/model"
    title = props.title
    if not title:
        title = bpy.path.basename(bpy.data.filepath).split('.')[0]
    
    model_contents = base64.encodestring(open(filepath, 'rb').read()).decode()
    data = {
        "title": title,
        "description": props.description,
        "contents": model_contents,
        "filename": filename,
        "tags": props.tags,
        "token": props.token
    }
    
    if props.thumbnail:
        model_thumb = base64.encodestring(open(thumbnail_path, 'rb').\
            read()).decode()
        data["thumbnail"] = model_thumb
    
    data_dump = json.dumps(data).encode()
    
    if test:
        props.message_type = 'INFO'
        props.message = "Test successful"
        return
    
    try:
        f = urllib.request.urlopen(url, data_dump)
    except urllib.error.HTTPError as error:
        errorcode = str(error.code)
        f = False
    if f:
        response = json.loads(f.read().decode())
        f.close()
    else:
        if errorcode == '403':
            response = {'error':"wrong token"}
        elif errorcode == '404':
            response = {'error':"url not found"}
        else:
            response = {'error':errorcode}
    
    if 'success' in response:
        props.message = "Upload available at: http://sketchfab.com/show/%s" \
            % response['id']
        props.message_type = 'INFO'
        props.result = "http://sketchfab.com/show/%s" % response['id']
    else:
        props.message = "Upload failed. Error: %s" % response['error']
        props.message_type = 'ERROR'


# operator to export model to sketchfab
class ExportSketchfab(bpy.types.Operator):
    '''Upload your model to Sketchfab'''
    bl_idname = "export.sketchfab"
    bl_label = "Upload"
    
    _timer = None
    _thread = None
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self._thread.is_alive():
                props = context.window_manager.sketchfab
                terminate(props.filepath, props.thumbnail,
                    props.thumbnail_path)
                if context.area:
                    context.area.tag_redraw()
                if not props.message_type:
                    props.message_type = 'ERROR'
                self.report({props.message_type}, props.message)
                if props.message_type == 'INFO':
                    bpy.ops.wm.call_menu(name="VIEW3D_MT_popup_result")
                context.window_manager.event_timer_remove(self._timer)
                self._thread.join()
                props.uploading = False
                return{'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        props = context.window_manager.sketchfab        
        if not props.token:
            self.report({'ERROR'}, "Token is missing")
            return{'CANCELLED'}
        props.uploading = True
        
        hidden, packed = prepare_assets()
        props.filepath, filename, size_blend = save_blend_copy()
        if props.thumbnail:
            props.thumbnail_path, size_thumb = create_thumbnail()
        else:
            props.thumbnail_path = ""
            size_thumb = 0
        props.size = format_size(size_blend + size_thumb)
        restore(hidden, packed)
        self._thread = threading.Thread(target=upload,
            args=(props.filepath, filename, props.thumbnail_path))
        self._thread.start()
        
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(1.0,
            context.window)

        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self._thread.join()
        
        return {'CANCELLED'}


# popup to say that something is already being uploaded
class ExportSketchfabBusy(bpy.types.Operator):
    '''Upload your model to Sketchfab'''
    bl_idname = "export.sketchfab_busy"
    bl_label = "Uploading"
    
    def execute(self, context):
        self.report({'WARNING'}, "Please wait till current upload is finished")
        
        return {'FINISHED'}


# menu class to display the url after uploading
class VIEW3D_MT_popup_result(bpy.types.Menu):
    bl_label = "Upload successful"

    def draw(self, context):
        layout = self.layout
        result = context.window_manager.sketchfab.result
        layout.operator("wm.url_open", text="View online").url = result


# user interface
class VIEW3D_PT_sketchfab(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Sketchfab"

    def draw(self, context):
        props = context.window_manager.sketchfab
        if props.token_reload:
            props.token_reload = False
            if not props.token:
                load_token()
        layout = self.layout
        
        col = layout.box().column(align=True)
        col.prop(props, "models")
        col.prop(props, "lamps")
        #col.prop(props, "split")
        col.prop(props, "thumbnail")

        col = layout.box().column(align=True)
        col.prop(props, "title")
        col.prop(props, "description")
        col.prop(props, "tags")
        
        layout.prop(props, "token")
        if props.uploading:
            layout.operator("export.sketchfab_busy",
                text="Uploading "+props.size)
        else:
            layout.operator("export.sketchfab")


# property group containing all properties for the user interface
class SketchfabProps(bpy.types.PropertyGroup):
    description = bpy.props.StringProperty(name="Description",
        description = "Description of the model (optional)",
        default = "")
    filepath = bpy.props.StringProperty(name="Filepath",
        description = "internal use",
        default = "")
    lamps = bpy.props.EnumProperty(name="Lamps",
        items = (('all', "All", "Export all lamps in the file"),
            ('none', "None", "Don't export any lamps"),
            ('selection', "Selection", "Only export selected lamps")),
        description = "Determines which lamps are exported",
        default = 'all')
    message = bpy.props.StringProperty(name="Message",
        description = "internal use",
        default = "")
    message_type = bpy.props.StringProperty(name="Message type",
        description = "internal use",
        default = "")
    models = bpy.props.EnumProperty(name="Models",
        items = (('all', "All", "Export all meshes in the file"),
            ('selection', "Selection", "Only export selected meshes")),
        description = "Determines which meshes are exported",
        default = 'selection')
    result = bpy.props.StringProperty(name="Result",
        description = "internal use, stores the url of the uploaded model",
        default = "")
    size = bpy.props.StringProperty(name="Size",
        description = "Current filesize being uploaded",
        default = "")
    split = bpy.props.BoolProperty(name="Split models",
        description = "Export each mesh as a seperate model",
        default = False)
    tags = bpy.props.StringProperty(name="Tags",
        description = "List of tags, separated by spaces (optional)",
        default = "")
    thumbnail = bpy.props.BoolProperty(name="Thumbnail",
        description = "Automatically generated, using the default camera",
        default = True)
    thumbnail_path = bpy.props.StringProperty(name="Thumbnail filepath",
        description = "internal use",
        default = "")
    title = bpy.props.StringProperty(name="Title",
        description = "Title of the model (determined automatically if \
left empty)",
        default = "")
    token = bpy.props.StringProperty(name="Api Key",
        description = "You can find this on your dashboard at the Sketchfab \
website",
        default = "",
        update = update_token)
    token_reload = bpy.props.BoolProperty(name="Reload of token necessary?",
        description = "internal use",
        default = True)
    uploading = bpy.props.BoolProperty(name="Busy uploading",
        description = "internal use",
        default = False)


# registration
classes = [ExportSketchfab,
    ExportSketchfabBusy,
    SketchfabProps,
    VIEW3D_MT_popup_result,
    VIEW3D_PT_sketchfab]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.sketchfab = bpy.props.PointerProperty(\
        type = SketchfabProps)
    load_token()
    bpy.app.handlers.load_post.append(load_token)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        del bpy.types.WindowManager.sketchfab
    except:
        pass


if __name__ == "__main__":
    register()
