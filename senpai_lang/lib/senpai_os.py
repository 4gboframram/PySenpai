from senpai_lang.pyutils import FuncBase, PyModule
import os


class System(FuncBase):
	"""
	Can take 2 or 1 argument
	First argument is always the command to execute.
	Second argument can be anything, 
	
	Second argument if it exists returns the value os.system()
	
	On Unix, the return value is the exit status of the process encoded in the format specified for wait().

	On Windows, the return value is that returned by the system shell after running command. The shell is given by the Windows environment variable COMSPEC: it is usually cmd.exe, which returns the exit status of the command run; on systems using a non-native shell, consult your shell documentation.
	"""
	name = 'cmd'
	def __init__(self):
		super().__init__(self.name, self.system)

	@staticmethod
	def system(*args):
		if len(args) == 1:
			os.system(*args)
		else:
			return os.system(args[0])
			
PyModule('os', [System])