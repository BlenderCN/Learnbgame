'''
Author :  Dominik Sand 
Date : 23.04.2013
#This part of the program is for processesing the specified to process file and add it the internal datastructure of python to prepare Blender API usage, there is NO assertion if selected file is valid or not.
'''

import os
from .Ion import *
from .dic_process import *

def FileImport(SrcFile):
	DataBeginn = False
	#assign  Variables for Indicies
	Ion_N = 0
	event = 0
	x = 0
	y = 0
	z = 0
	TOF = 0
	velocity = 0
	charge = 0
	mass = 0
	kinetic_energy = 0
	current_list_item = 0
	token_count = 0
	
	#create dictonary for Ions where the key is the Ionnumber
	Ionlist={}
	#create data dictonary so data is known which is avialable
	data_dic = { "X" : None , "Y" : None , "Z" : None ,"TOF" : None , "Events" : None , "Charge" : None , "Vt" : None , "KE" : None , "Mass" : None }
	index_dic = { "X" : None , "Y" : None , "Z" : None ,"TOF" : None , "Events" : None , "Charge" : None , "Vt" : None , "KE" : None , "Mass" : None }
	#check available data
	for line in SrcFile:
		if "Ion N" in line:
			#count Tokens(",") until Index of Data  is found
			#transfer data allocation to dictonary
			Ion_N = 0
			x_index = line.find("X")
			index_dic["X"] = line.count(",",0,x_index)
			y_index = line.find("Y")
			index_dic["Y"] = line.count(",",0,y_index)
			z_index = line.find("Z")
			index_dic["Z"] = line.count(",",0,z_index)
			TOF_index  = line.find("TOF")
			index_dic["TOF"] = line.count(",",0,TOF_index)
			
			#following data is only processed if found
			event_index = line.find("Events")
			if ( event_index != -1 ):
				index_dic["Events"]= line.count(",",0,event_index)
			
			charge_index  = line.find("Charge")
			if ( charge_index != -1 ):
				index_dic["Charge"]= line.count(",",0,charge_index)
			
			velocity_index  = line.find("Vt")
			if ( velocity_index != -1 ):
				index_dic["Vt"] = line.count(",",0,velocity_index)
			
			kinetic_energy_index  = line.find("KE")
			if ( velocity_index != -1 ):
				index_dic["KE"] = line.count(",",0,kinetic_energy_index)
			
			mass_index = line.find("Mass")
			if ( mass_index != -1 ):
				index_dic["Mass"] = line.count(",",0,mass_index)
			
			#total number of tokens in the explanation line, used for data processing on file
			token_count = line.count(",")
			break
	#real process, token[0] is always Ion Number
	for line in SrcFile:
		#create tokens from line considering , as value Seperator
		token =  line.split(',')
		#if bad line skip line
		if len(token) != token_count and not token[0].isdigit():
			continue
		#break if End of Dataset is reached
		if "" in line:
			break
		#process real data if found, ignoring blanklines
		if((DataBeginn  == True) or (token[0].isdigit())):
			DataBeginn = True
			#function to move tokens to a dictonary for easier processesing and potential upgrades of Simblend
			process_data(data_dic,index_dic,token)
			#check if list is empty? if yes insert first dataset
			if not Ionlist:		
				Ionlist[(token[0])] = Ion(token[0])
				Ionlist[(token[0])].ins_mand_data(x = data_dic["X"], y = data_dic["Y"], z = data_dic["Z"] ,TOF = data_dic["TOF"])
				Ionlist[(token[0])].ins_opt_data(data_dic)
				continue
			#check if current data belongs to already created Ion,then attach data to Ion
			if (token[0] in Ionlist):
				Ionlist[(token[0])].ins_mand_data(x = data_dic["X"], y = data_dic["Y"], z = data_dic["Z"] ,TOF = data_dic["TOF"])
				Ionlist[(token[0])].ins_opt_data(data_dic)
			#if not new Ion must be created,increment current_list_item
			else:
				Ionlist[(token[0])] =Ion(token[0])
				Ionlist[(token[0])].ins_mand_data(x = data_dic["X"], y = data_dic["Y"], z = data_dic["Z"] ,TOF = data_dic["TOF"])
				Ionlist[(token[0])].ins_opt_data(data_dic)
		
	return Ionlist