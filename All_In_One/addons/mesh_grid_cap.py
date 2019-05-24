bl_info = {
    "name": "Grid Cap",
    "author": "Lell",
    "version": (0, 9, 9),
    "blender": (2, 6, 1),
    "location": "View3D > Mesh > Faces (Ctrl-F)",
    "description": "Fill a hole with a grid of faces",
    "warning": "Doesn't work with some vertical faces",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}
	
import bpy, math
from bpy.props import *

def grid_calculation():
               
    ob = bpy.context.active_object #oggetto attivo #active object
    me = ob.data  #dati geometrie oggetto attivo   #mesh data of active object
         
    bpy.ops.object.mode_set(mode = 'OBJECT')  #passo in Object Mode #go in object mode

    sel = []  #lista dei vertici selezionati #list of selected vertices
    vert_list = [] #lista dei vertici visibili della mesh #visible vertices list
    for vert in me.vertices:  #riempimento lista vertici selezionati #create list of selected vertices
        if vert.hide == False:  
            vert_list.append(vert.index)
            if vert.select:
                sel.append(vert.index)
    
    corners = []  #lista degli angoli della selezione e della futura griglia
					#list of selection corners and of the future grid
    sel_edges = [] #lista degli edge che formano il bordo del buco
					#hole border edges list
    edge_list = [] #lista degli indici di tutti gli edge visibili
					#list of indeces of all visible adges
    for e in me.edges:  #creo lista degli indici di tutti gli edge
        if e.hide == False: #tiene conto solo dei vertici visibili
            edge_list.append(e.index)
            if e.select:  #creo la lista degli edge selezionati  #create list of selected edges
                sel_edges.append(e.index)
    
    #un vertice selezionato, per essere considerato corner, deve avere almeno 4 edge connessi
    # e due vertici selezionati connessi
	#a selected vertex must have 4 edges connected and two connected and selected vertices 
	#to be considered as corner
    for v in sel:      #ricerca dei vertici degli angoli fra i selezionati #searching for coners in selected vertices
        lati = 0       #indicatore degli edge connessi ad un vertice, per trovare i corners
        for e in me.edges:
            if e.hide == False:    
                if v in e.vertices:  #se il vertice appartiene all'edge
                    lati +=1         #segnamo che un edge in piu' appartiene a quel vertice
        if lati == 4:   #se il vertice appartiene a 4 edge diversi #if vertex has 4 connected edges
            corners.append(v)   #va nella lista degli angoli   #goes in the corners list
    
    #un vertice non selezionato, per essere considerato corner, 
	#deve essere connesso a due vertici selezionati,
    # i quali pero non devono essere diretamente connessi fra loro
	#a non-selected vertex must be connected to two selected vertices, not connected to themself,
	#to be considered as corner
    for v in vert_list: #ricerca corner non selezionati  #searching for not selected corners
        lati = 0
        if me.vertices[v].select == False:    #se il vertice non e' selezionato
            v_lati = []       #vertici appartenenti ai lati connessi al vertice analizzato
            c_lati = []       #tengo conto dei due edge connessi al vertice
            for e in me.edges:
                if e.hide == False:            
                    if v in e.vertices:    #se il vertice appartiene all'edge analizzato
                        # se almeno uno dei vertici dell'edge e' selezionato
                        if e.vertices[0] in sel or e.vertices[1] in sel:
                            v_lati.append(e.vertices[0]) #creo una lista dei vertici di quei lati connessi
                            v_lati.append(e.vertices[1])
                            c_lati.append(e.index)
                            lati += 1  #dico che ho trovato un altro edge connesso
            if lati == 2:  #se gli edge connessi al vertice v ha vertici selezionati e' 2            
                v_lati.remove(v)
                v_lati.remove(v)            
                for e2 in sel_edges: #cerco nei lati selezionati
                    #se i vertici  sono dell'edge e2
                    chiave = 1
                    if me.edges[e2].vertices[0] in v_lati and me.edges[e2].vertices[1] in v_lati:
                        chiave = 0
                        break
                else:   #se non ci sono edge che connettono i due vertici trovati 
                     corners.append(v)     #il vertice v puo' essere considerato un corner
                     me.vertices[v].select = 1    #lo seleziono
                     sel_edges.append(c_lati[0])  #i due lati a lui connessi possono essere considerati appartenenti al bordo
                     sel_edges.append(c_lati[1])
                        
    
    if len(corners) == 4:   #se i corners sono esattamente 4 #if corners are exactly 4
        for c in corners:   #rimuovo i corner dalla selezione se eventualmente ci sono #remove them if they are in the sel list
            if c in sel:
                sel.remove(c)    
        
        sel_edges_p = sel_edges[:]  #creo copie provvisorie delle liste
        sel_p = sel[:]				#create temporary copies of the lists
        
		#function to find a vertex connected to another selected one
        def find_vert(rif, lati):   #funzione per trovare un vertice connesso ad un'altro vertice fra i selezionati
            for v in sel_p:
                if v != rif:
                    for e in lati:
                        #se il riferimento e il vertice cercato appartengono ad uno stesso edge
						#if reference vertex and searched vertex are on the same edge
                        if rif in me.edges[e].vertices and v in me.edges[e].vertices:
                            sel_edges_p.remove(e)
                            result = v    
                            return result
        
        def find_next_corner(last_vert, edges): #funzione che trova il prossimo corner #function that finds next corner
            for c in corners:
                for e in edges:
                    if rif in me.edges[e].vertices and c in me.edges[e].vertices:
                        sel_edges_p.remove(e)
                        sel_p.remove(rif)
                        return c
        
        lato1 = []
        rif = corners[0]
        
        #assegno i vertici ai lati
		#assign vertices to the sides
        for i in range(len(sel_p)):
            result = find_vert(rif, sel_edges_p)
            if result == None:
                new_corn = find_next_corner(rif, sel_edges_p)
                rif = new_corn
                break
            lato1.append(result)
            if rif in sel_p:
                sel_p.remove(rif)
            rif = result               
        
        latoA = []
        
        for i in range(len(sel_p)):
            result = find_vert(rif, sel_edges_p)
            if result == None:
                new_corn = find_next_corner(rif, sel_edges_p)
                rif = new_corn
                break
            latoA.append(result)
            if rif in sel_p:
                sel_p.remove(rif)
            rif = result              
        
        lato2 = []
        
        for i in range(len(sel_p)):
            result = find_vert(rif, sel_edges_p)
            if result == None:
                new_corn = find_next_corner(rif, sel_edges_p)
                rif = new_corn
                break
            lato2.append(result)
            if rif in sel_p:
                sel_p.remove(rif)
            rif = result                       
        
        latoB = []
        
        for i in range(len(sel_p)):
            result = find_vert(rif, sel_edges_p)
            if result == None:
                new_corn = find_next_corner(rif, sel_edges_p)
                rif = new_corn
                break
            latoB.append(result)
            if rif in sel_p:
                sel_p.remove(rif)
            rif = result                                                                                                                                              
            
        #controlla se c'e' almeno un vertice per ogni lato
		#if there at least a vertex for side
        if len(lato1) > 0 and len(lato2) > 0 and len(latoA) > 0 and len(latoB) > 0:                                        
            
            #calcolo degli step di creazione dei vertici
			#steps calculation for vertices creation
            if len(lato1) >= len(lato2):   #si decide quale lato comanda (che ha piu vertici) #what side as more vertices
                seg1_2 = len(lato1)   #determina il numero di edge che si andranno a creare per quella direzione #how many edges for that direction
                step1_2 = len(lato2)/len(lato1)  #si calcola il rapporto per gestire lati di lunghezze diverse #ratio betwen different sides lenghts
            else: 
                seg1_2 = len(lato2)
                step1_2 = len(lato1)/len(lato2)
            
            if len(latoA) >= len(latoB):
                segA_B = len(latoA)
                stepA_B = len(latoB)/len(latoA)
            else: 
                segA_B = len(latoB)
                stepA_B = len(latoA)/len(latoB)
            
            #creo la griglia vuota secondo le lunghezze dei lati
			#create grid based on sides lengths
            global grid
            grid = [[ None for i in range(segA_B+2)] for j in range(seg1_2+2)]
            
            #assegnare i corners alla griglia in base al lato a cui sono attaccati
			#assign corners to the grid based on their side
            for e in sel_edges:
                if lato1[len(lato1)-1] in me.edges[e].vertices:                
                    for c in corners:
                        if c in me.edges[e].vertices:
                            grid[seg1_2+1][0] = c
                elif lato2[len(lato2)-1] in me.edges[e].vertices:
                    for c in corners:
                        if c in me.edges[e].vertices:
                            grid[0][segA_B+1] = c
                elif latoA[len(latoA)-1] in me.edges[e].vertices:
                    for c in corners:
                        if c in me.edges[e].vertices:
                            grid[seg1_2+1][segA_B+1] = c
                elif latoB[len(latoB)-1] in me.edges[e].vertices:
                    for c in corners:
                        if c in me.edges[e].vertices:
                            grid[0][0] = c                                          
            
            #assegno i vertici del bordo alla griglia
			#assign border vertices to the grid list
            for x in range(seg1_2):
                if len(lato1) >= len(lato2):
                    grid[x+1][0] = lato1[x]
                    x2 = int(len(lato2)-(step1_2*(x+1)))                
                    grid[x+1][segA_B+1] = lato2[x2]
                else:
                    x2 = seg1_2-x-1
                    grid[x+1][segA_B+1] = lato2[x2]
                    x2 = int((step1_2*x))
                    grid[x+1][0] = lato1[x2]                                
                    
            for y in range(segA_B):
                if len(latoA) >= len(latoB):
                    grid[seg1_2+1][y+1] = latoA[y]
                    y2 = int(len(latoB)-(stepA_B*(y+1)))
                    grid[0][y+1] = latoB[y2]
                else:
                    y2 = int((stepA_B*y))                
                    grid[seg1_2+1][y+1] = latoA[y2]
                    y2 = segA_B-y-1
                    grid[0][y+1] = latoB[y2]   
            
            
            due_punti = [0,0]
            #funzione per trovare l'intersezione dei lati
			#function to find edges intersection
            def trova_punti(vert1, vert2, vertA, vertB):
                p1 = me.vertices[vert1].co  #assegno le coordinate di ogni vertice a variabili
                p2 = me.vertices[vert2].co  #assign every vertex's coordinate to variables
                pA = me.vertices[vertA].co  
                pB = me.vertices[vertB].co 
                
                
                F = p1 - p2
                T = pA - pB
                
                #se gli edge non sono paralleli
				#if edges are parallel
                if not F[0]/T[0] == F[1]/T[1] == F[2]/T[2]:
                    fb=F*T
                    ab=p1*T
                    cb=pA*T
                    bb=T*T
                    bf=T*F
                    cf=pA*F
                    ff=F*F
                    af=p1*F
                    
                    k=(cb-ab+((bb*af)/(bf))-((cf*bb)/(bf)))/(bf - (ff/bf)*(bb))
                    q=(af+k*ff-cf)/(bf)
                     
                    pR = pA + q*T
                    pS = p1 + k*F
                    due_punti[0] = pR
                    due_punti[1] = pS
                    return due_punti
            
            global grid_up   #grid with upper grid coordinates
            global grid_down  #grid with lower grid coordinates
            grid_up = [[ [0,0,0] for i in range(segA_B+2)] for j in range(seg1_2+2)]
            grid_down = [[ [0,0,0] for i in range(segA_B+2)] for j in range(seg1_2+2)]
            
            #write vertices coordinates
            for i in range(seg1_2):
                for j in range(segA_B):
                    if grid[i][j] != None:
                        grid_up[i][j] = me.vertices[grid[i][j]].co
                        grid_down[i][j] = me.vertices[grid[i][j]].co
                        
            due_punti = [None,None]
            for v1 in range(seg1_2):
                for vA in range(segA_B):                
                    due_punti = trova_punti(grid[v1+1][0], grid[v1+1][segA_B+1], grid[0][vA+1], grid[seg1_2+1][vA+1])                    
                    grid_up[v1][vA] = due_punti[0]
                    grid_down[v1][vA] = due_punti[1]            
            global good_selection    #use to say if the vertices selection is appropriate for the script execution        
            global xSide    #number of horizontal grid cells
            global ySide    #number of vertical grid cells
            good_selection = True
            xSide = seg1_2
            ySide = segA_B            
                  
        else: 
            global good_selection
            good_selection = False                        
            
    else: 
        global good_selection
        good_selection = False        
    bpy.ops.object.mode_set(mode = 'EDIT')            

