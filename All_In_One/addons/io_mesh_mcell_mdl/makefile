
INSTALL_DIR = ~/.config/blender/2.68/scripts/addons/io_mesh_import_mcell_mdl/

SHELL = /bin/sh
OBJS = mdlparse.bison.o mdlmesh_parser.o vector.o mdlmesh_parser_wrap.o

_mdlmesh_parser.so: makefile setup.py mdlobj.py mdlparse.bison.c mdlmesh_parser.c vector.c mdlmesh_parser_wrap.c 
	python3.4 setup.py build_ext --inplace
	@if [ -e _mdlmesh_parser.cpython-34m.so ] ; then \
	    mv _mdlmesh_parser.cpython-34m.so _mdlmesh_parser.so; \
	fi

mdllex.flex.c: mdllex.l
	flex -Crema mdllex.l

mdlparse.bison.c: mdllex.flex.c mdlparse.y mdlmesh_parser.h
	bison -v -d mdlparse.y

mdlmesh_parser_wrap.c: mdlmesh_parser.i mdlmesh_parser.c mdlmesh_parser.h
#	swig -python mdlmesh_parser.i
	swig -python -py3 -nothreads mdlmesh_parser.i

clean:
	rm -rf $(OBJS) build mdllex.flex.c mdlparse.bison.c mdlparse.bison.h mdlparse.bison.output mdlmesh_parser_wrap.c mdlmesh_parser.py mdlmesh_parser.pyc _mdlmesh_parser.so

install:
	@if [ "$(INSTALL_DIR)" ]; then \
	  if [ ! -s $(INSTALL_DIR) ]; then \
	    echo mkdir -p $(INSTALL_DIR); \
	    mkdir -p $(INSTALL_DIR); \
	  fi; \
	  echo cp __init__.py $(INSTALL_DIR); \
	  cp __init__.py $(INSTALL_DIR); \
	  echo cp _mdlmesh_parser.so $(INSTALL_DIR); \
	  cp _mdlmesh_parser.so $(INSTALL_DIR); \
	  echo cp mdlobj.py $(INSTALL_DIR); \
	  cp mdlobj.py $(INSTALL_DIR); \
	  echo cp mdlmesh_parser.py $(INSTALL_DIR); \
	  cp mdlmesh_parser.py $(INSTALL_DIR); \
	  echo cp import_mcell_mdl.py $(INSTALL_DIR); \
	  cp import_mcell_mdl.py $(INSTALL_DIR); \
	fi

