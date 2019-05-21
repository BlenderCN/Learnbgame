
# Linux:
INSTALL_DIR = ~/.config/blender/2.76/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.74/scripts/addons/

SHELL = /bin/sh

SUBDIRS = icons io_mesh_mcell_mdl data_plotters developer_utilities
SOURCES = $(shell python cellblender_source_info.py)
ZIPFILES = $(SOURCES) cellblender/io_mesh_mcell_mdl/_mdlmesh_parser.so cellblender/io_mesh_mcell_mdl/mdlmesh_parser.py cellblender/SimControl.jar cellblender/SimControl cellblender/data_plotters/java_plot/PlotData.jar cellblender/cellblender_id.py

ZIPOPTS = -X -0 -D -o

.PHONY: all
all: cellblender subdirs cellblender.zip SimControl.jar SimControl

cellblender:
	ln -s . cellblender

.PHONY: subdirs $(SUBDIRS)
subdirs: makefile $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@


# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
# A phony target should not be a prerequisite of a real target file;
# if it is, its recipe will be run every time make goes to update that file.
# As long as a phony target is never a prerequisite of a real target, the phony
# target recipe will be executed only when the phony target is a specified goal
#  (see Arguments to Specify the Goals). 

# Note that files which auto-change but are included in the zip file are not part of the source list
cellblender.zip: $(SOURCES) SimControl
	@echo Updating cellblender.zip
	@echo Sources = $(SOURCES)
	touch -t 201502050000 cellblender_id.py
	@zip $(ZIPOPTS) cellblender.zip $(ZIPFILES)


SimControl.jar: SimControl.java
	rm -f *.class
	javac SimControl.java
	touch -t 201407160000 *.class
	zip $(ZIPOPTS) SimControl.jar META-INF/MANIFEST.MF SimControl.java *.class
	rm -f *.class


SimControl: SimControl.o
	gcc -lGL -lglut -lGLU -o SimControl SimControl.o

SimControl.o: SimControl.c
	gcc -c -std=c99 -I/usr/include/GL SimControl.c


.PHONY: clean
clean:
	rm -f cellblender.zip
	rm -f SimControl.jar
	rm -f SimControl.o
	rm -f SimControl
	(cd io_mesh_mcell_mdl ; make clean)
	(cd data_plotters ; make clean)



.PHONY: install
install: cellblender.zip
	@if [ "$(INSTALL_DIR)" ]; then \
	  unzip -o cellblender.zip -d $(INSTALL_DIR); \
	  cp test_suite/cellblender_test_suite.py $(INSTALL_DIR); \
	fi
	@echo ===========================================================
	@cat $(INSTALL_DIR)cellblender/cellblender_id.py
	@echo ===========================================================

