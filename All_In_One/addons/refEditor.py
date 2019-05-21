bl_info = {
    "name": "Ref Editor",
    "author": "Christophe Seux",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


import bpy
from bpy.app.handlers import persistent

Dupligroups={}

# Scan list of objects and return objects with linked dupligroup
def filter_dupliGroups(objects):
    dupliGroups =[]
    for o in objects :
        if o.dupli_group and o.dupli_group.library :
            dupliGroups.append(o)
    return dupliGroups

# Convert adress '/ob/ob'in bpy.data.objects['ob'].dupli_group.object['ob']
def pathConvert(path):
    blenderPath = 'bpy.data.objects'

    for index,name in enumerate(path.split('/')[1:]):
        if index ==0 :
            blenderPath+='["%s"]'%name
        else :
            blenderPath+='.dupli_group.objects["%s"]'%name

    return(eval(blenderPath))

# analyse scene for store level of linked dupli_grou in a dict
def link_analyser(objects,Path) :
    RefEditor = bpy.context.scene.RefEditor
    if not RefEditor.get('objects') :
        RefEditor['objects'] = {}

    for o in filter_dupliGroups(objects):
        #path = '%s["%s"]'%(Path,o.name)

        if not RefEditor['objects'].get(Path+'/'+o.name) :
            RefEditor['objects'][Path+'/'+o.name] = {'hide':False , 'expand' : False}

        else :
            o.hide = RefEditor['objects'][Path+'/'+o.name]['hide']

        filter_dupli = filter_dupliGroups(o.dupli_group.objects)
        if filter_dupli :
            link_analyser(filter_dupli,Path+'/'+o.name)

#bpy.context.scene.RefEditor['objects'] =Dupligroups



class refEditorSettings(bpy.types.PropertyGroup):
    search = bpy.props.StringProperty(options={'TEXTEDIT_UPDATE'})
    filterSelect = bpy.props.BoolProperty()
    objects = {}

class RefEditorHide(bpy.types.Operator):
    bl_idname = "refedit.hide"
    bl_label = "Hide linked dupligroup"

    object = bpy.props.StringProperty()

    def execute(self, context):
        object = self.object
        RefEditor = context.scene.RefEditor

        if RefEditor['objects'][object]['hide'] == True :
            pathConvert(object).hide = False
            RefEditor['objects'][object]['hide'] = False

        else :
            pathConvert(object).hide = True
            RefEditor['objects'][object]['hide'] = True

        return {'FINISHED'}

class RefEditorExpand(bpy.types.Operator):
    bl_idname = "refedit.expand"
    bl_label = "Expand dupligroup"

    object = bpy.props.StringProperty()

    def execute(self, context):
        object = self.object
        RefEditor = context.scene.RefEditor

        if RefEditor['objects'][object]['expand'] == True :
            RefEditor['objects'][object]['expand'] = False

        else :
            RefEditor['objects'][object]['expand'] = True

        return {'FINISHED'}

class RefEditorCreateProxy(bpy.types.Operator):
    bl_idname = "refedit.create_proxy"
    bl_label = "Create Proxy"

    object = bpy.props.StringProperty()

    def execute(self, context):
        object = self.object
        RefEditor = context.scene.RefEditor

        pathConvert(object)


        return {'FINISHED'}



class RefEditorPanel(bpy.types.Panel) :
    bl_label = "Reference Editor"
    bl_category = "Refs Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw_header(self, context):
        view = context.space_data
        layout = self.layout
        layout.label(icon= "OOPS")
        row = layout.row()

    def draw(self,context):
        layout = self.layout
        row = layout.row(align= True)
        row.prop(context.scene.RefEditor,'filterSelect',icon = 'RESTRICT_SELECT_OFF',text='',emboss=True)
        row.prop(context.scene.RefEditor,'search',icon = 'VIEWZOOM',text='')
        row.operator("refedit.hide",icon='EYEDROPPER',text='',emboss = False)

        box = layout.box()
        box.alignment='EXPAND'

        RefEditor = context.scene.RefEditor

        col = layout.column(align=True)

        if RefEditor.get('objects') :

            for key in sorted(RefEditor['objects']):

                object = pathConvert(key)
                depth = key.split('/')[1:]

                if RefEditor['objects'][key]['expand'] == True :
                    expandIcon = 'DISCLOSURE_TRI_DOWN'
                else :
                    expandIcon = 'DISCLOSURE_TRI_RIGHT'

                if RefEditor['objects'][key]['hide'] == False :
                    hideIcon ='RESTRICT_VIEW_OFF'
                else :
                    hideIcon ='RESTRICT_VIEW_ON'


                ExcludeObject=[]
                ChildObject = []


                if RefEditor.search.lower() not in object.name.lower() :
                    ExcludeObject.append(key)

                for otherKey,value in RefEditor['objects'].items() :
                    if otherKey != key and key.startswith(otherKey) and RefEditor['objects'][otherKey]['expand']==False :
                        ExcludeObject.append(key)

                    if otherKey != key and otherKey.startswith(key):
                        ChildObject.append(otherKey)

                if RefEditor.filterSelect == True and object not in context.selected_objects :
                    ExcludeObject.append(key)

                if key not in ExcludeObject :

                    row = col.row(align=True)

                    for i in range(1, len(depth)) :
                        row.separator()

                    if  not ChildObject:
                        row.label(icon ='LAYER_USED')
                    else :
                        row.operator("refedit.expand",emboss = False,icon=expandIcon,text='').object =key

                    row.label(object.name)
                    row.operator("refedit.create_proxy",emboss = False,icon='EMPTY_DATA',text ='').object = key
                    row.operator("refedit.hide",emboss = False,icon=hideIcon,text ='').object =key



cls = [refEditorSettings,RefEditorHide,RefEditorExpand,RefEditorPanel,RefEditorCreateProxy]

@persistent
def my_handler(dummy):
    link_analyser(bpy.context.scene.objects,'')



def register():
    for c in cls :
        bpy.utils.register_class(c)

    bpy.types.Scene.RefEditor= bpy.props.PointerProperty(type = refEditorSettings)
    bpy.app.handlers.load_post.append(my_handler)

def unregister():
    for c in cls :
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.RefEditor
    bpy.app.handlers.load_post.remove(my_handler)
