# vi:et:ts=2:sw=2

import sys
import re
import textwrap
from . import util
from .util import error_result
from . import debugging

__doc__ = """
This module provides a full-featured pure-python framework for building tokenizing LR language parsers and interpreters for context-free grammars.  (The :mod:`modgrammar` parsing engine is implemented as a recursive-descent parser with backtracking, using an object-oriented grammar model.)

The :mod:`modgrammar` parser is designed such that language grammars can be defined in python modules using standard python syntax.  To create a new grammar, simply create a new class definition (or multiple class definitions) derived from the :class:`Grammar` base class, and set its :attr:`grammar` attribute to a list of sub-grammars to match.  (Such definitions can be combined together into full grammar trees.)  Several basic pre-defined grammar constructs are also available in this module which larger grammars can be built up from.

Once a grammar is defined, the :meth:`~Grammar.parser` method can be called on the toplevel grammar class to obtain a :class:`GrammarParser` object, which can be used to parse text against the defined grammar.
"""

# A note on how different descriptive attrs/methods are used:
#   grammar_name = alternative to class name (used by repr, str, ebnf)
#   grammar_desc = description of grammar used in error messages
#   grammar_details() = full description of grammar (used by repr)

__all__ = [
    "ReferenceError", "UnknownReferenceError", "BadReferenceError", "ParseError", "Grammar",
    "Terminal",
    "Literal", "Word", "Repetition", "ListRepetition", "Reference",
    "GRAMMAR", "G", "ANY", "EMPTY", "REF", "LITERAL", "L", "OR", "EXCEPT", "WORD", "REPEAT", "LIST_OF", "OPTIONAL", "NOT_FOLLOWED_BY",
    "ZERO_OR_MORE", "ONE_OR_MORE", "ANY_EXCEPT", "BOL", "EOL", "EOF",
    "REST_OF_LINE", "WHITESPACE", "SPACE",
    "generate_ebnf",
    "WS_DEFAULT", "WS_NOEOL",
]

WS_DEFAULT = re.compile(r'\s+')
WS_NOEOL = re.compile('[^\S' + util.EOL_CHARS + ']+')

grammar_whitespace = WS_DEFAULT
grammar_whitespace_mode = 'explicit'

class _Singleton:
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return self.name

DEFAULT = _Singleton("DEFAULT")  # singleton used for detecting default args

def _gclass_reconstructor(name, bases, cdict):
  return GrammarClass(name, bases, cdict)

def _ginstance_reconstructor(name, bases, cdict):
  cls = GrammarClass(name, bases, cdict)
  return cls.__new__(cls)

###############################################################################
#                                 Exceptions                                  #
###############################################################################

class InternalError (Exception):
  """
  This exception is raised by the parser if something happens which should never happen.  It usually indicates that a grammar with a custom :meth:`~Grammar.grammar_parse` definition has done something it shouldn't.
  """
  pass

class GrammarDefError (Exception):
  """
  This exception is raised when creating/defining new grammar classes if there is a problem with the definition which cannot be resolved.
  """
  pass

class ReferenceError (Exception):
  """
  This is the base class for :exc:`UnknownReferenceError` and :exc:`BadReferenceError`.  It can be used to easily catch either exception.
  """
  pass

class UnknownReferenceError (ReferenceError):
  """
  An attempt was made to resolve a :func:`REF` reference, but no grammar with the given name could be found, and no default was provided in the :func:`REF` declaration.
  """
  pass

class BadReferenceError (ReferenceError):
  """
  An attempt was made to resolve a :func:`REF` reference, and the reference name was resolved to an object, but the object is not a valid grammar object.
  """
  pass

class ParseError (Exception):
  """
  Raised by the parser when the provided text cannot be matched against the grammar.

  This exception has several useful attributes:
    .. attribute:: grammar

       The top-level grammar the parser was attempting to match.

    .. attribute:: buffer

       The contents of the text buffer the parser was attempting to match against the grammar.

    .. attribute:: pos

       The position within the buffer at which the problem occurred.

    .. attribute:: char

       The (total parsing) character position at which the problem occurred (similar to the :attr:`GrammarParser.char` attribute).

    .. attribute:: line

       The line at which the problem occurred (similar to the :attr:`GrammarParser.line` attribute).

    .. attribute:: col

       The column position within the line at which the problem occurred (similar to the :attr:`GrammarParser.col` attribute).

    .. attribute:: expected

       A list of possible sub-grammars which the parser expected to find at this position (but didn't).

    .. attribute:: message

       The text message which would be printed if this exception were printed.  (This is of the form "Expected ...: Found ...")
  """
  def __init__(self, grammar, buf, pos, char, line=None, col=None, expected=None, message=None):
    if message is None:
      if not expected:
        message = ""
      else:
        noteworthy = [e for e in expected if e.grammar_noteworthy]
        if not noteworthy:
          noteworthy = expected
        expected_txt = " or ".join(sorted(e.grammar_desc for e in noteworthy))
        found_txt = util.get_found_txt(buf, pos)
        message = "Expected {}: Found {}".format(expected_txt, found_txt)
    self.buffer = buf
    self.buffer_pos = pos
    self.char = char
    self.line = line
    self.col = col
    self.expected = expected
    self.message = message

  def __str__(self):
    lc = []
    if self.line is not None:
      lc.append("line {}".format(self.line + 1))
    if self.col is not None:
      lc.append("column {}".format(self.col + 1))
    if lc:
      return "[{}] {}".format(", ".join(lc), self.message)
    else:
      return "[char {}] {}".format(self.char + 1, self.message)

###############################################################################
#                           Core (internal) Classes                           #
###############################################################################

class GrammarClass (type):
  "The metaclass for all Grammar classes"

  def __init__(cls, name, bases, classdict):
    if getattr(cls, 'grammar', None) is None:
      # This is an abstract class definition.  Don't do any of our usual setup.
      return
    cls._hash_id = None
    if "grammar_name" not in classdict:
      cls.grammar_name = cls.__name__
    if "grammar_desc" not in classdict:
      cls.grammar_desc = cls.grammar_name
    cls.grammar = util.regularize(cls.grammar)
    if not hasattr(cls, 'grammar_min'):
      cls.grammar_min = len(cls.grammar)
    if not hasattr(cls, 'grammar_max'):
      cls.grammar_max = len(cls.grammar)
    tags = getattr(cls, "grammar_tags", ())
    if isinstance(tags, str):
      # This is going to be a common slip-up.. might as well handle it
      # gracefully...
      tags = (tags,)
    cls.grammar_tags = tags
    mod = sys.modules[cls.__module__]
    if "grammar_whitespace" not in classdict and cls.grammar_whitespace is None:
      whitespace = getattr(mod, "grammar_whitespace", grammar_whitespace)
      cls.grammar_whitespace = whitespace
    if "grammar_whitespace_mode" not in classdict and cls.grammar_whitespace_mode is None:
      whitespace_mode = getattr(mod, "grammar_whitespace_mode", grammar_whitespace_mode)
      cls.grammar_whitespace_mode = whitespace_mode
    cls.__class_init__(classdict)

  def __reduce__(cls):
    # Note: __reduce__ on metaclasses does not currently work, so this is
    # currently unused.  The hope is that someday it will actually work.
    try:
      lookup = sys.modules[cls.__module__].__dict__[cls.__name__]
    except KeyError:
      lookup = None
    if lookup == cls:
      return cls.__name__
    cdict = dict(cls.__dict__)
    for key in cls.__dict__.keys():
      if key.startswith('__'):
        del cdict[key]
    return (_gclass_reconstructor, (cls.__name__, cls.__bases__, cdict))

  def __repr__(cls):
    return cls.__class_repr__()

  def __str__(cls):
    return cls.__class_str__()

  def __add__(cls, other):
    return util.add_grammar(cls, other)

  def __radd__(cls, other):
    return util.add_grammar(other, cls)

  def __or__(cls, other):
    return OR(cls, other)

  def __ror__(cls, other):
    return OR(other, cls)

  def __sub__(cls, other):
    return EXCEPT(cls, other)

  def __rsub__(cls, other):
    return EXCEPT(other, cls)

  def __setattr__(cls, attr, value):
    if attr in cls.grammar_hashattrs and cls._hash_id is not None:
      # Python hashability requires that once something obtains our hash, it
      # should never change, so we just consider these attributes read-only if
      # our hash value has ever been calculated before.
      raise AttributeError("Changing the value of the {!r} attribute would change the hash value of the object.".format(attr))
    return type.__setattr__(cls, attr, value)

  def __hash__(cls):
    hash_id = cls._hash_id
    if hash_id is None:
      hash_id = hash(cls.grammar_hashdata())
      cls._hash_id = hash_id
    return hash_id

  def __eq__(cls, other):
    if not isinstance(other, GrammarClass):
      return NotImplemented
    return cls.grammar_hashdata() == other.grammar_hashdata()

  def __ne__(cls, other):
    if not isinstance(other, GrammarClass):
      return NotImplemented
    return cls.grammar_hashdata() != other.grammar_hashdata()

