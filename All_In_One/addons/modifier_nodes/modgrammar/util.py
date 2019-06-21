# vi:et:ts=2:sw=2

import re
import traceback
import sys
import warnings

import modgrammar

PARSEERROR_FOUNDTXT_LEN = 16

EOL_CHARS = '\r\n\f\v\u0085\u2028\u2029'
EOL_RE = re.compile('\r\n|\n\r|[' + EOL_CHARS + ']')

def update_best_error(current_best, err):
  if not current_best:
    return err
  errpos = err[0]
  bestpos = current_best[0]
  if errpos > bestpos:
    return err
  if errpos == bestpos:
    current_best[1].update(err[1])
  return current_best

def best_error_result(err_list):
  if len(err_list) == 1:
    # This will be by far the most common case, so check it first.
    err = err_list[0]
  else:
    pos = max((x[0] for x in err_list))
    nodes = set().union(*(x[1] for x in err_list if x[0] == pos))
    err = (pos, nodes)
  return (False, err)

def error_result(index, node):
  if not isinstance(node, set):
    node = set([node])
  return (False, (index, node))

def regularize(grammar):
  if hasattr(grammar, 'grammar_parse'):
    return (grammar,)
  if isinstance(grammar, str):
    return (modgrammar.LITERAL(grammar),)
  if grammar is None:
    return (modgrammar.EMPTY,)
  try:
    result = []
    for g in grammar:
      result.extend(regularize(g))
    return tuple(result)
  except TypeError:
    raise modgrammar.GrammarDefError("object of type '%s' cannot be converted to Grammar" % (type(grammar).__name__,))

_anongrammar_attrs = ('grammar_collapse', 'grammar_desc', 'grammar_name', 'grammar_whitespace', 'grammar_whitespace_mode', 'grammar_tags')

def is_simple_anongrammar(cls):
  if not issubclass(cls, AnonGrammar):
    return False
  for attr in _anongrammar_attrs:
    if getattr(cls, attr) != getattr(AnonGrammar, attr):
      return False
  return True

def add_grammar(one, two):
  one = regularize(one)
  two = regularize(two)
  if len(one) == 1 and is_simple_anongrammar(one[0]):
    one = one[0].grammar
  if len(two) == 1 and is_simple_anongrammar(two[0]):
    two = two[0].grammar
  return modgrammar.GRAMMAR(*(one + two))

classdict_map = dict(
    count='grammar_count',
    min='grammar_min',
    max='grammar_max',
    collapse='grammar_collapse',
    collapse_skip='grammar_collapse_skip',
    tags='grammar_tags',
    greedy='grammar_greedy',
    whitespace='grammar_whitespace',
    whitespace_mode='grammar_whitespace_mode',
    name='grammar_name',
    desc='grammar_desc',
    noteworthy='grammar_noteworthy',
    terminal='grammar_terminal',
    error_override='grammar_error_override',
)

def make_classdict(base, grammar, kwargs, **defaults):
  cdict = {}
  for d in defaults, kwargs:
    for key, value in d.items():
      key = classdict_map.get(key, key)
      cdict[key] = value
  cdict['grammar'] = grammar
  if not "grammar_whitespace" in cdict and base.grammar_whitespace is None:
    mod = get_calling_module()
    whitespace = getattr(mod, "grammar_whitespace", modgrammar.grammar_whitespace)
    cdict["grammar_whitespace"] = whitespace
  if not "grammar_whitespace_mode" in cdict and base.grammar_whitespace_mode is None:
    mod = get_calling_module()
    whitespace_mode = getattr(mod, "grammar_whitespace_mode", modgrammar.grammar_whitespace_mode)
    cdict["grammar_whitespace_mode"] = whitespace_mode
  return cdict

def calc_line_col(string, count, line=0, col=0, tabs=1):
  pos = 0
  while True:
    m = EOL_RE.search(string, pos, count)
    if not m:
      break
    pos = m.end()
    line += 1
    col = 0
  if tabs != 1:
    lastline = (" " * col) + string[pos:count]
    lastline = lastline.expandtabs(tabs)
    col = len(lastline)
  else:
    col += count - pos
  return (line, col)

def get_calling_module(stack=None):
  return get_calling_modinfo(stack)[2]

def get_calling_stacklevel(stack=None):
  return get_calling_modinfo(stack)[0]

def get_calling_modinfo(stack=None):
  if stack is None:
    stack = traceback.extract_stack(None)
  stacklevel = -2
  for s in reversed(stack):
    stacklevel += 1
    filename = s[0]
    if filename == "<stdin>":
      return (stacklevel, s, sys.modules["__main__"])
    elif filename == __file__ or filename == modgrammar.__file__:
      continue
    else:
      for m in sys.modules.values():
        if getattr(m, "__file__", None) == filename:
          return (stacklevel, s, m)
  # For some reason, we weren't able to determine the module.  Not much we
  # can do here..
  return (None, None, modgrammar)

class RepeatingTuple (tuple):
  def __new__(cls, first_item, successive_items, len=None):
    o = tuple.__new__(cls, [first_item, successive_items])
    o.len = len
    return o

  def __getitem__(self, index):
    if self.len is not None and index >= self.len:
      raise IndexError('tuple index out of range')
    if index == 0:
      return tuple.__getitem__(self, 0)
    else:
      return tuple.__getitem__(self, 1)

  def __len__(self):
    return self.len

def get_ebnf_names(glist, opts):
  names = []
  nts = []
  for g in glist:
    if g not in nts:
      nts.append(g)
    name, ntlist = g.grammar_ebnf_lhs(opts)
    names.append(name)
    for nt in ntlist:
      if nt not in nts:
        nts.append(nt)
  return (names, nts)

def ebnf_specialseq(grammar, opts, name=None, details=None, desc=None):
  style = opts['special_style']
  if style == 'python':
    text = details or grammar.grammar_details()
  elif style == 'name':
    text = name or grammar.grammar_name
  else:
    text = desc or getattr(grammar, 'grammar_desc', None)
    if not text:
      text = name or grammar.grammar_name
  return '? {} ?'.format(text)

def find_match_func(elem, type_or_tag):
  try:
    if isinstance(elem, type_or_tag):
      return True
  except TypeError:
    pass
  return type_or_tag in getattr(elem, "grammar_tags", ())

def get_found_txt(buf, pos):
  end = min(len(buf), pos + PARSEERROR_FOUNDTXT_LEN)
  if end == pos:
    return "(end of input)"
  try:
    end = min(end, buf.index('\n', pos))
  except ValueError:
    pass
  try:
    end = min(end, buf.index('\r', pos))
  except ValueError:
    pass
  found_txt = buf[pos:end]
  if found_txt:
    return repr(found_txt)
  else:
    return "(end of line)"

depwarnings_issued = set()

def depwarning(msg, stacklevel=2, module=None):
  if module == modgrammar:
    return
  winfo = (module, msg)
  if not winfo in depwarnings_issued:
    depwarnings_issued.add(winfo)
    warnings.warn("modgrammar: " + msg, DeprecationWarning, stacklevel=stacklevel+1)
