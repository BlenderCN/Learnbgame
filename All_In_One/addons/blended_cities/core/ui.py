##\file
# ui.py
# core and shared user interface components
print('ui.py')
import bpy
import bgl
import blf

from blended_cities.utils.meshes_io import *
from blended_cities.utils.ui_tools import *
from blended_cities.core.common import *

########################
## COMMON UI OPERATORS 
########################

## city and outlines methods from ui
# example city.init() is called from here by the ui : ops.city.methods(action = 'init')
class OP_BC_cityMethods(bpy.types.Operator) :
    bl_idname = 'city.methods'
    bl_label = 'city methods'

    action = bpy.props.StringProperty()

    def execute(self, context) :
        city = bpy.context.scene.city
        act = objs = builder = opt1 = opt2 = ''
        args = self.action.split(' ')
        if len(args)   == 1 : act = args[0]
        elif len(args) == 2 : act, objs = args
        elif len(args) == 3 : act, objs, builder = args
        elif len(args) == 4 : act, objs, builder, opt1 = args
        else : act, objs, builder, opt1, opt2 = args

        print('\naction : %s \nobjects : %s \nbuilder : %s \nopt1 : %s \nopt2 : %s\n'%(act,objs,builder,opt1,opt2))

        if act == 'init' :
            city.init()
            return {'FINISHED'}

        elif act == 'build' :
            objs = city.build(objs,builder)
            print('builded %s objects'%(len(objs)))
            return {'FINISHED'}

        elif act == 'list' :
            city.list(objs,builder)
            return {'FINISHED'}

        elif act == 'stack_grp' :
            new_grps = city.groupStack(objs,builder)
            print('stacked %s new %s\n'%(len(new_grps),builder))
            # list & select them
            if len(new_grps) > 0 :
                for grp in new_grps :
                    display(grp,'group')
            return {'FINISHED'}

        elif act == 'add' :
            new_objs = city.elementAdd(objs,builder)
            print('created %s new %s\n'%(len(new_objs),builder))
            if len(new_objs) > 0 :
                for grp, otl in new_objs :
                    display(otl)
            return {'FINISHED'}

        elif act == 'remove_otl' :
            if opt1 == 'elm_obj' :
                rem_self = True
                rem_elements = True
                rem_objects = True
            elif opt1 == 'elm_only' :
                rem_self = True
                rem_elements = True
                rem_objects = False
            elif opt1 == 'obj_only' :
                rem_self = False
                rem_elements = False
                rem_objects = True
            rem_childs = eval(opt2)
            del_objs = city.outlineRemove(objs,rem_self,rem_elements,rem_objects,rem_childs)
            print('removed %s objects from %s\n'%(len(del_objs),builder))
            # list them
            return {'FINISHED'} 

        elif act == 'add_grp' :
            if opt1 == '' : opt1 = 'True'
            new_grps = city.groupAdd(objs,builder)
            return {'FINISHED'} 

        elif act == 'remove_grp' :
            if opt1 == 'elm_obj' :
                rem_self = True
                rem_elements = True
                rem_objects = True
            elif opt1 == 'elm_only' :
                rem_self = True
                rem_elements = True
                rem_objects = False
            elif opt1 == 'obj_only' :
                rem_self = False
                rem_elements = False
                rem_objects = True
            rem_childs = eval(opt2)
            del_objs = city.groupRemove(objs,rem_self,rem_elements,rem_objects,rem_childs)
            return {'FINISHED'} 

        elif act == 'replace_grp' :
            rep_objs = city.groupReplace(objs,builder)
            if len(rep_objs) > 0 :
                for grp in rep_objs :
                    display(grp,'group')
            return {'FINISHED'} 

        else : return {'CANCELLED'}


## Operator called by drawElementSelector
class OP_BC_Selector(bpy.types.Operator) :
    bl_idname = 'city.selector'
    bl_label = 'Next'

    action = bpy.props.StringProperty()

    def execute(self, context) :
        city = bpy.context.scene.city
        elm, action = self.action.split(' ')
        otl = city.elements[elm].asOutline()
        if action == 'child' :
            otl.selectChild(True)
        elif action == 'parent' :
            otl.selectParent(True)
        elif action == 'next' :
            otl.selectNext(True)
        elif action == 'previous' :
            otl.selectPrevious(True)
        elif action == 'edit' :
            otl.select()
            bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

################
## MODAL CONTROL
################

