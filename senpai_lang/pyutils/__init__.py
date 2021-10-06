import logging
from senpai_lang.src.classes import SenpaiBuiltinFunction, SenpaiInterpreter
logger = logging.getLogger()


FuncBase = SenpaiBuiltinFunction

class PyModule:
	def __init__(self, name, functions, *, rename_funcs=True):
		logger.info(f"Importing Python module {name!r}")
		self.name = name
		self.functions = functions
		self.rename = rename_funcs
		if self.rename:
			
			for func in self.functions:
				func.name = f'{self.name}_{func.name}'
		logger.info(f"Adding functions {[i.name for i in self.functions]}")
		for func in self.functions:
			func()
		logger.info(f"Imported {self.name!r} successfully")
		logger.info(f"State of builtins: {SenpaiInterpreter.builtins}")