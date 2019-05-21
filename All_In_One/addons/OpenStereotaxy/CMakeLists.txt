cmake_minimum_required(VERSION 2.8.9)

project(SurfaceModels)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/SurfaceModels")
set(EXTENSION_CATEGORY "Custom")
set(EXTENSION_CONTRIBUTORS "AIdan Murphy (National Institutes of Health), ")
set(EXTENSION_DESCRIPTION "This extension is designed to simplify the process of importing CT and MRI data, and constructing surface models for planning surgical implantation of experimental neurophysiological recording devices in non-human subjects.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SurfaceModels.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SurfaceModels/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
