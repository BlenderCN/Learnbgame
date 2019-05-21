bl_info = {
    "name": "interface dafaulter",
    "version": (1, 0, 0),
    "blender": (2, 8, 0), 
    "category": "3D View",
    "author": "nikitron",
    "location": "View3D > Tool Shelf > 1D interface",
    "description": "interface turn to default screen areas position and size",
    "warning": "",
    "wiki_url": "",          
    "tracker_url": "",  
}


# https://github.com/nortikin/nikitron_tools/blob/master/interface_reset.py

import bpy
from collections import Counter as coc
from bpy.props import EnumProperty, IntProperty, BoolProperty



type = (('default','default','default'),('sverchok','sverchok','sverchok'))
bpy.types.Screen.screentype1D = EnumProperty(name='screentype1D',items=type,description='screentype for 1d scripts',default='default')
bpy.types.Screen.keys1D = BoolProperty(name='keys1D', default=True)

def renew_screen(pick=False):
    '''lets leave this comments as evidence of 
    my search of correct update screen way
    maybe there is better solution or will be in 2.8+'''
    #bpy.ops.screen.spacedata_cleanup()
    bpy.ops.screen.screen_set(delta=1)
    bpy.ops.screen.screen_set(delta=-1)
    if pick:
        context = bpy.context
        context.screen.areas.update()
        window = context.window
        areas = context.screen.areas 
        main = context.area # [i for i in areas if i.type == 'VIEW_3D'][0] # shit
        screen = context.screen
        bpy.ops.screen.screen_full_area(dict(screen=screen,window=window,region=main.regions[0],area=main,blend_data=blend_data))
        bpy.ops.screen.screen_full_area(dict(screen=screen,window=window,region=main.regions[0],area=main,blend_data=blend_data))
    # bpy.ops.screen.back_to_previous(dict(screen=screen,window=window,region=region,area=context.area,blend_data=blend_data))
    # print('joined and die')
    # context.screen.update_tag(refresh=set({'DATA'})) # id ONLY



class OP_Area_get(bpy.types.Operator):
    '''Area get - get areas type and order
    !!!!!! WIP. Not working yet !!!!!!'''
    bl_idname = "screen.areaget"
    bl_label = "area get"



    def execute(self, context):
        wd = context.window
        ww,wh = wd.width, wd.height
        w,h,dir,types,ars,pxy = [],[],[],[],[],[]
        for area in context.areas:
            aw, ah = area.width/ww, area.height/wh
            w.append(aw)
            h.append(ah)
            pxy.append((area.x/ww+aw/2+area.y/wh+ah/2)/2)
            types.append(area.type)

        #dv, dh = 'VERTICAL', 'HORIZONTAL'
        #factor = [0.98,0.8,0.4,0.5,0.2]
        #dirs = [dh,dv,dh,dv,dh]
        #ars = [0,0,0,-1,-2]
        #types = ['NODE_EDITOR','INFO','PROPERTIES','VIEW_3D','TEXT_EDITOR','TIMELINE']
        # сортировать чтобы порядок следовал за тем, у кого больше индекс высоты и ширины 
        # (максимальный индекс Ш и В + превалирует ширина или высота - 
        # даёт направление сразу по итерации сортированного)
        # сортировать затем по этим весам типы и ширины(или высоты в зависимости от направления)
        # затем попробовать присвоить индекс в зависимости от центра предполагаемой 
        # оставшейся площади, насколько она близка к центру окна, наверное для этого надо смоделировать
        # разбивку площадей или просто оставить и найти по итерации ближайшую к центру, может заработает.
        return {'FINISHED'}



