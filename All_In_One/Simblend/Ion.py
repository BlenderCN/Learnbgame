'''
Author :  Dominik Sand 
Date : 23.04.2013

Core class for storing the information of each ion in every timestep, so they can be used for processesing the data to Mesh / Animation.

'''
import bpy

class Ion():
	def __init__(self,Ion_N):
		self.Ion_N = Ion_N
		self.events = []
		self.xyz = []
		self.TOF = []
		self.charge = []
		self.velocity=[]
		self.kinetic_energy=[]
		self.mass = []
		#number of informations in the lists
		self.datacount= 0
	
	#mandantory data insertion	
	def ins_mand_data(self,x,y,z,TOF):
		self.AppXYZ(x,y,z)
		self.AppToF(TOF)
		self.datacount +=1
	
	#uses a dictonary of data to transfer to the Ion, optional data insert
	def ins_opt_data(self, data_dic):
		#check what data is inside and move it to Ion
		if (data_dic["Events"] != None):
			self.AppEvent(data_dic["Events"])
		if (data_dic["Charge"] != None):
			self.AppCharge(data_dic["Charge"])
		if (data_dic["Vt"] != None):
			self.AppVelocity(data_dic["Vt"])
		if (data_dic["KE"] != None):
			self.AppKinetic_Energy(data_dic["KE"])
		if (data_dic["Mass"] != None):
			self.AppMass(data_dic["Mass"])
	
	#export function
	def export_data(self,n):
		xyz = self.GetXYZ(n)
		result_dic={ "Ion_N" : self.GetIonN ,"X" : xyz[0] , "Y" : xyz[1] ,"Z" : xyz[2] , "TOF" : self.GetToF(n)}
		if self.events:
			result_dic["Events"] = self.GetEvent(n)
		if self.charge:
			result_dic["Charge"] = self.GetCharge(n)	
		if self.velocity:
			result_dic["Vt"] = self.GetVelocity(n)
		if self.kinetic_energy:
			result_dic["KE"] = self.GetKinetic_Energy(n)
		if self.mass:
			result_dic["Mass"] = self.GetMass(n)
		return result_dic
	
	
	#Getter / Setter methods
	
	
	def GetIonN(self):
		return self.Ion_N
	def SetIonN(self,Ion_number):
		self.Ion_N = Ion_number
	
	
	def GetToF(self,n):
		return self.TOF[n]
	def SetToF(self,n,time_of_flight):
		self.TOF[n] = time_of_flight
	def AppToF(self,TOF):
		self.TOF.append(TOF)
	
	
	def GetXYZ(self,n):
		return self.xyz[n]
	def SetXYZ(self,n,x,y,z):
		self.xyz[n] = [x,y,z]
	def AppXYZ(self,x,y,z):
		self.xyz.append([x,y,z])
	
	
	def GetCharge(self,n):
		return self.charge[n]
	def SetCharge(self,n,charge):
		self.charge[n] = charge
	def AppCharge(self,charge):
		self.charge.append(charge)
	
	
	def GetVelocity(self,n):
		return self.velocity[n]
	def SetVelocity(self,n,velocity):
		self.velocity[n] = velocity
	def AppVelocity(self,velocity):
		self.velocity.append(velocity)
	
	
	def GetKinetic_Energy(self,n):
		return self.kinetic_energy[n]
	def SetKinetic_Energy(self,n,kinetic_energy):
		self.kinetic_energy[n] = kinetic_energy
	def AppKinetic_Energy(self,kinetic_energy):
		self.kinetic_energy.append(kinetic_energy)
	
	
	def GetMass(self,n):
		return self.mass[n]
	def SetMass(self,n,mass):
		self.mass[n] = mass
	def AppMass(self,mass):
		self.mass.append(mass)
	
	
	def GetEvent(self,n):
		return self.events[n]
	def SetEvent(self,n,event):
		self.events[n] = event
	def AppEvent(self,event):
		self.events.append(event)