class BC_City_ui_helpers(bpy.types.PropertyGroup) :

    def start(self) :
        mdl = bpy.context.scene.city.modal
        mdl.func = 'bpy.context.scene.city.ui.helpers.modal(self,context,event)'
        mdl.hudfunc = 'bpy.context.scene.city.ui.helpers.hud'
        mdl.area = 'VIEW_3D'
        mdl.hud = True
        mdl.status = True
        return mdl.status

    def stop(self) :
        mdl = bpy.context.scene.city.modal
        mdl.status = False
        return mdl.status
        print('stopped?')

    ## the HUD function called from script events (TO DO)
    def hud(dummy, self, context) :
        if 'type' in dir(self) :
            city = bpy.context.scene.city
            mdl = city.modal
            evt = self
            
            x_min,x,x_max = self._regions
            y_min,y_max = self._regionsy

            if x < self.mouse_x < x_max and y_min < self.mouse_y < y_max :
                mouse_x = self.mouse_x - x
                mouse_y = self.mouse_y - y_min
            else :
                mouse_x = False
                mouse_y = False
                
            # timer
            if mdl.timer :
                if evt.type == 'TIMER' : self.idx = (self.idx + 1)%4
                blf.size(0, 11, 72)
                blf.position(0, 35, 50, 0)
                blf.draw(0, "timer %1.3f : %s"%( mdl.timer_refresh, ('|/-\\')[self.idx]) )

            # is over ?
            overcrop = False
            bgl.glColor4f(1,1,1,1)
            #if mouse_x :
            blf.position(0, 35, 35, 0)
            blf.size(0, 11, 72)
            blf.draw(0, 'Mx: %s My: %s %s'%(mouse_x, mouse_y,self._regions))
            blf.position(0, 35, 20, 0)
            blf.size(0, 11, 72)
            blf.draw(0, 'Mx: %s My: %s'%(self.mouse_x, self.mouse_y))



    ## the modal function called from script events (TO DO)
    def modal(self,self_mdl,context,event) :
            city = bpy.context.scene.city
            #dprint('modal')
            #print('chui la')
            if bpy.context.mode == 'OBJECT' and \
            len(bpy.context.selected_objects) == 1 and \
            type(bpy.context.active_object.data) == bpy.types.Mesh :
                elm, grp, otl = city.elementGet('active',True)
                if elm :
                    if elm.className(False) == 'outlines' :
                        otl.build()
                    else :
                        grp.build()
            '''
                if elm.className() == 'buildings' or elm.peer().className() == 'buildings' :
                    dprint('rebuild')
                    if elm.className() == 'buildings' :
                        blg = elm
                    else :
                        blg = elm.peer()
                    dprint('rebuild')
                    blg.build(True)

            if event.type in ['TAB','SPACE'] :
                self.go_once = True

            if event.type in ['G','S','R'] :
                self.go=False
                
                if bpy.context.mode == 'OBJECT' and \
                len(bpy.context.selected_objects) == 1 and \
                type(bpy.context.active_object.data) == bpy.types.Mesh :
                    elm = self.elementGet(bpy.context.active_object)
                    if elm : self.go=True

            elif event.type in ['ESC','LEFTMOUSE','RIGHTMOUSE'] :
                    self.go=False
                    self.go_once=False
                    #dprint('modal paused.')
                    #mdl.log = 'paused.'
                    #context.region.callback_remove(self._handle)

            if event.type == 'TIMER' and (self.go or self.go_once) :
                        #self_mdl.log = 'updating...'

                        #dprint('event %s'%(event.type))
                        elm = self.elementGet(bpy.context.active_object)
                        #dprint('modal acting')

                        if elm.className() == 'buildings' or elm.peer().className() == 'buildings' :
                            if elm.className() == 'buildings' :
                                blg = elm
                            else :
                                blg = elm.peer()
                            dprint('rebuild')
                            blg.build(True)
            #bpy.ops.object.select_name(name=self.name)
                        self.go_once = False
                        #if self.go == False : mdl.log = 'paused.'
            '''


#################################################
## set of generic update functions used in builders classes
#################################################


## can be used by the update function of the panel properties of a builder
#
# to rebuild the selected element. group it's a 'link' function to the groups.build() function
#
# defined in the builders class element
def updateBuild(self,context='') :
    self = self.asGroup()
    self.build()


#
#
def updateStartModal(self,context='') :
    ui = bpy.context.scene.city.ui
    helpers = ui.helpers
    if ui.startmodal_updated == False :
        ui.startmodal_updated = True
        if ui.startmodal :
            ui.startmodal = helpers.start()
        else :
            ui.startmodal = helpers.stop()
        print('there')
    else :
        ui.startmodal_updated = False

