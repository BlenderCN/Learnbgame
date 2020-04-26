bl_info = {
    "name" : "Cell division metaball modeller",
    "author" : "David C. King",
    "version" : (2, 79, 0),
    "location" : "View3D > Tools > Create",
    "description" : "Model cell divisions as nuclear and membrane metaballs",
    "tracker_url" : "https://github.com/meekrob/c-blenderi/issues",
    "warning" : "",
    "wiki_url" : "https://github.com/meekrob/c-blenderi/wiki",
    "category": "Learnbgame",
}
import sys
import os

IN_BLENDER=False

try:
    import bpy
    from mathutils import Vector
    IN_BLENDER=True
except ImportError:
    print("bpy not found", file=sys.stderr)
    IN_BLENDER=False

def CreateLineageTracker( tips ):
    tree_nodes = Lineage.build_tree_from_tips( tips )
    root = Lineage.get_root( tree_nodes )
    return LineageTracker(tree_nodes, root['name'], root)

class LineageTracker:
    # persistant object wrapper around the static methods
    def __init__(self, tree_nodes, current=None, tree=None):
        self.tree_nodes = tree_nodes
        self.current = current
        self.root = tree

    def print_tree(self):
        Lineage.print_tree(self.root)

    def set(self, node_str):
        #print( self.tree_nodes.keys(), file=sys.stderr)
        node_names = [node_name for node_name in self.tree_nodes.keys()]
        if node_str in node_names:
            self.current = node_str
        else:
            print("KeyError with %s" % node_str, file=sys.stderr)
            raise "KeyError"

    def __str__(self):
        return self.current

    def get_parent(self):
        return Lineage.get_parent(self.current, self.tree_nodes)

    def get_child_names(self):
        return Lineage.get_child_names(self.current, self.tree_nodes)        

    def get_children(self):
        names = Lineage.get_child_names(self.current, self.tree_nodes)
        pointers = []
        for name in names:
            pointer = self.clone_pointer()
            pointer.set(name)
            pointers.append(pointer)

        return pointers

    def clone_pointer(self):
        return LineageTracker(self.tree_nodes, self.current)
        
