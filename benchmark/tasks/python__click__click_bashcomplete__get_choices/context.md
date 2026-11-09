# Context for the function to implement

- **Language:** python
- **File:** `click/_bashcomplete.py`

## Imports / includes available in this file

```
import copy
import os
import re
from .utils import echo
from .parser import split_arg_string
from .core import MultiCommand, Option, Argument
from .types import Choice
```

## Other functions defined in the same file (signatures only; you may call them)

```
add_subcommand_completions( ctx , incomplete , completions_out )
bashcomplete( cli , prog_name , complete_var , complete_instr )
do_complete( cli , prog_name , include_descriptions )
get_completion_script( prog_name , complete_var , shell )
get_user_autocompletions( ctx , args , incomplete , cmd_param )
get_visible_commands_starting_with( ctx , starts_with )
is_incomplete_argument( current_params , cmd_param )
is_incomplete_option( all_args , cmd_param )
resolve_ctx( cli , prog_name , args )
start_of_option( param_str )
```