# checkbox trick for remove option
# ui.updated = 3 since this func will be called 3 times each time because of update recursion.
def updateRemoveOptions(self,context='') :
    ui = bpy.context.scene.city.ui
    if ui.updated == 0 :
        if ui.elm_obj  != ui.remove_options[0] :
            ui.remove_options[0] = True
            ui.remove_options[1] = False
            ui.remove_options[2] = False
            ui.updated = 3
            ui.elm_obj = True
            ui.elm_only = False
            ui.obj_only = False
        elif ui.elm_only  != ui.remove_options[1] :
            ui.remove_options[0] = False
            ui.remove_options[1] = True
            ui.remove_options[2] = False
            ui.updated = 3
            ui.elm_obj = False
            ui.elm_only = True
            ui.obj_only = False
        elif ui.obj_only  != ui.remove_options[2] :
            ui.remove_options[0] = False
            ui.remove_options[1] = False
            ui.remove_options[2] = True
            ui.updated = 3
            ui.elm_obj = False
            ui.elm_only = False
            ui.obj_only = True
    else : ui.updated -= 1
    
########################
## UI PROPERTIES
########################
class BC_City_ui(bpy.types.PropertyGroup) :
    debug = bpy.props.IntProperty( name='debug level', min=0, max=5)
    # panel expand status
    expand_otl = bpy.props.BoolProperty(default=False)
    expand_grp = bpy.props.BoolProperty(default=False)
    # outline/group tabs toggle
    outlines_tabs_ops = bpy.props.EnumProperty(
            items = [ ('outline','Outline','display outline operations'),\
                      ('group','Group','display group operations')\
                    ]
            )
    outline_ops = bpy.props.EnumProperty( 
            items = [ ('remove_otl','Remove','remove the selected builders')
             ]
            )
    group_ops = bpy.props.EnumProperty(
            items = [ ('add_grp','Add','add a new builder to each selected outline'),\
                      ('stack_grp','Stack','stack this new builder over each selected ones'),\
                      ('replace_grp','Replace','replace each selected builders by this one'),\
                      ('remove_grp','Remove','remove the selected builders') ]
            )
    # the proper enum way for options, but an option is missing to display it the checkbox way.
    #remove_options = bpy.props.EnumProperty(
    #        items = [ ('elm_obj','All','Remove elements and their generated objects.'),\
    #                  ('elm_only','Elements','Remove only the elements. This will detach any generated object.'),\
    #                  ('obj_only','Objects','Remove only the generated objects.') ],
    #        options={'ANIMATABLE'}
    #        )
    # below is a trick using an update function (updateRemoveOptions above)
    remove_options = [True,False,False]
    elm_obj  = bpy.props.BoolProperty(
        name = 'All',
        default = remove_options[0],
        update = updateRemoveOptions,
        description = 'Remove elements and their generated objects')

    elm_only = bpy.props.BoolProperty(
        name='Elements',
        default=remove_options[1],
        update=updateRemoveOptions,
        description = 'Remove only the elements. This will detach any generated object.')

    obj_only = bpy.props.BoolProperty(
        name='Objects',
        default=remove_options[2],
        update=updateRemoveOptions,
        description = 'Remove only the generated objects.')

    updated  = bpy.props.IntProperty(default=0)

    remove_options_childs =  bpy.props.BoolProperty(
            name= 'Remove childs',
            default=True,
            description = 'Remove parented elements/objects'
            )

    main_tabs = bpy.props.EnumProperty(
            items = [ ('setup','Setup',''),\
                      ('tools','Tools','') ]
            )
    
    builder_tabs = bpy.props.EnumProperty( 
            items = [ ('builder','Main','builder properties'),\
                      ('materials','Materials','') ]
            )
    
    # modal buttons
    startmodal_updated = bpy.props.BoolProperty()
    startmodal = bpy.props.BoolProperty(update=updateStartModal)
    
##################################################
## COMMON UIs PANEL
##################################################

## can be called from panel a draw() function
#
# header just to centralize icons
def drawHeader(self,classtype) :
    text = classtype
    if classtype == 'builders'   : icn = 'OBJECT_DATAMODE'
    elif classtype == 'outlines' : icn = 'MESH_DATA'
    elif classtype == 'elements' : icn = 'WORDWRAP_ON'
    elif classtype == 'main'     : icn = 'SCRIPTWIN'
    elif classtype == 'selector' : icn = 'RESTRICT_SELECT_OFF' ; return icn
    layout = self.layout
    row = layout.row(align = True)
    row.label(icon = icn)