# static
class Lineage:
    def build_tree_from_tips( tips ):
        nodes = {}
        
        for tip in tips:
            
            this_cell = { 'name': tip, 'parent': None, 'children': [] }
            nodes[tip] = this_cell
            Lineage.recursively_link_parents(this_cell, nodes)

        return nodes

    def recursively_link_parents(child_node, nodes):
            DEBUG = False
            node_dict = ",".join(nodes.keys())

            if DEBUG:
                print("\n= ENTER ================= ========================", file=sys.stderr) 
                print("Lineage.recursively_link_parents( <%s>, {%s})" % (child_node['name'], node_dict), file=sys.stderr)


            parent_cell_name = Lineage.get_parent_name( child_node['name'] )
            if DEBUG: print("child_node %s parent? %s" % (child_node['name'], parent_cell_name), file=sys.stderr)

            # stop at the top
            if parent_cell_name is None: 
                if DEBUG: print("============= RETURN ===============>", file=sys.stderr)
                return
                
            # create parent, unless sibling has already done so
            if parent_cell_name not in nodes:
                if DEBUG: print("CREATE NODE:", parent_cell_name, file=sys.stderr)
                nodes[parent_cell_name] = { 'name': parent_cell_name, 'parent': None, 'children': [] }
            else:
                names = [child['name'] for child in nodes[parent_cell_name]['children']]
                if DEBUG: print("PARENT EXISTS:", parent_cell_name, str(names), file=sys.stderr)

            node_dict = ",".join(nodes.keys())
            if DEBUG: print("node_dict:", '{' + node_dict + '}', file=sys.stderr)

            child_node['parent'] = nodes[parent_cell_name]
            try:
                names = [child['name'] for child in child_node['parent']['children']]
                if child_node['name'] not in names:
                    child_node['parent']['children'].append( child_node )
                    new_names = [child['name'] for child in child_node['parent']['children']]
                    if DEBUG: print(child_node['name'], "not in %s['children']:" % parent_cell_name, str(names), "=>", str(new_names), file=sys.stderr)
            except RecursionError as re:
                names = [child['name'] for child in child_node['parent']['children']]
                print("Maximum recursion exceeded on child_node (name:%s) in" % child_node['name'], str(names), file=sys.stderr)
                Lineage.print_tree(child_node)
                raise re

            # do grandparent
            node_dict = ",".join(nodes.keys())
            if DEBUG: print("Lineage.recursively_link_parents(child_node['parent'], nodes)", file=sys.stderr)
            if DEBUG: print("Lineage.recursively_link_parents( <%s>, {%s})" % (child_node['parent']['name'], node_dict), file=sys.stderr)
            if DEBUG: print("============= Recurse ===============>", file=sys.stderr)
            Lineage.recursively_link_parents(child_node['parent'], nodes)

    def print_node(node, depth=0, file=sys.stderr):
        tab = "    "

        print(tab * depth, "name %s [%x]: (children=%d)" % (root['name'], id(root), len(root['children'])), file=file, end=' ')

        if node['parent'] is None:
            print('parent: None', file=file)
        else:
            print('parent: %s' % node['parent']['name'], file=file)
        
        

    def print_tree(root, depth=0):
        tab = "    "
        print(tab * depth, end="")

        print("name %s [%x]: (children=%d)" % (root['name'], id(root), len(root['children'])))
        for i,child in enumerate(root['children']):
            print(tab * depth, i, end="")
            Lineage.print_tree(child, depth+1)
    

    def get_root(tree_nodes):
        node = next(iter(tree_nodes.values()))
        while node['parent'] is not None:
            node = node['parent']

        return node

    def get_parent(cellname, tree_nodes):
        if cellname in tree_nodes:
            return tree_nodes[cellname]['parent']

        return None

    def get_children(cellname, tree_nodes):
        if cellname in tree_nodes:
            return tree_nodes[cellname]['children']

        return None

    def get_child_names(cellname, tree_nodes):
        children = Lineage.get_children(cellname, tree_nodes)
        if children:
            names = [child['name'] for child in children]
            names.sort()
            return names

        return []

    def get_parent_name(celltype):
        if celltype == 'P0': return None
        # top level 
        if celltype == 'P1' or celltype == 'AB':  return 'P0'

        if celltype == 'E' or celltype == 'MS':   return 'EMS'

        if celltype == 'EMS' or celltype == 'P2': return 'P1'

        if celltype == 'C' or celltype == 'P3':  return 'P2'

        if celltype == 'D' or celltype == 'P4':  return 'P3'

        if celltype == 'Z3' or celltype == 'Z2': return 'P4'

        if celltype == 'Z1': return 'MSpppaap'

        # celltypes whose parents 
        # ARE one letter shorter
        return celltype[:-1]


class Cell_Datum:
    def __init__(self, cellname, obj, mball, mball_el):
        self.cellname = cellname
        self.obj = obj
        self.mball = mball
        self.mball_el = mball_el
    def copy(self):
        return Cell_Datum(self.cellname, self.obj, self.mball, self.mball_el)

    # static utils
    def debut_mball_copy_at_current_frame(new_name, mball, scene):
        current_frame = scene.frame_current
        new_mball = bpy.data.metaballs.new()

    def debut_obj_copy_at_current_frame(new_name, obj_template, mball, scene):
        current_frame = scene.frame_current
        obj = bpy.data.objects.new(new_name, mball)
        # objects are kept at origin, don't set location
        obj.hide = False
        obj.keyframe_insert("hide")
        scene.frame_current = 1
        obj.hide = True
        obj.keyframe_insert("hide")
        scene.frame_current = current_frame
        return obj

    def debut_el_copy_at_current_frame(el_template, mball, scene):
        print("Cell_Datum.debut_el_copy_at_current_frame( " + mball.name + " ) at frame", scene.frame_current, file=sys.stderr)
        # this is a new element of mball, cloning properties of el_template
        current_frame = scene.frame_current
        el = Cell.clone_el_inside_metaball(el_template)
        el.keyframe_insert("co")
        # reduction factor to keep the volumes the same
        el.radius = el_template.radius * 5/6
        el_template.radius = el.radius
        el_template.keyframe_insert("radius")
        el.keyframe_insert("radius")
        print("Cell_Datum.debut_el_copy_at_current_frame( " + mball.name + " )", "el_template.radius=%f, el.radius=%f" % (el_template.radius, el_template.radius), file=sys.stderr)
        # debut in timeline
        Cell.hide_at_frame(el, scene, 1)
        Cell.show_at_frame(el, scene, current_frame)
        return el

