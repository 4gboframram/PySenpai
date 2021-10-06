from senpai_lang.pyutils import FuncBase, PyModule
import os
class Love(FuncBase):
    """Wrapper for python's print() function"""
    name = 'love'
    def __init__(self):
        super().__init__(self.name, print)
    
class Reason(FuncBase):
    """Wrapper for python input() function"""
    name = 'reason'
    def __init__(self):
        super().__init__(self.name, input)

class PrintStack(FuncBase):
    """Prints the current stack. Meant for debugging."""
    name = 'stack'
    def __init__(self):
        super().__init__(self.name, self.print_stack)

    def print_stack(self):
        print(self.interpreter.stacks.current_stack)

class Crash(FuncBase):
    """
    Exits the underlying python process. Wraps python exit() function
    """
    name = 'crash'
    def __init__(self):
        super().__init__(self.name, os._exit)
# You can manipulate the stacks of the interpreter with self.interpreter.stacks 
# or even the vars with self.interpreter.vars
        
PyModule("__builtins__", [Love, Reason, PrintStack, Crash], rename_funcs=False)