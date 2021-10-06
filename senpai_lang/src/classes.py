import decimal
import lark
import operator
from collections import deque
from senpai_lang.src.senpai_import import SenpaiModule, PythonModule
import sys
import logging


class SenpaiInterpreter(lark.visitors.Interpreter):	
	builtins = {}
	def __init__(self, tree, *, python_traceback=False):
		self.id = hex(id(self))
		logging.info(f"Initializing Interpreter at {self.id}")
		if not python_traceback:
			sys.excepthook = self.custom_except_hook
			logging.info(self.format_log(f"Created custom except hook"))

		logging.info(self.format_log(f"Interpreting the following tree:\n {tree.pretty()}"))
		self.tree = tree
		self.vars = {}
		self.stacks = StackHolder('bedroom', **{'bedroom': Stack()})
		self.visit(tree)
	
	def custom_except_hook(self, _type, value, tb):
		print("Sorry senpai, you messed up somewhere UmU", file=sys.stderr)
		
		print(f"{_type.__name__}: {value}", file=sys.stderr, end='\n\n')
		print("The status of stacks before the error occured were:\n", file=sys.stderr)

		for name in self.stacks:
			print(f'\t{name}: ', file=sys.stderr, end='\n\t\t')
			for i, item in enumerate([repr(item) for item in self.stacks[name]]):
				print(i, item, file=sys.stderr,sep='\t', end='\n\t\t')
			print()

		print("\nThe values of all of the variables before the error were:", file=sys.stderr, end='\n\n\t')

		for var in self.vars:
			print(f"{var}:", repr(self.vars[var]), file=sys.stderr, end='\n\t')
		print('\b \b', file=sys.stderr)
		logging.error(f"Exception was raised: {_type.__name__}: {value}")

	def format_log(self, message):
		return f"\n{self.id} - {message}\n"

	def declaration(self, tree):
		return Declaration(tree, self)	
	
	def assignment(self, tree):
		return Assignment(tree, self)

	def stack_op(self, tree):
		op = tree.children[0]
		op_name = op.data

		if op_name == 'push':
			var_name = op.children[0].children[0].value
			logging.info(self.format_log(f"Pushing {var_name!r} onto the current stack"))
			try:
				self.stacks.current_stack.appendleft(self.vars[var_name])
			except KeyError:
				self.stacks.current_stack.appendleft(SenpaiInterpreter.builtins[var_name])
		elif op_name == 'pop':
			logging.info(self.format_log("Popping TOS"))
			self.stacks.current_stack.popleft()
		elif op_name == 'rot2':
			logging.info(self.format_log("Swapping top 2 items on the stack"))
			self.stacks.current_stack.rot2()
		elif op_name == 'rot3':
			logging.info(self.format_log("Swapping top 3 items on the stack"))
			self.stacks.current_stack.rot3()
		elif op_name == 'switch_stack':
			
			stack_name = op.children[0].children[0].value
			logging.info(self.format_log(f"Switching the current stack to {stack_name!r}"))
			self.stacks.switch_stack(stack_name)
		d = {self.stacks.current_stack_name: self.stacks.current_stack}
		logging.info(self.format_log(f"State of current stack: {d}"))
		
	def if_block(self, tree):
		IfBlock(tree, self).run()

	def if_else_block(self, tree):
		IfElseBlock(tree, self).run()
		
	def loop(self, tree):
		Loop(tree, self).run()
	
	def call(self, tree):
		number_args = len(tree.children[0].value) if tree.children else 0
		stack = self.stacks.current_stack

		if (number_args + 1) > len(stack):
			func = self.stacks.current_stack[0]
			raise ValueError(f"Insufficient number of arguments on the stack. Failed to call function {func.name!r}.")

		function = self.stacks.current_stack.popleft()

		d = {self.stacks.current_stack_name: self.stacks.current_stack}

		logging.info(self.format_log(f"Calling function {function} with {number_args} args"))
		logging.info(self.format_log(f"Current stack state before calling function: {d}"))
		if number_args:
			args = [self.stacks.current_stack.popleft() for _ in range(number_args)] 
		else:
			args = []
		function.call(args, self)

		logging.info(self.format_log(f"Current stack state after calling function: {d}"))
	def function_definition(self, tree):
		return SenpaiFunction(tree, self)
	
	def import_statement(self, tree):
		path = tree.children[0].children[0].value.strip('"')
		logging.info(self.format_log(f"Importing module from {path!r}"))
		try:
			module = SenpaiModule.from_path(path)
			self.vars.update(module.run(self.__class__))
			logging.info(self.format_log(f"Import of Senpai module at {path!r} was successful"))

		except lark.exceptions.UnexpectedCharacters:
			try: 
				PythonModule.from_path(path).run(SenpaiInterpreter)
				logging.info(self.format_log(f"Import of Python module at {path!r} was successful"))
			except AttributeError:
				raise ImportError(f"Could not find a module at {path!r}")
	
	def transfer_top(self, tree):
		d = {self.stacks.current_stack_name: self.stacks.current_stack}

		item = self.stacks.current_stack.popleft()
		var_name = tree.children[0].children[0].value

		logging.info(self.format_log(f"Transferring TOS ({item}) to variable {var_name!r}"))
		logging.info(self.format_log(f"Current interpreter's stack status before transfer: {d}"))
		logging.info(self.format_log(f"Current interpreter's var status before transfer: {self.vars}"))

		if var_name not in self.vars:
			raise NameError(f"{var_name!r} is not defined!")
		self.vars[var_name] = item
	
	def delete_var(self, tree):
		var_name = tree.children[0].children[0].value
		logging.info(self.format_log(f"Deleting variable {var_name!r}"))
		logging.info(self.format_log(f"Current interpreter's var status before deletion: {self.vars}"))
		del self.vars[var_name]
		logging.info(self.format_log(f"Current interpreter's var status after deletion: {self.vars}"))
		logging.info(self.format_log(f"Deleted {var_name!r} successfully!"))