class Text:
  """Text objects are used to hold the current working text being matched against the grammar.  They keep track of both the text contents and certain other useful state information such as whether we're at the beginning of a line or the end of a file, etc.
     Do not use this class directly.  This is only intended to be used internally by the modgrammar module.
  """
  def __init__(self, string, bol=False, eof=False):
    self.string = ""
    self.append(string, bol=bol, eof=eof)

  def append(self, string, bol=None, eof=None):
    if bol is not None:
      if not self.string:
        self.bol = bol
      elif bol:
        self.string += "\n"
        eof = bool(eof)
    if string:
      self.string += string
      eof = bool(eof)
    if eof is not None:
      self.eof = eof
    return self

  def skip(self, count):
    if count:
      self.bol = (self.string[count-1] == "\n")
      self.string = self.string[count:]
    return self

  def __str__(self):
    return self.string

  def __repr__(self):
    cls = self.__class__
    return "{0.__module__}.{0.__name__}({1.string!r}, bol={1.bol}, eof={1.eof})".format(cls, self)

class ParserSession:
  def __init__(self, data={}):
    self.data = data
    self.parser = None
    self.debugger = None

class GrammarParser:
  """
  Parser objects are the way in which an application can actually make use of a grammar definition.  They provide the core interface to take input texts and attempt to match them against an associated grammar definition.

  :class:`GrammarParser` objects are not generally instantiated directly.  Instead, to obtain one, call the :meth:`~Grammar.parser` method on the appropriate grammar class.

  Parser objects have the following useful attributes:

  .. attribute:: char

     The number of characters we've successfully parsed since the beginning of parsing (or the last :meth:`reset`).

  .. attribute:: line

     The number of lines we've successfully parsed since the beginning of parsing (or the last :meth:`reset`).  This is measured based on the number of line-end sequences we've seen thus far.

  .. attribute:: col

     The position within the current :attr:`line` we're at.
  """

  def __init__(self, grammar, sessiondata, tabs, debug, debug_flags):
    self.grammar = grammar
    self.tabs = tabs
    self.session = ParserSession(sessiondata)
    if not debug:
      self.debugger = None
    elif isinstance(debug, debugging.GrammarDebugger):
      self.debugger = debug
    else:
      self.debugger = debugging.GrammarDebugger(debug, debug_flags)
    self.reset()

  def reset(self):
    """
    Reset this parser back to its initial state.

    This will clear any remainder in the buffer and reset all (line, column, etc) counters to zero.
    """
    self.char = 0
    self.line = 0
    self.col = 0
    self.clear_remainder()

  def clear_remainder(self):
    """
    Clear any un-matched text left in the buffer.
    """

    self.text = Text("", bol=True)
    self.state = (None, None)

  def remainder(self):
    """
    Return the left over unmatched text in the buffer, if any.  (This method does not actually change the buffer, only report its current contents.  If you want to clear the buffer, use :meth:`clear_remainder`.)
    """
    return self.text.string

  def append(self, string, bol=None, eof=None):
    self.text.append(string, bol=bol, eof=eof)

  def _parse(self, pos, session, matchtype):
    debugger = session.debugger
    parsestate, matches = self.state
    best_error = None
    while True:
      if not parsestate:
        matches = []
        parsestate = self.grammar.grammar_parse(self.text, pos, session)
        if debugger:
          parsestate = debugger.debug_wrapper(parsestate, self.grammar, pos, self.text)
        count, obj = next(parsestate)
      else:
        count, obj = parsestate.send(self.text)
      if count is False:
        # We're done
        if matches:
          break
        # No results.  We must have errored out.
        if pos == len(self.text.string):
          # This happens when we've hit EOF but we want to do one more pass
          # through in case anything wants to match the EOF itself.  If nothing
          # does, we don't really expect anything else to match on an empty
          # string, so ignore the error.
          return (None, None)
        best_error = util.update_best_error(best_error, obj)
        errpos, expected = best_error
        if errpos == len(self.text.string) and self.grammar.grammar_whitespace_mode != 'explicit':
          # If we hit EOF and this grammar is whitespace-consuming, check to
          # see whether we had only whitespace before the EOF.  If so, treat
          # this like the pos == len(self.text.string) case above.
          whitespace_re = self.grammar.grammar_whitespace
          m = whitespace_re.match(self.text.string, pos)
          if m and m.end() == len(self.text.string):
            return (None, None)
        char = self.char + errpos
        line, col = util.calc_line_col(self.text.string, errpos, self.line, self.col, self.tabs)
        raise ParseError(self.grammar, self.text.string, errpos, char, line=line, col=col, expected=expected)
      if count is None:
        # We need more input
        if self.text.eof:
          # Grammars should not be asking for more data after eof.
          raise InternalError("Grammar requested more data when at EOF (invoke with debug mode for more detailed info)")
        self.state = (parsestate, matches)
        return (None, None)
      if matchtype == 'complete' and (pos + count) != len(self.text.string):
        # We're only looking for complete matches and this one has a remainder
        # Pretend there was an EOI grammar at the end that didn't match
        obj = error_result(pos + count, EOI)[1]
        best_error = util.update_best_error(best_error, obj)
        continue
      matches.append((count, obj))
      if matchtype in ('first', 'complete'):
        # We only need the first one, no need to keep looping
        break

    # At this point we've gotten one or more successful matches
    self.state = (None, None)
    if matchtype == 'first':
      count, obj = matches[0]
    elif matchtype == 'complete':
      count, obj = matches[0]
    elif matchtype == 'last':
      count, obj = matches[-1]
    elif matchtype == 'longest':
      count, obj = max(matches, key=lambda m: m[0])
    elif matchtype == 'shortest':
      count, obj = min(matches, key=lambda m: m[0])
    elif matchtype == 'all':
      objs = [x[1] for x in matches]
      count = max(x[0] for x in matches)
      pp_objs = []
      for obj in objs:
        result = obj.grammar_postprocess(None, session)
        if len(result) == 1:
          result = result[0]
        pp_objs.append(result)
      return (count, pp_objs)
    else:
      raise ValueError("Invalid value for 'matchtype' parameter: {!r}".format(matchtype))

    result = obj.grammar_postprocess(None, session)
    if len(result) == 1:
      result = result[0]
    return (count, result)

  def _parse_text(self, string, bol, eof, data, matchtype):
    if data is None:
      session = self.session
    else:
      session = ParserSession(data)
    self.append(string, bol=bol, eof=eof)
    pos = 0
    session.parser = self #FIXME
    session.debugger = self.debugger

    while True:
      count, obj = self._parse(pos, session, matchtype)
      if count is None:
        # Partial match
        break
      elif matchtype != 'all':
        self.skip(count)
      yield obj
      if not count:
        # We matched a zero-length string.  If we keep looping, we'll just loop
        # infinitely doing the same thing.  Best to stop now.
        break
      if not self.text.eof and pos == len(self.text.string):
        # We've done all we can for now.
        # Note: if we're at EOF, we loop one more time in case something wants
        # to match the EOF, and then we'll break on either the error-on-EOF
        # case or the count-is-zero case next time through.
        break

  def parse_text(self, string, bol=None, eof=None, reset=False, multi=False, data=None, matchtype='first'):
    """
    Add *string* to the parse buffer and attempt to match it against the associated grammar.  If successful, returns a corresponding match object.  If there is an incomplete match (or it is impossible to determine yet whether the match is complete or not), save the current text in the match buffer and return :const:`None` to indicate more text is required.  If the text does not match any valid grammar construction, raise :exc:`ParseError`.

    Optional parameters:
      *reset*
        Call :meth:`reset` before starting to parse the supplied text.
      *multi*
        Instead of returning a single match result, keep matching as many times as possible before returning, and return a list of matches, in sequence.
      *eof*
        Indicates that no more text will be coming, and the parser should return the best match it can with the supplied text instead of asking for more.  (If *eof* is set, the parser will never return a :const:`None` result, unless the buffer is completely empty.)
      *data*
        Use the provided data instead of the default *sessiondata* during this parse run.
      *matchtype*
        If a grammar could match multiple ways, determine how the best match is chosen:
          'first' (default)
            The first successful match the grammar comes up with (as determined by normal grammar test ordering).
          'last'
            The last successful match.
          'longest'
            The match which uses up the longest portion of the input text.
          'shortest'
            The match which uses up the shortest portion of the input text.
          'complete'
            The first match which exactly matches the input text (i.e. there is no remainder).
          'all'
            Return all possible matches, in a list.  Note that in this case the buffer position will not be automatically advanced.  You must call :func:`~GrammarParser.skip` manually.
      *bol*
        Treat the input text as starting at the beginning of a line (for the purposes of matching the :const:`BOL` grammar element).  It is not usually necessary to specify this explicitly.
    """
    if reset:
      self.reset()
    if multi:
      return list(self._parse_text(string, bol, eof, data, matchtype))
    else:
      for result in self._parse_text(string, bol, eof, data, matchtype):
        # This will always just return the first result
        return result
      return None

  def parse_string(self, string, data=None):
    """
    Assume that *string* is a complete self-contained text and attempt to match it (exactly) against the associated grammar.  This will discard any data previously in the buffer and will require that the grammar match the entire string (i.e. no remainder is allowed).

    This is equivalent to ``.parse_text(string, reset=True, eof=True, matchtype='complete')``
    """
    self.reset()
    for result in self._parse_text(string, True, True, data, 'complete'):
      # This will always just return the first result
      return result
    return None

  def parse_lines(self, lines, bol=False, eof=False, reset=False, data=None, matchtype='first'):
    """
    *(generator method)*

    Attempt to match a list (or actually any iterable) of strings against the associated grammar.  This is effectively the same as calling :meth:`parse_text` repeatedly for each string in the list to obtain all matches in sequence.

    Return values, exceptions, and optional parameters are all exactly the same as for :meth:`parse_text`.

    .. note::
       Be careful using ``matchtype="all"`` with parse_lines/parse_file.  You must manually call :func:`~GrammarParser.skip` after each yielded match, or you will end up with an infinite loop!
    """
    if reset:
      self.reset()
    for line in lines:
      for result in self._parse_text(line, bol, False, data, matchtype):
        yield result
      bol = None
    if eof:
      for result in self._parse_text("", None, True, data, matchtype):
        yield result

  def parse_file(self, file, encoding=None, bol=False, eof=True, reset=False, data=None, matchtype='first'):
    """
    *(generator method)*

    Open and process the contents of a file using the associated grammar.  This is basically the same as opening the specified file, and passing the resulting file object to :meth:`parse_lines`.

    *file* and *encoding* are passed directly to :meth:`open`.  Return values, exceptions, and other optional parameters are all exactly the same as for :meth:`parse_text`.

    .. note::
       Be careful using ``matchtype="all"`` with parse_lines/parse_file.  You must manually call :func:`~GrammarParser.skip` after each yielded match, or you will end up with an infinite loop!
    """
    if isinstance(file, str):
      with open(file, "r", encoding=encoding) as f:
        for result in self.parse_lines(f, bol=bol, eof=eof, reset=reset, data=data, matchtype=matchtype):
          yield result
    else:
      for result in self.parse_lines(file, bol=bol, eof=eof, reset=reset, data=data, matchtype=matchtype):
        yield result

  def skip(self, count):
    """
    Skip forward the specified number of characters in the input buffer (discarding the text skipped over).
    """

    if count:
      if count > len(self.text.string):
        raise ValueError("Attempt to skip past end of available buffer.")
      # The state may contain index values in it, which will become invalid if
      # we change the starting point, so we (unfortunately) need to nuke it.
      self.state = (None, None)
      self.char += count
      self.line, self.col = util.calc_line_col(self.text.string, count, self.line, self.col, self.tabs)
      self.text.skip(count)

  def remainder(self):
    """
    Return the remaining contents of the parse buffer.  After parsing, this will contain whatever portion of the original text was not used by the parser up to this point.
    """
    return self.text.string

