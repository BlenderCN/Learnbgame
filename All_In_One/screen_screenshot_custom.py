bl_info = {
    "name": "Custom Screenshot Creator",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "Save Screenshot Custom",
    "description": "Create screenshots of all the individual areas in the current screen (and the whole area also if you want)",
    "warning": "",
    "category": "Learnbgame",
}


import bpy
import os


class OutputFilename(object):
    filename = 'untitled'
    suffix = None
    suffix_char = '_'
    dirname = os.getcwd()

    def __init__(self, filepath, ext, suffix=''):
        self.filename = bpy.path.display_name_from_filepath(filepath)
        self.dirname = os.path.dirname(filepath)
        self.ext = ext

        if suffix:
            self.suffix=suffix

    def getSuffix(self):
        return self.suffix_char + self.suffix

    @property
    def filepath(self):
        filename = self.filename
        if self.suffix:
            filename += self.getSuffix()

        filename += '.' + self.ext
        return os.path.join(self.dirname, filename)


class OutputIndexedFilename(OutputFilename):
    suffix_index = 0

    def __init__(self, filepath, ext, suffix='', suffix_index=0):
        super(OutputIndexedFilename, self).__init__(filepath, ext, suffix)
        if suffix_index:
            self.suffix_index = suffix_index

    def getSuffix(self):
        suffix_base = super(OutputIndexedFilename, self).getSuffix()
        return '.'.join([suffix_base, "{0:02}".format(self.suffix_index)])


class ScreenCaptureTask(object):
    def __init__(self, context, full=True, filepath=''):
        self.context = context
        self.full = full
        self.filepath = filepath

    @property
    def kwargs(self):
        return {'full': self.full, 'filepath': self.filepath}


class ScreenCapture(object):
    def __init__(self, context):
        self.context = context
        self.tasks = []

    def __call__(self, mode):
        if mode in map(lambda mode: mode[0], self.modes):
            getattr(self, mode.lower())()
        else:
            return False

        self.run()
        return True

    def run(self):
        for task in self.tasks:
            before = getattr(task, 'before', None)

            if before:
                print("Before: ", task.kwargs['filepath'])
                before(task)
                print(self.context.scene.render.filepath)
                print(self.context.scene.render.image_settings.file_format)

            self.execute(task.context, **task.kwargs)

            after = getattr(task, 'after', None)

            if after:
                print("After: ", task.kwargs['filepath'])
                after(task)
                print(self.context.scene.render.filepath)
                print(self.context.scene.render.image_settings.file_format)

    @staticmethod
    def _prepare_context(context, area=None):
        overridden_context = context.copy()

        if area:
            overridden_context.update((
                                ('area', area),
                                ('region', area.regions[1]),
                                ('space_data', area.spaces.active)
                            ))

        return overridden_context

    def getOutput(self, area=None, index=0):
        if area:
            return OutputIndexedFilename(self.context.blend_data.filepath, self.ext, area.type, index)
        else:
            return OutputFilename(self.context.blend_data.filepath, self.ext)

    def createTask(self, context, full, output):
        task = ScreenCaptureTask(context, full, output.filepath)
        self.tasks.append(task)
        return task

    def _handle_area(self, area, index=0):
        context = self.__class__._prepare_context(self.context, area)

        output = self.getOutput(area, index)
        self.dirname = output.dirname

        self.createTask(context, False, output)

    def screen(self):
        context = self.__class__._prepare_context(self.context)

        output = self.getOutput()
        self.dirname = output.dirname

        self.createTask(context, True, output)

    def screen_active_area(self):
        area = self.context.area
        self._handle_area(area)


class Screenshot(ScreenCapture):
    execute = bpy.ops.screen.screenshot
    ext = 'png'

    modes = [('SCREEN', 'Current Screen', 'Capture the current screen'),
              ('SCREEN_ACTIVE_AREA', 'Active Screen Area', 'Capture the active screen area'),
              ('SCREEN_ALL_AREAS', 'All Screen Areas', 'Capture all the areas of the current screen'),
              ('SCREEN_AND_ALL_AREAS', 'Current Screen and all Areas', 'Capture screen and also all its areas'),
            ]

    def __init__(self, context):
        super(Screenshot, self).__init__(context)

    def screen_all_areas(self):
        from itertools import groupby

        area_map = {}

        criterion = lambda area: area.type

        for key, group in groupby(sorted(self.context.screen.areas, key=criterion), criterion):
            area_map[key] = tuple(group)

        for area_type, areas in area_map.items():
            for index, area in enumerate(areas):
                self._handle_area(area, index)

    def screen_and_all_areas(self):
        self.screen()
        self.screen_all_areas()


def before_screencast(self):
    scene = self.context['scene']
    render = scene.render
    imgs = render.image_settings

    self.overrides = {}

    self.overrides['filepath'] = render.filepath
    render.filepath = self.kwargs['filepath']

    self.overrides['file_format'] = imgs.file_format
    imgs.file_format = 'H264'

    scene.update()


def after_screencast(self):
    scene = self.context['scene']
    render = scene.render
    imgs = render.image_settings

    render.filepath = self.overrides['filepath']
    imgs.file_format = self.overrides['file_format']

    scene.update()


