SUBDIRS = java_plot

.PHONY: subdirs $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

.PHONY: clean
clean:
	(cd java_plot ; make clean)


