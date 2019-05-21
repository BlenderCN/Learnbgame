#ANTLR_EXE=/usr/share/java/antlr-complete.jar
ANTLR_EXE=antlr-complete.jar
EXE_CALL=java -jar $(ANTLR_EXE)

python:
	$(EXE_CALL) -Dlanguage=Python3 -no-visitor -no-listener lsystem.g4

python-dev:
	$(EXE_CALL) -Dlanguage=Python3 -visitor -no-listener lsystem.g4

java:
	$(EXE_CALL) lsystem.g4
	javac -cp '$(ANTLR_EXE):$$CLASSPATH' lsystem*.java


test: java
	cat ../../examples/sierpinski.txt | java -cp .:$(ANTLR_EXE) org.antlr.v4.gui.TestRig lsystem code -gui

clean:
	rm -f lsystemParser.py lsystemLexer.py lsystemListener.py lsystemVisitor.py lsystem.tokens lsystemLexer.tokens
	rm -f *.java *.class
