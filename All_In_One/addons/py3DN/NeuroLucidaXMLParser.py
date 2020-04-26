# Author: Paulo de Castro Aguiar	
# Date: July 2012
# email: pauloaguiar@fc.up.pt

"""
Functions associated with parsing the data contained in the NeuroLucida XML files. Function Load_Neuron DOES NOT require Blender and may be used to import NeuroLucida XML data to a python interpreter shell.
"""

import numpy
import time
import xml.etree.ElementTree as ET

from DataContainers import *

import myconfig





#------------------------------------------------------------------------------------------


def Load_Neuron( filename, minimal_d, remove_points ):
    """Read the NeuroLucida XML file and put all data in memory. This function DOES NOT require Blender and may be used to import NeuroLucida XML data to a python shell"""

    # some initializations
    t0 = time.clock()
    neuron      = NEURON()
    morphology  = MORPHOLOGY()

    # open the NeuroLucida XML file and parse it to a ElementTree
    print( '\nReading ' + filename + '...' )
    xml_root = ET.parse( filename ).getroot()  # parse an XML file by name

    # capture the annoying namespace
    namespace = '{%s}' % xml_root.tag[1:].split("}")[0]
    print( str(namespace) )

    # core code block to parse all the data components in the DOM
    Contours_Handle( xml_root, namespace, neuron, morphology )
    Trees_Handle( xml_root, namespace, neuron, morphology, minimal_d, remove_points )

    myconfig.neuron.append(       neuron   )
    myconfig.morphology.append( morphology )
    print( 'Parsing finished! Total of {0:.2f} seconds processing time\n'.format( time.clock() - t0 ) )    


    return


#------------------------------------------------------------------------------------------


def Contours_Handle( xml_root, namespace, neuron, morphology ):
    """Handle to import contours from the Neurolucida XML file"""

    print( '\nTaking care of Contours\n-----------------------' )

    listofnames = []    

    # get all contours
    xml_contours = xml_root.findall( '%scontour' % namespace )

    # go through all the contour tags and parse the data
    for xml_contour in xml_contours:

        # start by checking if this contour is new or not
        name = xml_contour.attrib['name']
        if name in listofnames:
            index = listofnames.index(name)
        else:
            # add name to list of already know structures
            listofnames.append(name)
            # create a new anatomical structure
            morph_struct = MORPH_STRUCT()            
            morph_struct.name = name
            morph_struct.color = xml_contour.attrib['color']
            # add this new structure to the morphology list
            morphology.structure.append( morph_struct )
            morphology.total_structures = morphology.total_structures + 1
            index = morphology.total_structures - 1

        # create the new contour and fill it with the data (attributes 'color' and 'name' are not saved again)
        xml_points = xml_contour.findall( '%spoint' % namespace )
        contour = CONTOUR()
        contour.total_points = len( xml_points )
        contour.color = xml_contour.attrib['color']
        for xml_point in xml_points:
            x = float( xml_point.attrib['x'] )
            y = float( xml_point.attrib['y'] )
            z = float( xml_point.attrib['z'] )
            contour.point.append( [x,y,z] )

        # add the new contour to the appropriate structure
        morphology.structure[ index ].rawcontour.append( contour )
        morphology.structure[ index ].total_contours = morphology.structure[ index ].total_contours + 1


    # now check if any of the contours is named 'Cell Body' or 'CellBody' and copy(!) it to the neuron strcuture
    for s in range( 0, morphology.total_structures ):
        if morphology.structure[s].name == 'Cell Body' or morphology.structure[s].name == 'CellBody' or morphology.structure[s].name == 'Soma Contour':
            # important! this is copying the address, not the data values (which is what we want!)
            neuron.cellbody = morphology.structure[s]
            print( '\nAll contours with name = ' + str(morphology.structure[s].name) + ' have been copied to neuron.cellbody' )

    return


#------------------------------------------------------------------------------------------