###############################################################################
#                            Base (public) Classes                            #
###############################################################################

class Grammar (metaclass=GrammarClass):
  """
  This class is not intended to be instantiated directly.  Instead, it is a base class to be used for defining your own custom grammars.

  Subclasses of :class:`Grammar` serve two purposes.  The first is to actually define the grammar used for parsing.  The second is to serve as a base type for result objects created as the result of parsing.

  To define a new grammar, you should create a new class definition, descended from :class:`Grammar`.  In this class definition, you can override several class attributes and class methods to customize the behavior of the grammar.
  """

  grammar_terminal = False
  grammar_collapse = False
  grammar_greedy = True
  grammar_null_subtoken_ok = True
  grammar_whitespace = None
  grammar_whitespace_mode = None
  grammar_error_override = False
  grammar_noteworthy = True
  grammar_hashattrs = ('grammar_name', 'grammar', 'grammar_min', 'grammar_max', 'grammar_collapse', 'grammar_greedy', 'grammar_whitespace', 'grammar_whitespace_mode')

  @classmethod
  def __class_init__(cls, attrs):
    pass

  @classmethod
  def parser(cls, sessiondata=None, tabs=1, debug=False, debug_flags=None):
    """
    Return a :class:`GrammarParser` associated with this grammar.

    If provided, *sessiondata* can contain data which should be provided to the :meth:`grammar_elem_init` method of each result object created during parsing.

    The *tabs* parameter indicates the width of "tab stops" in the input (i.e. how far a "tab" character will advance the column position when encountered).  This is only used to correctly report column numbers in :exc:`ParseError`\ s.  If you don't care about that, or your input does not contain tabs, you can ignore this parameter.

    The *debug* and *debug_flags* options control whether and how debugging information will be output while using this parser.  For more information on grammar debugging, see the :mod:`modgrammar.debugging` module documentation.
    """
    return GrammarParser(cls, sessiondata, tabs, debug, debug_flags)

  # Yields:
  #   Success:     (count, obj)
  #   Incomplete:  (None, None)
  #   Parse error: (False, error_tuple)
  @classmethod
  def grammar_parse(cls, text, index, session):
    """
    This method is called by the :mod:`modgrammar` parser system to actually attempt to match this grammar against a piece of text.  This method is not intended to be called directly by an application (use the :meth:`parser` method to obtain a :class:`GrammarParser` object and use that).  In advanced cases, this method can be overridden to provide custom parsing behaviors for a particular grammar type.

    .. note::
       Overriding this method is very complicated and currently beyond the scope of this documentation.  This is not recommended for anyone who does not understand the :mod:`modgrammar` parser design very well.  (Someday, with luck, there will be some more documentation written on this advanced topic.)
    """

    grammar = cls.grammar
    grammar_min = cls.grammar_min
    grammar_max = cls.grammar_max
    greedy = cls.grammar_greedy
    whitespace_mode = cls.grammar_whitespace_mode
    whitespace_re = cls.grammar_whitespace
    if whitespace_mode == 'optional':
      whitespace_skip = True
      whitespace_reqd = False
    elif whitespace_mode == 'required':
      whitespace_skip = True
      whitespace_reqd = True
    else:
      whitespace_skip = False
      whitespace_reqd = False
    debugger = session.debugger
    objs = []
    states = []
    positions = []
    best_error = None
    pos = index
    first_pos = None

    while True:
      # Forward ho!
      while True:
        if not greedy and len(objs) >= grammar_min:
          # If we're not "greedy", then try returning every match as soon as we
          # get it (which will naturally return the shortest matches first)
          yield (pos - index, cls(text.string, index, pos, objs))
          # We need to copy objs for any further stuff, since it's now part of
          # the object we yielded above, which our caller may be keeping for
          # later, so if we modify it in-place we'll be screwing up the
          # 'entities' list of that object in the process.
          objs = list(objs)
        if len(objs) >= grammar_max:
          break
        prews_pos = pos
        if whitespace_skip:
          while True:
            m = whitespace_re.match(text.string, pos)
            if m:
              if debugger:
                debugger.ws_skipped(cls, pos, text, m.end() - pos)
              pos = m.end()
            if pos < len(text.string) or text.eof:
              break
            text = yield (None, None)
          if whitespace_reqd and objs and pos == prews_pos:
            # We didn't match any whitespace before the next sub-grammar, but
            # whitespace is required between sub-grammars.  Handle this as if
            # there were a WHITESPACE grammar in this spot that gave us back an
            # error result.
            if debugger:
              debugger.ws_not_found(cls, pos, text)
            obj = util.error_result(pos, WHITESPACE)[1]
            best_error = util.update_best_error(best_error, obj)
            break
        if first_pos is None:
          first_pos = pos
        g = grammar[len(objs)]
        s = g.grammar_parse(text, pos, session)
        if debugger:
          s = debugger.debug_wrapper(s, g, pos, text)
        while True:
          offset, obj = next(s)
          while offset is None:
            text = yield (None, None)
            offset, obj = s.send(text)
          if cls.grammar_null_subtoken_ok or offset is not 0:
            break
        if offset is False:
          best_error = util.update_best_error(best_error, obj)
          pos = prews_pos
          break
        objs.append(obj)
        states.append((pos, s))
        pos += offset
      # Went as far as we can forward and it didn't work.  Backtrack until we
      # find something else to follow...
      while True:
        if greedy and len(objs) >= grammar_min:
          # If we are greedy, then return matches only after we've gone as far
          # forward as possible, while we're backtracking (returns the longest
          # matches first)
          yield (pos - index, cls(text.string, index, pos, objs))
          # We need to copy objs for any further stuff, since it's now part of
          # the object we yielded above, which our caller may be keeping for
          # later, so if we modify it in-place we'll be screwing up the
          # 'entities' list of that object in the process.
          objs = list(objs)
        if not states:
          break
        pos, s = states[-1]
        offset, obj = next(s)
        while offset is None:
          text = yield (None, None)
          offset, obj = s.send(text)
        if offset is False:
          best_error = util.update_best_error(best_error, obj)
          states.pop()
          objs.pop()
        else:
          objs[-1] = obj
          pos += offset
          break
      # Have we gone all the way back to the beginning?
      # If so, give up.  If not, loop around and try going forward again.
      if not states:
        break
    if cls.grammar_error_override:
      # If our sub-grammars failed to match, but we've got
      # grammar_error_override set, return ourselves as the failed match
      # grammar instead.
      yield error_result(index, cls)
    elif ((len(cls.grammar) == 1)
          and (best_error[0] == first_pos)
          and (cls.grammar_desc != cls.grammar_name)):
      # We're just a simple wrapper (i.e. an alias) around another single
      # grammar class, and it failed to match, and we have a custom
      # grammar_desc.  Return ourselves as the failed match grammar so the
      # ParseError will contain our grammar_desc instead.
      yield error_result(index, cls)
    else:
      yield error_result(*best_error)

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    """
    Determines the string to be used for this grammar when it occurs in the left-hand-side (LHS) of an EBNF definition.  This can be overridden to customize how this grammar is represented by :func:`generate_ebnf`.

    Returns a tuple *(string, grammars)*, where *string* is the EBNF LHS string to use, and *grammars* is a list of other grammars on which this one depends (i.e. grammars whose names are referenced in *string*).
    """

    return (cls.grammar_name, ())

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    """
    Determines the string to be used to describe this grammar when it occurs in the right-hand-side (RHS) of an EBNF definition.  This can be overridden to customize how this grammar is represented by :func:`generate_ebnf`.

    Returns a tuple *(string, grammars)*, where *string* is the EBNF RHS string to use, and *grammars* is a list of other grammars on which this one depends (i.e. grammars whose names are referenced in *string*).
    """

    if cls.grammar_terminal and not opts["expand_terminals"]:
      return None
    if cls.grammar_parse.__func__ is Grammar.grammar_parse.__func__:
      names, nts = util.get_ebnf_names(cls.grammar, opts)
      return (", ".join(names), nts)
    else:
      return (util.ebnf_specialseq(cls, opts), ())

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    """
    Returns a string containing a description of the contents of this grammar definition (such as used by :func:`repr`).

    *depth* specifies a recursion depth to use when constructing the string description.  If *depth* is nonzero, this method will recursively call :meth:`grammar_details` for each of its sub-grammars in turn to construct the final description.  If *depth* is zero, this method will just return this grammar's name (:attr:`grammar_name`).  If *depth* is negative, recursion depth is not limited.

    *visited* is used for detecting circular references during recursion.  It can contain a tuple of grammars which have already been seen and should not be descended into again.
    """

    if cls.grammar_parse.__func__ is Grammar.grammar_parse.__func__:
      if depth != 0:
        if not visited:
          visited = (cls,)
        elif cls in visited:
          # Circular reference.  Stop here.
          return cls.grammar_name
        else:
          visited = visited + (cls,)
        if len(cls.grammar) == 1:
          return cls.grammar[0].grammar_details(depth - 1, visited)
        else:
          return "(" + ", ".join((g.grammar_details(depth - 1, visited) for g in cls.grammar)) + ")"
    return cls.grammar_name

  @classmethod
  def __class_str__(cls):
    """
    Returns the string to be used when :func:`str` is used on this grammar class (**Note:** This is for the class itself, not for instances of the class.  For those, the usual :meth:`__str__` is used).
    """

    return cls.grammar_name

  @classmethod
  def __class_repr__(cls):
    """
    Returns the string to be used when :func:`repr` is used on this grammar class (**Note:** This is for the class itself, not for instances of the class.  For those, the usual :meth:`__repr__` is used).
    """

    if not hasattr(cls, 'grammar'):
      # This is an abstract class, so most of our grammar-related methods won't
      # work right.  Just return a simple repr similar to Python's default.
      return "<class '{}.{}'>".format(cls.__module__, cls.__name__)
    name = cls.grammar_name
    details = cls.grammar_details(1)
    if name == details or name.startswith("<"):
      return "<Grammar: {}>".format(details)
    else:
      return "<Grammar[{}]: {}>".format(name, details)

  @classmethod
  def grammar_hashdata(cls):
    return (cls.grammar_parse.__func__, tuple(getattr(cls, x) for x in cls.grammar_hashattrs))

  @classmethod
  def grammar_resolve_refs(cls, refmap={}, recurse=True, follow=False, missing_ok=False, skip=None):
    """
    Resolve any :func:`REF` declarations within the grammar and replace them with the actual sub-grammars they refer to.  The following optional arguments can be provided:

      *refmap*
        If provided, contains a dictionary of reference-name to grammar mappings to use.  If a reference's name is found in this dictionary, the dictionary value will be used to replace it, instead of using the standard name-lookup procedure.
      *recurse*
        If set to :const:`True`, will perform a recursive search into each of this grammar's sub-grammars, calling :meth:`grammar_resolve_refs` on each with the same parameters.
      *follow*
        If set to :const:`True` (and *recurse* is also :const:`True`), will also call :meth:`grammar_resolve_refs` on the result of each :func:`REF` after it is resolved.
      *missing_ok*
        If :const:`True`, it is not considered an error if a :func:`REF` construct cannot be resolved at this time (it will simply be left as a :func:`REF` in the resulting grammar).  If :const:`False`, then all references must be resolvable or an :exc:`UnresolvedReference` exception will be raised.
      *skip*
        An optional list of grammars which should not be searched for :func:`REF` constructs (useful in conjunction with *recurse* to exclude certain parts of the grammar).
    """

    if not skip:
      skip = set()
    else:
      # We maintain 'skip' as a set of ids, because it's quicker and
      # technically more correct than keeping the objects themselves (which
      # will compare based on hash)
      skip = set(x if isinstance(x, int) else id(x) for x in skip)
    if id(cls) in skip:
      return
    skip.add(id(cls))
    grammar = []
    for g in cls.grammar:
      rec = recurse
      while issubclass(g, Reference):
        try:
          g = g.resolve(refmap)
        except UnknownReferenceError:
          if not missing_ok:
            raise
        if not follow:
          rec = False
          break
      # We have to calculate the hash value now before we potentially create a
      # cyclic grammar tree, as trying to calculate it afterward would result
      # in an infinite loop.
      hash(g)
      grammar.append(g)
      if rec and hasattr(g, "grammar_resolve_refs"):
        g.grammar_resolve_refs(refmap, recurse, follow, missing_ok, skip)
    # We have to bypass the normal __setattr__ here because we're technically
    # changing a hash-related attr after our hash may already have been
    # calculated.  In this case, it's ok, because the two grammars are
    # effectively the same anyway.
    type.__setattr__(cls, 'grammar', tuple(grammar))

  def __init__(self, string, start=0, end=None, parsed=()):
    self._str_info = (string, start, end)
    self.elements = parsed
    self.string = ""

  def grammar_collapsed_elems(self, sessiondata):
    """
    Return the list of elements to be used in place of this one when collapsing (this is only used if :attr:`grammar_collapse` is :const:`True`).
    """
    elems = []
    if not self.elements:
      return (None,)
    for e in self.elements:
      if not getattr(e, "grammar_collapse_skip", False):
        elems.append(e)
    if elems:
      return elems
    else:
      return self.elements

  def grammar_postprocess(self, parent, session):
    self.parent = parent
    if hasattr(self, '_str_info'):
      s, start, end = self._str_info
      self.string = s[start:end]
      #del self._str_info
      if self.grammar_collapse:
        elems = self.grammar_collapsed_elems(session.data)
        pp_elems = []
        for e in elems:
          if e is None:
            pp_elems.append(e)
          else:
            pp_elems.extend(e.grammar_postprocess(parent, session))
        return tuple(pp_elems)
      else:
        elems = self.elements
        pp_elems = []
        for e in elems:
          pp_elems.extend(e.grammar_postprocess(self, session))
        self.elements = tuple(pp_elems)
        del self._str_info
    if hasattr(self, 'elem_init'):
      for c in type.mro(self.__class__):
        if 'elem_init' in c.__dict__:
          break
      else:
        c = self.__class__
      util.depwarning("In class {}.{}: 'elem_init' method is deprecated.  Use 'grammar_elem_init' instead.".format(c.__module__, c.__name__), util.get_calling_stacklevel())
      self.elem_init(session.data)
    self.grammar_elem_init(session.data)
    return (self,)

  def grammar_elem_init(self, sessiondata):
    """
    This method is called on each result object after it is fully initialized, before the resulting parse tree is returned to the caller.  It can be overridden to perform any custom initialization desired (the default implementation does nothing).

    Note: If :attr:`grammar_collapse` is :const:`True`, this method is not called, and :meth:`grammar_collapsed_elems` is called instead.
    """
    pass

  def get_all(self, *tt_path):
    """
    Return all immediate sub-elements of the given type, or posessing the given tag.

    If more than one type/tag parameter is provided, it will treat the types as a "path" to traverse: for all sub-elements matching the first type/tag, retrieve all sub-elements of those matching the second type/tag, and so on, until it reaches the last type/tag in the list.  (It will thus return all elements of the parse tree which are of the final type/tag, which can be reached by traversing the previous types/tags in order.)

    Note that types and tags can be intermingled, as well.
    """
    return list(self._search_recursive(util.find_match_func, False, tt_path))

  def get(self, *tt_path):
    """
    Return the first immediate sub-element of the given type/tag (or by descending through multiple types/tags, in the same way as :meth:`get_all`).

    This is equivalent to ``.get_all(*tt_path)[0]`` except that it is more efficient, and will return :const:`None` if there are no such objects (instead of raising :exc:`IndexError`).
    """
    try:
      return next(self._search_recursive(util.find_match_func, False, tt_path))
    except StopIteration:
      return None

  def find_all(self, *tt_path):
    """
    Return all elements anywhere in the parse tree matching the given type/tag.

    Similar to :meth:`get_all`, if more than one type/tag parameter is provided, it will treat them as a "path" to traverse in order.  The difference from :meth:`get_all` is that, for each step in the path, the elements found do not have to be direct sub-elements, but can be anywhere in the sub-tree.
    """
    return list(self._search_recursive(util.find_match_func, True, tt_path))

  def find(self, *tt_path):
    """
    Return the first element anywhere in the parse tree matching the given type/tag (or by descending through multiple types/tags, in the same way as :meth:`find_all`).

    This is equivalent to ``.find_all(*tt_path)[0]`` except that it is more efficient, and will return :const:`None` if there are no such objects (instead of raising :exc:`IndexError`).
    """
    try:
      return next(self._search_recursive(util.find_match_func, True, tt_path))
    except StopIteration:
      return None

  def _search_recursive(self, func, skip, args):
    subargs = list(args)
    a = subargs.pop(0)
    for e in self.elements:
      if func(e, a):
        if subargs:
          for result in e._search_recursive(func, skip, subargs):
            yield result
        else:
          yield e
      elif skip and e is not None:
        for o in e._search_recursive(func, skip, args):
          yield o

  def terminals(self):
    """
    Return an ordered list of all result objects in the parse tree which are terminals (that is, where :attr:`grammar_terminal` is :const:`True`).
    """
    if self.grammar_terminal:
      return [self]
    results = []
    for e in self.elements:
      if e is None:
        pass
      else:
        results.extend(e.terminals())
    return results

  def tokens(self):
    """
    Return the parsed string, broken down into its smallest grammatical components.  (Another way of looking at this is that it returns the string values of all of the :meth:`terminals`.)
    """
    return [e.string for e in self.terminals()]

  def __getitem__(self, index):
    if isinstance(index, int):
      return self.elements[index]
    else:
      e = self.get(index)
      if e is not None:
        return e
      raise IndexError('no subgrammar matching {!r} found'.format(index))

  def __len__(self):
    return len(self.string)

  def __bool__(self):
    return bool(self.elements) or self.grammar_terminal

  def __str__(self):
    return self.string

  def __repr__(self):
    name = self.__class__.grammar_name
    details = [repr(str(e) if e is not None else e) for e in self.elements]
    if not details:
      details = (repr(self.string),)
    return "{}<{}>".format(name, ", ".join(details))

  def __reduce__(self):
    # This allows pickling of result objects based on classes which were dynamically generated at runtime (such as the results of LITERAL and WORD).  Normally, these are not pickleable because any pickleable object must be an instance of a class which can be looked up (by name) in the module's dictionary.  We provide a special function to unpickle such objects which will recreate the dynamic class first, and then provide an instance for the unpickler to use.
    # Note: This does not handle dynamic-subclasses of dynamic-subclasses, but we don't generally have those for Grammar class types anyway.
    cls = self.__class__
    try:
      lookup = sys.modules[cls.__module__].__dict__[cls.__name__]
    except KeyError:
      lookup = None
    if lookup == cls:
      return object.__reduce__(cls, self)
    cdict = dict(cls.__dict__)
    for key in cls.__dict__.keys():
      if key.startswith('__'):
        del cdict[key]
    if hasattr(self, '__getstate__'):
      state = self.__getstate__()
    else:
      state = self.__dict__
    return (_ginstance_reconstructor, (cls.__name__, cls.__bases__, cdict), state)

