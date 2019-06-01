# ImportMeshes.py



SurfaceDir  = "/Volumes/projects/murphya/Surgery/Jasper/Surfaces/"
SkullModel  = SurfaceDir + "M11_m01_Jasper_20170627-skull_decimated.stl"
#BrainModel  = SurfaceDir + "M11_m01_Jasper_20170627-skull_decimated.stl"
#ROIModel    = SurfaceDir + 
#AngioModel  = SurfaceDir + 
#TissueModel = ""



#=========== PREPARE MATERIALS (IF THEY DONT ALREADY EXIST)

SkullMat                    = bpy.data.materials.new('Bone')
SkullMat.diffuse_color      = (0.1,0.0,0.7)
SkullMat.diffuse_shader     = 'LAMBERT'
SkullMat.diffuse_intensity  = 1.0
SkullMat.alpha              = 0.5



#=========== IMPORT SKULL MODEL
bpy.ops.import_mesh.stl(filepath=SkullModel, filter_glob="*.stl", files=[{"name":"KAPPA.stl", "name":"KAPPA.stl"}], directory=SurfaceDir)
objH            = bpy.context.object            # Get the imported object
objH.name       = "Skull"                       # Name the object
objH.location   = (0,0,0);                      # Set the object's location to world origin
SkullMat        = bpy.data.materials['Bone']    # Get the bone material
if len(objH.data.materials):                    # if the object already has a material, overwrite it
    obj.data.materials[0] = SkullMat            # Assign bone material to skull

