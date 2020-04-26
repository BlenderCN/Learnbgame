bl_info = {
    "name": "Viewport to SVG",
    "version": (0, 2, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar",
    "description": "Generate an SVG file from active view",
    "category": "Import-Export"}

import bpy, bmesh, os, math, time
import mathutils as M, random as R, bpy_extras
from bpy_extras import view3d_utils as V3D
from mathutils import Vector


class ExportSVG(bpy.types.Operator):
    bl_idname = 'export.svg'
    bl_label = 'Export SVG'
    bl_description = 'Generate SVG file from active view'
    bl_options = {'REGISTER', 'UNDO'}
    render_range = bpy.props.BoolProperty(default = False)

    def execute(self, context):

        sce = bpy.context.scene
        col = M.Color((0,0,0))
        wm = bpy.context.window_manager
        region = context.region
        region3d = context.space_data.region_3d
        centro = (region.width/2, region.height/2)
        cam_co = V3D.region_2d_to_origin_3d(region, region3d, centro)
        orto = (region3d.is_perspective == False)
        dec = 4  # precision

        # use a plane named 'bisect' to cut meshes
        if wm.bisect in sce.objects:
            bis = sce.objects.get(wm.bisect)
            bis_co = bis.location
            bis_no = Vector((0,0,1))
            bis_no.rotate(bis.matrix_world)
            bis.select_set(False) ###
        else: bis = False

        sel = bpy.context.selected_objects

        # definir una escala constante para modo ortogonal -> 1BU = 100px
        if orto and wm.auto_sca:
            BU = Vector((1,0,0))
            BU.rotate(region3d.view_matrix.inverted())
            X0 = V3D.location_3d_to_region_2d(region, region3d, (0,0,0))
            X1 = V3D.location_3d_to_region_2d(region, region3d, BU)
            svg_sca = 100 / (X1-X0).length * wm.svg_scale
            slide_x = - X0[0] * svg_sca
            slide_y = - X0[1] * svg_sca
        else:
            svg_sca = wm.svg_scale
            slide_x = slide_y = 0
    
        def visible(mes, indice, tipo):

            if hasattr(mes.verts, "ensure_lookup_table"):
                mes.verts.ensure_lookup_table();
                mes.faces.ensure_lookup_table();

            if tipo == 'cara':
                val = mes.faces[indice].calc_center_median()
                coo = V3D.location_3d_to_region_2d(region, region3d, val)
                if not coo:
                    return(0, 0, 0, 0, 0, False)
                for v in mes.faces[indice].verts:
                    if not V3D.location_3d_to_region_2d(region, region3d, mes.verts[v.index].co):
                        return(0, 0, 0, 0, 0, False)
                ojo = V3D.region_2d_to_vector_3d(region, region3d, coo).normalized()
                dot = mes.faces[indice].normal.dot(ojo)
                if orto:
                    dis = M.geometry.distance_point_to_plane(val, cam_co, ojo)
                    dot = -dot
                else:
                    dis = (cam_co - val).length
            elif tipo == 'vert':
                v = mes.verts[indice]
                val = v.co
                coo = V3D.location_3d_to_region_2d(region, region3d, val)
                if not coo:
                    return(0, 0, 0, 0, 0, False)
                ojo = V3D.region_2d_to_vector_3d(region, region3d, coo)
                dot = mes.verts[indice].normal.dot(ojo)
                dis = (cam_co - val).length
            return(val, coo, ojo, dot, dis, True)
        # 3d co - 2d co - vector vista - producto - distancia - valida

        def str_xy(coo3D, esc=svg_sca, xxx=wm.offset_x + slide_x, yyy=wm.offset_y + slide_y):
            coo = V3D.location_3d_to_region_2d(region, region3d, coo3D)
            if not coo:
                return(0, 0, 0, 0, False)
            x = round(coo[0] * esc + xxx, dec)
            if orto:
                y = round((-region.height + coo[1]) * -esc + yyy, dec)
            else:
                y = round((region.height - coo[1]) * esc + yyy, dec)
            return(str(x), str(y), str(x)+','+str(y)+' ', Vector((x,y)), True)
            # str x - str y - str x,y - vector x,y - valido

        def ruido(a,b):
            return (round(R.gauss(a,b),dec))

        def vcol(col, r=0.25):
            ncol = col.copy()
            ncol.h = (ncol.h + R.random() * 2 * r - r) % 1
            ncol.s = max(0, min(1, ncol.s + 0.2 * R.triangular(-r,r)))
            ncol.v = max(0, min(1, ncol.v + 0.4 * R.triangular(-r,r)))
            return (ncol)

        def str_rgb(vector):
            r,g,b = vector[0],vector[1],vector[2]
            color = 'rgb(%s,%s,%s)' % (round(r*255), round(g*255), round(b*255))
            return(color)

        def render_linea(obj):
            modo_curva, modo_bezier = False, False
            if obj.type == 'CURVE':
                if not o.data.bevel_object and o.data.bevel_depth < .001 and o.data.extrude < .001:
                    modo_curva = True
                if 'BEZIER' in [s.type for s in o.data.splines]:
                    modo_bezier = True
            return(modo_curva, modo_bezier)

        def objeto_2_bm(context, obj, bm, convertir=False):
            if convertir:
                tmp = obj.to_mesh(context.depsgraph, apply_modifiers=True) ###
                tmp.transform(obj.matrix_world)
                bm.from_mesh(tmp)
                bpy.data.meshes.remove(tmp)
            else:
                if wm.disolver or wm.colapsar < 1:
                    mod = obj.modifiers.new('mod','DECIMATE') ###
                    mod.decimate_type = wm.deci_type
                    if wm.deci_type == 'DISSOLVE':
                        mod.angle_limit = wm.disolver
                        mod.use_dissolve_boundaries = False
                    else:
                        mod.ratio = wm.colapsar
                if obj.type == 'MESH':
                    bm.from_object(obj, context.depsgraph)
                    bm.transform(obj.matrix_world)
                else:
                    tmp = obj.to_mesh(context.depsgraph, apply_modifiers=True) ###
                    tmp.transform(obj.matrix_world)
                    bm.from_mesh(tmp)
                    bpy.data.meshes.remove(tmp)

                if wm.disolver or wm.colapsar < 1:
                    obj.modifiers.remove(mod)

            # use a plane named 'bisect' to cut meshes
            if bis: 
                bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], 
                                plane_co=bis_co, plane_no=bis_no, clear_outer=True)

            bm.normal_update()
            return(bm)


        if self.render_range == True:
            frame_list = range(sce.frame_start, sce.frame_end)
        else:
            frame_list = [sce.frame_current]
        restore_frame = sce.frame_current

        ## LOOP ANIMACION >>

        for frame in frame_list:
            sce.frame_set(frame)
            # Atom adds frame number to file name.
            parte_izq = os.path.splitext(wm.ruta)[0]
            parte_der = os.path.splitext(wm.ruta)[1]
            parte_num = str(int(sce.frame_current)).zfill(4)
            if self.render_range:
                nueva_ruta = bpy.path.abspath('%s_%s%s' % (parte_izq, parte_num, parte_der))
            else:
                nueva_ruta = bpy.path.abspath(wm.ruta)

            tim = time.time()

            if not wm.use_seed:
                wm.ran_seed = R.randrange(0,9999)
            R.seed(wm.ran_seed)

            # incrementar archivo..?
            if wm.use_continuar:
                try:
                    dibujo = open(nueva_ruta, 'r')
                    datos = dibujo.readlines()
                    dibujo.close()
                except: cierre = 'nada'
                try: cierre = datos[-2]
                except: cierre = 'vacio'
                if cierre != '</svg>\n':
                    wm.use_continuar = False
                    return{'FINISHED'}

            # abrir archivo para escribir
            dibujo = open(nueva_ruta, 'w').write
            if wm.use_continuar:
                for nl in datos[:-3]: dibujo(nl)
                dibujo('\n\n<!-- new blender session -->\n\n\n')
            else:
                x = str(sce.render.resolution_x)
                y = str(sce.render.resolution_y)
                dibujo('<svg xmlns="http://www.w3.org/2000/svg" '
                'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
                'xmlns:xlink="http://www.w3.org/1999/xlink" width="'+x+'px" height="'+y+'px">\n\n')

            # nueva capa de inkscape
            dibujo('<g inkscape:groupmode="layer" id="'+str(time.asctime())+'">\n\n')

            # valor de opacidad
            if wm.col_opacity < 1: opa = ' opacity="'+str(round(wm.col_opacity,dec))+'"'
            else: opa = ''

            # objeto para clonar
            if wm.algo_vert != 'nada' and wm.use_clon:
                clon = 'X_'+str(R.choice(list(range(999))))
                dibujo('<g id="'+clon+'" stroke-width="2"'+opa+' stroke="'+str_rgb(wm.col_4)+'">'+
                '\n  <line x1="-10" y1="0" x2="10" y2="0" /><line x1="0" y1="10" x2="0" y2="-10" />\n</g>\n\n')

            # patrones de rayas
            if wm.algo_color == 'patron':
                ran = str(R.randint(0,999))
                if wm.pat_col: fondo = 'none'
                else: fondo = str_rgb(wm.col_2)
                dibujo('<g id="raya'+ran+'"><rect fill="'+fondo+'" x="0" y="0" height="10" width="1" />'
                '<rect fill="'+str_rgb(wm.col_3)+'" x="0" y="0" height="2" width="1" /></g>\n\n<defs>\n')
                c = [2.5,3.5,5,7,10]
                for i in range(5):
                    dibujo('<pattern id="pat_'+ran+'_'+str(i)+'" patternUnits="userSpaceOnUse" width="1" '
                    'height="'+str(c[i])+'" patternTransform="rotate('+str(R.randrange(-45,45))+') scale('
                    +str(wm.pat_sca)+')"><use xlink:href="#raya'+ran+'" /></pattern>\n')
                dibujo('</defs>\n\n')

            ## OPERACIONES A NIVEL MALLA >>

            # remover objetos con coordenadas no validas
            sel_valid = [o for o in sel if str_xy(o.matrix_world.to_translation())[4]]

            # ordenar los objetos segun distancia al visor -usa origen de objetos-
            if wm.order_obj:
                distancia = [(round((cam_co-o.location).length_squared,5), o.name) for o in sel_valid]
                distancia.sort(reverse=True)
                sel_valid = [sce.objects[d[1]] for d in distancia]

            sel = [o for o in sel_valid if o.type in {'MESH','CURVE','FONT','SURFACE'}]
            if not sel: self.report({'ERROR'}, 'No selected objects..!')

            # unir todos los objetos en una sola malla
            if wm.join_objs and len(sel) > 1:
                bpy.ops.object.select_all(action='DESELECT')
                for i, o in enumerate(sel):
                    tmp = o.to_mesh(context.depsgraph, apply_modifiers=True) ###
                    tmp.transform(o.matrix_world)
                    if not i:
                        join = bpy.data.objects.new('join',tmp)
                        sce.collection.objects.link(join)
                    else:
                        add = bpy.data.objects.new('add',tmp)
                        sce.collection.objects.link(add)
                        add.select_set(True)
                        join.select_set(True)
                        context.view_layer.objects.active = join ###
                        bpy.ops.object.join()
                        try: bpy.data.meshes.remove(tmp) ###
                        except: pass
                sel = [join]

            # superponer beziers
            if wm.use_bezier: bez = ''

            # loop mallas
            for o in sel:

                # convertir objeto + modificadores en malla
                mes = bmesh.new()
                linea = render_linea(o)
                objeto_2_bm(context, o, mes, linea)
                ver = mes.verts

                dibujo('<g id="'+o.name+'">  <!-- start '+o.name+' -->\n\n')

                # dibujar una curva en el SVG
                if linea[0]:
                    I = [str_xy(v.co) for v in mes.verts]
                    V = [v for v in I if v[4]]
                    if len(V) > 1:
                        dibujo('  <path id="curva_3D.'+o.name+'" d="M '+V[0][0]+','+V[0][1]+' L ')
                        for c in V:
                            dibujo(c[2])
                        dibujo('" stroke="'+str_rgb(wm.col_5)+'" stroke-width="'+
                        str(round(wm.stroke_wid,2))+'" stroke-linecap="round" fill="none" />\n\n')

                # superponer beziers
                if wm.use_bezier and linea[1]:
                    if not linea[0]:
                        I = [str_xy(v.co) for v in mes.verts]
                        V = [v for v in I if v[4]]
                    if len(V) > 1:
                        cur = o.data.copy()
                        cur.transform(o.matrix_world)
                        for spline in cur.splines:
                            if spline.type == 'BEZIER':
                                bp = spline.bezier_points
                                bez += (' <path stroke="black" opacity=".5" fill="none" d="')
                                bez += ('M'+str_xy(bp[0].co)[2])
                                nodos = [(bp[i-1].handle_right, bp[i].handle_left, bp[i].co) for i in range(1,len(bp))]
                                for v in nodos: bez += ('C'+str_xy(v[0])[2]+str_xy(v[1])[2]+str_xy(v[2])[2])
                                if spline.use_cyclic_u:
                                    bez += ('C'+str_xy(bp[-1].handle_right)[2]+str_xy(bp[0].handle_left)[2]+str_xy(bp[0].co)[2]+'z')
                                bez += ('" />\n')
                        bpy.data.curves.remove(cur)

                # juntar info para las caras
                FF = {}
                for i, f in enumerate(mes.faces):
                    FF[i] = visible(mes, i, 'cara') # 3D - 2D - vector vista - producto - distancia - valida

                # listado de caras visibles
                S = wm.use_select - 1

                if  wm.use_frontal:
                    P = [k for k in FF.keys() if mes.faces[k].select > S and FF[k][5] 
                    and mes.faces[k].calc_area() > wm.min_area and FF[k][3] < 0]
                else:
                    P = [k for k in FF.keys() if mes.faces[k].select > S if FF[k][5] 
                    and mes.faces[k].calc_area() > wm.min_area]

                # listado de vertices en caras visibles ####
                I = []
                for k in P:
                    I.append([v.index for v in mes.faces[k].verts])
                V = list(set([v for f in I for v in f]))

                # juntar info para los vertices en caras visibles
                QQ = {} # str x - str y - str x,y - vector x,y - valido
                for v in V:
                    QQ[v] = str_xy(ver[v].co)

                # ordenar las caras segun distancia al visor -usa centroide-
                distancia = [(round(FF[f][4], dec), f) for f in P]
                if orto: distancia.sort()
                else: distancia.sort(reverse=True)
                P = [d[1] for d in distancia]

                # eliminar vertices dentro de caras 3 y 4 lados -ver de extender a ngons-
                if wm.use_occ:
                    if wm.extra_bordes != 'nada' or wm.algo_vert != 'nada':
                        for c in P:
                            if mes.faces[c].calc_area() > wm.min_area * 10:
                                pv = mes.faces[c].verts
                                for v in V:
                                    if len(pv) == 3:
                                        q = M.geometry.intersect_point_tri_2d(QQ[v][3], 
                                        QQ[pv[0].index][3], QQ[pv[1].index][3], QQ[pv[2].index][3])
                                    else:
                                        q = M.geometry.intersect_point_quad_2d(QQ[v][3], 
                                        QQ[pv[0].index][3], QQ[pv[1].index][3], QQ[pv[2].index][3], QQ[pv[3].index][3])
                                    if q and v in V:
                                        if (cam_co - ver[v].co) > (cam_co - FF[c][0]):
                                            V.remove(v)

                # llenar CARAS & trazar BORDES
                if P and (wm.algo_color!='nada' or wm.algo_edge!='nada' or wm.algo_shade=='nada'):

                    # ancho de bordes
                    w = ''
                    stroke = ''
                    if wm.algo_edge != 'nada':
                        if wm.edge_wid: 
                            w = ' stroke-width="'+str(wm.edge_wid)+'px" stroke-linejoin="'\
                                +wm.edge_join+'" stroke-linecap="round"'

                    # estilo de bordes
                    dibujo('<g id="caras_bordes.'+o.name+'"'+w)
                    if wm.algo_edge == 'regular':
                        dibujo(' stroke="'+str_rgb(wm.col_3)+'">\n')
                    elif wm.algo_edge == 'rayas':
                        u = str(1 + 3 * wm.edge_wid)+','+str(1 + 1.5 * wm.edge_wid)
                        dibujo(' stroke="'+str_rgb(wm.col_3)+'" stroke-dasharray="'+u+'">\n')
                    else:
                        dibujo('>\n')

                    # calcular paso profundidad
                    if wm.algo_shade == 'profundidad' or wm.use_effect == 'explotar':
                        if len(P): rango = abs((distancia[0][0] - distancia[-1][0])) + 1e-05
                        else: rango = 0.5
                        # if wm.algo_shade == 'profundidad':
                            # col = vcol(wm.col_1, wm.col_noise)

                    # color por objeto

                    if wm.algo_color == 'objetos':
                        colobj = vcol(wm.col_1, wm.col_noise)

                    elif wm.algo_color == 'pal_objetos':
                        colobj = R.choice([wm.col_1,wm.col_2,wm.col_3,wm.col_4,wm.col_5])

                    # loop caras ------------------------------------------------------>

                    for i,f in enumerate(P):

                        if wm.algo_shade == 'profundidad' or wm.use_effect == 'explotar':
                            dis = (distancia[0][0] - distancia[i][0]) / rango

                    # aplicar color por caras

                        if wm.algo_color == 'objetos' or wm.algo_color == 'pal_objetos':
                            col = colobj

                        elif wm.algo_color == 'caras':
                            col = vcol(wm.col_2, 0.01 + wm.col_noise / 2)

                        elif wm.algo_color == 'pal_caras':
                            col = R.choice([wm.col_1,wm.col_2,wm.col_3,wm.col_4,wm.col_5])

                        elif wm.algo_color == 'material':
                            sl = mes.faces[f].material_index
                            if o.material_slots and o.material_slots[sl].name:
                                col = M.Color(o.material_slots[sl].material.diffuse_color[:-1])
                                col = vcol(col, wm.col_noise)
                            else: col = wm.col_1

                        elif wm.algo_color == 'indices':
                            val = round(f/len(mes.faces), dec)
                            col.r = 1 - val
                            col.g = col.b = val

                        elif wm.algo_color == 'patron':
                            n = int(5.25*abs(FF[f][3])-.5)
                            if n > 4: fill = fondo
                            else: fill = 'url(#pat_'+ran+'_'+str(n)+')'

                        # aplicar sombreado

                        copiacol = col.copy()

                        if wm.algo_shade == 'sombra_dentro':
                            dot = abs(FF[f][3])
                            copiacol.v = max(1-dot,.001)
                            copiacol.s *= dot

                        elif wm.algo_shade == 'sombra_fuera':
                            dot = abs(FF[f][3])
                            copiacol.v = dot
                            copiacol.s *= 1-dot
                            
                        elif wm.algo_shade == 'indices':
                            val = round(f/len(mes.faces), dec)
                            copiacol.v = 1 - val
                            copiacol.s = .75 - val/2

                        elif wm.algo_shade == 'prisma':
                            dot = abs(FF[f][3])
                            copiacol.v = dot
                            copiacol.h = math.modf(copiacol.h + dot)[0]
                            
                        elif wm.algo_shade == 'suave':
                            dot = abs(FF[f][3])
                            copiacol.v = dot

                        elif wm.algo_shade == 'posterize':
                            dot = round(abs(FF[f][3]) * wm.pos_step)
                            copiacol.v = dot / wm.pos_step

                        elif wm.algo_shade == 'profundidad':
                            copiacol.v = dis
                            copiacol.s = dis * col.s

                        elif wm.algo_shade == 'backfaces':
                            dot = (FF[f][3]) < 0
                            copiacol.v = .5 * dot + .25

                        if wm.algo_color != 'patron':
                            fill = str_rgb(copiacol)

                        if wm.algo_color == 'nada':
                            fill = 'none'

                        # borde por cara
                        if wm.algo_color != 'nada' or wm.algo_shade == 'patron':
                            if wm.algo_edge == 'relleno':
                                stroke = ' stroke="'+fill+'"'

                        # dibujar los vertices de las caras
                        if wm.use_effect == 'nada' or wm.use_effect == 'explotar':
                            dibujo('  <polygon'+stroke+' fill="'+fill+'" points="')
                            for v in mes.faces[f].verts:
                                if wm.use_effect == 'explotar':
                                    m = Vector((ruido(0,wm.fac_noise), ruido(0,wm.fac_noise), (ruido(0,wm.fac_noise))))
                                    test = str_xy(ver[v.index].co + m/50)
                                    if test[4]:
                                        dibujo(test[2])
                                else: 
                                    dibujo(str(QQ[v.index][2]))

                            if wm.use_effect == 'explotar':
                                try: m = str(FF[i][1][0])+','+str(-FF[i][1][1]+region.height)
                                except: m = '0,0'
                                dibujo('"'+opa+' transform="rotate('+str(dis*ruido(0,wm.fac_expl))+','+m+')" />\n')
                            else:
                                dibujo('"'+opa+' />\n')

                        else:
                            dot = abs(FF[f][3])
                            delta = FF[f][4]
                            a = math.sqrt(mes.faces[f].calc_area())
                            l = a * dot * 100 * wm.shape_size / delta * wm.svg_scale / ( 1 + 25 * orto ) ####
                            xy = str_xy(FF[f][0])
                            x = float(xy[0])
                            y = float(xy[1])

                            if wm.use_effect == 'circulos' and l > 1:
                                dibujo('  <circle cx="%s" cy="%s" r="%s" %s fill="%s" %s />\n' % (x,y,l,stroke,fill,opa))

                            if wm.use_effect == 'cuadrados' and l > 1:
                                dibujo('  <rect x="%s" y="%s" width="%s" height="%s" %s fill="%s" %s />\n' % \
                                (x-l,y-l,l*2,l*2,stroke,fill,opa))

                    dibujo('</g>\n\n')


                # dibujar VERTICES como circulos / clones
                if wm.algo_vert != 'nada':
                    dibujo('<g id="vertices.'+o.name+'" fill="'+str_rgb(wm.col_4)+'">\n')
                    for i,v in enumerate(V):
                        test = visible(mes,v,'vert')
                        if test[5]:
                            vis = True
                            dot = test[3]
                            # if wm.use_frontal and dot > 0:
                                # vis = False
                            if vis:
                                if wm.algo_vert == 'regular':
                                    r = round(wm.svg_scale * wm.diam1, dec)
                                elif wm.algo_vert == 'normales_dentro':
                                    r = round(wm.svg_scale * wm.diam1 * abs(dot), dec)
                                elif wm.algo_vert == 'normales_fuera':
                                    r = round(wm.svg_scale * wm.diam1 * (1-abs(dot)), dec)
                                else:
                                    # algo: usar distancia sobre un eje
                                    if wm.ver_spa == 'local':
                                        matriz = o.matrix_world.to_translation()
                                        z = abs(ver[v].co[int(wm.ver_axis)] - matriz[int(wm.ver_axis)])
                                    else:
                                        z = abs(ver[v].co[int(wm.ver_axis)])
                                    r = round(wm.svg_scale * z * wm.diam1 , dec)

                                # dibujar vertices
                                c = str_xy(ver[v].co)
                                if r >= 1:
                                    if wm.use_clon:
                                        dibujo('  <use xlink:href="#'+clon+'" transform="translate('+c[2]+
                                        ') scale('+str(round(r/10,dec))+','+str(round(r/10,dec))+') rotate('
                                        +str(round(R.random()*360))+')" />\n')
                                    else:
                                        dibujo('  <circle cx="'+c[0]+'" cy="'+c[1]+'" r="'+str(r/2)+'"'+opa+' />\n')
                    dibujo('</g>\n\n')

                # valor de paso por objeto
                lev = len(ver)
                if lev: offset = R.randrange(0, lev)
                extra = R.randrange(0, wm.curve_var+1)

                # TRAZO vertices -paso + variacion-
                if wm.vert_conn and len(ver) > 1:
                    i = 1
                    off = offset
                    c = str_xy(ver[off].co)
                    if c[4]:
                        dibujo('<path id="trazo.'+o.name+'" d="M '+c[0]+','+c[1]+' '+wm.curva+' ')
                        while i <= lev: ####
                            if i+off >= lev: off -= lev
                            c = str_xy(ver[i+off].co)
                            if c[4]: dibujo(c[2])
                            i += wm.curve_step + extra
                        dibujo(' z" stroke="'+str_rgb(wm.col_5)+'" fill="none" />\n\n')

                # NUMERAR vertices -paso + variacion-
                if wm.use_num and len(ver) > 1:
                    i = 1
                    off = offset
                    c = str_xy(ver[off].co)
                    if c[4]:
                        dibujo('<g id="indices.'+o.name+'" font-size="'+str(wm.fon_size)+'" text-anchor="middle">\n')
                        while i <= lev: ####
                            if i+off >= lev: off-=lev
                            c = str_xy(ver[i+off].co)
                            if c[4]: dibujo('  <text x="'+c[0]+'" y="'+c[1]+'">'+str(i)+'</text>\n')
                            i += wm.curve_step + extra
                        dibujo('</g>\n\n')

                # salida EXTRA de bordes
                if wm.extra_bordes != 'nada':
                    edg = mes.edges
                    dibujo('<g id="bordes.'+o.name+'" stroke="'+str_rgb(wm.col_6)+
                    '" stroke-linecap="round" fill="none">\n')

                    for e in edg:
                        vis = True
                        if e.verts[0].index not in V or e.verts[1].index not in V:
                            vis = False
                        if wm.use_boundary:
                            vis = e.is_boundary
                        if vis:
                            vis = e.calc_face_angle() > wm.stroke_ang
                        if vis:
                            v1 = str_xy(ver[e.verts[1].index].co)[3]
                            v2 = str_xy(ver[e.verts[0].index].co)[3]
                            delta = v1 - v2
                            le = delta.length * wm.svg_scale
                            if le > wm.min_len:
                                # mover los extremos
                                if wm.extra_bordes == 'extender':
                                    if wm.edg_displ:
                                        v1 += delta * wm.edg_displ
                                        v2 -= delta * wm.edg_displ
                                    if wm.edg_noise:
                                        v1 += delta * (ruido(0,wm.edg_noise))
                                        v2 -= delta * (ruido(0,wm.edg_noise))
                                if wm.extra_bordes == 'modular':
                                    w = wm.stroke_wid + le / 25
                                    v1 -= delta * w / 250
                                    v2 += delta * w / 250

                                a, b = str(round(v1[0], dec)), str(round(v1[1], dec))
                                c, d = str(round(v2[0], dec)), str(round(v2[1], dec))

                                if wm.extra_bordes == 'extender':
                                    dibujo('  <line stroke-width="'+str(round(wm.stroke_wid,2))+
                                    '" x1="'+a+'" y1="'+b+'" x2="'+c+'" y2="'+d+'" />\n')

                                elif wm.extra_bordes == 'curvas':
                                    v3 = v1 - delta/2 + Vector((ruido(0, le*wm.cur_noise), ruido(0, le*wm.cur_noise)))
                                    e, f = str(round(v3[0], dec)), str(round(v3[1], dec))
                                    dibujo('  <path stroke-width="'+str(round(wm.stroke_wid,2))+
                                    '" d="M '+a+' '+b+' Q '+e+','+f+' '+c+','+d+'" />\n')

                                elif wm.extra_bordes == 'modular':
                                    r1, r2 = Vector((ruido(0, w), ruido(0, w))), Vector((ruido(0, w), ruido(0, w)))
                                    v3, v4 = v1 - delta/2 + r1, v1 - delta/2 + r2
                                    e, f = str(round(v3[0], dec)), str(round(v3[1], dec))
                                    g, h = str(round(v4[0], dec)), str(round(v4[1], dec))
                                    dibujo('  <path fill="'+str_rgb(wm.col_6)+'" d="M '
                                    +a+','+b+' Q '+e+','+f+' '+c+','+d+' Q '+g+','+h+' '+a+','+b+'" />\n')

                                else: # contorno
                                    W = visible(mes, e.verts[0].index, 'vert')[3]
                                    W += visible(mes, e.verts[1].index, 'vert')[3]
                                    W = 10 - round(abs(W*5),dec)
                                    if W > wm.stroke_con * 9:
                                        dibujo('  <line stroke-width="'+str(round(W*wm.stroke_wid/5,2))+
                                        '" x1="'+a+'" y1="'+b+'" x2="'+c+'" y2="'+d+'" />\n')
                    dibujo('</g>\n\n')

                dibujo('</g>  <!-- end '+o.name+' -->\n\n')

                # eliminar malla de la memoria
                mes.free()

            # superponer beziers
            if wm.use_bezier: dibujo(bez)

            ## OPERACIONES A NIVEL OBJETOS >>

            OO = [str_xy(o.matrix_world.to_translation()) for o in sel_valid]

            # origen como circulo / nombre
            if wm.use_origin:
                dibujo('<g id="origen.Objetos" fill="'+str_rgb(wm.col_5)+'">\n')
                for i,o in enumerate(sel_valid):
                    s = max(.5, abs(o.dimensions[0]*wm.obj_x)+abs(o.dimensions[1]*wm.obj_y) \
                    +abs(o.dimensions[2]*wm.obj_z))
                    n = wm.obj_x + wm.obj_y + wm.obj_z
                    if n: s /= n
                    else: s = 1
                    r = round(wm.svg_scale * s * wm.diam2, dec)
                    c = OO[i]
                    if wm.use_name:
                        dibujo('  <text font-size="'+str(round(wm.fon_size*r/10,1))+'" text-anchor="middle"'
                        +opa+' transform = "rotate('+str(round(ruido(0,s*2)))+','+c[2]+')" '
                        'x="'+c[0]+'" y="'+c[1]+'">'+str(o.name)+'</text>\n')
                    else:
                        dibujo('  <circle cx="'+c[0]+'" cy="'+c[1]+'"'+opa+' r="'+str(r)+'" />\n'
                        '  <circle fill="'+str_rgb(vcol(wm.col_2))+'" cx="'+c[0]+'" cy="'+c[1]+'"'
                        +opa+' r="'+str(r/2)+'" />\n')
                dibujo('</g>\n\n')

            # TRAZO continuo objetos
            if wm.obj_conn:
                if len(OO) > 1:
                    for i,c in enumerate(OO[:-1]):
                        if i == 0:
                            dibujo('  <path id="conexion.Objetos" d="M '+c[0]+','+c[1]+' '+wm.curva+' ')
                        else: dibujo(c[2])
                        if wm.curva != 'L':
                            delta = OO[i+1][3] - c[3]
                            le = round(delta.length) * 5
                            cc = c[3] + delta / 2 + Vector((ruido(0,le*wm.cur_noise),ruido(0,le*wm.cur_noise)))
                            dibujo(str(cc[0])+','+str(cc[1])+' ')
                    dibujo(OO[-1][2]+'" stroke="'+str_rgb(wm.col_5)+'" fill="none" />\n\n')

            # dibujar jerarquias / relaciones entre objetos
            if wm.obj_rel:
                dibujo('<g id="relaciones" stroke="'+str_rgb(wm.col_5)+'" fill="none">\n')
                for i,o in enumerate(sel_valid):
                    if o.parent:
                        h = str_xy(o.matrix_world.to_translation())
                        p = str_xy(o.parent.matrix_world.to_translation())
                        dibujo('  <path id="rel.'+o.name+'.'+o.parent.name+'" d="M '+h[2]+' L '+p[2]+'" />\n')
                dibujo('</g>\n')

            dibujo('</g>\n\n</svg>\n\n')
            
            if wm.join_objs: ### and len(sel) > 1:
                for o in sel_valid: o.select_set(True)
                context.view_layer.objects.active = sel_valid[-1] ###
                tmp = join.data
                sce.collection.objects.unlink(join)
                bpy.data.objects.remove(join)
                bpy.data.meshes.remove(tmp)

            print ('Frame',frame,'>',round(time.time()-tim,4),'seconds')

        sce.frame_set(restore_frame)
        return{'FINISHED'}