## can be called from panel a draw() function
#
# to navigate into parts (elements) of an object.
# it dispplays navigation buttons that can select an element related to the selected one : parent, child or sibling element.
def drawElementSelector(layout,elm) :
    row = layout.row(align = True)
    row.operator( "city.selector", text='', icon = 'TRIA_DOWN').action='%s parent'%elm.name
    row.operator( "city.selector",text='', icon = 'TRIA_UP' ).action='%s child'%elm.name
    row.operator( "city.selector",text='', icon = 'TRIA_LEFT' ).action='%s previous'%elm.name
    row.operator( "city.selector",text='', icon = 'TRIA_RIGHT' ).action='%s next'%elm.name

## draw start/stop modal buttons
def drawModal(layout) :
    ui = bpy.context.scene.city.ui
    row = layout.row()
    row.label(text = 'AutoRefresh :')
    row.prop(ui,'startmodal',text='%s'%('on' if ui.startmodal else 'off'))

## depending on the user selection in the 3d view, display the corresponding builder panel
# if the selection exists in the elements class
# the function is called from the builders guis poll() function, like buildings_ui.py
# @param classname String. the name of the builder as in the dropdown.
def pollBuilders(context, classname, obj_mode = 'OBJECT') :
    city = bpy.context.scene.city
    if bpy.context.mode == obj_mode :
    #type(bpy.context.active_object.data) == bpy.types.Mesh :
        elm = city.elementGet()
        if elm :
            #print(elm.name,elm.className(),elm.peer().className(),classname)
            #if ( bld.className() == 'outlines' and bld.peer().className() == classname) or \
            if elm.className(True) == classname or elm.asGroup().collection == classname :
                return True
    return False
    '''
    if bpy.context.mode == obj_mode and \
    len(bpy.context.selected_objects) == 1 and \
    type(bpy.context.active_object.data) == bpy.types.Mesh :
        bld, otl = city.elementGet()
        if bld :
            #print(elm.name,elm.className(),elm.peer().className(),classname)
            #if ( bld.className() == 'outlines' and bld.peer().className() == classname) or \
            if bld.className() == classname :
                return True
    return False
    '''

## depending on the user selection in the 3d view, display the element selector panel
# will display the selector panel it the current selection as childs or parent
def pollSelector(context, obj_mode = 'OBJECT') :
    city = bpy.context.scene.city
    if bpy.context.mode == obj_mode and \
    len(bpy.context.selected_objects) == 1 and \
    type(bpy.context.active_object.data) == bpy.types.Mesh :
        elm = city.elementGet()
        #if otl : print(otl.name,otl.parent,otl.childs)
        if elm and ( otl.parent != '' or otl.childs != '' ) :
            return True
    return False

def drawBuilderMaterials(layout,bld) :
    '''
    items=[('niet','niet','')]
    for m in bpy.data.materials :
            items.append( (m.name,m.name,'') )
    BC_City_ui.matmenu = bpy.props.EnumProperty(items=items)
    ui = bpy.context.scene.city.ui
    row = layout.row()
    row.prop(ui,'matmenu')
    '''

    for slot in bld.materialslots :
        row = layout.row()
        row.label(text = '%s :'%slot)


# some functions that remove/recreate globally the objects of the city. (tests)
def drawMainbuildingsTool(layout) :
    scene = bpy.context.scene

    row = layout.row()
    row.prop(scene.unit_settings,'scale_length')
    
    row = layout.row()
    row.operator('city.methods',text = 'Rebuild All').action = 'build all'    

    row = layout.row()
    row.operator('city.methods',text = 'Initialise').action = 'init'

    row = layout.row()
    row.operator('city.methods',text = 'List Elements').action = 'list all'
    
    row = layout.row()
    row.operator('city.methods',text = 'Remove objects').action = 'remove_otl all all obj_only True'

    row = layout.row()
    row.operator('city.methods',text = 'Remove obj. and tags').action = 'remove_otl all all elm_obj True'

