'''
Author :  Dominik Sand 
Date : 23.04.2013

creates a list of existing ionmasses in order to group existing ions and create materials for them.

'''

def masslist_create(Ionlist):
	masslist = []
	for item in Ionlist:
		#check only for first entry of mass because mass is considered as constant
		if(Ionlist[item].GetMass(0) not in masslist):
			masslist.append(Ionlist[item].GetMass(0))
	return masslist