.PHONEY: lint, todos, update_submodules, display_version, zip

ver_str := v$(shell grep -Po '(?<=version": \().*(?=\),)' __init__.py | sed 's/, /./g')

lint:
	pylint *.py

todos:
	pylint -d all -e fixme *.py

update_submodules:
	git submodule update --init --recursive

display_version:
	@echo $(ver_str)

zip: update_submodules
	git-archive-all --force-submodules --prefix BlenderPanda BlenderPanda-$(ver_str).zip