class Cell:


    MODE_GROWTH = "GROWTH"
    MODE_MITOSIS = "MITOSIS"
    
    def show_at_frame(obj, scene, frame):
        Cell.hide_at_frame(obj, scene, frame, False)

    def hide_at_frame(obj, scene, frame, hide=True):
        save_frame = scene.frame_current
        scene.frame_current = frame
        obj.hide = hide
        obj.keyframe_insert("hide")
        scene.frame_current = save_frame

    def clone_el_inside_metaball(metaball_element):
        mball = metaball_element.id_data
        new_el = mball.elements.new()
        new_el.co = metaball_element.co.copy()
        new_el.radius = metaball_element.radius
        # ... what else?
        return new_el

    def clone_mobj(new_name, template_el): 
        # old mball is the id_data of the template element
        old_mobj_mball = template_el.id_data

        # create a new metaball object
        new_mobj = bpy.data.objects.new(new_name, bpy.data.metaballs.new(new_name))
        new_mobj_mball = new_mobj.data # new mball is the data of the new_mobj

        # copy metaball properties
        new_mobj_mball.resolution = old_mobj_mball.resolution
        new_mobj_mball.render_resolution = old_mobj_mball.render_resolution
        new_mobj_mball.threshold = old_mobj_mball.threshold

        # clone metaball elements
        new_el = new_mobj_mball.elements.new()
        new_el.co = template_el.co.copy()
        new_el.radius = template_el.radius
        # new object with name "new_name", data is a metaball, clones of all objects
        return new_mobj
            
    def spawn(cellname, scene):
        # nucleus
        mball = bpy.data.metaballs.new(str(cellname) + "_nuc")
        obj = bpy.data.objects.new(str(cellname) + "_nuc", mball)
        scene.objects.link(obj)
        mball.resolution = 0.16
        mball.render_resolution = 0.1
        el = mball.elements.new()
        el.radius = .5
        el.keyframe_insert("radius")
        print("SPAWN %s, nucleus radius %f at frame %d" % (cellname, el.radius, scene.frame_current), file=sys.stderr)
        ## insert visibility keyframe (should it go here?)
        el.keyframe_insert("hide")
        ## visibility keyframe
        nuc_data = Cell_Datum(cellname, obj, mball, el)
        # membrane
        mball = bpy.data.metaballs.new(str(cellname) + "_mem")
        obj = bpy.data.objects.new(str(cellname) + "_mem", mball)
        scene.objects.link(obj)
        mball.resolution = 0.16
        mball.render_resolution = 0.1
        el = mball.elements.new()
        ## insert visibility keyframe (should it go here?)
        el.keyframe_insert("hide")
        ## visibility keyframe
        el.radius = 1
        el.keyframe_insert("radius")
        print("SPAWN %s, membrane radius %f at frame %d" % (cellname, el.radius, scene.frame_current), file=sys.stderr)
        mem_data = Cell_Datum(cellname, obj, mball, el)
        
        # make a Cell
        return Cell(cellname, scene, nuc_data, mem_data)
        
    def __init__(self, cellname, scene, nucleus_datum, membrane_datum):
        print("__init__(" + str(cellname) + ")", file=sys.stderr)
        self.cellname = cellname
        self.scene = scene 
        self.set_nucleus_datum(nucleus_datum)
        self.set_membrane_datum(membrane_datum)
        self.mode = Cell.MODE_GROWTH
        self.sibling = None
        self.mitosis_ticks = 0
        self.n_divisions = 0

    def set_nucleus_material(self, material):
        self.nucleus_obj.active_material = material

    def set_membrane_material(self, material):
        self.membrane_obj.active_material = material
        
    def set_nucleus_datum(self, nucleus_datum):
        print(str(self.cellname) + ".set_nucleus_datum(" + nucleus_datum.mball.name + ")", file=sys.stderr)
        self.nucleus = nucleus_datum
        self.nucleus_mball = nucleus_datum.mball
        self.nucleus_el = nucleus_datum.mball_el
        self.nucleus_obj = nucleus_datum.obj

    def set_membrane_datum(self, membrane_datum):
        print(str(self.cellname) + ".set_membrane_datum(" + membrane_datum.mball.name + ")", file=sys.stderr)
        self.membrane = membrane_datum
        self.membrane_mball = membrane_datum.mball
        self.membrane_el = membrane_datum.mball_el
        self.membrane_obj = membrane_datum.obj

    def __str__(self):
        return str(self.cellname)

    def in_mitosis(self):
        return self.mode == Cell.MODE_MITOSIS

    def move_to(self, vec, insert_keyframes=True):
        print(str(self.cellname) + ".move_to" + str(vec), "at frame %d" % self.scene.frame_current, file=sys.stderr, end=' ')
        if self.mode == Cell.MODE_MITOSIS:
            self.mitosis_ticks += 1
            print("%d moves in mitosis" % self.mitosis_ticks, file=sys.stderr,)
        else:
            print("mode: " + self.mode, file=sys.stderr,)

        self.membrane_el.co = vec
        self.nucleus_el.co = vec
        if insert_keyframes:
            self.membrane_el.keyframe_insert("co")
            self.nucleus_el.keyframe_insert("co")

    def start_mitosis(self):
        print(str(self.cellname) + ".start_mitosis at frame %d" % self.scene.frame_current, file=sys.stderr)
        if self.mode != Cell.MODE_GROWTH:
            print(self.cellname, "called start_mitosis() in error: it not in MODE_GROWTH, it is in %s" % self.mode, file=sys.stderr)
            return

        self.mode = Cell.MODE_MITOSIS
        leftCell = None
        rightCell = None
        # Duplicate geometry, and return new Cell objects that encapsulate the children of the current cell.
        # They will still share the same base metaballs so they can separate in a smooth manner. Object naming 
        # will change stay the same for parent to represent child1, and parent.child2 will be added, with its visibility hidden until the current frame
        child_names = self.cellname.get_children()

        if len(child_names) > 0:
            nucleus_left = self.nucleus
            membrane_left = self.membrane
            cell_left_name = child_names[0]
            leftCell = Cell(cell_left_name, self.scene, nucleus_left, membrane_left)

        if len(child_names) > 1:
            nucleus_right = self.nucleus.copy() # "shallow" copy
            membrane_right = self.membrane.copy() # "shallow" copy
            cell_right_name = child_names[1] 

            ## Add keyframes to the current_frame - 1
            current_frame = self.scene.frame_current
            previous_frame = current_frame - 1
            self.scene.frame_current = previous_frame
            ### key exact position before duplication to prevent a "studder"
            nucleus_left.mball_el.keyframe_insert("co")
            membrane_left.mball_el.keyframe_insert("co")
            ### account for apparent "blow-up" of metaballs when doubled
            nucleus_left.mball_el.keyframe_insert("radius")
            membrane_left.mball_el.keyframe_insert("radius")

            ## Restore current position
            self.scene.frame_current = current_frame

            # debut new mesh elements for "right", includes reducing the radius of the new elements to account for the change in volume
            nucleus_right.mball_el = Cell_Datum.debut_el_copy_at_current_frame( nucleus_left.mball_el, nucleus_left.mball, self.scene )
            membrane_right.mball_el = Cell_Datum.debut_el_copy_at_current_frame( membrane_left.mball_el, membrane_left.mball, self.scene )

            # make new Cell for right-hand element (only the metaball element is different)
            rightCell = Cell(cell_right_name, self.scene, nucleus_right, membrane_right)

        if leftCell: 
            leftCell.sibling = rightCell
            leftCell.mode = Cell.MODE_MITOSIS
            leftCell.n_divisions += 1
        if rightCell: 
            rightCell.sibling = leftCell
            rightCell.mode = Cell.MODE_MITOSIS
            rightCell.n_divisions += 1

        return leftCell, rightCell

    def end_cytokinesis(self):
        print(str(self.cellname) + ".end_cytokinesis at frame %d" % self.scene.frame_current, file=sys.stderr)
        if self.mode != Cell.MODE_MITOSIS:
            print(self.cellname, "called end_cytokinesis() in error: it is not in MODE_MITOSIS, it is in %s" % self.mode, file=sys.stderr)
            return

        self.mode = Cell.MODE_GROWTH
        # Copy all data and create new metaballs and objects specific to this cell only
        # this will prevent the current cell from re-merging into its sibling, and will allow
        # its material and texture properties to be set individually
        current_frame = self.scene.frame_current
        scene = self.scene

        # make the size changes gradual
        self.nucleus_el.radius *= 6/5
        self.membrane_el.radius *= 6/5
        self.nucleus_el.keyframe_insert("radius")
        self.membrane_el.keyframe_insert("radius")

        ### nucleus
        new_nucleus = Cell.clone_mobj(str(self.cellname) + "_nuc", self.nucleus_el)
        new_nucleus.active_material = self.nucleus_obj.active_material
        scene.objects.link(new_nucleus)
        new_nucleus_el = new_nucleus.data.elements[0]
        new_nucleus_el.keyframe_insert("co")
        ## replace in timeline
        # hide previous
        Cell.hide_at_frame(self.nucleus_el, scene, current_frame) 
        # debut new
        Cell.hide_at_frame(new_nucleus_el, scene, 1)
        Cell.show_at_frame(new_nucleus_el, scene, current_frame)
        
        ### membrane
        new_membrane = Cell.clone_mobj(str(self.cellname) + "_mem", self.membrane_el)
        new_membrane.active_material = self.membrane_obj.active_material
        scene.objects.link(new_membrane)
        new_membrane_el = new_membrane.data.elements[0]
        new_membrane_el.keyframe_insert("co")
        ## replace in timeline
        # hide previous
        Cell.hide_at_frame(self.membrane_el, scene, current_frame) 
        # debut new
        Cell.hide_at_frame(new_membrane_el, scene, 1)
        Cell.show_at_frame(new_membrane_el, scene, current_frame)

        # replace Cell_Datum instances
        self.set_nucleus_datum(Cell_Datum(self.cellname, new_nucleus, new_nucleus.data, new_nucleus.data.elements[0]))
        self.set_membrane_datum(Cell_Datum(self.cellname, new_membrane, new_membrane.data, new_membrane.data.elements[0]))

        # restore unhalved size
        self.nucleus.mball_el.radius *= 6/5
        self.membrane.mball_el.radius *= 6/5

