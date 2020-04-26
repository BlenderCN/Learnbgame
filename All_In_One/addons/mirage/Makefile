# Makefile for Mirage Addon
# Diego Gangl - <diego@sinestesia.co>
# ---------------------------------------------------------------


# /./././././././././././././././././././././././././././././././
# SETTINGS
# /./././././././././././././././././././././././././././././././

NAME 		= Mirage
VERSION	       	= 2_0
BUILD_DIR      	= ../release/
BUILD_FILE	= $(BUILD_DIR)/$(NAME)_$(VERSION).zip
FILES 		= *.py icons/* docs/*
FILE_BROWSER 	= nautilus

.DEFAULT_GOAL 	:= build


# /./././././././././././././././././././././././././././././././
# TARGETS
# /./././././././././././././././././././././././././././././././

.PHONY: docs
docs:
	sphinx-build -b html docs_src docs


clean:
	rm -rf $(BUILD_FILE)
	@echo "Release zip deleted - " $(BUILD_FILE)


build: 	docs

	mkdir -p $(BUILD_DIR)

	zip -r9T $(BUILD_FILE) $(FILES)

	@echo
	@echo $(NAME)" "$(VERSION) " is ready"
	$(FILE_BROWSER) $(BUILD_DIR) &
