"""
Extensions of interpreter's stack manipulation through functions. Allows creation and deletion of stacks with names that are determined by variables. Useful to use with list module, as the Stack class and the SenpaiList class both inherit off of collections.deque
"""
from senpai_lang.pyutils import FuncBase, PyModule

class CurrentStack(FuncBase):
	"""Returns a reference to the current stack. Things can get weird..."""
	name = "cur"
	def __init__(self):
		super().__init__(self.name, self.current_stack)

	def current_stack(self):
		return self.interpreter.stacks.current_stack

class GetStack(FuncBase):
	"""Returns a reference to the stack with that name. All changes to that stack will be reflected in the stack returned and vice versa."""
	name = "get"
	def __init__(self):
		super().__init__(self.name, self.get_stack)

	def get_stack(self, name):
		return self.interpreter.stacks[name]

class SwitchStack(FuncBase):
	"""Switch the current stack to a stack with that name. Creates an empty stack if the name does not exist. Essentially the same thing as the builtin instruction, but it can take any hashable object as the key and allows the creation of stacks with undetermined names"""
	name = "switch"
	def __init__(self):
		super().__init__(self.name, self.switch_stack)

	def switch_stack(self, name):
		self.interpreter.stacks.switch_stack(name)

class DeleteStack(FuncBase):
	"""Deletes a stack with a given name"""
	name = "del"
	def __init__(self):
		super().__init__(self.name, self.del_stack)

	def del_stack(self, name):
		del self.interpreter.stacks[name]

PyModule('stack', [CurrentStack, GetStack, SwitchStack, DeleteStack])
	