class IncrSVG(bpy.types.Operator):
    bl_idname = 'add_to.svg'
    bl_label = 'Add to SVG'
    bl_description = 'Add shapes to the end of a file'

    def execute(self, context):
        wm = bpy.context.window_manager
        wm.use_continuar = True
        bpy.ops.export.svg()
        if wm.use_continuar == False:
            self.report({'ERROR'}, 'Can not append to this file')
        wm.use_continuar = False
        bpy.ops.ed.undo()
        return{'FINISHED'}


class ComprSVG(bpy.types.Operator):
    bl_idname = 'compress.svg'
    bl_label = 'Compress'
    bl_description = 'Compress selected file to an SVGZ file'

    def execute(self, context):
        import gzip
        wm = bpy.context.window_manager
        if wm.ruta.endswith('.svg'):
            svzruta = wm.ruta+'z'
            try:
                with open(wm.ruta, 'rb') as entrada:
                    with gzip.open(svzruta, 'wb') as salida:
                        salida.writelines(entrada)
            except:
                self.report({'ERROR'}, 'Verify the path')
        else: self.report({'ERROR'}, 'Verify the path')

        return{'FINISHED'}


class OpenSVG(bpy.types.Operator):
    bl_idname = 'open.svg'
    bl_label = 'Open'
    bl_description = 'Open the file'

    def execute(self, context):
        wm = bpy.context.window_manager
        try: bpy.ops.wm.url_open(url=wm.ruta)
        # try: bpy.ops.wm.path_open(filepath=wm.ruta)
        except: pass
        return{'FINISHED'}


