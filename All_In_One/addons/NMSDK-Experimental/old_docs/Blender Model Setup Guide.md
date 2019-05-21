### Model Setup Guide for NMS Blender Exporter ###


# Introduction

First of all, for the noob modelers out there DO NOT PANIC. The procedure is really simple.
Some very basic stuff have to be done so that the script knows how to manipulate and recreate
nms compatible files. So lets get to the tasks.


# TASKS

#TASK 0 --- "Installation"
	
	After unpacking the archive, you have 2 things to do:
	1. Copy the "nms_imp" folder and the supplied version of MBINCompiler in Blender installation folder (it should be in the same 
	directory with the blender.exe)
	2. Open Blender, go to User Preferences->Addons, and install the supplied addon. Make sure to enable it as well (tick the checkbox)

#TASK 1 --- "Create main scene object"

	Due to how the importer works, every object that you want exported needs to be contained within an empty
	object in blender that has the name NMS_SCENE.
	Every object hierarchy that will be exported MUST be a child of this object.
	The location of this object is best set to the origin.

#TASK 2 --- "GEOMETRY/OBJECT PREPARATION"
	
	Make sure that every MESH object that you want to import contains a UVMap (even an empty one,
	it doesn't matter) and it has been assigned to a material. Literally those are the only
	requirements for getting models ready for the export process. Also overall, make sure that
	you save your blend in the disk, and you are not working on a temporary session of blender.
	This is critical for all the model file dependencies (such as textures) to work out.

#TASK 3 --- "TEXTURE OPTIONS"

	For now each material can have up to 3 different textures. There is a fixed way on how
	textures are handled and this is following the texture slot order in the material options.
	The sequence is the following

		#Slot 0 ---------> DiffuseMap
		#Slot 1 ---------> MaskMap
		#Slot 2 ---------> NormalMap

	Even without setting any texture at all, the object will be painted with the general diffuse
	material color, so even without setting textures right or setting any of them at all, will
	not cause errors on the export process.

#TASK 4 --- "LIT STATUS"
	
	LIT or UNLIT status of objects ingame is set via the "Shadeless" flag in the material options.
	For now lit objects are in experimental phase because they require quite some more info concerning
	both the geometry and the other material options in order to work properly. So the main option
	for now is to enable this flag, in order to toggle the UNLIT flag. Using that flag the model will
	use just the color information it gets from the diffuse texture or the main material color.

#TASK 5 --- "NAMING CONVENTION"
	
	Just to make things clearer and in order to enable modders to have full control over the objects
	that are going to be exported into the game we have setup a specific very simple naming convention
	for the "about to export" objects.
	Only objects that their name starts with "NMS_" will be exported. 

		- Meshes -
			Format: NMS_MESH_<name>
			Example: "NMS_MESH_SeanMurrayDoesntLie"
		- Collision Names - 
			Collision object names should have the following form : "NMS_COLLISION_[Collisiontype]_objectname"
			Collisiontype can be one of the following options: Mesh, Box, Cylinder, Capsule, Sphere.
			Example: "NMS_COLLISION_Mesh_SeanMurraysShip"
		- Locators - 
			Locators Follow the naming convention "NMS_LOCATOR_name"
		- References - 
			Format:		NMS_REFERENCE_<name>
			Optional arguments:	REF	- the path to the scene you want to have referenced at this point.
		- Lights:
			Format:		NMS_LIGHT_<name>
		- Joints:
			Format:		NMS_JOINT_<name>

#TASK 6 --- "COLLISIONS"
	
	Collisions are optional. Either you add collisions or not, the main model parts will be exported 
	without any problem. However if you want to be able to crash into your objects and give them a 
	substance you should add collision to every model that you're importing.

	Collisions are split into 2 main categories: Mesh or Primitives

		- Mesh Collisions are actually meshes like your main models with way less triangles than the original models
		just to capture roughly the outline of the main model. 
		
		-Primitive Collisions are game engine premade meshes that can be used at runtime as collision meshes. This
		mode requires no additional mesh defined at all and therefore no additional geometry is saved into the geometry
		mbin file. The available primitives are: Box, Cylinder, Capsule, Sphere.


	Collision Creation

	As mentioned in the "TASK 5" section, collision objects should follow the naming : "NMS_COLLISION_[Collisiontype]_objectname".
	If collisiontype is a mesh then the object should be the collision mesh as described above.
	If collisiontype is going to be one of the primitives then the object should be one of blenders appropriate primitives
	as well. For example if you want to create a sphere collision you should add an "IcoSphere" primitive, from the Add->Mesh
	menu, and name it "COLLISION_Sphere_whatever".


	Collision Assignment

	Just creating a collision object is not enough. The object should be assigned to the appropriate object. This is done by setting
	the main object as a parent of the collision object. The quickest way to do that is to go to the Outliner panel, select the collision
	object , then shift select the main object, then get your mouse pointer into the 3D View and hit Ctrl + P and select the "Object" option.

#TASK 7 --- "APPLY TRANSFORMS"
	
	To ensure the importer has the correct transforms on objects, make sure that you apply the rotation and scale only on every object that is being exported.

# (OPTIONAL) TASK 8 --- "ADD ANIMATIONS"
	Animations can now be added. All mesh objects that you want animated need to be the child of a JOINT object, and it is the joint that must have the animation attached, not the mesh (subject to change...)
	Further, mesh object needs a custom property called ANIM, with whatever value (also subject to change...)

#TASK 8 --- "EXPORT PROCEDURE"

	Once everything is setup properly you can proceed to the export process. The exporter is located in File->Export->Export to NMS XML Format.
	A dialog will prompt you to set the export filename and the export directory. For now the path doesn't mean anything at all. Because of the way
	the script works, and because of the multiple files that have to be prepared, all exported files will be located in the default Blender Installation directory. What's important here is the filename you set. The name should be a unique one so that you can identify the files that belong to this particular project that your exporting. For example if you set the export filename to "TEST", the script is going to create files with names like: "TEST.SCENE.MBIN" "TEST.GEOMETRY.MBIN.PC" and so on. 







