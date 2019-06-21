# vi:et:ts=2:sw=2

import logging
import io
import modgrammar

__doc__ = """
The :mod:`modgrammar.debugging` module contains classes and constants used for debugging :mod:`modgrammar` grammars, and in some cases the parser itself.
"""

DEBUG_NONE       = 0

DEBUG_TRY        = 0x00000001
DEBUG_RETRY      = 0x00000002
DEBUG_FAILURES   = 0x00000004
DEBUG_SUCCESSES  = 0x00000008
DEBUG_PARTIALS   = 0x00000010
DEBUG_WHITESPACE = 0x00000020
DEBUG_ALL        = 0x0000ffff

DEBUG_TERMINALS  = 0x00010000
DEBUG_OR         = 0x00020000
DEBUG_FULL       = 0xffff0000

DEBUG_DEFAULT = DEBUG_FAILURES | DEBUG_SUCCESSES | DEBUG_PARTIALS | DEBUG_WHITESPACE

def _noop(*args, **kwargs):
  pass

class StreamLogger:
  """
  This is a fake logger-like object which will just write all output to a file
  stream instead of using the main logging system.  It's used by
  GrammarDebugger if it's passed an open file instead of using the logging
  subsystem.
  """

  def __init__(self, output):
    self.output = output

  def log(self, msg, *args, **kwargs):
    self.output.write("-- {0}\n".format(msg))
    getattr(self.output, 'flush', _noop)()

  debug = log
  info = log
  warning = log
  error = log
  critical = log

