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
	windowed.py

	Creates a new so called "windowed list" from an existing Ionlist .
	The "windowed list" is containing average values of the existing Ionlist by taking a certain window size
    which is defined in the options_panel and creating the arithmetic mean of all data within this window.

	e.g: If the Ionlistentry for an item contains 2000 data points and the window size is 2 the resulting
	windowed list item has 1000 entries.
	The process merges the value of window_size data sets and calculates the arithmetic mean of them, except on events.
	The event number is calculated by a logic "&" operation in order to add all existing events to a data set.
	Background is that events in SIMION are represented by a "binary flag".
	If e.g. the "&" operation of 4 and the occurring value of the events results in "True"
	they will be processed by other program parts.

	Original author:  Dominik Sand
	Version: 0.1
'''


import math
from .ion import *

#process to gather data and add it to the Datadic
def list_data_process(IonDataDic, data, size):
	IonDataDic["X"] += float(data["X"])
	IonDataDic["Y"] += float(data["Y"])
	IonDataDic["Z"] += float(data["Z"])
	IonDataDic["TOF"] += float(data["TOF"])
	#process optional data
	if data["Events"]:
		if ((IonDataDic["Events"] & int(data["Events"])) == 0 ):
			IonDataDic["Events"] += int(data["Events"])
	if data["Charge"]:
		IonDataDic["Charge"] +=  float(data["Charge"])
	if data["Vt"]:
		IonDataDic["Vt"] +=  float(data["Vt"])
	if data["KE"]:
		IonDataDic["KE"] +=  float(data["KE"])
	if data["Mass"]:
		IonDataDic["Mass"] +=  float(data["Mass"])
	#calculate the arithmetic means
	IonDataDic["X"] = IonDataDic["X"] / (size)
	IonDataDic["Y"] = IonDataDic["Y"] / (size)
	IonDataDic["Z"] = IonDataDic["Z"] / (size)
	IonDataDic["TOF"] = IonDataDic["TOF"] / (size)
	if IonDataDic["Charge"]:
		IonDataDic["Charge"] = IonDataDic["Charge"] / (size)
	if IonDataDic["Vt"]:
		IonDataDic["Vt"] = IonDataDic["Vt"] / (size)
	if IonDataDic["KE"]:
		IonDataDic["KE"] = IonDataDic["KE"] / (size)
	if IonDataDic["Mass"]:
		IonDataDic["Mass"] = int(IonDataDic["Mass"] / (size))


#function to calc the arithmetic means and process the occourring events
def calc_mean(Ionlist,item,start_index, end_index):
	#set IonData to default
	IonDataDic = {"X" : 0 , "Y" : 0 , "Z" : 0 ,"TOF" : 0 , "Events" : 0 , "Charge" : 0 , "Vt" : 0 , "KE" : 0 , "Mass" : 0 }
	#need to make sure not dividing by zero
	if(start_index - end_index  != 0):
		size = end_index-start_index
		for i in range(start_index,end_index):
			#gather complete dataset of Ionlist and add it the values.
			data = Ionlist[item].export_data(i)
			list_data_process(IonDataDic, data, size)
	else:
		data = Ionlist[item].export_data(Ionlist[item].datacount-1)
		IonDataDic["X"] = float(Ionlist[item].GetXYZ(Ionlist[item].datacount-1)[0])
		IonDataDic["Y"] = float(Ionlist[item].GetXYZ(Ionlist[item].datacount-1)[1])
		IonDataDic["Z"] = float(Ionlist[item].GetXYZ(Ionlist[item].datacount-1)[2])
		IonDataDic["TOF"] = float(Ionlist[item].GetToF(Ionlist[item].datacount-1))
		if data["Events"]:
			IonDataDic["Events"] = data["Events"]
		if data["Charge"]:
			IonDataDic["Charge"] =  float(data["Charge"])
		if data["Vt"]:
			IonDataDic["Vt"] =  float(data["Vt"])
		if data["KE"]:
			IonDataDic["KE"] =  float(data["KE"])
		if data["Mass"]:
			IonDataDic["Mass"] =  int(data["Mass"])
	return IonDataDic
	
#function to calculate the windowed list
def windowedMeans(Ionlist, windowWidth):
	windowedIonlist={}
	IonDataDic ={}
	if windowWidth == 1:
		return Ionlist
	#function to gather the major part of the data. If datacount % windowWidth is not 0 remaining data has to be added.
	for item in Ionlist:
		windowsize = math.floor(Ionlist[item].datacount/windowWidth)
		maindata = windowsize*windowWidth
		restdata = Ionlist[item].datacount - maindata
		CurrentIon = Ionlist[item].GetIonN()
		windowedIonlist[CurrentIon] = Ion(CurrentIon)
		for i  in range(0,maindata,windowWidth):
			IonDataDic = calc_mean(Ionlist,item,i,i+windowWidth)
			windowedIonlist[CurrentIon].ins_mand_data(IonDataDic["X"],IonDataDic["Y"],IonDataDic["Z"],IonDataDic["TOF"])
			windowedIonlist[CurrentIon].ins_opt_data(IonDataDic)
	#add remaining data
	for item in Ionlist:
		windowsize = math.floor(Ionlist[item].datacount/windowWidth)
		maindata = windowsize*windowWidth
		restdata = Ionlist[item].datacount - maindata
		#index is based on available restdata
		IonDataDic = calc_mean(Ionlist,item,maindata,maindata+restdata)
		CurrentIon = Ionlist[item].GetIonN()
		windowedIonlist[CurrentIon].ins_mand_data(IonDataDic["X"],IonDataDic["Y"],IonDataDic["Z"],IonDataDic["TOF"])
		windowedIonlist[CurrentIon].ins_opt_data(IonDataDic)
	return(windowedIonlist)