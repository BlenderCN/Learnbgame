'''
Author :  Dominik Sand 
Date : 23.04.2013
function to process the parsed token and transfer it to data dictonary. Index_dic contains information on which column of token the data can be found.
the data Dictonary is used during the File processing during the import of the data to Python structures
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