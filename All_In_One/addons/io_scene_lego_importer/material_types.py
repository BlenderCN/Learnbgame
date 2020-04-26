##########################################################################################
# class solid_material                                                                   #
# -------------------------------------------------------------------------------------- #
# Member variables:                                                                      #
#     int    material_id: LDraw ID number of the material                                #
#     string name: Official Lego name of the material                                    #
#     float  r,g,b: Fractional RGB codes for the solid material                          #
#     tuple  color: 4-value float tuple of the Fractional RGBA color                     #
# -------------------------------------------------------------------------------------- #
# Constructor:                                                                           #
#     solid_material(id, name, color_hex)                                                #
#         int    id: LDraw ID number of the material                                     #
#         string name: Official Lego name of the Material                                #
#         string color_hex: Material RGB color in hex as a string                        #
##########################################################################################

class solid_material:
	def __init__(self, id, name, color_hex):
		self.material_id = id
		self.name = name
		# Takes RGB as hex as it is the most popular to find on the web
		r = float(int(color_hex[0] + color_hex[1], 16)) / 255.0
		g = float(int(color_hex[2] + color_hex[3], 16)) / 255.0
		b = float(int(color_hex[4] + color_hex[5], 16)) / 255.0
		#(r,g,b), a = map(lambda component: component / 255, bytes.fromhex(color_hex[-6:])), 1.0
		self.color = (r, g, b, 1.000)


##########################################################################################
# class transparent_material (DOC WIP)                                                   #
# -------------------------------------------------------------------------------------- #
# Member variables:                                                                      #
#     int    material_id: LDraw ID number of the material                                #
#     string name: Official Lego name of the material                                    #
#     float  r1,g1,b1: Fractional RGB codes for the solid material                       #
#     tuple  main_color: 4-value float tuple of the Fractional RGBA color                #
# -------------------------------------------------------------------------------------- #
# Constructor:                                                                           #
#     solid_material(id, name, color_hex)                                                #
#         int    id: LDraw ID number of the material                                     #
#         string name: Official Lego name of the Material                                #
#         string color_hex: Material RGB color in hex as a string                        #
##########################################################################################

class transparent_material:
	def __init__(self, id, name, color_main_hex, color_secondary_hex):
		self.material_id = id
		self.name = name
		r1 = float(int(color_main_hex[0] + color_main_hex[1], 16)) / 255.0
		g1 = float(int(color_main_hex[2] + color_main_hex[3], 16)) / 255.0
		b1 = float(int(color_main_hex[4] + color_main_hex[5], 16)) / 255.0

		r2 = float(int(color_secondary_hex[0] + color_secondary_hex[1], 16)) / 255.0
		g2 = float(int(color_secondary_hex[2] + color_secondary_hex[3], 16)) / 255.0
		b2 = float(int(color_secondary_hex[4] + color_secondary_hex[5], 16)) / 255.0

		#(r1, g1, b1), a = map(lambda component: component / 255, bytes.fromhex(color_main_hex[-6:])), 1.0
		#(r2, g2, b2) = map(lambda component: component / 255, bytes.fromhex(color_main_hex[-6:]))
		self.main_color = (r1, g1, b1, 1.000)
		self.secondary_color = (r2, g2, b2, 1.000)