def drawOutlinesTools(layout) :
    wm = bpy.context.window_manager

    row = layout.row()
    #row.operator('city.methods',text = 'Stack a %s'%wm.city_builders_dropdown).action='stack selected %s'%wm.city_builders_dropdown
    row.operator('city.methods',text = 'Stack a %s'%wm.city_builders_dropdown).action='stack selected %s'%wm.city_builders_dropdown

    row = layout.row()
    row.operator('city.methods',text = 'Remove').action='remove selected all True'

## if this outline is not generated by a builder, draw an edit button
def drawEditButton(row,elm) :
    if elm.asOutline().type != 'generated' :
        row.operator( "city.selector",text='Edit', icon = 'OUTLINER_OB_MESH' ).action='%s edit'%elm.asOutline().name
    else : # generated
        row.label( text='Generated outline, not editable')

####################################################
## the main Blended Cities panel
####################################################
class BC_main_panel(bpy.types.Panel) :
    bl_label = 'Blended Cities'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'main_ops'

    def draw_header(self, context):
        drawHeader(self,'main')

    def draw(self, context):
        scene  = bpy.context.scene
        city = scene.city
        layout  = self.layout
        layout.alignment  = 'CENTER'
        
        #  TABS
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(city.ui,'main_tabs','setup')
        row.prop_enum(city.ui,'main_tabs','tools')
        
        if city.ui.main_tabs == 'setup' :
            col = layout.column()
            col.label(text='Library path :')
            col.prop(city,'path_library')
            
        elif city.ui.main_tabs == 'tools' :
            drawMainbuildingsTool(layout)

            drawModal(layout)

####################################################
## the Outlines panel (OBJECT MODE)
####################################################
class BC_outlines_panel(bpy.types.Panel) :
    bl_label = 'Outlines'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'outlines_ops'



    @classmethod
    def poll(self,context) :
        return True
        city = bpy.context.scene.city
        if bpy.context.mode == 'OBJECT' and \
        len(bpy.context.selected_objects) >= 1 :
            return True
        return False

    def draw_header(self, context):
        drawHeader(self,'outlines')

    def draw(self, context):
        scene  = bpy.context.scene
        wm = bpy.context.window_manager
        city = scene.city
        city_ops = bpy.ops.city
        ob = bpy.context.active_object
        elm = city.elementGet()
        layout  = self.layout
        layout.alignment  = 'CENTER'

        # displays info about element if current selection
        # is already an element
        if elm :
            sel = elm.inClass(False)
            grp = elm.asGroup()
            otl = elm.asOutline()
            bld = elm.asBuilder()
            grps = otl.Childs()
            blds = grp.Childs()

            # display info about selection
            if drawExpand(layout,'outline : %s'%(otl.objectName()),'scene.city.ui.expand_otl') :
                box = layout.box()
                row = box.row()
                row.label( text = 'element name : %s'%(otl.name) )
                row = box.row()
                row.label( text = 'contains %s group%s'%(len(grps),'s' if len(grps) > 1 else '' ) )

            if drawExpand(layout,'group : %s'%(grp.name),'scene.city.ui.expand_grp') :
                box = layout.box()
                row = box.row()
                row.label( text = 'builder : %s'%(grp.collection) )
                row = box.row()
                row.label( text = 'contains %s object%s :'%(len(blds),'s' if len(blds) > 1 else '' ) )
                for bld in blds :
                    row = box.row()
                    row.label( text = '%s %s %s'%(bld.name, bld.objectName(), bld.className()) )

            row = layout.row()
            row.label( text = 'active object is %s (%s)'%(sel.name, sel.bc_element), icon = 'TRIA_RIGHT')

            ## operations
            box = layout.box()

            # request and info message
            if city.ui.outlines_tabs_ops == 'outline' :
                act = city.ui.outline_ops
                if act == 'remove_otl' : info = 'remove %s'%(otl.name)
                else : info = 'unknow'
                if act not in ['remove_otl'] : display_builder = True
                else : display_builder = False

            elif city.ui.outlines_tabs_ops == 'group' :
                act = city.ui.group_ops
                if act == 'add_grp' : info = 'add a %s builder group'%(wm.city_builders_dropdown)
                elif act == 'stack_grp' : info = 'stack a %s builder over %s'%(wm.city_builders_dropdown,grp.name)
                elif act == 'replace_grp' : info = 'replace group %s by %s'%(grp.name,wm.city_builders_dropdown)
                elif act == 'remove_grp' : info = 'remove group %s'%(grp.name)
                if act not in ['remove_grp'] : display_builder = True
                else : display_builder = False

            # outline / group operations (tabs)
            row = box.row(align=True)
            row.scale_y = 1.3
            row.prop_enum(city.ui,'outlines_tabs_ops','outline')
            row.prop_enum(city.ui,'outlines_tabs_ops','group')
            split = box.split(percentage=0.33)

            # column 1 : operations
            if city.ui.outlines_tabs_ops == 'outline' :
                col = split.column(align=True)
                col.props_enum(city.ui,'outline_ops')
                drawEditButton(col,elm)
            elif city.ui.outlines_tabs_ops == 'group' :
                col = split.column(align=True)
                col.props_enum(city.ui,'group_ops')

            # column 2 : options for this operation
            col = split.column(align=True)
            if display_builder : col.prop(wm,'city_builders_dropdown',text='')
            if act in ['remove_grp','remove_otl'] :
                # would be cool to have checkboxes with enum..
                # col.prop(city.ui,'remove_options',text='text',expand=True,toggle=True,index=-1)
                # col.props_enum(city.ui,'remove_options')
                col.prop(city.ui,'elm_obj')
                col.prop(city.ui,'elm_only')
                col.prop(city.ui,'obj_only')
                col.separator()
                col2 = col.column(align=True)
                col2.active = False
                col2.prop(city.ui,'remove_options_childs')

                if city.ui.elm_obj : options = 'elm_obj'
                elif city.ui.elm_only : options = 'elm_only'
                else: options = 'obj_only'
                options2 = city.ui.remove_options_childs

            else :
                options = True
                options2 = True

            # info about operation
            infobox = box.box()
            row = infobox.row()
            row.alignment = 'CENTER'
            row.active = False
            row.label(text = info)

            # update
            row = box.row(align=True)
            row.scale_y = 2
            row.operator('city.methods',text = 'Update',icon='FILE_TICK').action='%s selected %s %s %s'%(act,wm.city_builders_dropdown,options,options2)

            #row = layout.row()
            #row.operator('city.methods',text = 'Redefine the selection',icon='FILE_TICK').action='add selected %s'%wm.city_builders_dropdown
            #row = layout.row()
            #row.operator('city.methods',text = 'stack over the selection',icon='FILE_TICK').action='stack selected %s'%wm.city_builders_dropdown

    #row.operator('city.methods',text = 'Stack a %s'%wm.city_builders_dropdown).action='stack selected %s'%wm.city_builders_dropdown
   # row.operator('city.methods',text = 'Stack a %s'%wm.city_builders_dropdown).action='stack selected %s'%wm.city_builders_dropdown


        # add new element to create from the selected outline
        # or an existing one to change
        else :
            row = layout.row()
            row.label('Define Selected as :')
            row = layout.row(align=True)
            row.prop(wm,'city_builders_dropdown',text='')
            row.operator('city.methods',text = '',icon='FILE_TICK').action='add selected %s'%wm.city_builders_dropdown
            row = layout.row(align=True)
            row.label('Add as empty outline :')
            row.operator('city.methods',text = '',icon='FILE_TICK').action='add selected'
