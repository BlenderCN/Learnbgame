
import numpy as np
import sys
import FreeCAD
import math
import Part
from FreeCAD import Base


FREECADPATH = '/Applications/FreeCAD.app/Contents/lib'

def import_fcstd(path_freecad):
    sys.path.append(path_freecad)
    try:
        import FreeCAD
    except:
        print("Could not import FreeCAD")


import_fcstd(FREECADPATH)


class RecordingGrid:
    def__init__(selg, obj):
        '''Add the properties: GridRadius, GridHeight, HoleRadius, HoleSpacing'''
        obj.addProperty("App::PropertyLength", "GridRadius", "Grid", "Grid radius").Radius              = 6.75
        obj.addProperty("App::PropertyLength", "GridHeight", "Grid", "Grid height").Height              = 7.0
        obj.addProperty("App::PropertyLength", "HoleRadius", "Grid", "Radius of grid holes").HoleRadius = 0.25
        obj.addProperty("App::PropertyLength", "HoleSpacing", "Grid", "Spacing between adjacent holes").HoleSpacing = 1.0
	obj.addProperty("App::PropertyLength", "HoleAngle", "Grid", "Angle of holes relative to grid").HoleAngle = 0
        obj.Proxy = self

    def onChanged(self, fp, prop):
        if prop == "Radius" or prop == "Height" or prop == "HoleRadius" or prop == "HoleSpacing" or prop == "HoleAngle":   # if one of these is changed
            self.execute(fp)

    def execute(self, fp):  # main part of script

        HolePositions = -fp.GridRadius, fp.HoleSpacing, fp.GridRadius
        GridBase = Part.makeCylinder(fp.Radius, fp.Height) 				# Create a solid cylinder the size of the grid

	for X in HolePositions:
	     for Y in HolePositions:
		Eccentricity = sqrt(X^2 + Y^2) 						# Calculate the eccentricity of the hole from the grid center
		if Eccentricity < fp.GridRadius - 1
		     GridHole = Part.makeCylinder(fp.HoleRadius, fp.GridHeight) 	# Create a cylinder for current grid hole
		     GridHole.rotate(Vector(0,0,0),Vector(0,0,1),fp.HoleAngle) 		# Angle the grid hole
		     GridHole.translate(Base.Vector(X, Y, 0)) 				# Position the grid hole

		     AllGridHoles = AllGridHoles.fuse(GridHole) 			# Add grid hole to grid hole matrix
	diff = GridBase.cut(AllGridHoles)						# Boolean subtract matrix of grid holes from grid


def makeRecordingGrid():
    doc = FreeCAD.activeDocument()
    if doc == None:
        doc = FreeCAD.newDocument()
    grid = doc.addObject("Part::FeaturePython","Recording_Grid") #add object to document
    grid.Label = "Recording Grid"
    grid(grid)
    grid.ViewObject.Proxy=0

if __name__ == "__main__": # feature will be generated after macro execution
    makemakeRecordingGrid()