class AnonGrammar (Grammar):
  grammar_whitespace = None
  grammar_whitespace_mode = None

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    if len(cls.grammar) == 1:
      return cls.grammar[0].grammar_details(depth, visited)
    else:
      return "(" + ", ".join((g.grammar_details(depth, visited) for g in cls.grammar)) + ")"

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    if cls.grammar_name == "<GRAMMAR>":
      names, nts = util.get_ebnf_names(cls.grammar, opts)
      return (", ".join(names), nts)
    else:
      return (cls.grammar_name, (cls,))

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    if cls.grammar_name == "<GRAMMAR>":
      return None
    else:
      names, nts = util.get_ebnf_names(cls.grammar, opts)
      return (", ".join(names), nts)

class Terminal (Grammar):
  grammar_terminal = True

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    return cls.grammar_name

class Literal (Terminal):
  grammar_whitespace_mode = 'explicit'
  grammar_whitespace = None
  grammar = ()
  string = ""
  grammar_collapse_skip = True
  grammar_hashattrs = ('string',)

  @classmethod
  def __class_init__(cls, attrs):
    if "grammar_name" not in attrs:
      cls.grammar_name = "L({!r})".format(cls.string)
    if "grammar_desc" not in attrs:
      cls.grammar_desc = repr(cls.string)

  @classmethod
  def grammar_parse(cls, text, index, session):
    while (len(cls.string) + index > len(text.string)) and cls.string.startswith(text.string[index:]):
      if text.eof:
        break
      # Partial match.  Try again when we have more text.
      text = yield (None, None)
    if text.string.startswith(cls.string, index):
      yield (len(cls.string), cls(cls.string))
    yield error_result(index, cls)

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    return (repr(cls.string), ())