def test_lineage():
    LINEAGE = CreateLineageTracker(ALL_END_PNTS)
    LINEAGE.print_tree()

def run_file(filename):
    glow_nuc = bpy.data.materials['Glow_nuc_mat']
    nucleus_mat = bpy.data.materials['Nucleus_mat']
    membrane_mat = bpy.data.materials['Membrane_mat']

    print("About to parse file:", filename, file=sys.stderr)
    fh = open(filename, "r")
    header_names = fh.readline().strip().split(",")
    # create founder cell
    LINEAGE = CreateLineageTracker(ALL_END_PNTS)
    P0_cell = Cell.spawn(LINEAGE, bpy.context.scene)

    P0_cell.set_nucleus_material( nucleus_mat )
    P0_cell.set_membrane_material( membrane_mat )

    embryo = {}
    embryo['P0'] = P0_cell

    # sort fh
    rows = [{'line':row, 'time': int(row.split(',')[2])} for row in fh.readlines()]
    rows.sort(key=lambda a: a['time'])

    quit_after = 30000
    #for i,line in enumerate(fh):
    for i,line in enumerate( row['line'] for row in rows ):
        fields = line.strip().split(",")
        row = {}
        for key,value in zip(header_names,fields):
            row[key] = value

        x,y,z = float(row['x'])/50,float(row['y'])/50,float(row['z'])/5

        # set time point
        bpy.context.scene.frame_current = int(row['time']) * 12
        bpy.context.scene.frame_end = bpy.context.scene.frame_current

        if row['cell'] not in embryo:
            # we need to see if the parent of the current row's cell exists
            try:
                parent_cell_name = Lineage.get_parent(row['cell'], LINEAGE.tree_nodes)["name"]
            except TypeError as te:
                print("current cell [%s] COULD NOT FIND PARENT" % row['cell'], file=sys.stderr)
                Lineage.print_node(LINEAGE.tree_nodes[ row['cell'] ] )
                raise te

            #print("current cell [%s] ----PARENT---> [%s]" %(row['cell'], parent_cell_name), file=sys.stderr)
            if parent_cell_name in embryo:
                parent = embryo[parent_cell_name]
                # fork children
                children = parent.start_mitosis()
                for child in children:
                    if child is None: continue
                    childname = str(child.cellname)
                    print("spawning [%s] at frame %d" % (childname,bpy.context.scene.frame_current), file=sys.stderr)
                    embryo[childname] = child
                    #print(embryo.keys())
            else:
                print("parent_cell_name %s is not in {embryo}", parent_cell_name, file=sys.stderr)

        current_cell = embryo[ row['cell'] ]
        #print("move cell %s to %s,%s,%s" % (row['cell'], row['x'], row['y'], row['z']))
        current_cell.move_to( Vector( (x,y,z) ) )

        if current_cell.in_mitosis() and current_cell.mitosis_ticks > 4:
            current_cell.end_cytokinesis()
            if str(current_cell.cellname) != 'EMS' and str(current_cell.cellname).startswith('E'):
                current_cell.set_nucleus_material( glow_nuc )
        


        if i >= quit_after:
            break