class Screencast(ScreenCapture):
    execute = bpy.ops.screen.screencast
    ext = 'mp4'

    modes = [('SCREEN', 'Current Screen', 'Capture the current screen'),
              ('SCREEN_ACTIVE_AREA', 'Active Screen Area', 'Capture the active screen area')
            ]

    def __init__(self, context):
        super(Screencast, self).__init__(context)

    def createTask(self, context, full, output):
        task = super(Screencast, self).createTask(context, full, output)
        setattr(task, 'before', before_screencast)
        setattr(task, 'after', after_screencast)
        return task


def _observer_file_browser(subject):
    from rna_info import get_direct_properties

    window_manager = subject.context['window_manager']
    screen = subject.context['screen']

    FILE_BROWSER = lambda area: area.spaces.active.type == 'FILE_BROWSER'
    SCREENSHOT_DIRECTORY = lambda params: window_manager.clipboard in params.directory
    to_update_filebrowser = lambda area: FILE_BROWSER(area) and SCREENSHOT_DIRECTORY(area.spaces.active.params)
    use_filter_props = lambda prop: prop.identifier.startswith('use_filter')

    overrides = subject.context.copy()

    file_browser_areas = filter(to_update_filebrowser, screen.areas)

    for file_browser in file_browser_areas:
        params = file_browser.spaces.active.params

        for prop in filter(use_filter_props , get_direct_properties(params.bl_rna)):
            setattr(params, prop.identifier, False)

        params.use_filter = True
        params.use_filter_image = True
        params.display_type = 'FILE_IMGDISPLAY'

        overrides['area'] = file_browser
        overrides['space_data'] = file_browser.spaces.active

        bpy.ops.file.refresh(overrides)


def _observer_clipboard(subject):
    window_manager = subject.context['window_manager']
    window_manager.clipboard = subject.output.dirname


class ScreenCaptureBase(object):
    bl_options = {'REGISTER', 'MACRO', 'UNDO'}

    def __init__(self):
        print("Initializing " + self.bl_idname)

    def invoke(self, context, event):
        print("Invoking " + self.bl_idname)
        if (self.configuredKeys(event)):
            return self.execute(context)
        else:
            return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        print("Executing " + self.bl_idname)

        ret = self.delegated_execute(context)

        if not ret:
            self.report({'ERROR'}, "{0}: No other capture modes supported".format(self.bl_idname))
            return {'CANCELLED'}

        #self.report({'INFO'}, "Screenshot saved in {0}".format(context.window_manager.clipboard))

        return {'FINISHED'}

    def __del__(self):
        print("Destructing " + self.bl_idname)


class ScreenshotCustom(bpy.types.Operator, ScreenCaptureBase):
    """Create and save screenshots of different areas"""
    bl_idname = "screen.screenshot_custom"
    bl_label = "Save Screenshot Custom"

    capture_mode = bpy.props.EnumProperty(items=Screenshot.modes, name="Capture mode", default='SCREEN_AND_ALL_AREAS')

    def configuredKeys(self, event):
        return event.oskey and event.type == 'C'

    def delegated_execute(self, context):
        return Screenshot(context)(self.capture_mode)


class ScreencastCustom(bpy.types.Operator, ScreenCaptureBase):
    """Create and save screencasts"""
    bl_idname = "screen.screencast_custom"
    bl_label = "Save Screencast Custom"

    capture_mode = bpy.props.EnumProperty(items=Screencast.modes, name="Capture mode", default='SCREEN')

    def configuredKeys(self, event):
        return event.oskey and event.type == 'X'

    def delegated_execute(self, context):
        return Screencast(context)(self.capture_mode)


def keymap_items_add(keymap_items, capture_mode_mapping, operator, key):
    for capture_mode, kwargs in capture_mode_mapping:
        kmi = keymap_items.new(operator.bl_idname, key, 'PRESS', oskey=True, **kwargs)
        setattr(kmi.properties, 'capture_mode', capture_mode)


def keymap_items_remove(keymap_items, capture_modes, operator):
    for i in capture_modes:
        kmi = keymap_items[operator.bl_idname]
        keymap_items.remove(kmi)


def register():
    bpy.utils.register_class(ScreenshotCustom)
    bpy.utils.register_class(ScreencastCustom)

    addonKeyConfig = bpy.context.window_manager.keyconfigs.addon

    if 'Screen' not in addonKeyConfig.keymaps:
        addonKeyConfig.keymaps.new('Screen')

    keymap_items = addonKeyConfig.keymaps['Screen'].keymap_items

    capture_mode_mapping = (('SCREEN', {}),
                            ('SCREEN_ACTIVE_AREA', {'alt': True}),
                            ('SCREEN_ALL_AREAS', {'shift': True}),
                            ('SCREEN_AND_ALL_AREAS', {'ctrl': True}),
                            )

    keymap_items_add(keymap_items, capture_mode_mapping, ScreenshotCustom, 'C')

    capture_mode_mapping = (('SCREEN', {'ctrl': True}),
                            ('SCREEN_ACTIVE_AREA', {'alt': True, 'ctrl':True}),
                            )

    keymap_items_add(keymap_items, capture_mode_mapping, ScreencastCustom, 'X')

def unregister():
    keyconfigs = bpy.context.window_manager.keyconfigs
    keymap_items = keyconfigs.addon.keymaps['Screen'].keymap_items

    keymap_items_remove(keymap_items, Screenshot.modes, ScreenshotCustom)
    keymap_items_remove(keymap_items, Screencast.modes, ScreencastCustom)

    bpy.utils.unregister_class(ScreenshotCustom)
    bpy.utils.unregister_class(ScreencastCustom)


if __name__ == '__main__':
    register()
    #bpy.ops.screen.screenshot_custom()