# NOTE: GRAMMAR and LITERAL must occur before Repetition/ListRepetition because
# they use them in their __class_init__ constructors.

def GRAMMAR(*subgrammars, **kwargs):
  """
  Allows the construction of "anonymous grammars", that is, creating a grammar without explicitly defining a named class derived from the :class:`Grammar` superclass.  This can be useful for some simple grammars where a full class definition is not necessary.

   *subgrammars* is a list of other grammars which the new grammar should be made up of, the same as would be given as the :attr:`~Grammar.grammar` attribute in a grammar class definition.
  """
  grammar = util.regularize(subgrammars)
  if len(grammar) == 1 and not kwargs:
    return grammar[0]
  else:
    cdict = util.make_classdict(AnonGrammar, grammar, kwargs)
    return GrammarClass("<GRAMMAR>", (AnonGrammar,), cdict)

def LITERAL(string, **kwargs):
  """
  Create a simple grammar that only matches the specified literal string.  Literal matches are case-sensitive.
  """
  cdict = util.make_classdict(Literal, (), kwargs, string=string)
  return GrammarClass("<LITERAL>", (Literal,), cdict)

class ANY (Terminal):
  grammar_whitespace_mode = 'explicit'
  grammar_whitespace = None
  grammar = ()
  grammar_name = "ANY"
  grammar_desc = "any character"

  @classmethod
  def grammar_parse(cls, text, index, session):
    while index == len(text.string):
      # The only case we can't match is if there's no input
      if text.eof:
        yield error_result(index, cls)
      text = yield (None, None)
    yield (1, cls(text.string, index, index+1))
    yield error_result(index, cls)

class EMPTY (Terminal):
  grammar_whitespace_mode = 'explicit'
  grammar_whitespace = None
  grammar = ()
  grammar_collapse = True
  grammar_collapse_skip = True
  grammar_desc = "(nothing)"

  @classmethod
  def grammar_parse(cls, text, index, session):
    # This always matches, no matter where it is.
    yield (0, cls(""))
    yield error_result(index, cls)

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    return ("(*empty*)", ())

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None

def OR(*grammars, **kwargs):
  """
  An either-or grammar that will successfully match if any of its subgrammars matches.  :func:`OR` grammars can also be created by combining other grammars in python expressions using the or operator (``|``).

  .. note::
     Each of the possible grammars are attempted in left-to-right order.  This means that if more than one of the listed grammars could potentially match, the leftmost one will always match first.
  """
  collapsed = []
  for g in grammars:
    if hasattr(g, "grammar_OR_merge"):
      collapsed.extend(g.grammar_OR_merge())
    else:
      collapsed.append(GRAMMAR(g))
  cdict = util.make_classdict(OR_Operator, collapsed, kwargs)
  return GrammarClass("<OR>", (OR_Operator,), cdict)

