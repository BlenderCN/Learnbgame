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
	ion.py

	Core class for storing the trajectory information of each ion in every time step.

	Original author:  Dominik Sand
	Version: 0.1
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