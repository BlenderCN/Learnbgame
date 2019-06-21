PlotData.jar: PlotData.java makefile
	javac PlotData.java
	touch -t 201501260000 *.class
	zip -X PlotData.jar META-INF/MANIFEST.MF PlotData.java *.class
	rm -f *.class

# Using jar to create the jar file changed the SHA1 of the resulting file due to a time stamp on the manifest ... use zip procedure above instead.

#PlotData.jar: PlotData.java makefile
#	javac PlotData.java
#	jar -cfe PlotData.jar PlotData PlotData.java *.class
#	rm -f *.class

.PHONY: clean
clean:
	rm -f PlotData.jar


