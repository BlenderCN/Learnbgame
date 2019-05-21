cmake_minimum_required (VERSION 2.8)
project (libvoro) 

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}")

find_program(PYTHON_EXECUTABLE NAMES python3.2 python) #how to handle under windows ?
find_package(Cython)

if (PYTHON_EXECUTABLE)
    message(STATUS "Found Python 3.2: " ${PYTHON_EXECUTABLE})
    if (CYTHON_FOUND)
        add_custom_target(libvoro ${PYTHON_EXECUTABLE} setup.py build_ext --inplace)
    else(CYTHON_FOUND)
        message(STATUS "Cython not found, voronoi lib bindings will not be created")
    endif(CYTHON_FOUND)
else(PYTHON_EXECUTABLE)
    message(STATUS "Python 3.2 not found, voronoi lib bindings will not be created")
endif(PYTHON_EXECUTABLE)
