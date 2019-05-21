from .lgrammar import antlr4
from .lgrammar.antlr4.error import ErrorListener

from .lgrammar.lsystemLexer import lsystemLexer
from .lgrammar.lsystemParser import lsystemParser
from .lgrammarVisitor import lgrammarVisitor


class LoggingErrorListener(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self):
        self._log_dest = []

    def syntaxError(self, _recognizer, _offendingSymbol, line, column, msg, e):
        self._log_dest.append("line " + str(line) +
                              ":" + str(column) + " " + msg)

    def getErrors(self):
        return self._log_dest


def parse(text):
    my_error_log = LoggingErrorListener()
    my_lexer = lsystemLexer(antlr4.InputStream(text))
    my_lexer.addErrorListener(my_error_log)

    my_parser = lsystemParser(antlr4.CommonTokenStream(my_lexer))
    my_parser.addErrorListener(my_error_log)

    context = my_parser.code()
    my_lsystem = lgrammarVisitor().visit(context)

    if my_error_log.getErrors():
        raise RuntimeError("\n".join(my_error_log.getErrors()))
    if my_lsystem is None:
        raise RuntimeError("Could not parse")

    return my_lsystem