class OR_Operator (Grammar):
  grammar_whitespace_mode = 'explicit'

  @classmethod
  def __class_init__(cls, attrs):
    if not "grammar_desc" in attrs and cls.grammar:
      # This is not used directly when constructing ParseExceptions (because we
      # never return ourselves as a failure class, we only return the failures
      # from our subgrammars), but is needed by some other grammars which
      # construct their grammar_desc based on their subgrammar's grammar_descs
      # (i.e. NOT())
      cls.grammar_desc = " or ".join(g.grammar_desc for g in cls.grammar)

  @classmethod
  def grammar_parse(cls, text, index, session):
    debugger = session.debugger
    best_error = None
    for g in cls.grammar:
      results = g.grammar_parse(text, index, session)
      if debugger:
        results = debugger.debug_wrapper(results, g, index, text)
      for count, obj in results:
        while count is None:
          text = yield (None, None)
          count, obj = results.send(text)
        if count is False:
          best_error = util.update_best_error(best_error, obj)
          break
        yield (count, obj)
    yield error_result(*best_error)

  @classmethod
  def grammar_OR_merge(cls):
    return cls.grammar

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    if not depth:
      depth += 1
    return "("+" | ".join((c.grammar_details(depth-1, visited) for c in cls.grammar))+")"

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    names, nts = util.get_ebnf_names(cls.grammar, opts)
    return ("( "+" | ".join(names)+" )", nts)

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None

def NOT_FOLLOWED_BY(*grammar, **kwargs):
  """
  Returns a successful match as long as the next text after this point does NOT match the specified grammar.

  When successful (that is, the next text in the input does not match the specified grammar), this element of the parse tree will contain :const:`None`, and no input text will be consumed.  When unsuccessful (that is, the next text does match), a :exc:`ParseError` will be raised.
  """
  cdict = util.make_classdict(NotFollowedBy, grammar, kwargs)
  return GrammarClass("<NOT_FOLLOWED_BY>", (NotFollowedBy,), cdict)

class NotFollowedBy (Grammar):
  grammar_whitespace_mode = 'explicit'
  grammar_collapse = True

  @classmethod
  def __class_init__(cls, attrs):
    if not cls.grammar:
      cls.grammar = (EMPTY,)
    else:
      cls.grammar = (GRAMMAR(cls.grammar),)
    if not "grammar_desc" in attrs and cls.grammar:
      cls.grammar_desc = "anything except {}".format(cls.grammar[0].grammar_desc)

  @classmethod
  def grammar_parse(cls, text, index, session):
    best_error = None
    g = cls.grammar[0]
    debugger = session.debugger
    results = g.grammar_parse(text, index, session)
    if debugger:
      results = debugger.debug_wrapper(results, g, index, text)
    count, obj = next(results)
    while count is None:
      text = yield (None, None)
      count, obj = results.send(text)
    if count is not False:
      # The subgrammar matched.  That means we should consider this a parse
      # error.
      yield error_result(index, cls)
    else:
      # Subgrammar did not match.  Return a (successful) None match.
      yield (0, cls(''))
      # If the caller proceeds to the next "match", we need to yield an error
      # to indicate we're done with matching.
      yield error_result(index, cls)

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    if not visited:
      visited = (cls,)
    elif cls in visited:
      # Circular reference.  Stop here.
      return cls.grammar_name
    else:
      visited = visited + (cls,)
    return "NOT_FOLLOWED_BY({})".format(cls.grammar[0].grammar_details(depth, visited))

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    sub_lhs, sub_nts = cls.grammar[0].grammar_ebnf_lhs(opts)
    desc = "not followed by {}".format(sub_lhs)
    return (util.ebnf_specialseq(cls, opts, desc=desc), (cls.grammar[0],))

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None

def EXCEPT(grammar, exc_grammar, **kwargs):
  """
  Match *grammar*, but only if it does not also match *exception_grammar*.  (This is equivalent to the ``-`` (exception) operator in EBNF) :func:`EXCEPT` grammars can also be created by combining other grammars in python expressions using the except operator (``-``).

  .. note::
     In many cases there are more efficient ways to design a particular grammar than using this construct.  It is provided mostly for full EBNF compatibility.
  """
  cdict = util.make_classdict(ExceptionGrammar, (grammar, exc_grammar), kwargs)
  return GrammarClass("<EXCEPT>", (ExceptionGrammar,), cdict)

class ExceptionGrammar (Grammar):
  grammar_whitespace_mode = 'explicit'

  @classmethod
  def __class_init__(cls, attrs):
    if not "grammar_desc" in attrs and cls.grammar:
      cls.grammar_desc = "{} except {}".format(cls.grammar[0].grammar_desc, cls.grammar[1].grammar_desc)

  @classmethod
  def grammar_parse(cls, text, index, session):
    debugger = session.debugger
    best_error = None
    g = cls.grammar[0]
    exc = cls.grammar[1]
    results = g.grammar_parse(text, index, session)
    if debugger:
      results = debugger.debug_wrapper(results, g, index, text)
    for count, obj in results:
      while count is None:
        text = yield (None, None)
        count, obj = results.send(text)
      if count is False:
        best_error = util.update_best_error(best_error, obj)
        break
      # We found one, but now we need to check to make sure that the
      # exception-grammar does NOT match the same part of the text string.
      e_text = Text(text.string[:index+count], bol=text.bol, eof=True)
      e_results = exc.grammar_parse(e_text, index, session)
      if debugger:
        e_results = debugger.debug_wrapper(e_results, exc, index, e_text)
      for e_count, e_obj in e_results:
        if e_count == count:
          # Oops, we matched on the exception grammar (and it's a complete
          # match), don't return this one as a success.
          break
        elif e_count is False:
          # We've gone through all the possible exception grammar matches (if
          # any) and none of them were a fit.  Success!
          yield (count, obj)
          break
        elif e_count is None:
	  # We need to catch this here instead of at the toplevel because we
	  # explicitly called the exception grammar with eof=True even though
	  # the main buffer may not be at EOF yet.
          raise InternalError("{} requested more data when at EOF".format(g))
    # In some cases, our "best error" can lead to really confusing messages,
    # since it may say "expected foo" at a place where foo actually WAS found
    # (because the exclusion grammar prevented it from being returned).  If
    # this is the case (we're returning a best error at our own starting
    # position) return ourselves as the error object, so at least it will be
    # obvious there were extra conditions on the match that weren't fulfilled.
    if best_error[0] == index:
      yield error_result(index, cls)
    else:
      yield error_result(*best_error)

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    if not depth:
      depth += 1
    return "("+" - ".join((c.grammar_details(depth-1, visited) for c in cls.grammar))+")"

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    names, nts = util.get_ebnf_names(cls.grammar, opts)
    return ("( "+" - ".join(names)+" )", nts)

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None


def REPEAT(*grammar, **kwargs):
  """
  Match (by default) one-or-more repetitions of *grammar*, one right after another.  If the *min* or *max* keyword parameters are provided, the number of matches can be restricted to a particular range.
  """
  cdict = util.make_classdict(Repetition, grammar, kwargs)
  return GrammarClass("<REPEAT>", (Repetition,), cdict)

class Repetition (Grammar):
  grammar_count = None
  grammar_null_subtoken_ok = False
  grammar_min = 1
  grammar_max = None
  grammar_whitespace = None
  grammar_whitespace_mode = None

  @classmethod
  def __class_init__(cls, attrs):
    if not cls.grammar:
      grammar = EMPTY
    else:
      grammar = GRAMMAR(cls.grammar)
    if cls.grammar_count is not None:
      cls.grammar_min = cls.grammar_count
      cls.grammar_max = cls.grammar_count
    elif not cls.grammar_max:
      cls.grammar_max = sys.maxsize
    cls.grammar = util.RepeatingTuple(grammar, grammar, len=cls.grammar_max)

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    if cls.grammar_min == 0 and cls.grammar_max == 1 and cls.grammar_collapse:
      return "OPTIONAL({})".format(cls.grammar[0].grammar_details(depth, visited))
    params = ""
    if cls.grammar_min == cls.grammar_max:
      params += ", count={}".format(cls.grammar_min)
    else:
      if cls.grammar_min != 1:
        params += ", min={}".format(cls.grammar_min)
      if cls.grammar_max != sys.maxsize:
        params += ", max={}".format(cls.grammar_max)
    if cls.grammar_collapse:
      params += ", collapse=True"
    return "REPEAT({}{})".format(cls.grammar[0].grammar_details(depth, visited), params)

  @classmethod
  def grammar_resolve_refs(cls, refmap={}, recurse=True, follow=False, missing_ok=False, skip=None):
    # The default grammar_resolve_refs process will inadvertently replace our
    # RepeatingTuple with a simple tuple, so we need to convert it back to
    # RepeatingTuple after it's done.
    old_grammar = cls.grammar
    Grammar.grammar_resolve_refs.__func__(cls, refmap, recurse, follow, missing_ok, skip)
    type.__setattr__(cls, 'grammar', util.RepeatingTuple(*cls.grammar, len=old_grammar.len))

  #TODO: implement strict vs non-strict EBNF
  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    names, nts = util.get_ebnf_names((cls.grammar[0],), opts)
    name = names[0]
    if "," in name:
      ename = "( {} )".format(name)
    else:
      ename = name
    if cls.grammar_min == 0 and cls.grammar_max == 1:
      return ("[{}]".format(name), nts)
    if cls.grammar_min == 0:
      descs = []
    elif cls.grammar_min == 1:
      descs = ["{}".format(ename)]
    else:
      descs = ["{} * {}".format(cls.grammar_min, ename)]
    extra = cls.grammar_max - cls.grammar_min
    if cls.grammar_max == sys.maxsize:
      descs.append("{{{}}}".format(name))  # "{%s}"
    elif extra == 1:
      descs.append("[{}]".format(name))
    elif extra:
      descs.append("{} * [{}]".format(extra, name))
    return (", ".join(descs), nts)

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None

