from senpai_lang.pyutils import FuncBase, PyModule
from collections import deque

class SenpaiList(deque):
	def __repr__(self):
		# hide the name deque from users so they don't get scared
		return repr(list(self))

class NewList(FuncBase):
	name = "new"
	def __init__(self):
		super().__init__(self.name, self.new_list)
	
	@staticmethod
	def new_list(*args):
		return SenpaiList(args)

class InsertEnd(FuncBase):
	name = "insert_back"

	def __init__(self):
		super().__init__(self.name, self.insert_end)

	@staticmethod
	def insert_end(value, li):
		li.append(value)
		return li

class InsertBegin(FuncBase):
	name = "insert_front"

	def __init__(self):
		super().__init__(self.name, self.insert_front)

	@staticmethod
	def insert_front(value, li):
		li.appendleft(value)
		return li


# General container stuff
class GetItem(FuncBase):
	name = "get"
	def __init__(self):
		super().__init__(self.name, self.get_item, iter_results=True)

	@staticmethod
	def get_item(index, container):
		return container.__getitem__(index), container

class SetItem(FuncBase):
	name = "set"
	def __init__(self):
		super().__init__(self.name, self.set_item, iter_results=True)

	@staticmethod
	def set_item(obj, index, container):
		return container.__setitem__(index, obj), container

class DeleteItem(FuncBase):
	name = "del"
	def __init__(self):
		super().__init__(self.name, self.del_item, iter_results=True)

	@staticmethod
	def del_item(index, container):
		container.__delitem__(index)
		return container

class Unpack(FuncBase):
	name = "unpack"
	def __init__(self):
		super().__init__(self.name, lambda container: container, iter_results=True)
		
PyModule('list', [NewList, InsertEnd, InsertBegin], rename_funcs=True)
PyModule('container', [GetItem, SetItem, DeleteItem, Unpack], rename_funcs=True)

