import os

import numpy as np
from osgeo import gdal
from scipy.misc import imresize

class ReadGDAL():
    def __init__(self, path, crop=None):
        """
        Parameters
        ----------
        path        (str) The PATH to the input DTM
        crop        (list) The extent to crop the DTM
                           [xstart, ystart, xsize, ysize]

        Attributes
        ----------
        path        (str) PATH to the input file
        crop        (list) List of pixel or latlon crop coords (not yet impl)
        name        (str) Name of the file without suffix
        inds        (obj) GDAL file object
        size        (list) [xsize, ysize] - updated on resample
        worldfile   (dict) Python representation of teh geotransformation
        nband       (int) Number of bands
        band1       (obj) GDAL band proxy object
        NDV         (float) No Data Value
        projection  (str) WKT representation of the projection
        maxval      (float) Maximum DN
        minval      (float) Minimum DN
        dtype       (str) Input data type
        depth       (int) Input data type depth, e.g. 8, 16 or 32
        unsigned    (bool) Is the data unsigned?
        geosize     (list) [xsize, ysize] in geographic units
        geocenter   (list) [xcenter, ycenter] in geographic units
        geoext      (list) List of tuples of the corners in lat/long
        pixelextent (dict) Dict of corners keyed by ll, lr, ul, ur

        """

        self.path = path
        self.crop = crop
        self.name = os.path.basename(path).split('.')[0]

        self.inds = gdal.Open(self.path)
        self.size = [self.inds.RasterXSize, self.inds.RasterYSize]
        self.getworldfile()
        self.nband = self.inds.RasterCount
        self.band1 = self.inds.GetRasterBand(1)
        self.NDV = self.band1.GetNoDataValue()
        self.getdtype()
        self.projection = self.inds.GetProjection()
        self.maxval = self.band1.GetMaximum()
        self.minval = self.band1.GetMinimum()

        #Get the corner coordinates and the size in geographic coords
        self.geocorners()
        self.getgeosize()
        self.getgeocenter()

        #Extract the array and fill the NDV with NaN
        self.extractimage()
        self.fillNDV()

    def getworldfile(self):
        """
        Use the geotransform information to generate an in
        memory worldfile
        """
        ds = self.inds
        topleftx, pxsizex, rotx, toplefty, roty, pxsizey = ds.GetGeoTransform()
        #Adjust from pixel corner to pixel center
        topleftx += abs(pxsizex / 2.0)
        toplefty -= abs(pxsizey / 2.0)
        self.worldfile = {'xpixelsize': pxsizex,
                          'rotationx': rotx,
                          'rotationy': roty,
                          'ypixelsize': pxsizey,
                          'topleftx': topleftx,
                          'toplefty': toplefty}
        self.origin = [topleftx, toplefty, None]

    def getgeosize(self):
        """
        Compute the image size in geographic coordinates
        """
        xsize = self.size[0]
        ysize = self.size[1]
        xpixelsize = self.worldfile['xpixelsize']
        ypixelsize = self.worldfile['ypixelsize']
        self.geosize = [xsize * abs(xpixelsize), ysize * abs(ypixelsize)]

    def getpixelextent(self, x, y):
        """
        Compute the image size in Blender pixel space

        Parameters
        -----------
        x       (ndarray) meshgrid output [[1,2,3], [1,2,3], [...]]
        y       (ndarray) meshgrid output [[1,2,3], [1,2,3], [...]]
        """
        xmin = 0
        xmax = x.shape[1] - 1
        ymin = 0
        ymax = y.shape[0] - 1

        ul = [xmin, ymin, self.arr[ymin, xmin]]
        ll = [xmin, ymax, self.arr[ymax, xmin]]
        lr = [xmax, ymax, self.arr[ymax, xmax]]
        ur = [xmax, ymin, self.arr[ymin, xmax]]
        self.pixelextent = {'ul': ul, 'll': ll, 'lr': lr, 'ur': ur}

    def getpixelcenter(self):
        """
        Compute the image center in Blender pixel space
        """
        pxe = self.pixelextent
        centerx = int((pxe['lr'][0] - pxe['ul'][0]) / 2.0)
        centery = int((pxe['lr'][1] - pxe['ul'][1]) / 2.0)
        centerz = self.arr[centery, centerx]
        self.pixelcenter = [centerx, centery, centerz]

    def getgeocenter(self):
        """
        Compute the center of the image in geographic space
        """
        origin = self.geoext[0]  # Upper left
        self.geocenter = [origin[0] + self.geosize[0] / 2.0, origin[1] - self.geosize[1] / 2.0]

    def getdtype(self):
        """
        Assumes that all bands are homogeneous and gets the data type.
        """
        self.dtype = gdal.GetDataTypeName(self.band1.DataType)
        if self.dtype == "Byte":
            self.unsigned = True
            self.depth = 8
        else:
            self.depth = int(self.dtype[-2:])
            if self.dtype[0] is 'U':
                self.unsigned = True
            else:
                self.unsigned = False

    def fillNDV(self):
        """
        Fill the NDV value with np.NaN
        """
        if self.NDV != None:
            mask = np.where(self.arr == self.NDV)[0]
            if len(mask) > 0:
                self.arr[self.arr == self.NDV] = np.nan

    def extractimage(self):
        if self.crop == True:
            pass
        else:
            self.arr = self.band1.ReadAsArray().astype(np.float32)

    def resize(self, percentage_reduction=0.5, interpolation='cubic'):
        """
        Resize the array by a given percentage using the provided interpolation
        method.

        Parameters
        -----------
        percentage_reduction    (float) The percentage to reduce the image by.
        interpolateion          (str) Interpolation method
            Valid Arguments: nearest, bilinear, bicubic, cubic
        """
        self.arr = imresize(self.arr, percentage_reduction,
                            interp=interpolation.lower(),mode='F')

    def scale(self, zscale):
        """
        Scale the DTM z value by some amount

        Parameters
        ----------
        scale       (float) Values to scale by
        """
        self.arr *= zscale

    def pixel2latlon(self, x, y):
        """
        An affine transformation from pixel space (x,y) to lat,long

        Parameters
        ----------
        x       (int) x pixel value
        y       (int) y pixel value

        Return
        -------
        xp      (float) latitude
        yp      (float) longitude
        """

        wf = self.worldfile
        xp = wf['xpixelsize'] * x + wf['rotationx'] * y + wf['topleftx']
        yp = wf['rotationy'] * x + wf['ypixelsize'] * y + wf['toplefty']
        return xp,yp

    def geocorners(self):
        """
        Get the corner of the georeferenced image in lat/long

        Returns
        ext     (list) [ul, ll]
        """
        xsize = self.size[0]
        ysize = self.size[1]

        self.geoext = []

        for i in [(0, ysize),(xsize, ysize), (xsize, 0), (0, 0)]:
            self.geoext.append(tuple(self.pixel2latlon(i[0], i[1])))

        self.get_latlon_bounds()

    def get_latlon_bounds(self):
        """
        Parse the lat/long extents and get the min and max values
        """
        self.minlat = float('inf')
        self.maxlat = float('-inf')
        self.minlon = float('inf')
        self.maxlon = float('-inf')

        for e in self.geoext:
            if e[0] < self.minlon:
                self.minlon = e[0]
            if e[0] > self.maxlon:
                self.maxlon = e[0]
            if e[1] < self.minlat:
                self.minlat = e[1]
            if e[1] > self.maxlat:
                self.maxlat = e[1]
