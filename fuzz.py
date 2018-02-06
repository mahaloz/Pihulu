#!/usr/bin/env python3
# Zion L. Basque
# 2018-01-22
# This python program is the main runner for Pihulu and control the tracer, and mutator

import sys
from subprocess import call
from distutils.dir_util import copy_tree
global out_loc, in_loc, target;

def fuzz():
	# check all agrs
	if(len(sys.argv) != 7):
		print("No args or RUNNING IN GDB")
		print("Example: fuzz -Q -i /test/seeds -o /test/out /target/binary")
		return;
	# assign args
	out_loc = sys.argv[5]
	in_loc = sys.argv[3]
	target = sys.argv[6]
	
	with open('arg_file','w') as file:
		file.write(target + " " + out_loc)
		
	copy_tree(in_loc, in_loc+"../queue")
	
	print("STARTING TRACER...")
	# starting the tracer through gdb-setter.gdbinit
	call(['gdb', target, '-x', 'setter.gdbinit'])


fuzz()