'''
####################################################
## the Element Selector panel (OBJECT MODE)
####################################################
class BC_selector_panel(bpy.types.Panel) :
    bl_label = 'Selector'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'select_ops'

    #@classmethod
    #def poll(self,context) :
    #    return pollSelector(context,'OBJECT')

    def draw_header(self, context):
        city = bpy.context.scene.city

        layout = self.layout
        row = layout.row(align = True)
        elm, grp, otl = city.elementGet('active',True)
        if elm :
            #if elm.className() == 'outlines' and len(elm.Childs()) == 1 : elm = elm.Childs(0)
            if ( otl.parent != '' or grp.childs != '' ) :
                drawElementSelector(layout,elm)
        icn = drawHeader(self,'selector')
        row.label(icon = icn)

    def draw(self, context):

        scene  = bpy.context.scene
        wm = bpy.context.window_manager
        city = scene.city
        ob = bpy.context.active_object
        elm = city.elementGet()
        layout  = self.layout
        layout.alignment  = 'CENTER'
        if elm :
            # generic selection tool here
            # select this builder in selected
            pass
'''
def register() :
    bpy.utils.register_class(OP_BC_Selector)
    bpy.utils.register_class(BC_main_panel)
    bpy.utils.register_class(BC_outlines_panel)

def unregister() :
    bpy.utils.unregister_class(OP_BC_Selector)
    bpy.utils.unregister_class(BC_main_panel)
    bpy.utils.unregister_class(BC_outlines_panel)
    
if __name__ == '__main__' :
    register()