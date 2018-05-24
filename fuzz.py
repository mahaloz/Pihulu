#!/usr/bin/env python3
# Zion L. Basque
# 2018-01-22
# This python program is the main runner for Pihulu and control the tracer, and mutator

import sys
import os, shutil
from subprocess import call
from distutils.dir_util import copy_tree
global out_loc, in_loc, target;

def fuzz():
	# check all agrs
	if(len(sys.argv) != 7):
		print("Sytax Error: Not enough args!")
		print("Example: fuzz -Q -i test/seeds/ -o test/out/ target/binary")
		return;
	# clean the last queue
	folder = 'queue'
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			print(e)
	
	# assign args
	out_loc = sys.argv[5]
	in_loc = sys.argv[3]
	target = sys.argv[6]
	
	with open('arg_file','w') as file:
		file.write(target + " " + out_loc)
		
	copy_tree(in_loc, "queue")
	
	print("STARTING TRACER...")
	# starting the tracer through gdb-setter.gdbinit
	call(['gdb', target, '-x', 'setter.gdbinit'])


fuzz()
