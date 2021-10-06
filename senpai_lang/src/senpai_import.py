import importlib.util
import os
from senpai_lang.src.parser import parser
import logging
import pathlib
logger = logging.getLogger()

class SenpaiModule:
	"""The base class that imports a Senpai module. Imports from the relative or absolute file path."""
	lib_path = pathlib.Path(os.path.split(os.path.realpath(__file__))[0]).parent / 'lib'

	def __init__(self, code):
		self.code = code
		
	def run(self, interpreter_class):
		
		interpreter = interpreter_class(parser.parse(self.code), python_traceback=True)
		return interpreter.vars

	@classmethod
	def from_path(cls, path):
		logger.info(f"Trying to import senpai module from {path!r}")
		path = path.replace('%lib%', str(cls.lib_path))
		with open(path, "r") as f:
			code = f.read()
		module = cls(code)
		name = os.path.splitext(os.path.basename(path))[0]
		module.name = name
		return module
	
class PythonModule:
	"""The base class that imports a Senpai Python module to be accessable from the Senpai Interpreter. Imports from the relative or absolute file path."""

	lib_path = pathlib.Path(os.path.split(os.path.realpath(__file__))[0]).parent / 'lib'

	def __init__(self, module, spec, name):
		self.module = module
		self.spec = spec
		self.name = name
	
	@classmethod
	def from_path(cls, path):
		path = path.replace('%lib%', str(cls.lib_path))
		spec = importlib.util.spec_from_file_location('', path)
		module = importlib.util.module_from_spec(spec)
		return PythonModule(module, spec, 'module')

	def run(self, interpreter_class):
		self.spec.loader.exec_module(self.module)
		


