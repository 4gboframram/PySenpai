from senpai_lang.pyutils import FuncBase, PyModule
from pathlib import Path

class OpenFile(FuncBase):
	name = 'open'
	def __init__(self):
		super().__init__(self.name, self.file_setup)

	@staticmethod
	def file_setup(path):
		file = Path(path)
		file.touch(exist_ok=True)
		return open(path, 'rb+')

class ReadFile(FuncBase):
	name = 'read'
	def __init__(self):
		super().__init__(self.name, self.read, iter_results=True)
	
	@staticmethod
	def read(*args):
		if len(args) == 1:
			r = args[0].read(), args[0]
			return r
		elif len(args) == 2:
			print(args)
			return args[1].read(args[0]), args[1]
		else:
			raise IndexError(f"'file_read' takes 1 or 2 arguments, but {len(args)} were given")

class WriteFile(FuncBase):
	name = 'write'
	def __init__(self):
		super().__init__(self.name, self.write)
	
	@staticmethod
	def write(arg, file): 
		file.write(arg.encode() if isinstance(arg, str) else bytes(arg))
		return file

class FileSeek(FuncBase):
	name = 'seek'
	def __init__(self):
		super().__init__(self.name, self.seek)
	
	@staticmethod
	def seek(arg, file):
		file.seek(0, 2) if arg == 'end' else file.seek(arg)
		return file

class FileClose(FuncBase):
	name = 'close'
	def __init__(self):
		super().__init__(self.name, self.close)

	@staticmethod
	def close(file):
		file.close()

class FileTell(FuncBase):
	name = 'tell'
	def __init__(self):
		super().__init__(self.name, self.tell, iter_results=True)

	@staticmethod
	def tell(file):
		return file.tell(), file

PyModule('file', [OpenFile, ReadFile, WriteFile, FileSeek, FileClose, FileTell])