class PanelSVG(bpy.types.Panel):
    bl_label = 'Export SVG'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SVG"

    def draw(self, context):
        wm = bpy.context.window_manager
        layout = self.layout
        column = layout.column()
        split = column.split(align=True)
        split.operator('export.svg', text='Export SVG')
        split.operator('export.svg', text='Sequence').render_range = True
        split.operator('add_to.svg')
        column.prop(wm, 'ruta')
        split = column.split()
        split.operator('open.svg')
        split.operator('compress.svg')

        column.separator()
        split = column.split(align=True)
        split.prop(wm, 'svg_scale')
        split.prop(wm, 'offset_x')
        split.prop(wm, 'offset_y')

        column = layout.column()
        column.separator()
        column.prop(wm, 'algo_color', icon='FACESEL')
        column.prop(wm, 'algo_shade', icon='SNAP_FACE')
        column.prop(wm, 'algo_edge', icon='EDGESEL')
        column.prop(wm, 'extra_bordes', icon='SNAP_EDGE')
        column.prop(wm, 'algo_vert', icon='VERTEXSEL')
        column.prop(wm, 'use_effect', icon='CLIPUV_DEHLT')

        column = layout.column()
        column.separator()
        row=column.row(align=True)
        row.prop(wm, 'col_1')
        row.prop(wm, 'col_2')
        row.prop(wm, 'col_3')
        row.prop(wm, 'col_4')
        row.prop(wm, 'col_5')
        row=column.row(align=True)
        row.prop(wm, 'col_noise', slider=True)
        row.prop(wm, 'col_opacity', slider=True)

        column = layout.column(align=True)
        column.separator()
        split = column.split()

        izq = split.column(align=True)
        izq.label(text='Export Options:')
        izq.prop(wm, 'use_frontal')
        izq.prop(wm, 'order_obj')
        izq.prop(wm, 'use_select')
        izq.prop(wm, 'use_boundary')
        izq.prop(wm, 'use_occ')
        if not context.space_data.region_3d.is_perspective:
            izq.prop(wm, 'auto_sca')
        izq.prop(wm, 'join_objs')
        izq.prop(wm, 'bisect')

        der = split.column(align=True)
        der.label(text='Draw Extras:')
        der.prop(wm, 'use_origin')
        der.prop(wm, 'obj_conn')
        der.prop(wm, 'obj_rel')
        der.prop(wm, 'vert_conn')
        der.prop(wm, 'use_num')
        der.prop(wm, 'use_clon')
        der.prop(wm, 'use_bezier')

        column.separator()
        column = layout.column()
        column.label(text="Geometry:")
        split=column.split(align=True)
        split.prop(wm, 'deci_type')
        if wm.deci_type == 'DISSOLVE':
            split.prop(wm, 'disolver', slider=True)
        else:
            split.prop(wm, 'colapsar', slider=True)
        row=column.row(align=True)
        row.prop(wm, 'min_area', slider=True)
        row.prop(wm, 'min_len', expand=True)

        if wm.use_effect != 'nada':
            column.label(text="Effects:")
            if wm.use_effect == 'explotar':
                row=column.row(align=True)
                row.prop(wm, 'fac_expl', slider=True)
                row.prop(wm, 'fac_noise', slider=True)
            else:
                column.prop(wm, 'shape_size', slider=True)

        if wm.algo_edge != 'nada':
            column.label(text="Edges:")
            split = column.split(factor=.8, align=True)
            split.prop(wm, 'edge_wid', slider=True)
            split.prop(wm, 'edge_join')

        if wm.algo_shade == 'posterize':
            column.label(text="Posterization:")
            column.prop(wm, 'pos_step', slider=True)

        if wm.algo_color == 'patron':
            column.label(text="Hatch Pattern:")
            split = column.split()
            split.prop(wm, 'pat_sca', slider=True)
            split.prop(wm, 'pat_col', slider=True)

        if wm.extra_bordes != 'nada':
            column.label(text="Strokes:")
            column.prop(wm, 'stroke_ang', slider=True)
            split = column.split(factor=.8, align=True)
            split.prop(wm, 'stroke_wid', slider=True)
            split.prop(wm, 'col_6')
            if wm.extra_bordes == 'extender':
                split = column.split(align=True)
                split.prop(wm, 'edg_displ', slider=True)
                split.prop(wm, 'edg_noise', slider=True)
            if wm.extra_bordes == 'curvas':
                column.prop(wm, 'cur_noise', slider=True)
            if wm.extra_bordes == 'contorno':
                column.prop(wm, 'stroke_con', slider=True)

        if wm.use_origin or wm.algo_vert != 'nada':
            column.label(text="Objects | Verts:")
            if wm.use_origin:
                column.prop(wm, 'diam2', slider=True)
                split = column.split(align=True)
                izq = split.column(align=True)
                izq.prop(wm, 'use_name')
                der = split.row(align=True)
                der.prop(wm, 'obj_x')
                der.prop(wm, 'obj_y')
                der.prop(wm, 'obj_z')
            if wm.algo_vert != 'nada':
                column.prop(wm, 'diam1', slider=True)
                if wm.algo_vert == 'eje':
                    row=column.row(align=True)
                    row.prop(wm, 'ver_axis', expand=True)
                    row.prop(wm, 'ver_spa', expand=True)

        if wm.vert_conn or wm.use_num or wm.obj_conn:
            column.label(text="Connections:")
            split=column.row(align=True)
            if wm.use_num or wm.vert_conn:
                split.prop(wm, 'curve_step')
                split.prop(wm, 'curve_var')
            if wm.use_num:
                column.prop(wm, 'fon_size', slider=True)
            if wm.vert_conn or wm.obj_conn:
                row=column.row()
                row.prop(wm, 'curva', expand=True)

        column.label(text="Seed:")
        split = column.split(factor=0.35, align=True)
        split.prop(wm, 'use_seed')
        split.prop(wm, 'ran_seed', slider=True)