def WORD(startchars, restchars=None, fullmatch=False, escapes=False, **kwargs):
  """
  Match any text consisting of a sequence of the specified characters.  If *restchars* is not provided, all characters in the sequence must be in the set specified by *startchars*.  If *restchars* is provided, then *startchars* specifies the valid options for the first character of the sequence, and *restchars* specifies the valid options for all following characters.

  *startchars* and *restchars* are each strings containing a sequence of individual characters, or character ranges, in the same format used by python regular expressions for character-range (``[]``) operations (i.e. ``"0123456789"`` or ``"A-Za-z"``).  If the first character of *startchars* or *restchars* is ``^``, the meaning is also inverted, just as in regular expressions, so ``"^A-Z"`` would match anything *except* an upper-case ascii alphabet character.

  If *fullmatch* is true, then this construct will only match the longest possible sequence of matching characters in the input, and will not try to match any shorter sub-sequences (even if they would work better in the context of the larger grammar).  Effectively, this means any match returned is guaranteed to be followed by a non-word character or token.

  By default, only ``^`` (when at the beginning) and ``-`` (when not at the beginning or end) are interpreted specially.  In particular, backslashes and brackets (``[`` and ``]``) have no special meaning when in *startchars* or *restchars* and will result in the grammar matching a backslash or a bracket in the input (this is different than when specifying character-ranges in regular expressions, where these characters have special meaning).  However, if *escapes* is :const:`True`, backslash-sequences in *startchars* and *restchars* will be treated the same as in Python regular expressions.  In particular, this means you can use ``\\d``, ``\\D``, ``\\s``, ``\\S``, ``\\w``, and ``\\W``, just as in regular expressions (see the documentation for the :mod:`re` module for more information).
  """
  if 'longest' in kwargs:
    util.depwarning("'longest' argument to WORD() is deprecated.  Use 'fullmatch=True' instead.")
    fullmatch = kwargs['longest']
    del kwargs['longest']
  cdict = util.make_classdict(Word, (), kwargs, startchars=startchars, restchars=restchars, fullmatch_only=fullmatch, escapes=escapes)
  return GrammarClass("<WORD>", (Word,), cdict)

class Word (Terminal):
  grammar_whitespace_mode = 'explicit'
  grammar = ()
  startchars = ""
  restchars = None
  fullmatch_only = False
  escapes = False
  grammar_count = None
  grammar_min = 1
  grammar_max = None

  @classmethod
  def __class_init__(cls, attrs):
    if cls.grammar_count is not None:
      cls.grammar_min = cls.grammar_count
      cls.grammar_max = cls.grammar_count
    startchars = cls.startchars
    restchars = cls.restchars
    if not restchars:
      restchars = startchars
    #startchars = re.sub('([\\]\\\\])', '\\\\\\1', startchars)
    #restchars = re.sub('([\\]\\\\])', '\\\\\\1', restchars)
    if cls.escapes:
      startchars = re.sub(r']', r'\\]', startchars)
      restchars = re.sub(r']', r'\\]', restchars)
    else:
      startchars = re.sub(r'([]\\])', r'\\\1', startchars)
      restchars = re.sub(r'([]\\])', r'\\\1', restchars)
    if startchars == '^':
      startchars = r'\^'
    else:
      startchars = "[{}]".format(startchars)
    if restchars == '^':
      restchars = '\\^'
    else:
      restchars = "[{}]".format(restchars)
    max = cls.grammar_max
    if not max:
      regexp = "{}{}*".format(startchars, restchars)
    else:
      regexp = "{}{}{{,{}}}".format(startchars, restchars, max-1)
    if cls.grammar_min < 1:
      regexp = "({})?".format(regexp)
    cls.regexp = re.compile(regexp)
    if "grammar_name" not in attrs:
      if cls.restchars is None:
        argspec = repr(cls.startchars)
      else:
        argspec = "{!r}, {!r}".format(cls.startchars, cls.restchars)
      cls.grammar_name = "WORD({})".format(argspec)
    if "grammar_desc" not in attrs:
      cls.grammar_desc = cls.grammar_name

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    startchars = cls.startchars
    restchars = cls.restchars
    if restchars is None:
      argspec = repr(startchars)
    else:
      argspec = "{!r}, {!r}".format(startchars, restchars)
    min = cls.grammar_min
    max = cls.grammar_max
    if min != 1:
      argspec += ", min={}".format(min)
    if max:
      argspec += ", max={}".format(max)
    if cls.fullmatch_only:
      argspec += ", fullmatch=True"
    if cls.escapes:
      argspec += ", escapes=True"
    return "WORD({})".format(argspec)

  @classmethod
  def grammar_parse(cls, text, index, session):
    greedy = cls.grammar_greedy or cls.fullmatch_only
    returned = cls.grammar_min - 1
    while True:
      string = text.string
      m = cls.regexp.match(string, index)
      if not m:
        yield error_result(index, cls)
      end = m.end()
      matchlen = end - index
      if not greedy:
        while returned < matchlen:
          returned += 1
          yield (returned, cls(string, index, index+returned))
      if end < len(string) or matchlen == cls.grammar_max or text.eof:
        break
      # We need more text before we can be sure we"re at the end.
      text = yield (None, None)
    if greedy:
      while matchlen >= cls.grammar_min:
        yield (matchlen, cls(string, index, index+matchlen))
        if cls.fullmatch_only:
          break
        matchlen -= 1
    yield error_result(index, cls)

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    return (util.ebnf_specialseq(cls, opts), ())

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None

  def __bool__(self):
    return bool(self.string)

def REF(ref_name, module=DEFAULT, default=None):
  """
  Create a reference to a grammar named *ref_name*, to be resolved later.

  This can either be resolved by calling :meth:`~Grammar.grammar_resolve_refs` prior to parsing, or, alternately, :mod:`modgrammar` will automatically attempt to resolve any :func:`REF` whenever it is used in parsing, and will treat it the same as if it were actually an occurrence of the resolved grammar.

  By default, resolving a reference involves searching for a grammar class with the same name in the same python module.  The python module is determined based on the location where the :func:`REF` call occurred.  If you wish to use a different module to look for the grammar this :func:`REF` refers to, it can be provided in the *module* parameter.  If *module* is given as :const:`None`, then no module will be searched.

  If provided, *default* should contain a grammar which will be used if the given reference cannot be resolved.
  """
  if module is DEFAULT:
    # Try to figure out what module we were called from, as that should be what
    # we"ll later look things up relative to...
    module = util.get_calling_module()
  return GrammarClass("<REF>", (Reference,), dict(ref_name=ref_name, ref_base=module, ref_default=default))

class Reference (Grammar):
  ref_name = None
  ref_base = None
  ref_default = None
  grammar_whitespace_mode = 'explicit'
  grammar = ()

  @classmethod
  def __class_init__(cls, attrs):
    cls.grammar_name = "REF({!r})".format(cls.ref_name)

  @classmethod
  def resolve(cls, sessiondata={}):
    o = None
    if sessiondata:
      f = getattr(sessiondata, "grammar_resolve_ref", None)
      if f is not None:
        o = f(cls.ref_name)
      else:
        # Try using .get() first, because exceptions are expensive and this may
        # be being called many times from inside of grammar_parse..
        f = getattr(sessiondata, "get", None)
        if f is not None:
          o = f(cls.ref_name, None)
        else:
          try:
            o = sessiondata[cls.ref_name]
          except (KeyError, TypeError):
            pass
    if o is None:
      o = getattr(cls.ref_base, cls.ref_name, None)
    if o is None:
      o = cls.ref_default
    if o is None:
      raise UnknownReferenceError("Unable to resolve reference to {0.ref_name!r} in {0.ref_base}.".format(cls))
    if not hasattr(o, 'grammar_parse'):
      raise BadReferenceError("Resolving reference to {0.ref_name!r}: Object {1!r} does not appear to be a valid grammar.".format(cls, o))
    return o

  @classmethod
  def grammar_parse(cls, text, index, session):
    debugger = session.debugger
    resolved = cls.resolve(session.data)
    state = resolved.grammar_parse(text, index, session)
    if debugger:
      state = debugger.debug_wrapper(state, resolved, index, text)
    text = yield next(state)
    while True:
      text = yield state.send(text)

  @classmethod
  def grammar_ebnf_lhs(cls, opts):
    try:
      o = cls.resolve()
    except ReferenceError:
      return (util.ebnf_specialseq(cls, opts), ())
    return o.grammar_ebnf_lhs(opts)

  @classmethod
  def grammar_ebnf_rhs(cls, opts):
    return None

