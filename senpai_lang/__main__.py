from senpai_lang.src.classes import SenpaiInterpreter
import time
from senpai_lang.src.parser import parser
import logging
import argparse
import senpai_lang.src.senpai_builtins
# import os

cmdparse = argparse.ArgumentParser()
cmdparse.add_argument("-i", "--infile", type=str, help="Input file for interpreter") # for some reason using argparse.FileType and then reading causes EOF error with Lark. Idk why.
cmdparse.add_argument("-d", "--debugfile", default=None, type=str, help="File to write to for verbose logging. The log tracks almost everything the intepreter does down to the expression.")

cmdparse.add_argument("-tb", "--pytraceback", default=False, action='store_true', help="Enable Python exception traceback. Useful for taking note of bugs. Disables the Senpai except hook.")

cmdparse.add_argument("-ps", "--printstack", default=False, action='store_true', help="Print the execution time, variables, stacks, and builtins of the program after running")

cmdparse.add_argument("-w", "--wiki", default=False, action='store_true', help="Visit the wiki page for the Senpai language")

def main():
	args = cmdparse.parse_args()

	if args.wiki:
		print("https://esolangs.org/wiki/Senpai")
		exit(0)
		
	if args.debugfile:
		logging.basicConfig(filename=args.debugfile, level=logging.DEBUG, format='%(asctime)s.%(msecs)03d - %(message)s',datefmt='%Y-%b-%d, %H:%M:%S', )

		logging.info("\n\n\n===Starting logging of Senpai===")

	with open(args.infile) as f:
		# os.chdir(os.path.split(os.path.realpath(args.infile))[0])
		t = f.read()
	tree = parser.parse(t)
	# print(tree)
	p = time.perf_counter()
	i = SenpaiInterpreter(tree, python_traceback=args.pytraceback)

	t = (time.perf_counter() - p)
	logger = logging.getLogger()
	logger.info(f"Program executed successfully in {t} seconds!")
	if args.printstack:
		print("Time taken:", t*1000, "miliseconds")
		print("Variables:", i.vars)
		print("Stacks:", i.stacks)
		print("Builtins:", i.builtins)

if __name__ == "__main__":
	main()