bpy.types.WindowManager.ruta=bpy.props.StringProperty(name='', subtype='FILE_PATH',
        default='C:\\tmp\\algo.svg', description='Save the SVG file - use absolute path')
bpy.types.WindowManager.use_continuar=bpy.props.BoolProperty(name='Add to SVG',
        default=False, description='Adds geometry to the end of a file')
bpy.types.WindowManager.svg_scale=bpy.props.FloatProperty(name='Scale',
        min=.01, max=10, default=1, description='Document scale')
bpy.types.WindowManager.offset_x=bpy.props.IntProperty(name='Slide X',
        min=-10000, max=10000, default=-0, description='Horizontal offset')
bpy.types.WindowManager.offset_y=bpy.props.IntProperty(name='Slide Y',
        min=-10000, max=10000, default=0, description='Vertical offset')

bpy.types.WindowManager.algo_color=bpy.props.EnumProperty(name='Color', items=[('nada','0. Nothing', 
        'Skip from export'), ('objetos','1. Object: Random', 'Variations on first color - use slider'), 
        ('caras','3. Face: Random', 'Variations on second color - use slider'), ('pal_objetos',
        '2. Object: Palette','Pick colors from palette'), ('pal_caras','4. Face: Palette',
        'Pick colors from palette'), ('material','5. Materials','Diffuse color from Face Material'),
        ('indices','6. Indices','Based on face indices'), ('patron', '7. Pattern',
        'Generate a hatching effect using third and second color')], 
        description='Base color for selected shapes', default='objetos')
