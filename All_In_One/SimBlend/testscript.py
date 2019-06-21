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
	testscript.py

	a testscript to create artificial ion trajectory data for testing purposes

	Original author:  Dominik Sand
	Version: 0.1
'''
from .helper import *
from .windowed import *


def output_list(list):
	for item in list:
		for i in range(0,list[item].datacount):
			x = float(list[item].GetXYZ(i)[0])
			y = float(list[item].GetXYZ(i)[1])
			z = float(list[item].GetXYZ(i)[2])
			ion_n = str(list[item].GetIonN())
			print('Ion: {0},x: {1},  y: {2}, z: {3}\n'.format(ion_n,x,y,z))
def main():
	ions = 2
	steps = 25
	merge_ammount = 5
	Ionlist = CreateSyntheticIonData(ions, steps)
	windowed_list = windowedMeans(Ionlist, merge_ammount)
	output_list(Ionlist)
	print("Line Break\n")
	ions = 2
	steps = 25
	merge_ammount = 1
	Ionlist = CreateSyntheticIonData(ions, steps)
	windowed_list = windowedMeans(Ionlist, merge_ammount)
	output_list(Ionlist)
 
if __name__ == "__main__":
    main()
