from os.path import isfile, join
from os import walk
from struct import unpack
from io import BytesIO
import re
import collections

PREFIX = "nodes"
EXT = "nod"

def getBitFields(var, lOffset, size):
    return (var >> lOffset) & ((2 ** size) -1)

def getNodeNumberOfLinks(flags):
    return getBitFields(flags, 0, 3)

class IVPathSingleNode:
    def __init__(self, node):
        self.path = BytesIO(open(node, "rb").read())
        self.mHeader = {}
        self.mPathnodes = []
        self.mCarpathlinks = []
        self.___offset = 16

        # headers
        self.mHeader['NumNodes'] = unpack('I', self.path.read(4))[0]
        self.mHeader['NumVehNodes'] = unpack('I', self.path.read(4))[0]
        self.mHeader['NumIntersection'] = unpack('I', self.path.read(4))[0]
        self.mHeader['NumCarPathLinks'] = unpack('I', self.path.read(4))[0]

        self.__read_pathnodes()
        self.__read_carpathlinks()

    def __read_pathnodes(self):
        if len(self.mPathnodes) != self.mHeader['NumNodes']:
            self.path.seek(self.___offset, 0)
            for i in range(self.mHeader['NumNodes']):
                self.mPathnodes.append({})
                self.path.read(4)  # Memory Address
                self.path.read(4)  # Zero

                self.mPathnodes[i]['areaID'] = unpack('h', self.path.read(2))[0]
                self.mPathnodes[i]['nodeID'] = unpack('h', self.path.read(2))[0]
                
                self.mPathnodes[i]['middleX'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                self.mPathnodes[i]['middleY'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                
                self.path.read(2)  # heuristic path cost
                self.mPathnodes[i]['baseLink'] = unpack('h', self.path.read(2))[0]
                
                self.mPathnodes[i]['x'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                self.mPathnodes[i]['y'] = float(unpack('h', self.path.read(2))[0]) / 8.0
                self.mPathnodes[i]['z'] = float(unpack('h', self.path.read(2))[0]) / 128.0
                
                self.mPathnodes[i]['width'] = float(unpack('b', self.path.read(1))[0]) / 8.0
                self.mPathnodes[i]['floodcolor'] = unpack('b', self.path.read(1))[0]

                flags = unpack('B', self.path.read(1))[0]
                self.mPathnodes[i]['spawnProbability'] = flags & 15
                self.mPathnodes[i]['behaviourType'] = (flags >> 4) & 15
                
                flags = unpack('B', self.path.read(1))[0]
                
                flags = unpack('B', self.path.read(1))[0]
                self.mPathnodes[i]['numberOfLinks'] = flags & 15;
                self.mPathnodes[i]['isDeadEnd'] = True if (flags >> 4) & 1 == 1 else False
                self.mPathnodes[i]['isRoadBlock'] = True if (flags >> 6) & 1 == 1 else False
                self.mPathnodes[i]['isRestrictedAccess'] = True if (flags >> 7) & 1 == 1 else False
                self.mPathnodes[i]['speedlimit'] = (flags >> 5) & 3

                flags = unpack('B', self.path.read(1))[0]
                self.mPathnodes[i]['isEmergencyVehicleOnly'] = True if flags & 1 == 1 else False
                self.mPathnodes[i]['isWaterNode'] = True if (flags >> 1) & 1 == 1 else False
                self.mPathnodes[i]['isIgnoredNode'] = True if (flags >> 3) & 1 == 1 else False
                self.mPathnodes[i]['isDontWander'] = True if (flags >> 4) & 1 == 1 else False
                self.mPathnodes[i]['unk2'] = True if (flags >> 3) & 1 == 1 else False
                self.mPathnodes[i]['unk3'] = True if (flags >> 6) & 1 == 1 else False
                self.mPathnodes[i]['unk4'] = True if (flags >> 7) & 1 == 1 else False
        return self.mPathnodes


    def __read_carpathlinks(self):
        if len(self.mCarpathlinks) != self.mHeader['NumCarPathLinks']:
            self.path.seek(self.___offset + (self.mHeader['NumNodes'] * 32), 0)
            for i in range(self.mHeader['NumCarPathLinks']):
                self.mCarpathlinks.append({})
                self.mCarpathlinks[i]['targetArea'] = unpack('h', self.path.read(2))[0]
                self.mCarpathlinks[i]['targetNode'] = unpack('h', self.path.read(2))[0]
                flags = unpack('B', self.path.read(1))[0]
                self.mCarpathlinks[i]['trafficLightBehaviour'] = flags & 3
                self.mCarpathlinks[i]['isTrainCrossing'] = (flags >> 2) & 1
                flags = unpack('B', self.path.read(1))[0]
                self.mCarpathlinks[i]['numLeftLanes'] = flags & 7
                self.mCarpathlinks[i]['numRightLanes'] = (flags >> 3) & 7
                self.mCarpathlinks[i]['trafficLightDirection'] = (flags >> 4) & 1
                self.mCarpathlinks[i]['length'] = unpack('b', self.path.read(1))[0] / 8
                flags = unpack('B', self.path.read(1))[0]
        return self.mCarpathlinks
        
    def Close(self):
        self.path.close()


class IVPaths:
    def __init__(self):
        self.carnodes = []
        self.boatnodes = []

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
                    linkInfo['targetNode'] =    areafiles[currentfile.mCarpathlinks[linkArrayIndex]['targetArea']].mPathnodes[currentfile.mCarpathlinks[linkArrayIndex]['targetNode']]
                    linkInfo['length'] =        currentfile.mCarpathlinks[linkArrayIndex]['length']   # can be removed as we need to recalculate them anyway
                    # only add car path link if vehicle node
                    node['_links'].append(linkInfo)

                del node['numberOfLinks']
                del node['baseLink']

                # add to car or boat
                if node['isWaterNode']:
                    self.boatnodes.append(node)
                else:
                    self.carnodes.append(node)

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

        # DEBUG HELPER
        i = 0
        for node in self.carnodes:
            for link in node['_links']:
                if 'id' not in link:
                    link['id'] = i
                    i = i+1
                    self.carpathlinknodes.append(link)

        i = 0
        for node in self.boatnodes:
            for link in node['_links']:
                if 'id' not in link:
                    link['id'] = i
                    i = i+1
                    self.boatpathlinknodes.append(link)

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
            dict_path_files[area_id] = IVPathSingleNode(filepath)

        odict_path_files = collections.OrderedDict(sorted(dict_path_files.items()))

        #self.unify_all_nodes(self, odict_path_files)
        self.seperate_nodes(odict_path_files)