bpy.types.WindowManager.algo_shade=bpy.props.EnumProperty(name='Shading', items=[('nada','0. Nothing', 
        'Skip from export'), ('sombra_dentro','1. Back Light', 'Shading'), ('sombra_fuera','2. Front Light', 
        'Sombreado'), ('indices','3. Indices','Based on face indices'),('profundidad','4. Depth',
        'Distance from camera -local space ramp-'),('suave','5. Soft Shading','Soft Shading'),
        ('posterize','6. Posterization','Reduce the number of shade steps'),('prisma','7. Color Ramp',
        'Displace hue based on angle'),('backfaces','8. Backfacing','Front / Back shading')], 
        description='Shape shading - modifies the color', default='suave')
bpy.types.WindowManager.algo_edge=bpy.props.EnumProperty(name='Edges', items=[('nada','0. Nothing', 
        'Skip from export'),('regular','1. Linear','Regular Edges'),('rayas','2. Dotted','Dotted lines'), 
        ('relleno','3. Match Fill','Extend the fill to edges, helps on aliasing artifacts')], 
        description='Edges style on each face', default='relleno')
bpy.types.WindowManager.extra_bordes=bpy.props.EnumProperty(name='Strokes', items=[('nada','0. Nothing', 
        'Skip from export'),('extender','1. Extend Edges','Extend the edges with some variations'),
        ('curvas','2. Curved Strokes','Curved Strokes'),('contorno','3. Contour','Change width based on angle'),
        ('modular','4. Brush','Modulate width along curve')], 
        description='Export Strokes over shapes as a separate group', default='nada')
