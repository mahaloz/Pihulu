#!/usr/bin/env python3
# Zion L. Basque
# 2018-01-22
# This python program attempts to trace different branches executed in an ELF
# through jmp addresses called after a iomparision.

import re # used to sort trough objdump
import subprocess

prev_location = 0
shared_mem = [0]*(64*1024*10)
output = None
# objdump on the target binary
target = 'hello'
objdump = subprocess.Popen(['objdump', '-d', '-M', 'intel', target], stdout=subprocess.PIPE)
dump = objdump.stdout.read().decode('ASCII')

# take all jmp commands and addresses from objdump using a "regular expression"
jmps_all = re.findall("([0-9A-Fa-f]{3,16}):.+(j[a-z].{0,3})", dump)
jmps = []
for jmp in jmps_all:
	# remove unconditional jmps
	if("jmp" not in jmp): 
        	jmps.append("0x"+jmp[0]) # prepend hex type
        # call a break at every conditional jmp address
for jmp in jmps:
	gdb.execute("break *"+jmp)
    
def opener():
	global output
	output = open("path.txt","a")
	gdb.execute("run")
	path_math()
	return;
#TODO call with hook or something
def closer():
	global output
	global prev_location
	output.write("\n")
	output.close()
	prev_location = 0
	opener()
	return; 

def path_math():
	global prev_location
	global shared_mem
	global output
	# get the current position through the pointer counter
	try:
		register = gdb.execute("i r pc",to_string=True)
	# the end of the current program was reached
	except BaseException:
		closer()
		return;
	else:
		temp = re.findall("(pc).+(0x[A-Fa-f0-9]{3,16})",register)
		pc = temp[0][1]
		# derived from afl-fuzz
		cur_location = int(pc,0)
		print(cur_location)
		shared_mem[(cur_location ^ prev_location)%(64000)] += 1
		prev_location = cur_location >> 1  
		# output file   
		for loc in shared_mem:
			output.write(str(loc)+" ")
		gdb.execute("continue")
		path_math()
		return;
opener()	
