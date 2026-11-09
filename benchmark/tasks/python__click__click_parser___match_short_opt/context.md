# Context for the function to implement

- **Language:** python
- **File:** `click/parser.py`
- **Enclosing scope:** `class OptionParser(object)`

## Imports / includes available in this file

```
import re
from collections import deque
from .exceptions import UsageError, NoSuchOption, BadOptionUsage, \
```

## Other functions defined in the same file (signatures only; you may call them)

```
_error_opt_args( nargs , opt )
_match_long_opt( self , opt , explicit_value , state )
_process_args_for_args( self , state )
_process_args_for_options( self , state )
_process_opts( self , arg , state )
_unpack_args( args , nargs_spec )
_unpack_args._fetch( c )
add_argument( self , dest , nargs = 1 , obj = None )
add_option( self , opts , dest , action = None , nargs = 1 , const = None , obj = None )
normalize_opt( opt , ctx )
parse_args( self , args )
process( self , value , state )
split_arg_string( string )
split_opt( opt )
takes_value( self )
```


## Other definitions in `click/parser.py` and `click/exceptions.py` (you may rely on them)

```
def _error_opt_args(nargs, opt):
    if nargs == 1:
        raise BadOptionUsage(opt, '%s option requires an argument' % opt)
    raise BadOptionUsage(opt, '%s option requires %d arguments' % (opt, nargs))


def normalize_opt(opt, ctx):
    if ctx is None or ctx.token_normalize_func is None:
        return opt
    prefix, opt = split_opt(opt)
    return prefix + ctx.token_normalize_func(opt)


class Option(object):
    # one registered parser option
    def __init__(self, opts, dest, action=None, nargs=1, const=None, obj=None):
        ...
        self.dest = dest
        self.action = action      # 'store', 'store_const', 'append', 'append_const' or 'count'
        self.nargs = nargs
        self.const = const
        self.obj = obj

    @property
    def takes_value(self):
        return self.action in ('store', 'append')

    def process(self, value, state):
        """Records `value` (or the option's constant / count) in state.opts
        according to the action and appends self.obj to state.order."""


class ParsingState(object):
    def __init__(self, rargs):
        self.opts = {}       # dest -> value
        self.largs = []      # leftover positional/unprocessed args
        self.rargs = rargs   # remaining args still to be processed (a list)
        self.order = []


class OptionParser(object):
    def __init__(self, ctx=None):
        self.ctx = ctx                      # click.Context or None
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False  # copied from ctx when ctx is given
        ...
        self._short_opt = {}   # registered one-character option string (e.g. '-f') -> Option
        self._long_opt = {}    # every other registered option string (e.g. '--foo', '-foo') -> Option
        self._opt_prefixes = set(['-', '--'])


class NoSuchOption(UsageError):
    def __init__(self, option_name, message=None, possibilities=None, ctx=None):
        # default message: 'no such option: <option_name>'
        ...

class BadOptionUsage(UsageError):
    def __init__(self, option_name, message, ctx=None): ...
```