bpy.types.WindowManager.algo_vert=bpy.props.EnumProperty(name='Vertices', items=[
        ('nada','0. Nothing', 'Skip from export'),('regular','1. Constant','Same size for all vertices'), 
        ('normales_dentro', '2. Inside','Base diameter on normals'), ('normales_fuera', '3. Outside',
        'Base diameter on normals'), ('eje','4. Use an Axis','Base diameter on distance along an axis')],
        description='Export Vertices over shapes', default='nada')
bpy.types.WindowManager.use_effect=bpy.props.EnumProperty(name='Effects', items=[
        ('nada','0. Nothing', 'Skip from export'),('explotar','1. Explode','Explode Faces'), 
        ('cuadrados', '2. Squares','Faces as Squares'), ('circulos', '3. Circles',
        'Faces as Circles')], description='Distort faces for export', default='nada')

bpy.types.WindowManager.col_1 = bpy.props.FloatVectorProperty(name='', description='Objects', 
        default=(.8, .4, .1), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)
bpy.types.WindowManager.col_2 = bpy.props.FloatVectorProperty(name='', description='Faces', 
        default=(1, .9, .5), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)
bpy.types.WindowManager.col_3 = bpy.props.FloatVectorProperty(name='', description='Edges', 
        default=(.2, .1, 0), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)