#function the effectivelly creates the grid vertices    
def grid_creation(grid_up, grid_down, slide, xSide, ySide, grid):
    
    ob = bpy.context.active_object #oggetto attivo
    me = ob.data  #dati geometrie oggetto attivo  
        
    bpy.ops.object.mode_set(mode = 'OBJECT')  #passo in Object Mode
    
    #funzione per trovare le coordinate del nuovo vertice della griglia
	#function to find the new grid vertey coordinates, based on the slide value
    def punto_intermedio(coord0, coord1, slide):
        new_coord = coord1+(((coord0 - coord1)/2)-(((coord0 - coord1)/2)*slide))  #coordinata per il nuovo vertice #coordinate for new vertex
        return new_coord
    #calcolo e creazione dei vertici intermedi
    for v1 in range(xSide):
        for vA in range(ySide): 
            pU = grid_up[v1][vA]
            pD = grid_down[v1][vA]
                           
            if pU == pD:
                p0 = pU                
            else:
                p0 = punto_intermedio(pU, pD, slide)                
                                                                        
                
            me.vertices.add(1)    #crea il nuovo vertice
            me.vertices[-1].co = p0 
                  
            grid[v1+1][vA+1] = me.vertices[-1].index                
            
    #creazione delle facce
	#faces creation
    for x in range(xSide+1):
        for y in range(ySide+1):                
            me.faces.add(1)            
            me.faces[-1].vertices_raw = [grid[x][y],grid[x+1][y],grid[x+1][y+1],grid[x][y+1]]
    me.update(calc_edges = True) 
                
    bpy.ops.object.mode_set(mode = 'EDIT')
    #cancello le liste
    #sel = 0  #lista dei vertici selezionati
    #vert_list = 0 #lista dei vertici della mesh
    #corners = 0  #lista degli angoli della selezione e della futura griglia
    #sel_edges = 0 #lista degli edge che formano il bordo del buco
    #edge_list = 0 #lista degli indici di tutti gli edge
    
#operator creation
class MESH_OT_grid_cap(bpy.types.Operator):

    bl_idname = "mesh.grid_cap" 
    bl_label = "Fill a hole with a grid of faces"
    bl_options = {'REGISTER', 'UNDO'}    
    
    def __init__(self):        
        grid_calculation() #calculate the upper and lower grids just one time        
           
    #creates the slide controller
    slide = FloatProperty(name="Slide", default=0.0, min=-1.0, max=1.0) #valori dello slider
 
    def execute(self, context):
		#if the selection results appropiate from the grid_calculation function
        if good_selection == True:                        
			#executes the grid_creation function
            grid_creation(grid_up, grid_down, self.slide, xSide, ySide, grid) 
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Improper selection!")
            return {'CANCELLED'}       
    
def menu_func(self, context):
    self.layout.operator("mesh.grid_cap", text="Grid Cap")

def register():
   bpy.utils.register_module(__name__)
   bpy.types.VIEW3D_MT_edit_mesh_faces.prepend(menu_func) #Aggiunge al menu CTRL V

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(menu_func)

if __name__ == "__main__":
    register()   

            

    