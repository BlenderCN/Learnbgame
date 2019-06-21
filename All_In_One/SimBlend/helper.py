'''
	SimBlend, a Blender import module for SIMION ion trajectory data

	Copyright (C) 2013 - Physical and Theoretical Chemistry /
	Institute of Pure and Applied Mass Spectrometry
	of the University of Wuppertal, Germany


	This file is part of SimBlend

	SimBlend is free software: You may redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
	------------
	helper.py

	some helpling methods

	Original author:  Dominik Sand
	Version: 0.1
'''

from .ion import *
import math

def CreateSyntheticIonData(nIons,listLength):
	'''
	Creates a synthetic ion list for debugging and testing. This module creates a specified number of Iontrajectory data that can be processed by simblend.
	Normally this module is not used, because simblend processes the file specified during the lunch

	arguments: 
	listLength - 
	nIons 	   - 
	'''
	data_dic = { "X" : None , "Y" : None , "Z" : None ,"TOF" : None , "Events" : None , "Charge" : None , "Vt" : None , "KE" : None , "Mass" : None }

	#Ionlist is a dictionary, with the ion number / index as key
	Ionlist={}
	
	#create some ions on a easily predictable trajectory
	velocityX = 1
	radius = 5
	shiftY = 2
	freqY = 1
	freqZ = 1
	for k in range(0,nIons): 
		t = 0.0 # time
		for i in range(0,listLength):
			t = t+0.1
			x = t*velocityX
			y = math.sin(t*freqY)*radius + k*shiftY
			z = math.cos(t*freqZ)*radius
			TOF = t
			#dummy data for testing
			data_dic["Charge"] = 1
			data_dic["Vt"] = 1 # fixme: this should be calculated correctly
			data_dic["KE"]  = 1 # fixme: this should be calculated correctly
			data_dic["Mass"] = str(1)
			data_dic["Events"] = 1
			if i==0: 
				Ionlist[str(k)] = Ion(k)
			
			Ionlist[str(k)].ins_mand_data(x,y,z,TOF)
			Ionlist[str(k)].ins_opt_data(data_dic)

	return Ionlist