bpy.types.WindowManager.col_4 = bpy.props.FloatVectorProperty(name='', description='Vertices', 
        default=(.8, .1, .2), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)
bpy.types.WindowManager.col_5 = bpy.props.FloatVectorProperty(name='', description='Paths', 
        default=(.1, .2, .3), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)
bpy.types.WindowManager.col_6 = bpy.props.FloatVectorProperty(name='', description='Strokes', 
        default=(0, 0, 0), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)

bpy.types.WindowManager.col_noise=bpy.props.FloatProperty(name='Variation', min=0, soft_max=1, 
        max=5, default=.25, description='Modify solid color for Objects and Faces')
bpy.types.WindowManager.col_opacity=bpy.props.FloatProperty(name='Opacity', 
        min=0, max=1, default=.9, description='Affects the mixing of shapes')

bpy.types.WindowManager.deci_type=bpy.props.EnumProperty(name='', items=[('DISSOLVE','Dissolve', 
        'Merge faces based on angle'),('COLLAPSE','Collapse', 'Edge collapsing')], 
        description='Simplify mesh before exporting', default='DISSOLVE')
bpy.types.WindowManager.disolver=bpy.props.FloatProperty(name='Dissolve Faces', subtype='ANGLE', 
        min=0, max=0.7854, default=0.08727, description='Simplify mesh before export')
bpy.types.WindowManager.colapsar=bpy.props.FloatProperty(name='Collapse Edges', 
        min=0.01, max=1, default=.75, description='Simplify mesh before export')
bpy.types.WindowManager.min_area=bpy.props.FloatProperty(name='A', min=0, 
        max=5, default=0.0001, description='Area: skip smaller Faces from export')
bpy.types.WindowManager.min_len=bpy.props.FloatProperty(name='L', min=0, 
        max=15, default=0.025, description='Length: skip shorter Edges from export')
bpy.types.WindowManager.use_origin=bpy.props.BoolProperty(name='Objects Origin',
        default=False, description='Mark selected objects Location and Scale')
bpy.types.WindowManager.obj_conn=bpy.props.BoolProperty(name='Connect Objects',
        default=False, description='Connect selected objects with a Path')
bpy.types.WindowManager.obj_rel=bpy.props.BoolProperty(name='Hierarchy',
        default=False, description='Connect objects child objects to parent')
bpy.types.WindowManager.vert_conn=bpy.props.BoolProperty(name='Connect Vertices',
        default=False, description='Connect defined vertices with a Path')
bpy.types.WindowManager.use_num=bpy.props.BoolProperty(name='Number Vertices',
        default=False, description='Show index Number for defined vertices')
bpy.types.WindowManager.use_clon=bpy.props.BoolProperty(name='Clones on Vertices', default=False, 
        description='VERTICES: place instances of a symbol you can edit later in Inkscape')
bpy.types.WindowManager.use_expl=bpy.props.BoolProperty(name='Explode Faces',
        default=False, description='Distort and add explode effect to Faces')
bpy.types.WindowManager.disolver=bpy.props.FloatProperty(name='Dissolve Faces', subtype='ANGLE', 
        min=0, max=0.7854, default=0.08727, precision=1, description='Simplify mesh before export')
bpy.types.WindowManager.min_area=bpy.props.FloatProperty(name='A', min=0, 
        max=5, default=0.0001, description='Area: skip smaller Faces from export')
bpy.types.WindowManager.min_len=bpy.props.FloatProperty(name='L', min=0, 
        max=15, default=0.025, description='Length: skip shorter Edges from export')
bpy.types.WindowManager.edge_wid=bpy.props.FloatProperty(name='Edges Width', min=0, 
        max=50, default=1, description='Edges Width')