class GrammarDebugger:
  """
  GrammarDebugger objects are able to hook into the :mod:`modgrammar` parsing logic to inspect the parsing process as it progresses, perform validation checks, and output debugging information.  They are normally created automatically based on the *debug* parameter provided to the :meth:`~modgrammar.Grammar.parser` method when creating a new :class:`~modgrammar.GrammarParser`.

  For advanced users, it is possible to create your own subclass of :class:`~modgrammar.debugging.GrammarDebugger` and pass that to :meth:`~modgrammar.Grammar.parser` in order to perform customized debugging functions.
  """

  def __init__(self, output=True, flags=DEBUG_DEFAULT):
    """
    Initialize the GrammarDebugger.  *output* and *flags* correspond to the *debug* and *debug_flags* passed to :meth:`~modgrammar.Grammar.parser`.

    While not strictly required, it is strongly recommended if you override this method that you call ``GrammarDebugger.__init__(self, output, flags)`` from your own :meth:`__init__` method.  This will make sure that all of the standard attributes are configured properly.
    """
    if flags is None:
      flags = DEBUG_DEFAULT
    if output is True:
      self.logger = logging.getLogger('modgrammar')
    elif isinstance(output, str):
      self.logger = logging.getLogger(output)
    elif isinstance(output, io.IOBase):
      self.logger = StreamLogger(output)
    else:
      self.logger = output
    self.show_try = bool(flags & DEBUG_TRY)
    self.show_retry = bool(flags & DEBUG_RETRY)
    self.show_failures = bool(flags & DEBUG_FAILURES)
    self.show_successes = bool(flags & DEBUG_SUCCESSES)
    self.show_partials = bool(flags & DEBUG_PARTIALS)
    self.show_whitespace = bool(flags & DEBUG_WHITESPACE)
    self.debug_terminals = bool(flags & DEBUG_TERMINALS)
    self.show_or = bool(flags & DEBUG_OR)
    self.in_terminal = 0
    self.stack = [[None, None, None, []]]
    self.seen = set()

  def debug_wrapper(self, parser_generator, grammar, pos, text):
    """
    This is the main method called by the parser to hook into the debugger.  *parser_generator* is the generator object which was obtained by calling *grammar*'s :meth:`~modgrammar.Grammar.grammar_parse` method.  The :meth:`debug_wrapper` method is expected to wrap that generator and return a new generator to be used instead during parsing.

    The default implementation maintains the :attr:`stack`, :attr:`seen` and :attr:`in_terminal` attributes automatically, checks all ``yield``\ ed results by calling :meth:`check_result`, and then calls the various :meth:`match_*` methods, as appropriate.
    """

    gid = id(grammar)
    gp = (grammar, pos)
    gidp = (gid, pos)
    firstpass = True
    failure_returned = False
    t = None
    try:
      while True:
        if firstpass:
          substack = [gidp, grammar, None, []]
          self.match_try(grammar, pos, text, substack)
        else:
          prevstack = self.stack[-1][3]
          for i in range(len(prevstack)):
            if prevstack[i][0] == gidp:
              del prevstack[i:]
              break
          self.match_retry(grammar, pos, text, substack)
        self.stack.append(substack)
        # We use id(grammar) for the following because the usual equality-test
        # could produce false-positives (and is a lot slower, and has
        # side-effects (since it involves calculating the hash value for the
        # grammar tree))
        if gidp in self.seen:
          self.error_left_recursion(self.stack)
        self.seen.add(gidp)
        if grammar.grammar_terminal:
          self.in_terminal += 1

        result = parser_generator.send(t)
        offset, obj = self.check_result(grammar, pos, text, result)

        if grammar.grammar_terminal:
          self.in_terminal -= 1
        self.seen.remove(gidp)
        substack = self.stack.pop()
        if offset is False:
          failure_returned = True
          self.match_failed(grammar, pos, text, substack)
        elif offset is None:
          matched = text.string[pos:]
          self.match_partial(grammar, pos, text, substack, matched)
          self.stack[-1][3].append(substack)
        elif isinstance(offset, int):
          matched = text.string[pos:pos+offset]
          self.match_success(grammar, pos, text, substack, matched)
          substack[2] = matched
          self.stack[-1][3].append(substack)

        t = yield (offset, obj)

        if failure_returned:
          raise modgrammar.InternalError("{!r} called {!r} again after previous failure result.".format(self.stack[-1][1], grammar))
        if t is not None:
          text = t
        firstpass = False

    except StopIteration:
      pass
    raise modgrammar.InternalError("{!r} completed parse loop without returning a failure result".format(grammar))

  def ws_skipped(self, grammar, pos, text, offset):
    """
    Called by the parser when whitespace has been automatically skipped between subgrammars (when :attr:`~modgrammar.Grammar.grammar_whitespace_mode` is :const:`'optional'` or :const:`'required'`).
    """

    if self.show_whitespace:
      matched = text.string[pos:pos+offset]
      self.event("Skipped whitespace {!r}".format(matched), pos, grammar)

  def ws_not_found(self, grammar, pos, text):
    """
    Called by the parser when whitespace between subgrammars was required (because :attr:`~modgrammar.Grammar.grammar_whitespace_mode` is :const:`'required'`), but the required whitespace was not found.
    """

    if self.show_whitespace:
      self.event("Required whitespace not found", pos, grammar)

  def check_result(self, grammar, pos, text, result):
    """
    Called by :meth:`debug_wrapper` after every iteration of the parser function to validate that the result it returned was reasonable.

    (The default version of this method performs a number of special sanity checks which are not normally performed for performance reasons, because they should theoretically never happen.)
    """

    if not isinstance(result, tuple):
      raise modgrammar.InternalError("{!r} returned a grammar_parse result which was not a tuple: {!r}".format(grammar, result))
    elif len(result) != 2:
      raise modgrammar.InternalError("{!r} returned a grammar_parse tuple with the wrong length: {!r}".format(grammar, result))
    offset, obj = result
    if offset is False:
      if not isinstance(obj, tuple):
        raise modgrammar.InternalError("{!r} returned a match failure, but the best-match info is not a tuple: {!r}".format(grammar, obj))
      if len(obj) != 2:
        raise modgrammar.InternalError("{!r} returned a match failure, but the best-match info has the wrong length: {!r}".format(grammar, obj))
      if not isinstance(obj[0], int):
        raise modgrammar.InternalError("{!r} returned a match failure, but the best-match index is not an int: {!r}".format(grammar, obj[0]))
      if not isinstance(obj[1], set):
        raise modgrammar.InternalError("{!r} returned a match failure, but the best-match grammars is not a set: {!r}".format(grammar, obj[1]))
      if not obj[1]:
        raise modgrammar.InternalError("{!r} returned a match failure, but the best-match grammars is empty!".format(grammar))
      for g in obj[1]:
        if not isinstance(g, modgrammar.GrammarClass):
          raise modgrammar.InternalError("{!r} returned a match failure, but the best-match grammars contains something that is not a Grammar class: {!r}".format(grammar, g))
    elif offset is None:
      if text.eof:
        raise modgrammar.InternalError("{!r} requested more data when at EOF!".format(grammar))
      if obj is not None:
        self.logger.warn("{!r} returned None offset with non-None object!".format(grammar))
    elif isinstance(offset, int):
      if offset < 0 or pos+offset > len(text.string):
        raise modgrammar.InternalError("{!r} returned an invalid offset (pos={}, len={}): {!r}".format(grammar, pos, len(text.string), offset))
      if not isinstance(obj, modgrammar.Grammar):
        self.logger.warn("{!r} returned success, but the match object is not an instance of Grammar!: {!r}".format(grammar, (offset, obj)))
    else:
      raise modgrammar.InternalError("{!r} returned invalid type for offset: {!r}".format(grammar, (offset, obj)))
    return result

  def error_left_recursion(self, stack):
    """
    Called by :meth:`debug_wrapper` when left-recursion has been detected.

    The default implementation will construct an appropriately descriptive error message based on the current stack, and then raise a :exc:`~modgrammar.GrammarDefError`.
    """

    gidp = stack[-1][0]
    loop = [str(stack[-1][1])]
    for s in reversed(stack[:-1]):
      loop.append(str(s[1]))
      if s[0] == gidp:
        break
    loop_desc = ' --> '.join(reversed(loop))
    raise modgrammar.GrammarDefError("Left-recursion detected: {}".format(loop_desc))

  def match_try(self, grammar, pos, text, substack):
    """
    Called by :meth:`debug_wrapper` before trying to match a grammar (at a particular position) for the first time.
    """

    if self.show_try:
      self.event("Trying {}".format(grammar), pos, grammar)

  def match_retry(self, grammar, pos, text, substack):
    """
    Called by :meth:`debug_wrapper` before re-entering a grammar (at a particular position) to look for additional matches because a previously successful match did not work for the larger grammar.
    """

    if self.show_retry:
      self.event("Retrying {}".format(grammar), pos, grammar)

  def match_failed(self, grammar, pos, text, substack):
    """
    Called by :meth:`debug_wrapper` after a grammar returns a match-failure result.
    """

    if self.show_failures:
      if substack[2] is None:
        self.event("Failed to match {}".format(grammar), pos, grammar)
      else:
        self.event("No more matches for {}".format(grammar), pos, grammar)

  def match_partial(self, grammar, pos, text, substack, matched):
    """
    Called by :meth:`debug_wrapper` after a grammar returns a partial-match result (it needs more input or EOF to determine whether it has a match or not).
    """

    if self.show_partials:
      self.event("Partial match {}:{!r} (need more input or EOF)".format(grammar, matched), pos, grammar)

  def match_success(self, grammar, pos, text, substack, matched):
    """
    Called by :meth:`debug_wrapper` after a successful match is returned.
    """

    if self.show_successes:
      self.event("Matched {}:{!r}".format(grammar, matched), pos, grammar)

  def stack_summary(self, stack=None):
    """
    Accepts a stack (in the format of :attr:`stack`) and returns a string summary of the current state to display to the user.

    If *stack* is not provided, defaults to using the current contents of the :attr:`stack` attribute.
    """

    if stack is None:
      stack = self.stack
    if stack[0][0] is None:
      stack = stack[1:]
    if not stack:
      return '(toplevel)'
    formatted = []
    for s in stack:
      if not self.show_or and issubclass(s[1], modgrammar.OR_Operator):
        continue
      stackstr = str(s[1])
      if s[3]:
        f = []
        for m in s[3]:
          f.append(repr(m[2]))
        stackstr += "[{}]".format(' '.join(f))
      formatted.append(stackstr)
    return ':'.join(formatted)

  def event(self, msg, pos=None, grammar=None):
    """
    Output a debugging "event".  This is called by the default implementations of the :meth:`match_*` methods to actually output all debugging information.

    The default implementation checks :attr:`in_terminal` and the grammar type against :attr:`debug_terminals` and :attr:`show_or` to determine whether to display the event, and then calls :attr:`logger`'s :meth:`~logging.Logger.debug` method to output the message, along with a :meth:`stack_summary`.
    """

    if self.in_terminal and not self.debug_terminals:
      return
    if grammar and not self.show_or and issubclass(grammar, modgrammar.OR_Operator):
      return
    if pos is not None:
      msg = "{} at {}".format(msg, pos)
    self.logger.debug("{}  ## {}".format(self.stack_summary(self.stack), msg))