def frst_debug():
    global ALL_END_PNTS


    nucleus_mat = bpy.data.materials['Nuclear_mat']
    membrane_mat = bpy.data.materials['Membrane_mat']


    #P0 = CreateLineageTracker(['AB', 'P1', 'EMS', 'P2'])
    P0 = CreateLineageTracker(ALL_END_PNTS)

    P0_cell = Cell.spawn(P0, bpy.context.scene)
    P0_cell.set_nuclear_material( nucleus_mat )
    P0_cell.set_membrane_material( membrane_mat )

    P0_cell.move_to( Vector((0,0,1)) )

    bpy.context.scene.frame_current = 24
    AB_cell, P1_cell = P0_cell.start_mitosis()

    bpy.context.scene.frame_current = 128
    if AB_cell:
        AB_cell.move_to( Vector((5,1,2)) )
    if P1_cell:
        P1_cell.move_to( Vector((-5,0,2)) )

    bpy.context.scene.frame_current = 129
    AB_cell.end_cytokinesis()
    P1_cell.end_cytokinesis()
    bpy.context.scene.frame_current = 200
    AB_cell.move_to( Vector((5,1,10)) )
    P1_cell.move_to( Vector((-5,1,10)) )
    
    # 2nd division
    EMS_cell,P2_cell = P1_cell.start_mitosis()
        
    bpy.context.scene.frame_current = 250
    EMS_cell.move_to( Vector((-5,-10,10)) )
    P2_cell.move_to( Vector((-5,10,10)) )

    bpy.context.scene.frame_current = 1