bpy.types.WindowManager.edge_join=bpy.props.EnumProperty(name='', items=[
        ('miter','Miter','Miter'),('round','Round','Round'),('bevel','Bevel','Bevel')],
        description='Stroke Linejoin - corners', default='miter')
bpy.types.WindowManager.pat_col=bpy.props.BoolProperty(name='Transparent Pattern',
        default=False, description='Draw a transparent pattern')
bpy.types.WindowManager.pat_sca=bpy.props.FloatProperty(name='Scale', min=.25, 
        max=5, default=.75, description='Hatch pattern: Scale')
bpy.types.WindowManager.pos_step=bpy.props.IntProperty(name='Posterization Steps', min=2, 
        max=8, default=3, description='Posterization Steps')

bpy.types.WindowManager.use_frontal=bpy.props.BoolProperty(name='Facing Only',
        default=True, description='Export only facing faces and vertices')
bpy.types.WindowManager.order_obj=bpy.props.BoolProperty(name='Order Objects',
        default=True, description='Order objects based on distance from origin to view')
bpy.types.WindowManager.use_select=bpy.props.BoolProperty(name='Selected Faces',
        default=False, description='Export only Selected faces')
bpy.types.WindowManager.use_boundary=bpy.props.BoolProperty(name='Boundaries',
        default=False, description='Only export Strokes on boundaries of open meshes')
bpy.types.WindowManager.use_bezier=bpy.props.BoolProperty(name='Bezier Overlay',
        default=False, description='Bezier curve objects are exported as such - may be some distortion')

bpy.types.WindowManager.ver_axis=bpy.props.EnumProperty(name='A', items=[('0','X','Axis X'),
        ('1','Y','Axis Y'),('2','Z','Axis Z')],description='Vertex size from distance along axis', default='2')
bpy.types.WindowManager.ver_spa=bpy.props.EnumProperty(name='B', items=[('local','LOC', 'Local'),
        ('global','GLOB','Global')],description='Vertex size from distance along axis', default='local')
bpy.types.WindowManager.curva=bpy.props.EnumProperty(name='Path', items=[('L','L','Linear'),
        ('Q','Q','Quadratic'),('T','T','Smooth Quadratic'),('C','C','Cubic'),('S','S','Smooth Cubic')],
        description='The kind of SVG curve that connects objects and vertices', default='L')
bpy.types.WindowManager.use_occ=bpy.props.BoolProperty(name='Oclude Strokes',
        default=False, description='Hide Strokes that are ocluded by a tri or quad - very slow')
bpy.types.WindowManager.auto_sca=bpy.props.BoolProperty(name='Fixed Scale',
        default=False, description='Ortho Mode: use a fixed scale for output - default is 1BU = 100px')

bpy.types.WindowManager.diam1=bpy.props.FloatProperty(name='Vertices Diameter',
        min=.1, max=1000, default=10, description='Vertex Mark size')
bpy.types.WindowManager.diam2=bpy.props.FloatProperty(name='Objects Diameter',
        min=.1, max=1000, default=10, description='Object Mark size')
bpy.types.WindowManager.use_name=bpy.props.BoolProperty(name='Use Names',
        default=False, description='Show object name')
bpy.types.WindowManager.obj_x=bpy.props.BoolProperty(name='X', default=False, 
        description='Local X size affects diameter')
bpy.types.WindowManager.obj_y=bpy.props.BoolProperty(name='Y', default=True, 
        description='Local Y size affects diameter')
bpy.types.WindowManager.obj_z=bpy.props.BoolProperty(name='Z', default=False, 
        description='Local Z size affects diameter')
bpy.types.WindowManager.fon_size=bpy.props.IntProperty(name='Font Size',
        min=4, max=96, default=9, description='Font size to show names and numbers')
bpy.types.WindowManager.curve_step=bpy.props.IntProperty(name='Step', min=1, max=250,
        default=4, description='Step between vertices, affects Connect and Numerate')
bpy.types.WindowManager.curve_var=bpy.props.IntProperty(name='Var', min=0, max=250, default=4, 
        description='Step Variation between vertices, affects Connect and Numerate')
bpy.types.WindowManager.edg_displ=bpy.props.FloatProperty(name='Extend',
        min=0, max=.5, default=.05, description='Strokes: extend end points')
bpy.types.WindowManager.edg_noise=bpy.props.FloatProperty(name='Variation',
        min=0, max=.5, default=.05, description='Strokes: displace along edges')
bpy.types.WindowManager.cur_noise=bpy.props.FloatProperty(name='Curvature',
        min=0, max=.5, default=.05, description='Strokes: move center point')
bpy.types.WindowManager.stroke_ang=bpy.props.FloatProperty(name='Sharp Angle',
        min=0, max=math.radians(135), default=math.radians(15), subtype='ANGLE',
        description='Strokes: use angle to limit export')
bpy.types.WindowManager.stroke_wid=bpy.props.FloatProperty(name='Stroke Width',
        min=0, max=10, default=1.5, description='Strokes: width')
bpy.types.WindowManager.stroke_con=bpy.props.FloatProperty(name='Contrast',
        min=0, max=1, default=.5, description='Contour: contrast')
bpy.types.WindowManager.fac_expl=bpy.props.FloatProperty(name='Explode',
        min=0, max=90, default=5, description='Faces: explode')
bpy.types.WindowManager.fac_noise=bpy.props.FloatProperty(name='Distort',
        min=0, max=50, default=5, description='Faces: move vertices')
bpy.types.WindowManager.shape_size=bpy.props.FloatProperty(name='Shape Size',
        min=1, max=50, default=5, description='Square and Circles size multiplier')
bpy.types.WindowManager.bisect=bpy.props.StringProperty(name='', default='bisect_plane',
        description='Name of an object used as reference plane to cut geometries')
bpy.types.WindowManager.join_objs=bpy.props.BoolProperty(name='Join Objects', default=False, 
        description='Useful for Face sorting, breaks some shaders')
bpy.types.WindowManager.use_seed=bpy.props.BoolProperty(name='Fixed Seed', default=False, 
        description='Useful for animation, keeps variation values stable')
bpy.types.WindowManager.ran_seed=bpy.props.IntProperty(name='Seed',
        min=0, max=9999, default=5555, description='Random Seed')

'''
def register():
    bpy.utils.register_class(ExportSVG)
    bpy.utils.register_class(OpenSVG)
    bpy.utils.register_class(IncrSVG)
    bpy.utils.register_class(ComprSVG)
    bpy.utils.register_class(PanelSVG)


def unregister():
    bpy.utils.unregister_class(ExportSVG)
    bpy.utils.unregister_class(OpenSVG)
    bpy.utils.unregister_class(IncrSVG)
    bpy.utils.unregister_class(ComprSVG)
    bpy.utils.unregister_class(PanelSVG)
'''

classes = (
    ExportSVG,
    OpenSVG,
    IncrSVG,
    ComprSVG,
    PanelSVG
)
register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()