def Trees_Handle( xml_root, namespace, neuron, morphology, minimal_d, remove_points ):
    """Handle to import trees from the Neurolucida XML file"""

    print( '\nTaking care of Trees\n--------------------' )

    # redundant, but useful:
    minimal_radius = 0.5 * minimal_d
    corrected_diameters = 0
    discarded_points = 0

    # get all trees
    xml_trees = xml_root.findall( '%stree' % namespace )

    # go through all the tree tags and parse the data
    for xml_tree in xml_trees:

        # create new tree and write attributes
        tree = TREE()
        tree.color = xml_tree.attrib['color']
        tree.type  = xml_tree.attrib['type']
        tree.leaf  = xml_tree.attrib['leaf']

        # create a parents mapping to allow climbing the tree structure (to get the depths)
        parent_map = dict((c, p) for p in xml_tree.iter() for c in p)

        # create stack to hold segments hierarchy and fill it with the null pid = -1    
        ppid_stack     = [-1]
        branch_trigger = False


        # now go through all xml nodes in the xml tree
        for node in xml_tree.iter('*'):

            # what to do if the xml node is a 'point'
            # ---------------------------------------
            if node.tag == '%spoint' % namespace:
                a = parent_map[ node ].tag
                # don't want points inside 'spine' tag or 'marker' tag
                if parent_map[ node ].tag != '%smarker' % namespace  and parent_map[ node ].tag != '%sspine' % namespace:
                    x = float( node.attrib['x'] )
                    y = float( node.attrib['y'] )
                    z = float( node.attrib['z'] )
                    r = 0.5 * float( node.attrib['d'] )
                    if r < minimal_radius:
                        r = minimal_radius  
                        corrected_diameters += 1
                        print( 'Point ' + str(node.attrib) + ': diameter corrected' )
                        
                    # add point to the tree
                    P = [ x, y, z ]
                    if branch_trigger == True:
                        ppid = ppid_stack[-1]
                        branch_trigger = False
                    else:
                        ppid = tree.total_rawpoints - 1

                    level = len( ppid_stack ) - 1

                    if tree.total_rawpoints == 0:
                        rawpoint = RAWPOINT( P, r, ppid, level, 'standard' ) # ptype will be updated later
                        tree.rawpoint.append( rawpoint )
                        tree.total_rawpoints += 1
                    else:                        
                        l = numpy.array( P ) - numpy.array( tree.rawpoint[ ppid ].P )
                        dist = numpy.sqrt( numpy.dot(l,l) ) 
                        if dist < minimal_radius and remove_points == True: # SHOULD CHECK IF THIS IS A BIFURCATION POINT; OR HAVE ADDITIONAL MEASURES IF IT IS A BP; POINT REMOVAL COULD ALSO BE PERFORMED AFTER ALL POINTS HAVE BEEN LOADED AND TAGGED
                            # discard point
                            discarded_points += 1
                            print('Point ' + str( node.attrib ) + ': discarded')
                        else:
                            rawpoint = RAWPOINT( P, r, ppid, level, 'standard' ) # ptype will be updated later
                            tree.rawpoint.append( rawpoint )
                            tree.total_rawpoints += 1


            # what to do if the xml node is a 'branch'
            # ----------------------------------------
            elif node.tag == '%sbranch' % namespace:

                # set trigger
                branch_trigger = True

                # check branch level
                branch_level = GetBranchLevel( node, xml_tree, namespace, parent_map)
                level = len( ppid_stack ) - 1
                if branch_level == level:
                    # going DOWN a ramification 
                    ppid_stack.append( tree.total_rawpoints - 1 )
                    tree.rawpoint[ tree.total_rawpoints - 1 ].ptype = 'node'
                elif branch_level < level:
                    # going UP a ramification 
                    for i in range( level - branch_level - 1):
                        ppid_stack.pop()
                    tree.rawpoint[ tree.total_rawpoints - 1 ].ptype = 'endpoint'
                else:
                    print( 'CAREFUL!!! SOMETHING WENT WRONG IN TREE PARSING' )


            # what to do if the xml node is a 'spine'
            # ---------------------------------------
            elif node.tag == '%sspine' % namespace:

                xml_point = node.find( '%spoint' % namespace )
                x = float( xml_point.attrib['x'] )
                y = float( xml_point.attrib['y'] )
                z = float( xml_point.attrib['z'] )
                r = 0.5 * float( xml_point.attrib['d'] )
                if r < minimal_radius:
                    r = minimal_radius  
                    corrected_diameters += 1
                    print( 'Spine ' + str(xml_point.attrib) + ': diameter corrected' )

                P = tree.rawpoint[ tree.total_rawpoints - 1 ].P
                Q = [ x, y, z ]
                ppid = tree.total_rawpoints - 1
                spine = SPINE( P, Q, r , ppid)
                tree.spine.append( spine )
                tree.total_spines += 1                    
                tree.rawpoint[ tree.total_rawpoints - 1 ].contact = True


            # what to do if the xml node is a 'varicosity'
            # --------------------------------------------
            elif node.tag == '%smarker' % namespace and node.attrib['varicosity'] == 'true':

                xml_point = node.find( '%spoint' % namespace )
                x = float( xml_point.attrib['x'] )
                y = float( xml_point.attrib['y'] )
                z = float( xml_point.attrib['z'] )
                d = float( xml_point.attrib['d'] )
                r = 0.5 * d
                if r < minimal_radius:
                    r = minimal_radius  
                    corrected_diameters += 1
                    print( 'Varicosity ' + str(xml_point.attrib) + ': diameter corrected' )

                P = [ x, y, z ]

                # climb tree to get ppid
                match = False
                ppid = tree.total_rawpoints - 1
                while match == False and ppid > -1:
                    if tree.rawpoint[ppid].P == P:
                        match = True
                        tree.rawpoint[ppid].contact = True
                    else:
                        ppid = tree.rawpoint[ppid].ppid 

                varicosity = VARICOSITY( P, r, ppid)
                tree.varicosity.append( varicosity )
                tree.total_varicosities += 1


        # signal the last point in the tree as an 'endpoint'
        tree.rawpoint[ tree.total_rawpoints - 1 ].ptype = 'endpoint'

        # append this tree into the neuron data container
        neuron.tree.append( tree )
        neuron.total_trees += 1



    # inform the number of points corrected or removed
    print( '\nTotal number of corrected diameters ( changed to ' + str(2.0*minimal_radius) +' [um] ) : ' + str(corrected_diameters) )
    print( '\nTotal number of discarded points ( closer than ' + str(2.0*minimal_radius) +' [um] from previous point ) : ' + str(discarded_points) )
    print( '[careful: discarding points may create orphan spines/varicosities]' )
    print( '\n-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n' )


    return

   

#------------------------------------------------------------------------------------------


def GetBranchLevel( node, xml_tree, namespace, parent_map):
    """Auxiliary function to calculate the branch level of an XML node"""

    level = 0

    while node.tag != '%stree' % namespace:
        node = parent_map[ node ]
        if node.tag == '%sbranch' % namespace:
            level += 1    

    return level

   

#------------------------------------------------------------------------------------------
