
INSTALL_DIR = ~/my_blender_addons_link

SHELL = /bin/sh

SOURCES = ./neuropil_tools/__init__.py ./neuropil_tools/processor_tool.py ./neuropil_tools/spine_head_analyzer.py ./neuropil_tools/spine_head_analyzer_c.py ./neuropil_tools/spine_head_analyzer_sy.py ./neuropil_tools/connectivity_tool.py ./neuropil_tools/diameter_tool.py ./neuropil_tools/insert_mdl_region.py ./neuropil_tools/io_import_multiple_objs.py ./neuropil_tools/io_import_ser.py

ZIPFILES = $(SOURCES)

ZIPOPTS = -X -0 -D -o


all: neuropil_tools neuropil_tools.zip


neuropil_tools:
	ln -s . neuropil_tools


neuropil_tools.zip: $(SOURCES)
	@echo Updating neuropil_tools.zip
	@echo Sources = $(SOURCES)
	@zip $(ZIPOPTS) neuropil_tools.zip $(ZIPFILES)


clean:
	rm -f neuropil_tools.zip


install: neuropil_tools.zip
	@ mkdir -p $(INSTALL_DIR)
	@ unzip -o neuropil_tools.zip -d $(INSTALL_DIR); \