class Declaration:
	def __init__(self, tree, interpreter):
		assert len(tree.children) == 1
		self.interpreter = interpreter
		self.var_name = tree.children[0].children[0].value
		logging.info(interpreter.format_log(f"Processing declaration of variable {self.var_name!r} from the following tree:\n {tree.pretty()}"))
		
		if self.var_name in self.interpreter.vars:
			raise NameError(f"{self.var_name!r} is already declared!")

		self.interpreter.vars[self.var_name] = None
		logging.info(interpreter.format_log(f"State of variables: {interpreter.vars!r}"))


class Assignment:
	def __init__(self, tree, interpreter):
		children = tree.children
		self.interpreter = interpreter
		self.var_name = children[0].children[0]

		logging.info(interpreter.format_log(f"Processing assignment of variable {self.var_name.value!r} from the following tree:\n{tree.pretty()}"))

		if self.var_name not in self.interpreter.vars:
			raise NameError(f"{self.var_name!r} is not declared!")
		
		expression_value = Expression(tree.children[1], self.interpreter).parse().value[0]
		
		
		logging.info(interpreter.format_log(f"Assigning {self.var_name.value!r} to {expression_value!r}"))

		self.interpreter.vars[self.var_name] = expression_value

		logging.info(interpreter.format_log(f"Assignment to {self.var_name.value!r} succeeded!"))

class Expression:
	binop_dict = {
				'add': operator.add,
				'sub': operator.sub,
				'mul': operator.mul,
				'div': operator.truediv,
				'bit_or': operator.__or__,
				'xor': operator.xor,
				'bit_and': operator.__and__,
				'equality': operator.eq,
				'less_than': operator.lt,
				'greater_than': operator.gt,
				'greater_than_or_equals': operator.ge,
				'less_than_or_equals': operator.le,
				'logical_or': lambda a, b: a or b,
				'logical_and': lambda a, b: a and b,
				'modulus':  operator.mod,
				'inequality': operator.ne
			}
	unary_dict = {
		'neg': operator.neg,
		'bit_not': operator.__invert__,
		'char_convert': chr
	}
	def __init__(self, tree, interpreter):
		self.value = []
		self.tree = tree
		self.interpreter = interpreter
		logging.info(interpreter.format_log(f"Parsing expression from the following tree \n{tree.pretty()}"))

	@classmethod
	def number(cls, number):
		try: 
			return int(number)
		except ValueError:
			return decimal.Decimal(number)

	def parse(self):
		gen = (child for child in self.tree.children)
		for tree in gen:
			op = tree.data
		
			if op == 'number':
				self.value.append(Expression.number(tree.children[0].value))
			elif op == 'string':
				self.value.append(tree.children[0].value[1:-1])
			elif op == 'name':
				try:
					self.value.append(self.interpreter.vars[tree.children[0].value])
				except KeyError:
					self.value.append(self.interpreter.builtins[tree.children[0].value])
			elif op in Expression.binop_dict:
				self.value.append(Expression.binop_dict[op](*Expression(tree, self.interpreter).parse().value))
			elif op in Expression.unary_dict:
				self.value.append(Expression.unary_dict[op](*Expression(tree, self.interpreter).parse().value,))
		logging.info(self.interpreter.format_log(f"Parsed expression! Returned {self.value[0]}"))
		return self

	def __bool__(self):
		return bool(self.value[0])

class IfBlock:
	def __init__(self, tree, interpreter):
		logging.info(interpreter.format_log(f"Creating conditional from the following tree:\n{tree.pretty()}"))
		self.interpreter = interpreter
		self.truth_value = tree.children[0].data == 'true'
		self.truth_expression = tree.children[1]
		self.body = tree.children[2:]


	def run(self):
		logging.info(self.interpreter.format_log("Parsing if block"))
		if bool(Expression(self.truth_expression, self.interpreter).parse()) == self.truth_value:
			logging.info(self.interpreter.format_log("Truthiness matched"))
			for instruction in self.body:
				self.interpreter.visit(instruction)
		logging.info(self.interpreter.format_log("Finished parsing if block"))

		
