ver := $(subst v, , $(subst ., ,$(shell git describe --tags | grep -o -E "v[0-9]+\.[0-9]+\.[0-9]+")))
ver_maj := $(word 1,${ver})
ver_min := $(word 2,${ver})
ver_pat := $(word 3,${ver})

all: funscripting.zip

funscripting.zip: *.py
	-mkdir -p funscripting
	cp $^ funscripting/
	sed -i 's/"version": (0, 0, 0)/"version": ($(ver_maj), $(ver_min), $(ver_pat))/g' funscripting/__init__.py
	zip -FSr $@ funscripting
	-rm -r funscripting

.PHONY: clean
clean:
	-rm *.zip