###############################################################################
#                                   Extras                                    #
###############################################################################

L = LITERAL
G = GRAMMAR

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def LIST_OF(*grammar, **kwargs):
  """
  Match a list consisting of repetitions of *grammar* separated by *sep*.  As with other repetition grammars, the *min* and *max* keywords can also be used to restrict the number of matches to a certain range.

  .. note::
     Although this is most commonly used with a literal separator (such as the default ``","``), actually any (arbitrarily-complex) subgrammar can be specified for *sep* if desired.
  """
  cdict = util.make_classdict(ListRepetition, grammar, kwargs)
  return GrammarClass("<LIST>", (ListRepetition,), cdict)

class ListRepetition (Repetition):
  sep = LITERAL(",")
  grammar_min = 1
  grammar_whitespace = None
  grammar_whitespace_mode = None

  @classmethod
  def __class_init__(cls, attrs):
    grammar = GRAMMAR(cls.grammar)
    Repetition.__class_init__.__func__(cls, attrs)
    cls.sep = GRAMMAR(cls.sep)
    succ_grammar = GRAMMAR(cls.sep, grammar, whitespace=cls.grammar_whitespace, whitespace_mode=cls.grammar_whitespace_mode, name='<next-list-element>')
    cls.grammar = util.RepeatingTuple(grammar, succ_grammar, len=cls.grammar_max)

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    params = ""
    if cls.grammar_min == cls.grammar_max:
      params += ", count={}".format(cls.grammar_min)
    else:
      if cls.grammar_min != 1:
        params += ", min={}".format(cls.grammar_min)
      if cls.grammar_max != sys.maxsize:
        params += ", max={}".format(cls.grammar_max)
    if cls.grammar_collapse:
      params += ", collapse=True"
    return "LIST_OF({}, sep={}{})".format(cls.grammar[0].grammar_details(depth, visited), cls.sep.grammar_details(depth, visited), params)

  def grammar_postprocess(self, parent, session):
    # Collapse down the succ_grammar instances for successive matches
    elems = []
    for e in self.elements:
      if not elems:
        elems = [e]
      else:
        elems.extend(e.elements)
    self.elements = elems
    return Grammar.grammar_postprocess(self, parent, session)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def OPTIONAL(*grammar, **kwargs):
  """
  Specify that *grammar* is optional.  It will match if present, or it will match the empty string if *grammar* cannot be matched.

  If *grammar* is present in the matched input text, this element of the parse tree will contain a single grammar match object (the same as it would have if ``GRAMMAR(*grammar)`` had matched).  If *grammar* was not found, this element of the parse tree will contain :const:`None`.

  This construct is functionally equivalent to ``OR(grammar, EMPTY)``.  (It is is also functionally similar to ``REPEAT(*grammar, min=0, max=1, collapse=True)``, except that in the case of :func:`REPEAT`, an empty-match produces no elements at all in the resulting parse tree (not even :const:`None`).)
  """
  kwargs.update(min=0, max=1)
  kwargs.setdefault("collapse", True)
  kwargs.setdefault("grammar_name", "<OPTIONAL>")
  kwargs.setdefault("whitespace_mode", 'explicit')
  return REPEAT(*grammar, **kwargs)

def ZERO_OR_MORE(*grammar, **kwargs):
  """
  This is a synonym for ``REPEAT(*grammar, min=0)``
  """
  kwargs.update(min=0, max=None)
  return REPEAT(*grammar, **kwargs)

def ONE_OR_MORE(*grammar, **kwargs):
  """
  This is a synonym for ``REPEAT(*grammar, min=1)``
  """
  kwargs.update(min=1, max=None)
  return REPEAT(*grammar, **kwargs)

def ANY_EXCEPT(charlist, **kwargs):
  """
  Match a string of any characters except those listed in *charlist*.

  This is functionally equivalent to ``WORD("^"+charlist)``.
  """
  kwargs.setdefault("grammar_name", "ANY_EXCEPT({!r})".format(charlist))
  return WORD("^{}".format(charlist), **kwargs)

# FIXME: whitespace at beginning of line
class BOL (Terminal):
  grammar_whitespace_mode = 'explicit'
  grammar_whitespace = None
  grammar = ()
  grammar_desc = "beginning of line"

  @classmethod
  def grammar_parse(cls, text, index, session):
    if index:
      if text.string[index-1] in ("\n", "\r"):
        yield (0, cls(""))
    elif text.bol:
      yield (0, cls(""))
    yield error_result(index, cls)

class EOF (Terminal):
  grammar_whitespace_mode = 'explicit'
  grammar_whitespace = None
  grammar = ()
  grammar_desc = "end of file"
  grammar_noteworthy = False

  @classmethod
  def grammar_parse(cls, text, index, session):
    if text.eof and index == len(text.string):
      yield (0, cls(""))
    yield error_result(index, cls)

class EOI (EOF):
  """
  This "end-of-input" grammar is a special case of EOF only used internally by
  the parser to indicate the failure point when a user requested
  matchtype='complete' but there was more text present.

  EOI is not exported by default, as it is not expected to be used in ordinary
  grammars.
  """

  grammar_desc = "end of input"
  _hash_id = hash(EOF)  # EOI will compare equal to EOF, if necessary

class EOL (Terminal):
  grammar_whitespace_mode = 'explicit'
  grammar_whitespace = None
  grammar_desc = "end of line"
  grammar_collapse_skip = True
  grammar = (L("\n\r") | L("\r\n") | WORD(util.EOL_CHARS, count=1))

class WHITESPACE (Word):
  grammar_desc = "whitespace"
  grammar_noteworthy = False
  regexp = WS_DEFAULT

  @classmethod
  def __class_init__(cls, attrs):
    # Don't do the normal Word __class_init__ stuff.
    pass

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    return cls.grammar_name

class SPACE (WHITESPACE):
  regexp = WS_NOEOL

class REST_OF_LINE (Word):
  grammar_name = "REST_OF_LINE"
  grammar_desc = "rest of the line"
  startchars = "^" + util.EOL_CHARS
  grammar_min = 0

  @classmethod
  def grammar_details(cls, depth=-1, visited=None):
    return cls.grammar_name

###############################################################################

def generate_ebnf(grammar, **opts):
  """
  *(generator function)*

  Take a given grammar and produce a description of the grammar in Extended Backus-Naur Form (EBNF).  This generator produces fully-formatted output lines suitable for writing to a file, etc.

  As there are a few different variants of EBNF in common use, as well as some aspects which could be considered a matter of preference when producing such descriptions, this function also accepts a variety of configurable options, specified as keyword parameters:

    *wrap* (default 80)
      Wrap the output text at *wrap* columns.
    *align* (default True)
      Align each entry so that all of the RHSes start on the same column.
    *indent* (default True)
      The number of characters that subsequent (wrapped) lines should be indented.  Can be set to either a number or to :const:`True`.  If set to :const:`True`, the indent will be auto-calculated to line up with the position of the RHS in the first line.
    *expand_terminals* (default False)
      If grammars have subgrammars, show their expansion even if :attr:`~Grammar.grammar_terminal` is true.
    *special_style* (default "desc")
      How some grammars (which can't be easily represented as EBNF) should be represented inside EBNF "special sequences".  Valid options are "desc" (use the (human-readable) :attr:`~Grammar.grammar_desc` text), "name" (just use the grammar's name), or "python" (use a repr-like syntax similar to the python syntax used to create them).

  Additional options may also be offered by certain individual grammars.
  """
  defaults = dict(expand_terminals=False, special_style="desc", wrap=80, indent=True, align=True)
  defaults.update(opts)
  opts = defaults
  todo = [grammar]
  processed = set()
  results = []
  while todo:
    g = todo.pop(0)
    rhs = g.grammar_ebnf_rhs(opts)
    if rhs:
      processed.add(g)
      desc, nonterminals = rhs
      name, lhs_nt = g.grammar_ebnf_lhs(opts)
      results.append((name, desc))
      for nt in nonterminals:
        if nt not in processed and nt not in todo:
          todo.append(nt)
    elif not processed:
      # We were passed an anonymous grammar of some kind.  Wrap it in something
      # that has a name (and thus an EBNF LHS and RHS) and try again.
      todo.append(GRAMMAR(g, grammar_name="grammar"))
    else:
      processed.add(g)

  width = opts["wrap"]
  if not width:
    width = sys.maxsize
  align_width = 0
  if opts["align"]:
    max_align = width * 0.75 - 2
    for name, desc in results:
      w = len(name)
      if w <= max_align:
        align_width = max(align_width, w)
  indent = opts["indent"]
  if indent is True:
    if align_width:
      indent = align_width + 3
    else:
      indent = 8
  tw = textwrap.TextWrapper(width=width, subsequent_indent=(" " * indent), break_long_words=False, break_on_hyphens=False)
  for name, desc in results:
    yield tw.fill("{0:{1}} = {2};".format(name, align_width, desc))+"\n"
