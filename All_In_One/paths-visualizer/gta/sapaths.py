from os.path import isfile, join
from os import walk
from struct import unpack
from io import BytesIO
import re
import collections

PREFIX = "nodes"
EXT = "dat"

def getBitFields(var, lOffset, size):
    return (var >> lOffset) & ((2 ** size) -1)

def getNodeNumberOfLinks(flags):
    return getBitFields(flags, 0, 3)

class SAPathSingleNode:
    def __init__(self, node):
        self.path = BytesIO(open(node, "rb").read())
        self.mHeader = {}
        self.mPathnodes = []
        self.mCarpathlinks = []
        self.mLinks = []
        self.mNavi = []
        self.mLinklengths = []
        self.mPathintersectionsflags = []
        self.___offset = 20

        # headers
        self.mHeader['NumNodes'] = unpack('I', self.path.read(4))[0]
        self.mHeader['NumVehNodes'] = unpack('I', self.path.read(4))[0]
        self.mHeader['NumPedNodes'] = unpack('I', self.path.read(4))[0]
        self.mHeader['NumCarPathLinks'] = unpack('I', self.path.read(4))[0]
        self.mHeader['NumLinksArray'] = unpack('I', self.path.read(4))[0]

        self.__read_pathnodes()
        self.__read_carpathlinks()
        self.__read_links_array()
        self.__read_carpathlinks_array()
        self.__read_linklengths()
        self.__read_pathintersection_flags()

    def __read_pathnodes(self):
        if len(self.mPathnodes) != self.mHeader['NumNodes']:
            self.path.seek(self.___offset, 0)
            for i in range(self.mHeader['NumNodes']):
                self.mPathnodes.append({})
                self.path.read(4)  # Memory Address
                self.path.read(4)  # Zero