class OP_Area_do_please(bpy.types.Operator):
    '''Area do please
    execution: escape from fullscreen modes in all the ways '''
    bl_idname = "screen.areado_please"
    bl_label = "area do (jso)"



    def execute(self, context):
        # somehow it is needed
        context = bpy.context

        # veriables definitions
        window = context.window
        areas = context.screen.areas 
        main = context.area # [i for i in areas if i.type == 'VIEW_3D'][0] # shit
        region = main.regions[0] # bullshit
        screen = context.screen

        # ВЫЙТИ ИЗ <Ctrl><UP>/<Shift><SPACE> РЕЖИМА ЕСЛИ ОН АКТИВИРОВАН
        if context.screen.show_fullscreen:
            self.report({'INFO'}, 'It was fullscreen.')
            bpy.ops.screen.screen_full_area()
            #bpy.ops.screen.back_to_previous()

        # DEFINE PLATFORM AND ANALIZE WINDOW FROM SYSTEM VALUES
        if bpy.app.build_platform == b'Windows':
            import ctypes
            user32 = ctypes.windll.user32
            W,H = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        elif bpy.app.build_platform == b'Linux':
            import re
            from subprocess import run, PIPE
            output = run(['xrandr'], stdout=PIPE).stdout.decode()
            result = re.search(r'current (\d+) x (\d+)', output)
            W,H = map(int, result.groups()) if result else (800, 600)
        elif bpy.app.build_platform == b'MacOS':
            print('not working on MACOS')
            return {'CANCELLED'}
        else:
            print('not working on your OS')
            return {'CANCELLED'}

        # ВЫЙТИ ИЗ alt+F10 РЕЖИМА ЕСЛИ ОН АКТИВИРОВАН
        if context.window_manager.windows[0].width == context.area.width and not context.screen.show_fullscreen:
            bpy.ops.screen.screen_full_area(use_hide_panels=True)

        # ВЫЙТИ ИЗ alt+F11 РЕЖИМА ЕСЛИ ОН АКТИВИРОВАН
        if W == context.window.width and H == context.window.height:
            bpy.ops.wm.window_fullscreen_toggle()

        # OLD FINDINGS
            ''' HOWTO MAKE IT IN PYTHON? howto check full screen?
            /* fullscreen operator callback */
            int wm_window_fullscreen_toggle_exec(bContext *C, wmOperator *UNUSED(op))
            {
            	wmWindow *window = CTX_wm_window(C);
            	GHOST_TWindowState state;

            	if (G.background)
            		return OPERATOR_CANCELLED;

            	state = GHOST_GetWindowState(window->ghostwin);
            	if (state != GHOST_kWindowStateFullScreen)
            		GHOST_SetWindowState(window->ghostwin, GHOST_kWindowStateFullScreen);
            	else
            		GHOST_SetWindowState(window->ghostwin, GHOST_kWindowStateNormal);

            	return OPERATOR_FINISHED;
            	
            }
            '''

        # FINALLY JOIN THIS STUFF AND SEPARATE THAN
        bpy.ops.screen.areado()
        #renew_screen(pick=True)
        #bpy.ops.screen.areado(action='split')
        return {'FINISHED'}


