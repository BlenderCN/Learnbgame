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
	dic_process.py

	Function to process the parsed token and transfer it to data dictionary.
	Index_dic contains information on which column of token the data can be found.
	The data dictionary is used during the File processing during the import of the data to Python structures

	Original author:  Dominik Sand
	Version: 0.1
'''
def process_data(data_dic ,index_dic, token ):
	#do stuff in data_dic
	data_dic["X"] = token[index_dic["X"]]
	data_dic["Y"] = token[index_dic["Y"]]
	data_dic["Z"] = token[index_dic["Z"]]
	data_dic["TOF"] = token[index_dic["TOF"]]
	if (index_dic["Events"] != None):
		data_dic["Events"] = token[index_dic["Events"]]
	if (index_dic["Charge"] != None):
		data_dic["Charge"] = token[index_dic["Charge"]]
	if (index_dic["Vt"] != None):
		data_dic["Vt"] = token[index_dic["Vt"]]
	if (index_dic["KE"] != None):
		data_dic["KE"] = token[index_dic["KE"]]
	if (index_dic["Mass"] != None):
		data_dic["Mass"] = token[index_dic["Mass"]]