ALL_END_PNTS = [
'ABalaaaala',
'ABalaaaalp',
'ABalaaaarl',
'ABalaaaarr',
'ABalaaapal',
'ABalaaapar',
'ABalaaappl',
'ABalaaappr',
'ABalaapaaa',
'ABalaapaap',
'ABalaapapa',
'ABalaapapp',
'ABalaappaa',
'ABalaappap',
'ABalaapppa',
'ABalaapppp',
'ABalapaaaa',
'ABalapaaap',
'ABalapaapa',
'ABalapaapp',
'ABalapapaa',
'ABalapapap',
'ABalapappa',
'ABalapappp',
'ABalappaaa',
'ABalappaap',
'ABalappapa',
'ABalappapp',
'ABalapppaa',
'ABalapppap',
'ABalappppa',
'ABalappppp',
'ABalpaaaaa',
'ABalpaaaap',
'ABalpaaapa',
'ABalpaaapp',
'ABalpaapaa',
'ABalpaapap',
'ABalpaappa',
'ABalpaappp',
'ABalpapaaa',
'ABalpapaap',
'ABalpapapa',
'ABalpapapp',
'ABalpappaa',
'ABalpappap',
'ABalpapppa',
'ABalpapppp',
'ABalppaaaa',
'ABalppaaap',
'ABalppaapa',
'ABalppaapp',
'ABalppapaa',
'ABalppapap',
'ABalppappa',
'ABalppappp',
'ABalpppaaa',
'ABalpppaap',
'ABalpppapa',
'ABalpppapp',
'ABalppppaa',
'ABalppppap',
'ABalpppppa',
'ABalpppppp',
'ABaraaaaaa',
'ABaraaaaap',
'ABaraaaapa',
'ABaraaaapp',
'ABaraaapaa',
'ABaraaapap',
'ABaraaappa',
'ABaraaappp',
'ABaraapaaa',
'ABaraapaap',
'ABaraapapa',
'ABaraapapp',
'ABaraappaa',
'ABaraappap',
'ABaraapppa',
'ABaraapppp',
'ABarapaaaa',
'ABarapaaap',
'ABarapaapa',
'ABarapaapp',
'ABarapapaa',
'ABarapapap',
'ABarapappa',
'ABarapappp',
'ABarappaaa',
'ABarappaap',
'ABarappapa',
'ABarappapp',
'ABarapppaa',
'ABarapppap',
'ABarappppa',
'ABarappppp',
'ABarpaaaaa',
'ABarpaaaap',
'ABarpaaapa',
'ABarpaaapp',
'ABarpaapaa',
'ABarpaapap',
'ABarpaappa',
'ABarpaappp',
'ABarpapaaa',
'ABarpapaap',
'ABarpapapa',
'ABarpapapp',
'ABarpappaa',
'ABarpappap',
'ABarpapppa',
'ABarpapppp',
'ABarppaaaa',
'ABarppaaap',
'ABarppaapa',
'ABarppaapp',
'ABarppapaa',
'ABarppapap',
'ABarppappa',
'ABarppappp',
'ABarpppaaa',
'ABarpppaap',
'ABarpppapa',
'ABarpppapp',
'ABarppppaa',
'ABarppppap',
'ABarpppppa',
'ABarpppppp',
'ABplaaaaaa',
'ABplaaaaap',
'ABplaaaapa',
'ABplaaaapp',
'ABplaaapaa',
'ABplaaapap',
'ABplaaappa',
'ABplaaappp',
'ABplaapaaa',
'ABplaapaap',
'ABplaapapa',
'ABplaapapp',
'ABplaappaa',
'ABplaappap',
'ABplaapppa',
'ABplaapppp',
'ABplapaaaa',
'ABplapaaap',
'ABplapaapa',
'ABplapaapp',
'ABplapapaa',
'ABplapapap',
'ABplapappa',
'ABplapappp',
'ABplappaaa',
'ABplappaap',
'ABplappapa',
'ABplappapp',
'ABplapppaa',
'ABplapppap',
'ABplappppa',
'ABplappppp',
'ABplpaaaaa',
'ABplpaaaap',
'ABplpaaapa',
'ABplpaaapp',
'ABplpaapaa',
'ABplpaapap',
'ABplpaappa',
'ABplpaappp',
'ABplpapaaa',
'ABplpapaap',
'ABplpapapa',
'ABplpapapp',
'ABplpappaa',
'ABplpappap',
'ABplpapppa',
'ABplpapppp',
'ABplppaaaa',
'ABplppaaap',
'ABplppaapa',
'ABplppaapp',
'ABplppapaa',
'ABplppapap',
'ABplppappa',
'ABplppappp',
'ABplpppaaa',
'ABplpppaap',
'ABplpppapa',
'ABplpppapp',
'ABplppppaa',
'ABplppppap',
'ABplpppppa',
'ABplpppppp',
'ABpraaaaaa',
'ABpraaaaap',
'ABpraaaapa',
'ABpraaaapp',
'ABpraaapaa',
'ABpraaapap',
'ABpraaappa',
'ABpraaappp',
'ABpraapaaa',
'ABpraapaap',
'ABpraapapa',
'ABpraapapp',
'ABpraappaa',
'ABpraappap',
'ABpraapppa',
'ABpraapppp',
'ABprapaaaa',
'ABprapaaap',
'ABprapaapa',
'ABprapaapp',
'ABprapapaa',
'ABprapapap',
'ABprapappa',
'ABprapappp',
'ABprappaaa',
'ABprappaap',
'ABprappapa',
'ABprappapp',
'ABprapppaa',
'ABprapppap',
'ABprappppa',
'ABprappppp',
'ABprpaaaaa',
'ABprpaaaap',
'ABprpaaapa',
'ABprpaaapp',
'ABprpaapaa',
'ABprpaapap',
'ABprpaappa',
'ABprpaappp',
'ABprpapaaa',
'ABprpapaap',
'ABprpapapa',
'ABprpapapp',
'ABprpappaa',
'ABprpappap',
'ABprpapppa',
'ABprpapppp',
'ABprppaaaa',
'ABprppaaap',
'ABprppaapa',
'ABprppaapp',
'ABprppapaa',
'ABprppapap',
'ABprppappa',
'ABprppappp',
'ABprpppaaa',
'ABprpppaap',
'ABprpppapa',
'ABprpppapp',
'ABprppppaa',
'ABprppppap',
'ABprpppppa',
'ABprpppppp',
'Caaaaa',
'Caaaap',
'Caaapa',
'Caaapp',
'Caapa',
'Caappd',
'Caappv',
'Capaa',
'Capaaa',
'Capaap',
'Capapa',
'Capapp',
'Cappaa',
'Cappap',
'Capppa',
'Capppp',
'Cpaaaa',
'Cpaaap',
'Cpaapa',
'Cpaapp',
'Cpapaa',
'Cpapap',
'Cpappd',
'Cpappv',
'Cppaaa',
'Cppaap',
'Cppapa',
'Cppapp',
'Cpppaa',
'Cpppap',
'Cppppa',
'Cppppp',
'Daaa',
'Daap',
'Dapa',
'Dapp',
'Dpaa',
'Dpap',
'Dppa',
'Dppp',
'Ealaa',
'Ealap',
'Ealpa',
'Ealpp',
'Earaa',
'Earap',
'Earpa',
'Earpp',
'Eplaa',
'Eplap',
'Eplpa',
'Eplpp',
'Epraa',
'Eprap',
'Eprpa',
'Eprpp',
'MSaaaaaa',
'MSaaaaap',
'MSaaaapa',
'MSaaaapp',
'MSaaapaa',
'MSaaapap',
'MSaaapp',
'MSaapaaa',
'MSaapaap',
'MSaapapa',
'MSaapapp',
'MSaappa',
'MSaappp',
'MSapaaaa',
'MSapaaap',
'MSapaap',
'MSapapaa',
'MSapapap',
'MSapapp',
'MSapappp',
'MSappaa',
'MSappap',
'MSapppa',
'MSapppp',
'MSpaaaaa',
'MSpaaaap',
'MSpaaapa',
'MSpaaapp',
'MSpaapaa',
'MSpaapap',
'MSpaapp',
'MSpapaaa',
'MSpapaap',
'MSpapapa',
'MSpapapp',
'MSpappa',
'MSpappp',
'MSppaaaa',
'MSppaaap',
'MSppaap',
'MSppapa',
'MSppapaa',
'MSppapaaa',
'MSppapaap',
'MSppapap',
'MSppapp',
'MSppappa',
'MSppappp',
'MSpppaa',
'MSpppap',
'MSppppa',
'MSppppp',
'Z2',
'MSapappa',
'Z3']

if __name__ == '__main__':
    #frst_debug()
    if IN_BLENDER:
        run_file( '/Users/david/epic_gs_data/tbx-9_8_CD20080221.csv' )
    else:
        test_lineage()
