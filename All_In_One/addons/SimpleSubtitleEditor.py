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

# This directory is a Python package.

bl_info = {
    "name": "Simple Subtitle Editor",
    "author": "James Ruan",
    "version": (0, 2, 2),
    "blender": (2, 79, 0),
    "api": 40779,
    "location": "VSE > Properties > Simple Subtitle Editor",
    "description": "Simple subtitle editor",
    "warning": "Format guess is based on filename extension.",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Sequencer/SimpleSubtitleEditor",
    "tracker_url": "https://github.com/jamesruan/SimpleSubtitleEditor/issues",
    "category": "Learnbgame",
}

import bpy

def timecode2frameno(timecode, fps, format="srt"):
    if format == "srt":
        s = timecode.split(',')
        ms = int(s[1])
        h,m,s = map(int, s[0].split(':'))
        frame = int(ms/1000*fps+0.5)
        m += h*60
        s += m*60
        frame += s*fps
    elif format == "sub":
        s = timecode.split('.')
        hs = int(s[1])
        h, m, s = map(int, s[0].split(':'))
        frame = int(hs/100*fps+0.5)
        m += h*60
        s += m*60
        frame += s*fps
    return frame

def frameno2timecode(frameno, fps, format="srt"):
    if format == "srt":
        s, ms = divmod(frameno, fps)
        ms = int(ms/fps *1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d,%03d"%(h,m,s,ms)
    elif format == "sub":
        s, hs = divmod(frameno, fps)
        hs = int(hs/fps * 100)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d.%02d"%(h,m,s,hs)


class MarkerExportOperator(bpy.types.Operator):
    """Export markers to file"""
    bl_idname = "marker.sse_export"
    bl_label = "Export markers to file"

    def execute(self, context):
        scene = context.scene
        m = []
        if not scene.sse_outfile:
            raise Exception("You must select or name a file to write to.")
        ext = scene.sse_outfile.rsplit('.')[-1]
        if ext == "srt" or ext == "SRT":
            format = "srt"
        elif ext == "sub" or ext =="SUB":
            format = "sub"
        else:
            scene.sse_outfile += ".srt"
            format = "srt"

        if format == "srt":
            f = open(scene.sse_outfile, mode='wt')
            fps = scene.render.fps
            for n in scene.sse_sublist:
                s = scene.timeline_markers["S%03d"%(n.index)].frame
                e = scene.timeline_markers["E%03d"%(n.index)].frame
                s = frameno2timecode(s, fps, "srt")
                e = frameno2timecode(e, fps, "srt")
                l = "%d\n%s --> %s\n%s\n"%(n.index, s, e, n.text.replace('\\n','\n'))
                m.append(l)
            f.writelines("\n".join(m))
        elif format == "sub":
            f = open(scene.sse_outfile, mode='wt')
            fps = scene.render.fps
            for n in scene.sse_sublist:
                s = scene.timeline_markers["S%03d"%(n.index)].frame
                e = scene.timeline_markers["E%03d"%(n.index)].frame
                s = frameno2timecode(s, fps, "sub")
                e = frameno2timecode(e, fps, "sub")
                l = "%s,%s\n%s\n"%(s, e, n.text.replace('\\n','[br]'))
                m.append(l)
            header="""[INFORMATION]
[TITLE]
[AUTHOR]
[SOURCE]
[FILEPATH]
[DELAY]
[COMMENT]
[END INFORMATION]
[SUBTITLE]
"""
            f.write(header)
            f.writelines("\n".join(m))
#        print(m)
        return {'FINISHED'}

class MarkerImportOperator(bpy.types.Operator):
    bl_idname = "marker.sse_import"
    bl_label = "Import markers from file"

    def execute(self,context):
        scene = context.scene
        for i in range(0, len(scene.sse_sublist)):
            scene.sse_sublist.remove(0)

        for i in scene.timeline_markers:
            scene.timeline_markers.remove(i)
        m = []

        if not scene.sse_infile:
            raise Exception("You must select a file to open.")
            return
        ext = scene.sse_infile.rsplit('.')[-1]
        if ext == "srt" or ext == "SRT":
            format = "srt"
        elif ext == "sub" or ext =="SUB":
            format = "sub"
        else:
            raise Exception("Can not open file of format: %s"%(ext))
            return

        if format == "srt":
            f = open(scene.sse_infile)
            all = "".join(f.readlines()).replace('\n\n',"\n#SEP#").split('#SEP#')
            all = [x.strip('\n').splitlines() for x in all]
            all = [x for x in all if x != []]
            for i in all:
                n = {}
                n['i'] = int(i[0])
                t = i[1].split('-->')
                n['s'] = t[0].strip()
                n['e'] = t[1].strip()
                n['t'] = '\\n'.join(i[2:])
                m.append(n)
            f.close()
        elif format == "sub":
            f = open(scene.sse_infile)
            #skip all INFORMATION
            all = "".join(f.readlines()).rsplit('[SUBTITLE]\n')[-1].replace('\n\n',"\n#SEP#").split('#SEP#')
            all = [x.strip('\n').splitlines() for x in all]
            all = [x for x in all if x != []]
            print(all)
            for k in range(1, len(all)+1):
                n = {}
                n['i'] = k
                t = all[k-1][0].split(',')
                n['s'] = t[0].strip()
                n['e'] = t[1].strip()
                n['t'] = '[br]'.join(all[k-1][1:])
                m.append(n)
            f.close()
        #print(m)
        fps = scene.render.fps

        for n in m:
            i = scene.sse_sublist.add()
            s = scene.timeline_markers.new(name="S%03d"%(n['i']))
            s.frame = timecode2frameno(n['s'], fps, format)
            e = scene.timeline_markers.new(name="E%03d"%(n['i']))
            e.frame = timecode2frameno(n['e'], fps, format)
            i.index = n['i']
            i.text = n['t']
        return {'FINISHED'}

class MarkerSelectOperator(bpy.types.Operator):
    '''Select markers based on name'''
    bl_idname = "marker.sse_select"
    bl_label = "Select based on name"
    name = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.marker.select_all(action='DESELECT')
        context.scene.timeline_markers["S"+self.name].select = True
        context.scene.timeline_markers["E"+self.name].select = True
        return {'FINISHED'}

class MarkerAddOperator(bpy.types.Operator):
    '''Add markers with name'''
    bl_idname = "marker.sse_add"
    bl_label = "Add subtitle markers"
    name = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        item = scene.sse_sublist.add()
        item.index = int(len(scene.sse_sublist))
        m = scene.timeline_markers.new(name="S"+self.name)
        m.frame = scene.frame_current
        m = scene.timeline_markers.new(name="E"+self.name)
        m.frame = scene.frame_current+3

        item.text = "New Subtitle"
        return {'FINISHED'}

class MarkerDelOperator(bpy.types.Operator):
    '''Delelte markers with name'''
    bl_idname = "marker.sse_del"
    bl_label = "Delete subtitle markers"
    name = bpy.props.StringProperty()

    def execute(self, context):
        for i in range(0, len(context.scene.sse_sublist)):
            if context.scene.sse_sublist[i].index == int(self.name):
                context.scene.sse_sublist.remove(i)
                break
        bpy.ops.marker.sse_select(name=self.name)
        bpy.ops.marker.delete()
        for i in context.scene.sse_sublist:
            if i.index > int(self.name):
                i.index -= 1
                bpy.ops.marker.select_all(action='DESELECT')
                context.scene.timeline_markers["S"+"%03d"%(i.index+1)].select = True
                context.scene.timeline_markers["S"+"%03d"%(i.index+1)].name =("S"+"%03d"%(i.index))
                bpy.ops.marker.select_all(action='DESELECT')
                context.scene.timeline_markers["E"+"%03d"%(i.index+1)].select = True
                context.scene.timeline_markers["E"+"%03d"%(i.index+1)].name =("E"+"%03d"%(i.index))
        return {'FINISHED'}

class SSE_Sublist(bpy.types.PropertyGroup):
    index = bpy.props.IntProperty()
    text = bpy.props.StringProperty()

class SSEPanel(bpy.types.Panel):
    bl_label = "Simple Subtitle Editor"
    bl_idname = "OBJECT_PT_SSE"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        scene = context.scene

        layout = self.layout
        col = layout.column()
        row = col.row()
        row.label("Input:")
        row.prop(scene, "sse_infile", text="")
        row.operator("marker.sse_import",text="", icon='FILE_TICK')
        col.separator()

        for i in scene.sse_sublist:
            row = col.row()
            a = row.operator("marker.sse_select",text="%03d"%(i.index), icon='MARKER_HLT')
            a.name = "%03d"%(i.index)
            s = scene.timeline_markers["S"+"%03d"%(i.index)].frame
            e = scene.timeline_markers["E"+"%03d"%(i.index)].frame
            if s < e:
                row.label(text="S:%d"%(s))
                row.label(text="E:%d"%(e))
            else:
                row.label(text="S:%d"%(s), icon='ERROR')
                row.label(text="E:%d"%(e), icon='ERROR')
            a = row.operator("marker.sse_del", text="", icon='ZOOMOUT')
            a.name = "%03d"%(i.index)
            col.prop(i, "text")

        col.separator()
        a = col.operator("marker.sse_add",text="new", icon='ZOOMIN')
        a.name = "%03d"%(len(context.scene.sse_sublist)+1)
        row = col.row()
        row.label("Output:")
        row.prop(scene, "sse_outfile", text="")
        row.operator("marker.sse_export",text="", icon='FILE_TICK')

def register():
    bpy.utils.register_class(MarkerImportOperator)
    bpy.utils.register_class(MarkerExportOperator)
    bpy.utils.register_class(MarkerSelectOperator)
    bpy.utils.register_class(MarkerAddOperator)
    bpy.utils.register_class(MarkerDelOperator)
    bpy.utils.register_class(SSE_Sublist)
    bpy.utils.register_class(SSEPanel)
    setattr(bpy.types.Scene, "sse_infile", bpy.props.StringProperty(name="sse_infile", subtype='FILE_PATH', description="filename to import from"))
    setattr(bpy.types.Scene, "sse_outfile", bpy.props.StringProperty(name="sse_outfile", subtype='FILE_PATH', description="filename to export into"))
    setattr(bpy.types.Scene, "sse_sublist", bpy.props.CollectionProperty(type=SSE_Sublist))

def unregister():
    bpy.utils.unregister_class(MarkerImportOperator)
    bpy.utils.unregister_class(MarkerExportOperator)
    bpy.utils.unregister_class(MarkerSelectOperator)
    bpy.utils.unregister_class(MarkerAddOperator)
    bpy.utils.unregister_class(MarkerDelOperator)
    bpy.utils.unregister_class(SSE_Sublist)
    bpy.utils.unregister_class(SSEPanel)
    delattr(bpy.types.Scene, "sse_infile")
    delattr(bpy.types.Scene, "sse_outfile")
    delattr(bpy.types.Scene, "sse_sublist")

if __name__ == '__main__':
    register()