#                self.mPathnodes[i] = collections.OrderedDict()
                self.mPathnodes[i]['x'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                self.mPathnodes[i]['y'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                self.mPathnodes[i]['z'] = float(unpack('h', self.path.read(2))[0]) / 8.0

                self.path.read(2)  # heuristic path cost

                self.mPathnodes[i]['baseLink'] = unpack('h', self.path.read(2))[0]
                self.mPathnodes[i]['areaID'] = unpack('h', self.path.read(2))[0]
                self.mPathnodes[i]['nodeID'] = unpack('h', self.path.read(2))[0]
                self.mPathnodes[i]['width'] = float(unpack('b', self.path.read(1))[0]) / 8
                self.mPathnodes[i]['floodcolor'] = unpack('b', self.path.read(1))[0]

                flags = unpack('B', self.path.read(1))[0]
                self.mPathnodes[i]['numberOfLinks'] = flags & 15;
                self.mPathnodes[i]['isDeadEnd'] = True if (flags >> 4) & 1 == 1 else False
                self.mPathnodes[i]['isIgnoredNode'] = True if (flags >> 5) & 1 == 1 else False
                self.mPathnodes[i]['isRoadBlock'] = True if (flags >> 6) & 1 == 1 else False
                self.mPathnodes[i]['isWaterNode'] = True if (flags >> 7) & 1 == 1 else False

                flags = unpack('B', self.path.read(1))[0]
                self.mPathnodes[i]['isEmergencyVehicleOnly'] = True if flags & 1 == 1 else False
                self.mPathnodes[i]['isRestrictedAccess'] = True if (flags >> 1) & 1 == 1 else False
                self.mPathnodes[i]['isDontWander'] = True if (flags >> 2) & 1 == 1 else False
                self.mPathnodes[i]['unk2'] = True if (flags >> 3) & 1 == 1 else False
                self.mPathnodes[i]['speedlimit'] = (flags >> 4) & 3
                self.mPathnodes[i]['unk3'] = True if (flags >> 6) & 1 == 1 else False
                self.mPathnodes[i]['unk4'] = True if (flags >> 7) & 1 == 1 else False

                flags = unpack('B', self.path.read(1))[0]
                self.mPathnodes[i]['spawnProbability'] = flags & 15
                self.mPathnodes[i]['behaviourType'] = (flags >> 4) & 15
                flags = unpack('B', self.path.read(1))[0]  # padding?

                # blender specific
                self.mPathnodes[i]['_btraversed'] = False
        return self.mPathnodes


    def __read_carpathlinks(self):
        if len(self.mCarpathlinks) != self.mHeader['NumCarPathLinks']:
            self.path.seek(self.___offset + (self.mHeader['NumNodes'] * 28), 0)
            for i in range(self.mHeader['NumCarPathLinks']):
                self.mCarpathlinks.append({})
                self.mCarpathlinks[i]['x'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                self.mCarpathlinks[i]['y'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                self.mCarpathlinks[i]['targetArea'] = unpack('h', self.path.read(2))[0]
                self.mCarpathlinks[i]['targetNode'] = unpack('h', self.path.read(2))[0]
                self.mCarpathlinks[i]['dirX'] = float(unpack('b', self.path.read(1))[0]) / 100
                self.mCarpathlinks[i]['dirY'] = float(unpack('b', self.path.read(1))[0]) / 100

                self.mCarpathlinks[i]['width'] = unpack('b', self.path.read(1))[0] / 8

                flags = unpack('B', self.path.read(1))[0]
                self.mCarpathlinks[i]['numLeftLanes'] = flags & 7
                self.mCarpathlinks[i]['numRightLanes'] = (flags >> 3) & 7
                self.mCarpathlinks[i]['trafficLightDirection'] = (flags >> 4) & 1

                flags = unpack('B', self.path.read(1))[0]
                self.mCarpathlinks[i]['trafficLightBehaviour'] = flags & 3
                self.mCarpathlinks[i]['isTrainCrossing'] = (flags >> 2) & 1

                flags = unpack('B', self.path.read(1))[0]
        return self.mCarpathlinks

    def __read_links_array(self):
        if len(self.mLinks) != self.mHeader['NumLinksArray']:
            self.path.seek(self.___offset + (self.mHeader['NumNodes'] * 28) + (self.mHeader['NumCarPathLinks'] * 14), 0)
            for i in range(self.mHeader['NumLinksArray']):
                self.mLinks.append({})
                self.mLinks[i]['area'] = unpack('h', self.path.read(2))[0]
                self.mLinks[i]['node'] = unpack('h', self.path.read(2))[0]
        return self.mLinks


    def __read_carpathlinks_array(self):
        if len(self.mNavi) != self.mHeader['NumLinksArray']:
            self.path.seek(self.___offset + (self.mHeader['NumNodes'] * 28) + (self.mHeader['NumCarPathLinks'] * 14) + (self.mHeader['NumLinksArray'] * 4) + 768,0)
            for i in range(self.mHeader['NumLinksArray']):
                self.mNavi.append({})
                carpathlinkaddress = unpack('H', self.path.read(2))[0]
                self.mNavi[i]['carpathlink'] = carpathlinkaddress & 1023
                self.mNavi[i]['area'] = carpathlinkaddress >> 10
        return self.mNavi


    def __read_linklengths(self):
        if len(self.mLinklengths) != self.mHeader['NumLinksArray']:
            self.path.seek(self.___offset + (self.mHeader['NumNodes'] * 28) + (self.mHeader['NumCarPathLinks'] * 14) + (self.mHeader['NumLinksArray'] * 4) + 768 + (self.mHeader['NumLinksArray'] * 2), 0)
            for i in range(self.mHeader['NumLinksArray']):
                self.mLinklengths.append(unpack('b', self.path.read(1))[0])
        return self.mLinklengths

    # atm it seem buggy
    def __read_pathintersection_flags(self):
        if len(self.mPathintersectionsflags) != self.mHeader['NumLinksArray']:
            self.path.seek(self.___offset + (self.mHeader['NumNodes'] * 28) + (self.mHeader['NumCarPathLinks'] * 14) + (self.mHeader['NumLinksArray'] * 4) + 768 + (self.mHeader['NumLinksArray'] * 2) + self.mHeader['NumLinksArray'], 0)
            for i in range(self.mHeader['NumLinksArray']):
                self.mPathintersectionsflags.append({})
                flags = None
                try:
                    flags = unpack('B', self.path.read(1))[0]
                except:
                    # print("Error in reading path intersection. Ignoring...")
                    flags = 0
                self.mPathintersectionsflags[i]['isRoadCross'] = True if flags & 1 else False
                self.mPathintersectionsflags[i]['isTrafficLight'] = True if flags & 2 else False
        return self.mPathintersectionsflags

    def Close(self):
        self.path.close()


class SAPaths:
    def __init__(self):
        self.carnodes = []
        self.boatnodes = []
        self.pednodes = []

        self.carpathlinknodes = []
        self.boatpathlinknodes = []
        
    def __validateCarPathLink(self):
        for node in self.carnodes:
            for link in node['_links']:
                linkNode = link['targetNode']
                #print(linkNode)
                carpathlink = link['carpathlink']
                if node is not carpathlink['navigationTarget']:
                    print("LinkedNODE: ", linkNode['x'], linkNode['y'], linkNode['z'])
                    print("NavTarget: ", carpathlink['navigationTarget']['x'], carpathlink['navigationTarget']['y'], carpathlink['navigationTarget']['z'])
                    # sa path nodes are strange bugged here please check node 
                    

        for node in self.boatnodes:
            for link in node['_links']:
                linkNode = link['targetNode']
                carpathlink = link['carpathlink']
                if node is not carpathlink['navigationTarget']:
                    assert linkNode is carpathlink['navigationTarget']
        print("[x] Finished Validation: Check for assertion errors")

    def combine_carpathlink_nodes(self):
        """
        [x] CarPathLink Node are the directional nodes which they are placed between the two endpoints of a curve
        [x] MIGHT determine the interpolation in some cases
        [x] the navigation target node pointed is the vector it is heading in XY axis and disregarding its's z value: See Node 211, area 6
        [x] normal vector provide a very rough approximation
        """

    def seperate_nodes(self, areafiles):
        for area, currentfile in areafiles.items():
            for i in range(currentfile.mHeader['NumNodes']):
                node = currentfile.mPathnodes[i]

                # TODO: delete unused parameter
                # del node['areaID']
                # del node['nodeID']

                node['_links'] = []
                for k in range(node['numberOfLinks']):
                    linkArrayIndex = node['baseLink'] + k
                    linkInfo = {}
                    #print(area, node['nodeID'], node['numberOfLinks'], currentfile.mLinks[linkArrayIndex]['area'], currentfile.mLinks[linkArrayIndex]['node'])
                    linkInfo['targetNode'] =    areafiles[currentfile.mLinks[linkArrayIndex]['area']].mPathnodes[currentfile.mLinks[linkArrayIndex]['node']]
                    linkInfo['length'] =        currentfile.mLinklengths[node['baseLink'] + k]   # can be removed as we need to recalculate them anyway
                    linkInfo['intersection'] =  currentfile.mPathintersectionsflags[node['baseLink'] + k]
                    # only add car path link if vehicle node
                    if i < currentfile.mHeader['NumVehNodes']:
                        linkInfo['carpathlink'] = areafiles[currentfile.mNavi[linkArrayIndex]['area']].mCarpathlinks[currentfile.mNavi[linkArrayIndex]['carpathlink']]
                    node['_links'].append(linkInfo)

                del node['numberOfLinks']
                del node['baseLink']

                if i < currentfile.mHeader['NumVehNodes']:
                    # add to car or boat
                    if node['isWaterNode']:
                        self.boatnodes.append(node)
                    else:
                        self.carnodes.append(node)
                else:
                    self.pednodes.append(node)

                del node['isWaterNode']

            # car paths are automatically linked to nodes
            for i in range(currentfile.mHeader['NumCarPathLinks']):
                carpathlink = currentfile.mCarpathlinks[i]
                carpathlink['navigationTarget'] = areafiles[carpathlink['targetArea']].mPathnodes[carpathlink['targetNode']]
                del carpathlink['targetNode']
                del carpathlink['targetArea']

        for i in range(len(self.boatnodes)):
            self.boatnodes[i]['id'] = i

        for i in range(len(self.carnodes)):
            self.carnodes[i]['id'] = i

        for i in range(len(self.pednodes)):
            self.pednodes[i]['id'] = i

        # DEBUG HELPER
        i = 0
        for node in self.carnodes:
            for link in node['_links']:
                carpathlink = link['carpathlink']
                if 'id' not in carpathlink:
                    carpathlink['id'] = i
                    i = i+1
                    self.carpathlinknodes.append(carpathlink)

        i = 0
        for node in self.boatnodes:
            for link in node['_links']:
                carpathlink = link['carpathlink']
                if 'id' not in carpathlink:
                    carpathlink['id'] = i
                    i = i+1
                    self.boatpathlinknodes.append(carpathlink)

        # validation
        #self.__validateCarPathLink()

        # TODO: merge carpathlink
        # TODO: seperate lines by their unique properties

    def load_nodes_from_directory(self, dirpath):
        f = []
        for (dirpath, dirnames, filenames) in walk(dirpath):
            f.extend(filenames)
            break

        dict_path_files = {}
        for i in (files for files in f if files.lower().startswith(PREFIX) and files.lower().endswith("."+EXT)):
            area_id = int(re.search(r'\d+', i).group())
            filepath = join(dirpath, i)
            dict_path_files[area_id] = SAPathSingleNode(filepath)

        odict_path_files = collections.OrderedDict(sorted(dict_path_files.items()))

        #self.unify_all_nodes(self, odict_path_files)
        self.seperate_nodes(odict_path_files)