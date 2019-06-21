# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/1d_timeline_render
#
# Version history:
#   1.0. - Render frames from the first line of the text block by numbers and diapasones


import os
import bpy


class TimeLineRender:

    frames = []
    currentframe = None

    @staticmethod
    def startrender(context):
        print('-- STARTED --')
        __class__.clear()
        __class__.getframestorender()
        if __class__.frames:
            __class__.rendernextframe(context)
        else:
            __class__.clear()
            print('-- NO FRAMES TO RENDER --')

    @staticmethod
    def rendernextframe(context):
        if __class__.frames:
            __class__.currentframe = __class__.frames.pop()
            __class__.setframetorender(context, __class__.currentframe)
            if __class__.onrenderfinished not in bpy.app.handlers.render_complete:
                bpy.app.handlers.render_complete.append(__class__.onrenderfinished)
            if __class__.onrendercancel not in bpy.app.handlers.render_cancel:
                bpy.app.handlers.render_cancel.append(__class__.onrendercancel)
            if __class__.onsceneupdate_startrender not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate_startrender)
        else:
            __class__.clear()
            print('-- FINISHED --')

    @staticmethod
    def setframetorender(context, frame):
        context.screen.scene.frame_current = frame

    @staticmethod
    def getframestorender():
        if TimeLineRenderOptions.textblockname in bpy.data.texts:
            line = bpy.data.texts[TimeLineRenderOptions.textblockname].lines[0].body
            if line:
                linearr = line.split(TimeLineRenderOptions.framesdelimiter)
                linearrframes = [int(i) for i in linearr if TimeLineRenderOptions.diapasonedelimiter not in i]
                linearrdiapasones = sum([list(range(int(i.split('-')[0]), int(i.split('-')[1])+1)) for i in linearr if TimeLineRenderOptions.diapasonedelimiter in i], [])
                linearrframes.extend(linearrdiapasones)
                __class__.frames = list(set(linearrframes))

    @staticmethod
    def checktextblock(context):
        textblock = None
        textblockmode = None
        if TimeLineRenderOptions.textblockname in bpy.data.texts:
            textblock = bpy.data.texts[TimeLineRenderOptions.textblockname]
            textblockmode = 'OK'
        else:
            textblock = bpy.data.texts.new(name=TimeLineRenderOptions.textblockname)
            textblock.from_string(TimeLineRenderOptions.emptyshablon)
            textblock.name = TimeLineRenderOptions.textblockname
            textblockmode = 'SAMPLE'
        if textblock:
            areatoshow = None
            for area in context.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    areatoshow = area
            if not areatoshow:
                for area in context.screen.areas:
                    if area.type not in ['PROPERTIES', 'INFO', 'OUTLINER']:
                        areatoshow = area
                        break
            if areatoshow:
                areatoshow.type = 'TEXT_EDITOR'
                areatoshow.spaces.active.text = textblock
                textblock.current_line_index = 0
        return textblockmode

    @staticmethod
    def saverenderrezult():
        destdir = __class__.destdir()
        if destdir:
            filename = TimeLineRenderOptions.fileprefix + '{:04}'.format(__class__.currentframe) + '.' + __class__.extension(bpy.context)
            filepath = os.path.join(destdir, filename)
            for currentarea in bpy.context.window_manager.windows[0].screen.areas:
                if currentarea.type == 'IMAGE_EDITOR':
                    overridearea = bpy.context.copy()
                    overridearea['area'] = currentarea
                    bpy.ops.image.save_as(overridearea, copy=True, filepath=filepath)
                    print('-- FINISHED RENDER FRAME ', __class__.currentframe, ' --')
                    break
        else:
            print('Error - no destination directory')

    @staticmethod
    def destdir():
        dir = None
        if bpy.data.filepath:
            dir = os.path.join(os.path.dirname(bpy.data.filepath), os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        else:
            dir = os.path.join(os.path.dirname(bpy.context.user_preferences.filepaths.temporary_directory), 'TimeLineRender')
        return dir

    @staticmethod
    def extension(context):
        extensions = {'JPEG': 'jpg', 'PNG': 'png'}
        return extensions[context.scene.render.image_settings.file_format]

    @staticmethod
    def clear():
        __class__.frames = []
        __class__.currentframe = None
        if __class__.onrenderfinished in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(__class__.onrenderfinished)
        if __class__.onrendercancel in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(__class__.onrendercancel)
        if __class__.onsceneupdate_startrender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_startrender)
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)

    @staticmethod
    def onsceneupdate_startrender(scene):
        # start render on scene update
        if __class__.onsceneupdate_startrender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_startrender)
        status = bpy.ops.render.render('INVOKE_DEFAULT')
        if status == {'CANCELLED'}:
            if __class__.onsceneupdate_startrender not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate_startrender)

    @staticmethod
    def onsceneupdate_saverender(scene):
        # save render rezult on scene update
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)
        __class__.saverenderrezult()
        # and start next render
        __class__.rendernextframe(bpy.context)

    @staticmethod
    def onrenderfinished(scene):
        # render finished - save render result on next scene update
        if __class__.onsceneupdate_saverender not in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate_saverender)

    @staticmethod
    def onrendercancel(scene):
        # render aborted
        __class__.clear()
        print('-- ABORTED BY USER --')


class TimeLineRenderOptions:

    textblockname = 'TimeLineRender.txt'
    emptyshablon = '1,2,7-9,4\n# В первой строке указываются номера и диапазоны кадров для рендера'
    framesdelimiter = ','
    diapasonedelimiter = '-'
    fileprefix = 'TR_'
