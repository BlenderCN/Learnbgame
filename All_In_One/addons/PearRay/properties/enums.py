enum_debug_mode = (
    ('DEPTH', "Depth", "Show depth information"),
    ('NORMAL_BOTH', "Normal", "Show normals"),
    ('NORMAL_POSITIVE', "Normal Positive", "Show positive normals"),
    ('NORMAL_NEGATIVE', "Normal Negative", "Show negative normals"),
    ('NORMAL_SPHERICAL', "Normal Spherical",
     "Show normals in spherical coordinates"),
    ('TANGENT_BOTH', "Tangent", "Show tangents"),
    ('TANGENT_POSITIVE', "Tangent Positive", "Show positive tangents"),
    ('TANGENT_NEGATIVE', "Tangent Negative", "Show negative tangents"),
    ('TANGENT_SPHERICAL', "Tangent Spherical",
     "Show tangents in spherical coordinates"),
    ('BINORMAL_BOTH', "Binormal", "Show binormals"),
    ('BINORMAL_POSITIVE', "Binormal Positive", "Show positive binormals"),
    ('BINORMAL_NEGATIVE', "Binormal Negative", "Show negative binormals"),
    ('BINORMAL_SPHERICAL', "Binormal Spherical",
     "Show binormals in spherical coordinates"),
    ('UVW', "UVW", "Show UV/texture coordinates"),
    ('PDF', "PDF", "Show probability distribution function values"),
    ('EMISSION', "Emission", "Show emission part of the rendering equation"),
    ('VALIDITY', "Validity", "Show if material is valid"),
    ('FLAG_INSIDE', "Flag Inside",
     "Show if surface is inside or outside. Green inside, Red outside."),
    ('CONTAINER_ID', "Container ID",
     "Show id of the container which the primitive belongs to"),
    ('BOUNDING_BOX', "Bounding Box",
     "Visualize the bounding box"),
)

enum_sampler_mode = (
    ("RANDOM", "Random", "Random sampling technique"),
    ("UNIFORM", "Uniform", "Uniform sampling technique"),
    ("JITTER", "Jitter", "Jitter sampling technique"),
    ("MULTI_JITTER", "Multi-Jitter", "Multi-Jitter sampling technique"),
    ("HALTON_QMC", "Halton QMC",
     "Quasi-Monte Carlo sampling method based on the Halton sequence"),
)

enum_time_mapping_mode = (
    ("CENTER", "Center", "Center Mapping [-1/2,1/2]"),
    ("LEFT", "Left", "Left Mapping [-1,0]"),
    ("RIGHT", "Right", "Right Mapping [0,1]"),
)

enum_integrator_mode = (
    ('DIRECT', "Direct", "Direct Rendering"),
    ('BIDIRECT', "Bi-Direct", "Bidirect Rendering"),
    ('PPM', "Progressive Photon Mapping", "Progressive Photon Mapping"),
    ('AO', "Ambient Occulusion", "Ambient Occulusion"),
    ('VISUALIZER', "Debug Visualizer", "Debug Visualizer"),
)

enum_tile_mode = (
    ("LINEAR", "Linear", "From top-left to bottom-right"),
    ("TILE", "Tile", "From top-left to bottom-right in intervals"),
    ("SPIRAL", "Spiral", "From the mid to border"),
)

enum_photon_gathering_mode = (
    ("DOME", "Dome", "Gather only front side of surface"),
    ("SPHERE", "Sphere", "Gather around a point"),
)

enum_color_type = (
    ("COLOR", "Color", "Standard RGB value"),
    ("TEMP", "Temperature", "Blackbody Temperature in Kelvin"),
    ("TEX", "Texture", "Texture"),
    #("NODE", "Node", "Node"),
)

enum_flat_color_type = (
    ("COLOR", "Color", "Standard RGB value"),
    ("TEMP", "Temperature", "Blackbody Temperature in Kelvin"),
)

enum_ior_type = (
    ("VALUE", "Value", "Floating point value"),
    ("COLOR", "Color", "Standard RGB value"),
)

enum_temp_type = (
    ("LUM", "Luminance", "Blackbody curve output in luminance"),
    ("RAD", "Radiance", "Blackbody curve output in radiance"),
    ("LUM_NORM", "Luminance Normalized",
     "Normalized luminance blackbody output"),
    ("RAD_NORM", "Radiance Normalized",
     "Normalized radiance blackbody output"),
)

enum_material_bsdf = (
    ("DIFFUSE", "Diffuse", "Simple lambertian material"),
    ("ORENNAYAR", "Oren-Nayar", "Oren-Nayar BRDF"),
    ("COOK_TORRANCE", "Cook-Torrance", "Cook-Torrance BRDF"),
    ("WARD", "Ward", "Ward BRDF"),
    ("GRID", "Grid", "Special material grid"),
    ("GLASS", "Glass", "Specialized glass material"),
    ("MIRROR", "Mirror", "Specialized mirror material"),
)

enum_material_ct_fresnel_mode = (
    ("DIELECTRIC", "Dielectric", "Dielectric fresnel"),
    ("CONDUCTOR", "Conductor",
     "Conductor fresnel (for metal). Absorption based on diffuse term"),
)

enum_material_ct_distribution_mode = (
    ("BLINN", "Blinn", "Blinn based distribution term"),
    ("BECKMANN", "Beckmann", "Beckmann based distribution term"),
    ("GGX", "GGX", "GGX based distribution term"),
)

enum_material_ct_geometry_mode = (
    ("IMPLICIT", "Implicit", "Implicit based geometry term"),
    ("NEUMANN", "Neumann", "Neumann based geometry term"),
    ("COOK_TORRANCE", "Cook-Torrance", "Cook-Torrance based geometry term"),
    ("KELEMEN", "Kelemen", "Kelemen based geometry term"),
)