class OP_Area_do(bpy.types.Operator):
    '''Area do for preparations of UI
    execution: join screen, split screen, change the keymaps for sketchup '''
    bl_idname = "screen.areado"
    bl_label = "interface reset"


    def get_mergables(self, areas,hw):
        ' let it be for a while == True\
          maybe in future this text will be shorten\
          but not now . Return two areas for joining meshes \
          with min max x and y values'
        ws,hs = {},{}
        for a in areas:
            ws[a] = a.width
            hs[a] = a.height
        cws = coc(list(ws.values()))
        chs = coc(list(hs.values()))
        couple = []
        ok = False
        if hw == 'h':
            for h in chs:
                #print('height',chs[h],h)
                if chs[h] > 1:
                    areas_ = [key for key,val in (hs.items()) if val == h]
                    ax,aw,ay = [],[],[]
                    for i in areas_:
                        ax.append(i.x)
                        aw.append(i.width)
                        ay.append(i.y)
                    for c in range(len(areas_)-1):
                        da1 = ax[c]+aw[c]+1 == ax[c+1] or ax[c+1]+aw[c+1]+1 == ax[c]
                        da2 = ay[c] == ay[c+1]
                        if da1 and da2:
                            # ПРОШЕРСТИЬ ПОДХОДЯЩИЕ ПЛОЩАДИ ПОПАРНО, КОМБИНИРУЯ ИХ 
                            # ПАРЫ, ПОКА НЕ НАЙДЁМ СОСЕДСКИЕ
                            couple = [areas_[c], areas_[c+1]]
                            ok = True
                            break
                    if not ok:
                        print('OHOHOH! Too nesty layout \
                                \nfor the algorythm of join areas. \
                                \nhow did you achived this?')
                if ok:
                    break

        elif hw == 'w':
            for w in cws:
                #print('width',cws[w],w)
                if cws[w] > 1:
                    areas_ = [key for key,val in (ws.items()) if val == w]
                    #print('width areas ',areas_)
                    ay,ah,ax = [],[],[]
                    for i in areas_:
                        ay.append(i.y)
                        ah.append(i.height)
                        ax.append(i.x)
                    for c in range(len(areas_)-1):
                        #print(ay[c]+aw[c], ay[c+1]+1)
                        da1 = ay[c]+ah[c]+1 == ay[c+1] or ay[c+1]+ah[c+1]+1 == ay[c]
                        da2 = ax[c] == ax[c+1]
                        if da1 and da2:
                            # ПРОШЕРСТИЬ ПОДХОДЯЩИЕ ПЛОЩАДИ ПОПАРНО, КОМБИНИРУЯ ИХ 
                            # ПАРЫ, ПОКА НЕ НАЙДЁМ СОСЕДСКИЕ
                            couple = [areas_[c], areas_[c+1]]
                            #print('couple ', couple)
                            ok = True
                            break
                    if not ok:
                        print('OHOHOH! Too nesty layout \
                                \nfor the algorythm of join areas. \
                                \nhow did you achived this?')
                if ok:
                    break
                #print('equality',a.width, w)

        if len(couple) > 1 and hw == 'h':
            if couple[0].x > couple[1].x:
                b,a = couple
            else:
                a,b = couple
            #print('height return',a,b,b.x,b.y)
            return [a,b]+[b.x-a.width/2,b.y,b.x+b.width/2,b.y+b.height/2]
        elif len(couple) > 1 and hw == 'w':
            if couple[0].y > couple[1].y:
                b,a = couple
            else:
                a,b = couple
            #print('width return',a,b,b.x,b.y)
            return [a,b]+[b.x,b.y-a.height/2,b.x+b.width/2,b.y+b.height/2]
        return None,None,None,None,None,None

    def execute(self, context):
        context = bpy.context


        # veriables definitions
        window = context.window
        areas = context.screen.areas 
        main = context.area # [i for i in areas if i.type == 'VIEW_3D'][0] # shit
        region = main.regions[0] # bullshit
        screen = context.screen
        typ = context.screen.screentype1D
        wmkc = bpy.data.window_managers['WinMan'].keyconfigs

        # here is keymaps estimation 
        #if not '1D' in wmkc:
        #    wmkc.new(name='1D')
        #    wmkc['1D'].keymaps.new(name, space_type='VIEW_3D', region_type='WINDOW')
        wmkc1Dkm3D = wmkc.active.keymaps['3D View']
        wmkc1Dkm3Dkmi = wmkc1Dkm3D.keymap_items
        wmkc1Dkm3Dkmi['view3d.rotate'].shift = False
        wmkc1Dkm3Dkmi['view3d.rotate'].alt = False
        wmkc1Dkm3Dkmi['view3d.rotate'].ctrl = False
        wmkc1Dkm3Dkmi['view3d.rotate'].type = 'MIDDLEMOUSE'
        wmkc1Dkm3Dkmi['view3d.rotate'].value = 'PRESS'
        wmkc1Dkm3Dkmi['view3d.move'].shift = True
        wmkc1Dkm3Dkmi['view3d.move'].alt = False
        wmkc1Dkm3Dkmi['view3d.move'].ctrl = False
        wmkc1Dkm3Dkmi['view3d.move'].type = 'MIDDLEMOUSE'
        wmkc1Dkm3Dkmi['view3d.move'].value = 'PRESS'
        #    wmkc1Dkm3Dkmi.new(idname='view3d.rotate', type='MIDDLEMOUSE', value='PRESS', any=False, shift=False, ctrl=False, alt=False, oskey=False, key_modifier='NONE', head=False)
        #    wmkc1Dkm3Dkmi.new(idname='view3d.move', type='MIDDLEMOUSE', value='PRESS', any=False, shift=True, ctrl=False, alt=False, oskey=False, key_modifier='NONE', head=False)
        '''

        # if needed keys
        if bpy.context.screen.keys1D:
            if typ == 'default':
                context.user_preferences.inputs.select_mouse='LEFT'
                wmkc.active = wmkc['Blender']

            elif typ == 'sverchok':
                context.user_preferences.inputs.select_mouse='RIGHT'
                wmkc.active = wmkc['Blender']
        '''

        # ВЫЙТИ ИЗ ПОЛРНОЭКРАННОГО РЕЖИМА ЕСЛИ ОН АКТИВИРОВАН
        if context.screen.show_fullscreen:
            self.report({'INFO'}, 'It was fullscreen.')
            bpy.ops.screen.screen_full_area()
            #bpy.ops.screen.back_to_previous()

        # check height and width ping-pong till areas count rize 1
        hw = 'h'
        while True:
            if len(areas) == 1:
                break
            a,b,mix,miy,max,may = self.get_mergables(areas,hw)
            if a:
                bpy.ops.screen.area_join(dict(region=a.regions[0],area=a,window=window,screen=screen,sarea=a,narea=b),min_x=mix, min_y=miy, max_x=max, max_y=may)
                blend_data = context.blend_data
                renew_screen()
            if hw == 'h':
                hw = 'w'
            else:
                hw = 'h'
        # devide screen according to type predefined. here is definitions
        areas[0].type = 'VIEW_3D'
        if typ == 'default':
            dv, dh = 'VERTICAL', 'HORIZONTAL'
            factor = [0.98,0.8,0.12,0.7]
            dirs = [dh,dv,dh,dh]
            ars = [0,0,0,-2]
            types = ['VIEW_3D','INFO','PROPERTIES','TIMELINE','OUTLINER']
        elif typ == 'sverchok':
            dv, dh = 'VERTICAL', 'HORIZONTAL'
            factor = [0.98,0.8,0.4,0.5,0.2]
            dirs = [dh,dv,dh,dv,dh]
            ars = [0,0,0,-1,-2]
            types = ['NODE_EDITOR','INFO','PROPERTIES','VIEW_3D','TEXT_EDITOR','TIMELINE']
        
        # devide screen according to type predefined. here is devision
        for p,d,a in zip(factor,dirs,ars):
            are = context.screen.areas[a]
            bpy.ops.screen.area_split(dict(region=are.regions[0],area=are,screen=screen,window=window),direction=d,factor=p)
            renew_screen()
        # type arrange
        for a,t in zip(areas,types):
            a.type = t
            if t == 'VIEW_3D':
                a.spaces[0].clip_start = 0.1
                a.spaces[0].clip_end = 3000

        return {'FINISHED'} 



class VIEW3D_PT_area_do(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Interface reset"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = '1D'


    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(bpy.context.screen, 'keys1D', text='keys')
        col.prop(bpy.context.screen,'screentype1D',text='type')
        col.operator('screen.areado_please', text=bpy.context.screen.screentype1D)
        #col.operator('screen.areaget', text='get')



# registering 
def register():
    
    bpy.utils.register_class(OP_Area_get)
    bpy.utils.register_class(OP_Area_do_please)
    bpy.utils.register_class(OP_Area_do)
    bpy.utils.register_class(VIEW3D_PT_area_do)

# unregistering 
def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_area_do)
    bpy.utils.unregister_class(OP_Area_do)
    bpy.utils.unregister_class(OP_Area_do_please)
    bpy.utils.unregister_class(OP_Area_get)

if __name__ == "__main__":
    #unregister()
    register()
