'''
Author :  Dominik Sand 
Date : 23.04.2013

This programpart is for creating a new so called "windowed list" from an existing Ionlist . 
The "windowed list" is containing average values of the existing Ionlist by taking a certain window size,
 which is defined in the options_panel and creating the arithmetic mean of all data within this winodow. 
e.g: If the Ionlistentry for an item contains 2000 datasets and the window size is 2 the resulting windowed list item has 1000 entries.
The process merges the value of window_size datasets and calculates the arithmetic mean of them , except on events.
Eventsnumber is calculated by a logic "&" operation in order to add all existing events to a dataset.
Background is that Events are defined by a "binary flag". If e.g. the "&" operation of 4 and the occourring value of the events results in "True" they will be processed by other programparts.
'''
import math
from .Ion import *

#function to calc the arithmetic means and process the occourring events
def calc_mean(Ionlist,item,start_index, end_index):
	#set IonData to default
	IonDataDic = {"X" : 0 , "Y" : 0 , "Z" : 0 ,"TOF" : 0 , "Events" : 0 , "Charge" : 0 , "Vt" : 0 , "KE" : 0 , "Mass" : 0 }
	#need to make sure not dividing by zero
	if(start_index - end_index  != 0):
		for i in range(start_index,end_index):
			#gather complete dataset of Ionlist and add it the values.
			data = Ionlist[item].export_data(i)
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
		IonDataDic["X"] = IonDataDic["X"] / (end_index-start_index)
		IonDataDic["Y"] = IonDataDic["Y"] / (end_index-start_index)
		IonDataDic["Z"] = IonDataDic["Y"] / (end_index-start_index)
		IonDataDic["TOF"] = IonDataDic["TOF"] / (end_index-start_index)
		if IonDataDic["Charge"]:
			IonDataDic["Charge"] = IonDataDic["Charge"] / (end_index-start_index)
		if IonDataDic["Vt"]:
			IonDataDic["Vt"] = IonDataDic["Vt"] / (end_index-start_index)
		if IonDataDic["KE"]:
			IonDataDic["KE"] = IonDataDic["KE"] / (end_index-start_index)
		if IonDataDic["Mass"]:
			IonDataDic["Mass"] = int(IonDataDic["Mass"] / (end_index-start_index))
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
		windowedIonlist[Ionlist[item].GetIonN()] = Ion(Ionlist[item].GetIonN())
		for i  in range(0,maindata,windowWidth):
			IonDataDic = calc_mean(Ionlist,item,i,i+windowWidth)
			windowedIonlist[Ionlist[item].GetIonN()].ins_mand_data(IonDataDic["X"],IonDataDic["Y"],IonDataDic["Z"],IonDataDic["TOF"])
			windowedIonlist[Ionlist[item].GetIonN()].ins_opt_data(IonDataDic)
	#add remaining data
	for item in Ionlist:
		windowsize = math.floor(Ionlist[item].datacount/windowWidth)
		maindata = windowsize*windowWidth
		restdata = Ionlist[item].datacount - maindata
		#index is based on available restdata
		IonDataDic = calc_mean(Ionlist,item,maindata,maindata+restdata)
		windowedIonlist[Ionlist[item].GetIonN()].ins_mand_data(IonDataDic["X"],IonDataDic["Y"],IonDataDic["Z"],IonDataDic["TOF"])
		windowedIonlist[Ionlist[item].GetIonN()].ins_opt_data(IonDataDic)
	return(windowedIonlist)