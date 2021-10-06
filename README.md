# Senpai: A dynamically-typed, Stack-Based Esolang
- For general info about the language, visit the [esolang wiki page](https://esolangs.org/wiki/Senpai)
- This document is about implementation-specific details
## Implementation Features
- An implementation of the Senpai language purely interpreted in Python
- A simple Python API to create functions for the Senpai interpreter
- Many builtins that make the language easier to use that act as wrappers for Python classes
- An Earley parser, created with [Lark](https://github.com/lark-parser/lark)
- A 100x slower than Python run speed (Yeah, I'm sorry)
- Only a single dependency outside of the Python standard library (Lark) that can be installed with `pip install lark`
- A probably slightly buggy interpreter.

## Commandline Usage
- To use, use `python -m senpai_lang [commands]`
### Commands
- `-h`, `--help`: View the help for the commandline arguments
- `-i`, `--infile`: The input file with the Senpai code to interpret
- `-d`, `--debugfile`: The file to write to for verbose logging. The log tracks almost everything the intepreter does down to the expression.
- `-tb`, `--pytraceback`: Disable the custom except hook and enable normal Python traceback. Should be used for reporting bugs with the intepreter.
- `-w`, `--wiki`: Visit the wiki page for the Senpai language
- `-ps`, `--printstack`: Print the execution time, variables, stacks, and builtins of the program after running the file

## Python API
If you want to see the library of functions introduced using this api, read `lib/lib_docs.md`
### Basic Tutorial For Making Your Own Extension Modules
- 1. Import `senpai_lang.pyutils`
- 2. Create a class that inherits off of `senpai_lang.pyutils.FuncBase` with a class attribute of the name of the function
- 3. Create a `__init__` that inits the `super()` with args of `self.name` and the function you want to wrap.
- 4. Instantiate a `PyModule` object with args of `{name}` and the `class` of the command (not an instance of the class)
- 5. Import the module from Senpai
- Example implementation of a wrapper for `os.system`

```py
import os
from senpai_lang.pyutils import FuncBase, PyModule
class System(FuncBase):
	"""
	Can take 2 or 1 argument
	First argument is always the command to execute.
	Second argument can be anything, 
	
	Second argument if it exists returns the value os.system
	"""
	name = 'cmd' # allows for overriding by the module name 
	def __init__(self):
		super().__init__(self.name, self.system)

	@staticmethod
	def system(*args):
		if len(args) == 1:
			os.system(*args)
		else:
			return os.system(args[0])
	
PyModule('os', [System]) # initialize module
```
**NOTE: A function's return value is pushed onto the current stack and all arguments to the function are destroyed in the process of calling the function.**
### Full Python API Docs


### FuncBase 
- `def __init__(self, name, function, iter_results=False)` 
  - `self.name`: The name that the function will be referred to by calling from Senpai
  - `self.function`: The function that gets called from Senpai 
  - If `iter_results` is `True`, when function is called, iterate over the return value of `self.function` and push each item in the iterable on top of stack in reverse order such that the top item on the stack is the first item in the iterable.
  - Updates `SenpaiInterpreter.builtins` with `{self.name: self}`
  - Should probably not be instantiated manually unless you know what you are doing
- `def call(self, args, interpreter)`: 
  
  - Pops the arguments from the top of the `interpreter`'s current stack and calls `self.function` with the unpacked version of `args` as arguments. 
  - Should probably not be called explicitely unless you know exactly what you are doing. 
- `self.interpreter`: the interpreter that is calling the function. Only defined when the function is called.

### PyModule
- `def __init__(self, name, functions, rename_funcs=True)`
  - `self.name`: the name of the module
  - `self.functions`: an iterable of all of the classes for functions in the module
  - `rename_funcs` (`self.rename`): If `True` (should almost always be), add the name of the module followed by an underscore (`module_function`) before the name of all the functions in the module. Should be `True` (or omitted) in almost all cases.
  - Instantiates all of the classes in `self.functions` and adds them to the builtins of the `SenpaiInterpreter` class and logs imports. 

### SenpaiInterpreter
These are the useful attributes for making modules. If you want to know more methods and attributes of the `SenpaiInterpreter`, look at the source code. Most of the methods in there interpret the AST. **`SenpaiInterpreter` objects should generally not be instantiated manually. If you really need to, the `SenpaiInterpreter` class is located in senpai_lang.src.classes.SenpaiInterpreter.** 
- `SenpaiInterpreter.builtins`: All of the Python functions added to the interpreter.
- `self.vars`: The variables held by the interpreter. It is a dictionary that holds `{name: object}`. 
- `self.stacks`: A `StackHolder` object that holds the stacks. 

### StackHolder
A dictionary that holds the `{name: Stack([items])}` that also holds the name of the current stack.
**`StackHolder` objects should generally not be instantiated manually. The `StackHolder` class is located in `senpai_lang.src.classes.StackHolder`** 

- `def __init__(self, current_stack, **kwargs)`:
  - Creates a new `StackHolder` initialized with a current stack name of `current_stack`, and contains the dictionary of `**kwargs`. The dictionary should have values of `Stack` objects. 

- `self.current_stack_name`: The name of the current stack
- `self.current_stack`: A `Stack` object that represents the current stack of the interpreter.
- `def switch_stack(self, name)`: Switches the current stack to be the stack named `name` if it exists. If not, creates a stack named `name` initialized with an empty `Stack()`

### Stack
A class that inherits off of `collections.deque` that represents a stack in the Senpai language. **`Stack` objects should generally not be instantiated manually.**

- `def rot2(self)`: Performs a Senpai `rot2` operation on the stack (swaps the top 2 items).
* `def rot3(self)`: Performs a Senpai `rot3` operation on the stack.

## Embedding the Interpreter in Python Applications (If you *really* want to) (Why would you?)
- 1. Import `senpai_lang.src.classes.SenpaiInterpreter` and `senpai_lang.src.parser.parser`
- 2. Regret all of your life decisions.
- 3. Call `parser.parse(code)` to get the Tree
- 4. Instantiate the `SenpaiInterpreter` with the Tree as an argument
- 5. Enjoy
