'''
Copyright (C) 2018 CG Cookie
https://github.com/CGCookie/retopoflow
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import inspect
from ..common.debug import debugger

def get_state(state, substate):
    return '%s__%s' % (str(state), str(substate))

class FSM:
    def _generate_state_decorator(self):
        def gen(fsm_instance):
            class FSM_State:
                def __init__(self, state, substate='main'):
                    self.state = state
                    self.substate = substate
                def __call__(self, fn):
                    self.fn = fn
                    self.fnname = fn.__name__
                    def run(*args, **kwargs):
                        try:
                            return fn(*args, **kwargs)
                        except Exception as e:
                            print('Caught exception in function "%s" ("%s", "%s")' % (
                                self.fnname, self.state, self.substate
                            ))
                            debugger.print_exception()
                            return
                    run.fnname = self.fnname
                    m = get_state(self.state, self.substate)
                    #run.fsmstate = m
                    fsm_instance._fsm_states[m] = self.fn
                    return run
            return FSM_State
        return gen(self)

    def __init__(self, default_state='main'):
        self._state_default = default_state
        self._state = None
        self._state_next = default_state
        self._fsm_states = {}
        self._args = []
        self._kwargs = {}
        self.FSM_State = self._generate_state_decorator()
        #for (m,fn) in self._find_fns('fsmstate'):
        #    assert m not in self._fsm_states, 'Duplicate states registered!'
        #    self._fsm_states[m] = fn

    def set_call_args(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    @property
    def state(self):
        return self._state

    # def _find_fns(self, key):
    #     #c = type(self)
    #     c = self.FSM_State
    #     objs = [getattr(c,k) for k in dir(c)]
    #     fns = [fn for fn in objs if inspect.isfunction(fn)]
    #     return [(getattr(fn,key),fn) for fn in fns if hasattr(fn,key)]

    def _call(self, state, substate='main', fail_if_not_exist=False):
        s = get_state(state, substate)
        if s not in self._fsm_states:
            assert not fail_if_not_exist
            return
        try:
            return self._fsm_states[s](*self._args, **self._kwargs)
        except Exception as e:
            print('Caught exception in state ("%s")' % (s))
            debugger.print_exception()
            return

    def reset(self, state=None, call_enter=True):
        if state is None: state = self._state_default
        self._state = state
        self._state_next = None
        if call_enter: self._call(self._state, substate='enter')

    def can_change(self, state):
        if self._state == state: return True
        if self._call(self._state, substate='can exit') == False:
            print('Cannot exit %s to %s' % (str(self._state), str(state)))
            return False
        if self._call(state, substate='can enter') == False:
            print('Cannot enter %s from %s' % (str(state), str(self._state)))
            return False
        return True

    def change(self, state):
        self._state_next = None
        if self._state == state: return True
        if not self.can_change(state): return False
        print('State change: %s -> %s' % (str(self._state), str(state)))
        self._call(self._state, substate='exit')
        self._state = state
        self._call(self._state, substate='enter')
        return True

    def update(self):
        if self._state_next is not None:
            self.change(self._state_next)
        self._state_next = self._call(self._state, fail_if_not_exist=True)


