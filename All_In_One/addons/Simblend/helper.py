from .Ion import *
import math

def CreateSyntheticIonData(nIons,listLength):
	'''
	Creates a synthetic ion list for debugging and testing

	arguments: 
	listLength - 
	nIons 	   - 
	'''
	data_dic = { "X" : None , "Y" : None , "Z" : None ,"TOF" : None , "Events" : None , "Charge" : None , "Vt" : None , "KE" : None , "Mass" : None }
	Ion_N = 0
	x = 0
	y = 0
	z = 0
	TOF = 0
	velocity = 0
	charge = 0
	mass = 0
	kinetic_energy = 0
	current_list_item = 0
	
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
			data_dic["Charge"] = 1
			data_dic["Vt"] = 1 # fixme: this should be calculated correctly
			data_dic["KE"]  = 1 # fixme: this should be calculated correctly
			data_dic["Mass"] = str(1)
			
			if i==0: 
				Ionlist[str(k)] = Ion(k)
			
			Ionlist[str(k)].ins_mand_data(x,y,z,TOF)
			Ionlist[str(k)].ins_opt_data(data_dic)

	return Ionlist
