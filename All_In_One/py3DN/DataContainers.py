# Author: Paulo de Castro Aguiar	
# Date: July 2012
# email: pauloaguiar@fc.up.pt

# set base layer (bl): cellbody bl, trees bl+1, spines bl+2, varicos bl+3, structs bl+4, math bl+5

"""Data containers definitions"""

class POINT:
    """This is a container for point data"""
    def __init__(self, P=None, r=None, n=None, ppid=None, level=None, ptype=None, active=None):
        self.P        = P        ## position (numpy array)
        self.r        = r        ## radius
        self.n        = n        ## normal vector (numpy array)
        self.ppid     = ppid     ## parent point id
        self.level    = level    ## bifurcation level in the tree
        self.ptype    = ptype    ## flag to identify point type (standard; node; endpoint)
        self.active   = True     ## boolean to signal if this point should be drawn (avoiding mesh folding)


class RAWPOINT:
    """This is a container for raw point data"""
    def __init__(self, P=None, r=None, ppid=None, level=None, ptype=None, contact=None ):
        self.P       = P         ## position
        self.r       = r         ## radius
        self.ppid    = ppid      ## parent point id
        self.level   = level     ## bifurcation level in the tree
        self.ptype   = ptype     ## flag to identify point type (standard; node; endpoint)
        self.contact = False     ## boolean to identify presence of spine or varicosity


class VARICOSITY:
    """This is a container for varicosity data"""
    def __init__(self, P=None, r=None, rawppid=None):
        self.P       = P         ## position (list of floats)
        self.r       = r         ## marker radius
        self.rawppid = rawppid   ## parent raw point id


class SPINE:
    """This is a container for spine data"""
    def __init__(self, P=None, Q=None, r=None, rawppid=None):
        self.P       = P         ## start position (list of floats)
        self.Q       = Q         ## stop position (list of floats)
        self.r       = r         ## radius
        self.rawppid = rawppid   ## parent raw point id


class TREE:
    """This is a container for tree data"""
    def __init__(self):
        self.total_points       = 0                ## total number of points
        self.point              = []               ## array of points - class POINT
        self.total_rawpoints    = 0                ## total number of raw points
        self.rawpoint           = []               ## array of raw points - class RAW_POINT
        self.total_spines       = 0                ## total number of spines
        self.spine              = []               ## array of spines - class SPINE
        self.total_varicosities = 0                ## total number of varicosities
        self.varicosity         = []               ## array of varicosities - class VARICOSITY
        self.leaf               = 'unspecified'    ## type of tree ending
        self.type               = 'unspecified'    ## tree label/type
        self.color              = '#FFFFFF'        ## color in hex
        self.total_activepoints = -1               ## total number of active points (signaled to be drawn)


class CONTOUR:
    """This is a container for contour data"""
    def __init__(self):
        self.total_points = 0                  ## total number of point in this contour
        self.point        = []                 ## list of points
        self.centroid     = '[0.0, 0.0, 0.0]'  ## coordinates for the contour's centroid
        self.color        = '#FFFFFF'          ## color in hex


class NEURON:
    """This class is a container for the morphology data for each neuron, as extracted from the neurolucida XML file"""
    def __init__(self):
        self.cellbody    = []             ## holds cell body parameters
        self.total_trees = 0              ## total number of trees (axonal and dendritic)
        self.tree        = []             ## array of trees - class TREE
        self.label       = 'unspecified'  ## label used to identify this neuron


class MORPHOLOGY:
    """This class is a container for the anatomical data providing location/reference to the neuron"""
    def __init__(self):
        self.total_structures = 0   ## total number of anatomical structures
        self.structure        = []  ## array of anatomical structures


class MORPH_STRUCT:
    """This is a container for anatomical structures"""
    def __init__(self):
        self.total_contours = 0                  ## total number of contours
        self.rawcontour     = []                 ## array of raw contours
        self.contour        = []                 ## array of interpolated contours
        self.name           = 'unspecified'      ## name used to identify this anatomical structure
        self.color          = '#FFFFFF'          ## color in hex
        self.centroid       = '[0.0, 0.0, 0.0]'  ## coordinates for the structure's centroid