class IfElseBlock(IfBlock):

	def run(self):
		logging.info(self.interpreter.format_log("Parsing if else block"))

		if bool(Expression(self.truth_expression, self.interpreter).parse()) == self.truth_value:
			logging.info(self.interpreter.format_log("Truthiness matched!"))
			for instruction in [instruction for instruction in self.body if instruction.data != 'else']:
				self.interpreter.visit(instruction)
		else:
			logging.info(self.interpreter.format_log("Truthiness did not match! Executing other instructions"))
			for instruction in [instruction for instruction in self.body if instruction.data == 'else'][0].children:

				self.interpreter.visit(instruction)
		logging.info(self.interpreter.format_log(f"Finished parsing if else block"))
class Loop(IfBlock):
	def run(self):
		logging.info(self.interpreter.format_log("Parsing loop!"))
		while bool(Expression(self.truth_expression, self.interpreter).parse()) == self.truth_value:
			logging.info(self.interpreter.format_log("Truthiness matched!"))
			for instruction in self.body:# [instruction for instruction in self.body if instruction.data != 'else']:
				self.interpreter.visit(instruction)
			logging.info(self.interpreter.format_log("Looping again"))

class SenpaiBuiltinFunction:
	"""The base class for the Senpai Python function wrapper. Wraps an arbitrary function with position only arguments to be usable in senpai. Pops all items passed in as arguments from the stack. iter_results makes it so that if an iterable that contains results is returned, the results will be put onto the stack in the order they are returned.
	
	You can interact with the stacks of the interpreter by using self.interpreter.stacks, and the current stacks with self.interpreter.stacks.current_stack. 
	
	You can also interact with the variables defined with self.interpreter.vars and all the methods of the lark.visitors.Interpreter class if you want to. Not sure why you would, but you technically can. You can do as much as you want with it. You can even fuck up the AST if you want.
	"""
	def __init__(self, name, function, *,iter_results=False):

		self.name = name
		self.function = function
		self.iter_results = iter_results
		SenpaiInterpreter.builtins[self.name] = self
		# logging.info(f"Current state of builtins: {SenpaiInterpreter.builtins}")
		
	def call(self, args, interpreter):
		# Functions do not have return values. They only put values onto the stack
		logging.info(interpreter.format_log(f"Calling Python function {self.name!r} with arguments of {args}"))
		
		self.interpreter = interpreter
		result = self.function(*args)
		if result is not None: 
			if self.iter_results:
				
				b = [i for i in result][::-1]
				for value in b:
					interpreter.stacks.current_stack.appendleft(value)
			else:
				interpreter.stacks.current_stack.appendleft(result)
	
	def __repr__(self):
		return (f"<Builtin: {self.__class__.__name__}"+'>')

class SenpaiFunction:
	def __init__(self, tree, interpreter):
		logging.info(interpreter.format_log(f"Creating function from the following tree:\n{tree.pretty()}"))

		self.name = tree.children[0].children[0].value
		args_tree = tree.children[1]
		self.interpreter = interpreter
		self.args = [i.children[0].value for i in args_tree.children] if args_tree.data == 'function_args' else None
		self.body = tree.children[2] if self.args else tree.children[1]

		logging.info(interpreter.format_log(f"Adding function with name {self.name!r} to vars"))

		self.interpreter.vars[self.name] = self

		logging.info(interpreter.format_log(f"Current state of vars: {interpreter.vars}"))
		

	def call(self, args, interpreter):
		logging.info(interpreter.format_log(f"Calling Senpai function {self.name!r} with arguments of {args}"))
		if len(args) != len(self.args):
			raise ValueError(f"Expected {len(self.args)} parameters for calling function {self.name!r}")

		logging.info(interpreter.format_log(f"Assigning temporary variables {self.args} to {args}"))
		for i, j in zip(self.args, args):
			interpreter.vars[i] = j
		
		logging.info(interpreter.format_log(f"State of current interpreter's vars: {interpreter.vars}"))
		logging.info(interpreter.format_log(f"Excuting body of function {self.name!r}"))	
		interpreter.visit(self.body)
		logging.info(interpreter.format_log(f"Deleting temporary variables {self.args}"))
		
		for i in self.args:
			del interpreter.vars[i]
		logging.info(interpreter.format_log(f"Function {self.name!r} called successfully"))

class Stack(deque):
	
	def rot2(self):
		self[0], self[1] = self[1], self[0]
	
	def rot3(self):
		self[0], self[1], self[2] = self[2], self[0], self[1]

class StackHolder(dict):
	def __init__(self, current_stack, **kwargs):
		super().__init__(kwargs)
		self.current_stack_name = current_stack
		self.current_stack = self[self.current_stack_name]
		
	def switch_stack(self, name):
		self.current_stack_name = name
		if name in self:
			self.current_stack = self[name]
		else:
			self[name] = Stack()
			self.current_stack = self[name]

	