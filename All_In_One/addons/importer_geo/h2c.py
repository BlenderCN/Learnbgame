"""
Load GEO / JSON Files and creates a Class with all accessible Values

Version:
0.1     - Reads Triangulated and Quads Polys
        - Polysoup support
        - UV support (has a bug)


"""
__author__ = 'fra'
__version__ = '0.1'

from . import hgeo

from itertools import count

# Houdini File Info Class
class hdata:
    fileversion = ''
    """ Returns the Fileversion Example: 15.0.270 """
    hasindex  = ''
    """ Returns the index Example: ??? """
    pointcount = 0
    """ Returns the pointcount Example: ??? """
    vertexcount = 0
    """ Returns the vertexcount Example: ??? """
    primitivecount = 0
    """ Returns the primitivecount Example: ??? """
    class info:
        """ Returns the index Example: ??? """
        software = ''
        date = ''
        hostname = ''
        artist = ''
        bounds = ''
        primcount_summary = ''
        attribute_summary = ''

    """
    The Object class has all Values for a simple setup. the speed will be surly slow
    """
    attributes  = []
    topology    = ''
    primitive   = ''
    points      = ''
    data        = []
    group       = []

# Inserts values into the
def __addInfo(data):
    """
    Creates a Object with all Informations in it
    :param data: File Tulpe [[value A],[Value B], [Value C].....]
    """

    data.fileversion        = data.data['fileversion']
    data.hasindex           = data.data['hasindex']
    data.pointcount         = data.data['pointcount']
    data.vertexcount        = data.data['vertexcount']
    data.primitivecount     = data.data['primitivecount']

    infodata = data.data['info']
    data.info.software             = infodata['software']
    data.info.date                 = infodata['date']
    data.info.hostname             = infodata['hostname']
    data.info.artist               = infodata['artist']
    data.info.bounds               = infodata['bounds']
    data.info.primcount_summary    = infodata['primcount_summary']
    data.info.attribute_summary    = infodata['attribute_summary']


def __addAttributeToDatatree(data):
    """
    Creates a Tulpe

    Definition, Value
    [Attributes, Type, Size, Storage, Name, Value]

    :param data:
    :return:
    """
    attrData = data['attributes']
    _dataDict = {'Attributes' : '', 'Type' : '', 'Size' : '', 'Storage' : '', 'Name' : '',  'Value' : ''}
    _dataTulpe = []

    count = 0
    while (count < len(attrData)):
        _dataDict['Attributes'] = attrData[count]
        count += 1
        for c in range(len(attrData[count])):
            _dataDict['Type'] = attrData[count][c][0][3]
            _dataDict['Name'] = attrData[count][c][0][5]
            _dataDict['Size'] = attrData[count][c][1][1]
            _dataDict['Storage'] = attrData[count][c][1][3]
            _dataDict['Value'] = count, c   # @todo: maybe not a good idea....needs a better solution
            if(_dataDict['Name'] == "P"):
                pt = []
                for p in attrData[count][c][1][7][5]:
                    pt.append(tuple(p))
                hdata.points = tuple(pt) # Add the Point data to hdata.points
            else:
                _dataTulpe.append(dict(_dataDict))
        count += 1
    return _dataTulpe


def __addGroupToDatatree(data):
    """

    """
    GROUPS = ["pointgroups","primitivegroups","edgegroups" ]
    _dataDict = {'Type' : '', 'Name' : '',  'Value' : ''}
    _dataTulpe = []

    for val in GROUPS:
        try:
            groupData = data[val]
        except:
            break
        for item in groupData:
            _dataDict['Type'] = val
            _dataDict['Name'] = item[0][1]
            _dataDict['Value'] = item[1][1][1][1]
            _dataTulpe.append(dict(_dataDict))
    return _dataTulpe


def __addTopologyToDatatree(data):
    """
    Add's the Topology tuple to hdata.topology
    """
    attrData = data['topology']
    return attrData[1][1]


def __loopTulpe(start, end, count, value):
    t = []
    tt = []
    c = 1
    while(start < end):
        tt.append(hdata.topology[value[start]])
        if (c == count):
            t.append(tuple(tt))
            c = 0
            tt = []
        start += 1
        c += 1
    return tuple(t)


def __addPrimitiveToDatatree(data):           # @todo needs a better solution at least it works bad code!
    type = data['primitives'][0][0][1]

    if (type == "run"):
        _primitive = data['primitives'][0][1]
        prim = []
        x = 0
        count = 0
        while(x < len(_primitive)):
            pp = []
            y = 0
            while(y < len(_primitive[x][0])):
                #print (count)
                pp.append(hdata.topology[count])
                y +=1
                count += 1
            prim.append(tuple(pp))
            x +=1
        return tuple(prim)

    elif (type == 'PolySoup'):
        _primitive = data['primitives'][0][1]
        polySetup = _primitive[3][0]
        polyCounts = _primitive[3][1]
        value = _primitive[3][2]

        p1 =__loopTulpe(0,polyCounts[0]*polySetup[0],polySetup[0],value)
        p2 = __loopTulpe(polyCounts[0]*polySetup[0],polyCounts[0]*polySetup[0]+polyCounts[1]*polySetup[1],polySetup[1],value)
        return p1
    elif (type == "Poly"):
        # _primitive = tuple(data['primitives'][0][1][1])
        return tuple(hdata.topology)



def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True
 
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
 
    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update()    
    return ob



def load(filename):
    """
    Loads file and Builds Dict's and for the info data it has a Class for simple access
    :param filename: path/to/file/Filename.geo (json/geo)
    :return:
    """
    object_file = open(filename, "r")
    fdata = hgeo.hjson.load(object_file)
    data = hgeo.listToDict(fdata)
    hdata.data = data # @todo not a ideal solution
    __addInfo(hdata)
    #__addObject(hdata)  # Old test code can be deleted
    
    hdata.attributes   = __addAttributeToDatatree(hdata.data)
    hdata.topology     = __addTopologyToDatatree(hdata.data)
    hdata.primitive    = __addPrimitiveToDatatree(hdata.data)
    hdata.group        = __addGroupToDatatree(hdata.data)

class Test:
    def showInfo():
        """
        Prints the Information from the file out.
        """
        print("\n**************************************")
        print("Fileversion: \t\t", hdata.fileversion)
        print("Hasindex: \t\t\t", hdata.hasindex)
        print("Pointcount: \t\t", hdata.pointcount)
        print("Vertexcount: \t\t", hdata.vertexcount)
        print("Primitivecount: \t", hdata.primitivecount)
        print("----------------------------------------")
        print("INFO:")
        print("\tSoftware:\t\t\t", hdata.info.software)
        print("\tDate:\t\t\t\t", hdata.info.date)
        print("\tHostname:\t\t\t", hdata.info.hostname)
        print("\tArtist:\t\t\t\t", hdata.info.artist)
        print("\tBound:\t\t\t\t", hdata.info.bounds)
        print("\tPrimcount summary:", hdata.info.primcount_summary)
        print("\tAttribute summary:", hdata.info.attribute_summary)
        print("**************************************")