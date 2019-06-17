import bpy
from bpy.props import BoolProperty, FloatVectorProperty, FloatProperty, EnumProperty, IntProperty, StringProperty, PointerProperty, CollectionProperty, IntVectorProperty
import os
from mathutils import Matrix
from . utils.math import flatten_matrix
from . utils.system import abspath
from . utils.registration import get_prefs, reload_panels
from . utils.batch import toggle_glossyrays, toggle_parallax, toggle_normaltransfer_render, toggle_normaltransfer_viewport, switch_normalinterpolation, switch_colorinterpolation
from . utils.batch import switch_alpha_blendmode, change_ao_strength, invert_infodecals, switch_edge_highlights, toggle_material_visibility, toggle_texture_visibility, toggle_decaltype_collection_visibility, toggle_decalparent_collection_visibility
from . utils.collection import sort_into_collections, purge_decal_collections
from . items import interpolation_items, alpha_blendmode_items, edge_highlights_items, auto_match_items, align_mode_items
from . items import bake_resolution_items, bake_aosamples_items, bake_supersample_items
from . items import create_decaltype_items, create_infotype_items, create_infotext_align_items
from . items import decaltype_items, texturetype_items


# COLLECTION PROPERTIES

class DecalLibsCollection(bpy.types.PropertyGroup):
    def update_islocked(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        assetspath = get_prefs().assetspath
        library = self.name

        hasislocked = os.path.exists(os.path.join(assetspath, library, ".islocked"))

        if hasislocked:
            self.avoid_update = True
            self.islocked = True

    def update_ispanel(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        assetspath = get_prefs().assetspath
        library = self.name

        hasispanel = os.path.exists(os.path.join(assetspath, library, ".ispanel"))

        if hasispanel:
            self.avoid_update = True
            self.ispanel = True

    name: StringProperty()
    isvisible: BoolProperty(default=True, description="Show in Pie Menu")
    ispanel: BoolProperty(default=False, description="Available to Slice Tool. Requires Library Reload", update=update_ispanel)
    islocked: BoolProperty(default=False, description="Prevent User Decal Creation and Removal. Requires Library Reload", update=update_islocked)

    # hidden
    avoid_update: BoolProperty(default=False)


class DecalScalesCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    index: IntProperty()
    scale: FloatVectorProperty(name="Scale")


class ExcludeCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    index: IntProperty()


# ID TYPE PROPERTIES


class DecalSceneProperties(bpy.types.PropertyGroup):
    debug: BoolProperty(default=False)
    avoid_update: BoolProperty(default=False)


    # PANEL REGISTRATION

    def update_register_panels(self, context):
        reload_panels()

    register_panel_creation: BoolProperty(default=True, update=update_register_panels)
    register_panel_update_legacy: BoolProperty(default=True, update=update_register_panels)
    register_panel_debug: BoolProperty(default=True, update=update_register_panels)
    register_panel_help: BoolProperty(default=True, update=update_register_panels)


    # DECAL INSERTION SETTINGS

    globalscale: FloatProperty(name="Scale", description="Global Scale modifier.\nAdjust as needed, if decals come into the scene too big or small, for the scale you are working at\nGlobal Scale is also multiplied with Panel Width.", default=1, precision=3, min=0.001, max=1000, step=1)
    individualscales: CollectionProperty(type=DecalScalesCollection)
    panelwidth: FloatProperty(name="Panel Width", description="Default Panel Width, used by Slice and set by Adjust", default=0.04, step=1, min=0)
    height: FloatProperty(name="Height", description="Default Decal Height - mid_level in Displace modifier", default=0.9999, precision=4, step=0.001, max=1, min=0.5)

    quickinsertlibrary: StringProperty()
    quickinsertdecal: StringProperty()
    quickinsertisinstant: BoolProperty()


    # DECAL DEFAULTS

    def update_collections(self, context):
        """
        only affect decals in the current scene
        """
        decals = [obj for obj in bpy.data.objects if obj.DM.isdecal and not obj.DM.isbackup and context.scene in obj.users_scene]

        for obj in decals:
            sort_into_collections(context.scene, obj, purge=False)

        purge_decal_collections(debug=True)

    def update_hide_materials(self, context):
        toggle_material_visibility(self.hide_materials)

    def update_hide_textures(self, context):
        toggle_texture_visibility(self.hide_textures)

    def update_hide_decaltype_collections(self, context):
        toggle_decaltype_collection_visibility(self.hide_decaltype_collections)

    def update_hide_decalparent_collections(self, context):
        toggle_decalparent_collection_visibility(self.hide_decalparent_collections)

    def update_glossyrays(self, context):
        toggle_glossyrays(self.glossyrays)

    def update_parallax(self, context):
        toggle_parallax(self.parallax)

    def update_normaltransfer_render(self, context):
        toggle_normaltransfer_render(self.normaltransfer_render)

    def update_normaltransfer_viewport(self, context):
        toggle_normaltransfer_viewport(self.normaltransfer_viewport)

    def update_normalinterpolation(self, context):
        switch_normalinterpolation(self.normalinterpolation)

    def update_colorinterpolation(self, context):
        switch_colorinterpolation(self.colorinterpolation)

    def update_alpha_blendmode(self, context):
        switch_alpha_blendmode(self.alpha_blendmode)

    def update_ao_strength(self, context):
        change_ao_strength(self.ao_strength)

    def update_invert_infodecals(self, context):
        invert_infodecals(self.invert_infodecals)

    def update_edge_highlights(self, context):
        switch_edge_highlights(self.edge_highlights)


    collection_decaltype: BoolProperty(name="Decal Type Collection", description="Create Decal Type Collections", default=True, update=update_collections)
    collection_decalparent: BoolProperty(name="Decal Parent Collection", description="Create Decal Collections based on Decal Parent Object's Membership", default=False, update=update_collections)
    collection_active: BoolProperty(name="Active Collection", description="Add Decals to Active Collection", default=False, update=update_collections)

    hide_materials: BoolProperty(name="Hide Materials", default=True, update=update_hide_materials)
    hide_textures: BoolProperty(name="Hide Textures", default=True, update=update_hide_textures)
    hide_decaltype_collections: BoolProperty(name="Hide Decal Type Collections", default=False, update=update_hide_decaltype_collections)
    hide_decalparent_collections: BoolProperty(name="Hide Decal Parent Collections", default=False, update=update_hide_decalparent_collections)

    glossyrays: BoolProperty(name="Glossy Rays", default=True, update=update_glossyrays)
    parallax: BoolProperty(name="Parallax", default=True, update=update_parallax)

    normaltransfer_render: BoolProperty(name="Normal Transfer Render", default=True, update=update_normaltransfer_render)
    normaltransfer_viewport: BoolProperty(name="Normal Transfer Viewport", default=True, update=update_normaltransfer_viewport)

    normalinterpolation: EnumProperty(name="Normal Interpolation", items=interpolation_items, default="Linear", update=update_normalinterpolation)
    colorinterpolation: EnumProperty(name="Color Interpolation", items=interpolation_items, default="Linear", update=update_colorinterpolation)
    alpha_blendmode: EnumProperty(name="Alpha Blend Mode", items=alpha_blendmode_items, default="BLEND", update=update_alpha_blendmode)

    ao_strength: FloatProperty(name="AO Strength", default=1, min=0, max=1, step=0.1, update=update_ao_strength)
    invert_infodecals: BoolProperty(name="Invert Info Decals", default=False, update=update_invert_infodecals)
    edge_highlights: EnumProperty(name="Edge Highlights", items=edge_highlights_items, default="0.5", update=update_edge_highlights)


    align_mode: EnumProperty(name="Align Mode", items=align_mode_items, default="RAYCAST")
    auto_match: EnumProperty(name="Auto-Match Materials", items=auto_match_items, default="AUTO")

    revision: StringProperty()


    # LEGACY DECALS

    def update_updatelibrarypath(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        self.avoid_update = True

        if self.updatelibrarypath:
            # get and set absolute path
            path = abspath(self.updatelibrarypath)

            # check if the target path is a legacy library
            if os.path.exists(path):

                if all(name in [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))] for name in ["blends", "icons"]):
                    self.updatelibrarypath = path
                    return

        self.updatelibrarypath = "CHOOSE A LEGACY DECAL LIBRARY!"

    updatelibrarypath: StringProperty(name="Update Library Path", subtype='DIR_PATH', update=update_updatelibrarypath)


    # DECAL CREAtiON

    update_fix_legacy_normals: BoolProperty(name="Fix Legacy Normals", default=True)
    update_keep_old_thumbnails: BoolProperty(name="Keep Old Thumbnails", default=False)
    update_store_uuid_with_old_decals: BoolProperty(name="Store UUID with Old Decals", default=True)

    addlibrary_decalname: StringProperty(name="Name (optional)")

    create_decaltype: EnumProperty(name="Decal Type", description="Decal Type", items=create_decaltype_items, default="SIMPLESUBSET")
    create_infotype: EnumProperty(name="Info Decal Creation Type", description="Info Decal Creation Type", items=create_infotype_items, default="IMAGE")
    create_infoimg_crop: BoolProperty(name="Crop", default=True)
    create_infoimg_padding: IntProperty(name="Padding", default=1)
    create_infotext: StringProperty(name="Text", default="")
    create_infotext_color: FloatVectorProperty(name="Text Color", subtype='COLOR', default=[1, 1, 1, 1], size=4, min=0, max=1)
    create_infotext_bgcolor: FloatVectorProperty(name="Text Background Color", subtype='COLOR', default=[1, 1, 1, 0], size=4, min=0, max=1)
    create_infotext_align: EnumProperty(name="Align Text", items=create_infotext_align_items, default='left')
    create_infotext_size: IntProperty(name="Size", default=100)
    create_infotext_padding: IntVectorProperty(name="Padding", default=[1, 1], size=2)
    create_infotext_offset: IntVectorProperty(name="Offset", default=[0, 0], size=2)


    create_thumbnail_tint: FloatVectorProperty(name="Thumbnail Tint", subtype='COLOR', default=[0.14, 0.15, 0.16, 1], size=4, min=0, max=1)

    bake_supersample: EnumProperty(name="Supersample", description="Supersample", items=bake_supersample_items, default="2")
    bake_supersamplealpha: BoolProperty(name="Supersample Alpha", default=False)
    bake_resolution: EnumProperty(name="Resolution", description="Resolution", items=bake_resolution_items, default="256")
    bake_aosamples: EnumProperty(name="Samples", description="AO Samples", items=bake_aosamples_items, default="256")
    bake_aocontrast: FloatProperty(name="Contrast", default=1.5, min=0)
    bake_curvaturewidth: FloatProperty(name="Width", default=1.0, min=0)
    bake_curvaturecontrast: FloatProperty(name="Contrast", default=2.0, min=0)
    bake_heightdistance: FloatProperty(name="Distance", default=1.0, min=0)
    bake_limit_alpha_to_active: BoolProperty(name="Limit Alpha to Active", default=True)
    bake_limit_alpha_to_boundary: BoolProperty(name="Limit Alpha to Boundary", default=False)
    bake_flatten_alpha_normals: BoolProperty(name="Flatten Alpha Normals", default=True)
    bake_maskmat2: BoolProperty(name="Material 2", default=True)
    bake_inspect: BoolProperty(name="Inspect Bakes", default=False)


    """
    # atlas creation defaults
    atlasdownsample = BoolProperty(name="Downsample Atlas", default=False)
    atlaspadding = IntProperty(name="Padding", default=-1, min=0, max=10)  # we initiate it at -1 so it can be fetched from prefs
    atlastype = StringProperty(name="Atlas Type", default="")
    maptype = StringProperty(name="Map Type", default="")

    # atlasing and export defaults
    autoopenfolderforexistingatlas = BoolProperty(name="Open Atlas Folder for Existing Atlas Solution", default=True)
    autoinitiateafterreset = BoolProperty(name="Initiate new Atlas when Resetting", default=False)
    autoopenfolderafterexport = BoolProperty(name="Open Export Folder after Exporting", default=True)

    exporttype = EnumProperty(name='Export to Target Platform', items=get_export_types(), default="unity3d_machin3")
    quickexport = BoolProperty(name="Quick Export", default=True)
    exportname = StringProperty(name="", default="Untitled")

    simpleexportgroup = BoolProperty(name="Simple Export Group", default=False)
    createnondecalsgroup = BoolProperty(name="Create 'DM_non-decals' Group", default=True)
    removedisplace = BoolProperty(name="Ignore Decal Heights", default=False)

    extradisplace = BoolProperty(name="Extra Displ.", default=True)
    extradisplaceamnt = FloatProperty(name="Amount", default=2, min=0, max=10)
    createarchive = BoolProperty(name=" » Create Archive", default=True)

    extrasbsatlas = BoolProperty(name="Extra Substance Atlas", default=False)
    parenttoroot = BoolProperty(name="Parent Objects to Root", default=True)
    unityrotfix = BoolProperty(name=" » Unity Rotation Fix (experimental)", default=True)
    triangulize = BoolProperty(name="Triangulize", default=True)
    normalflipgreen = BoolProperty(name="Flip Green Normal", default=False)
    assignuniquematerials = BoolProperty(name="Assign Unique Materials", default=False)
    treatfreestyleasseam = BoolProperty(name=" » Treat Freestyle edges as Seams", default=False)

    # DECALBakeDown
    bakedownexportfbx = BoolProperty(name="Export FBX", default=True)
    bakedownresolution = IntProperty(name="Resolution", default=1024, min=64, max=8192)
    bakedowndistance = FloatProperty(name="Distance", default=0.01, min=0, max=10)
    bakedownbias = FloatProperty(name="Bias", default=0.01, min=0, max=10)
    bakedowntransfersharps = BoolProperty(name="Transfer Sharps", default=False)
    bakedowncombine = BoolProperty(name="Combine Bakes (per Material)", default=True)
    bakedowncombineall = BoolProperty(name=" » Combine all-to-one", default=False)

    bakedownmapao = BoolProperty(name="Ambient Occlusion", default=True)
    bakedownmapcurvature = BoolProperty(name="Curvature", default=True)
    bakedownmapheight = BoolProperty(name="Height", default=True)
    bakedownmapnormal = BoolProperty(name="Normal", default=True)
    bakedownmapsubset = BoolProperty(name="Subset Mask", default=True)
    bakedownmapcolor = BoolProperty(name="Color", default=True)
    bakedownsbsnaming = BoolProperty(name="Substance Naming", default=True)

    """


class DecalObjectProperties(bpy.types.PropertyGroup):
    uuid: StringProperty(name="decal uuid")
    decaltype: EnumProperty(name="decal type", items=decaltype_items, default="NONE")
    decallibrary: StringProperty(name="decal library")
    decalname: StringProperty(name="decal name")
    decalmatname: StringProperty(name="decal material name")

    isdecal: BoolProperty(name="is decal", default=False)
    isbackup: BoolProperty(name="is backup", default=False)
    isprojected: BoolProperty(name="is projected", default=False)
    issliced: BoolProperty(name="is sliced", default=False)

    decalbackup: PointerProperty(name="decal backup object", type=bpy.types.Object)
    projectedon: PointerProperty(name="projected on Object", type=bpy.types.Object)
    slicedon: PointerProperty(name="sliced on Object", type=bpy.types.Object)

    creator: StringProperty(name="Decal Creator")

    backupmx: FloatVectorProperty(name="Backup Matrix in Parent's Local Space", subtype="MATRIX", size=16, default=flatten_matrix(Matrix()))


class DecalMaterialProperties(bpy.types.PropertyGroup):
    uuid: StringProperty(name="decal uuid")
    decaltype: EnumProperty(name="decal type", items=decaltype_items, default="NONE")
    decallibrary: StringProperty(name="decal library")
    decalname: StringProperty(name="decal name")
    decalmatname: StringProperty(name="decal material name")

    isdecalmat: BoolProperty(name="is decalmat", default=False)
    ismatched: BoolProperty(name="is matched", default=False)
    isparallaxed: BoolProperty(name="is parallaxed", default=False)

    matchedmaterialto: PointerProperty(name="matched Decal Material Parameters to", type=bpy.types.Material)
    matchedmaterial2to: PointerProperty(name="matched Decal Material2 Parameters to", type=bpy.types.Material)
    matchedsubsetto: PointerProperty(name="matched Decal Subset Parameters to", type=bpy.types.Material)

    parallaxnodename: StringProperty(name="parallax node name")

    creator: StringProperty(name="Decal Creator")


class DecalImageProperties(bpy.types.PropertyGroup):
    uuid: StringProperty(name="decal uuid")
    decaltype: EnumProperty(name="decal type", items=decaltype_items, default="NONE")
    decallibrary: StringProperty(name="decal library")
    decalname: StringProperty(name="decal name")
    decalmatname: StringProperty(name="decal material name")

    isdecaltex: BoolProperty(name="is decaltex", default=False)

    decaltextype: EnumProperty(name="decal texture type", items=texturetype_items, default="NONE")

    creator: StringProperty(name="Decal Creator")


class DecalCollectionProperties(bpy.types.PropertyGroup):
    isdecaltypecol: BoolProperty(name="is decaltype collection", default=False)
    isdecalparentcol: BoolProperty(name="is decal parent collection", default=False)
