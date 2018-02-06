#!/usr/bin/env python3
# Zion L. Basque
# 2018-01-22
# This python program attempts to trace different branches executed in an ELF
# through jmp addresses called after a comparison.

from collections import deque
import re # used to sort trough objdump
import subprocess
import os
from shutil import copy
import sys
import time
from random import *

# get args of fuzz call
args = []
with open("arg_file","r") as file:
	args = file.read().split(' ')
# globalization of variables
prev_location = 0 # location of last address
shared_mem = [0]*(64*1024) # a single path of an app
tup_str = "" # a reduced form of shared_mem
mem_map = [] # map of all tup_str
cur_file = '.'
out_dir = args[1]
target = args[0]


# objdump on the target binary
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

# starts process
def opener(input_file):
	global shared_mem
	shared_mem = [0]*(64*1024)
	gdb.execute("run " +"<"+ input_file)
	path_math()
	return;
# closes process
def closer(reason):
	global prev_location
	global shared_mem
	global mem_map
	global tup_str
	global cur_file
	global out_dir
	# check if a crash happened
	if(reason == "SIGSEGV"):
		copy(cur_file, out_dir)

	# reset previous location for first run
	prev_location = 0
	
	# trim the shared_mem arr to a tuple string
	tup_str = ""
	for counter, value in enumerate(shared_mem):
		if(value != 0):
			tup_str += str(counter)+":"+str(value)+" "
	# put ever shared_mem into an array
	mem_map.append(tup_str)
	return; 

def reason():
	res = gdb.execute("info program", to_string=True).splitlines()
	if not res:
		return "NOT RUNNING"
	for line in res:
		line = line.strip()
		if line.startswith("It stopped with signal "):
			return line.replace("It stopped with signal ", "").split(",", 1)[0]
		if line == "The program being debugged is not being run.":
			return "NOT RUNNING"
		if line == "It stopped at a breakpoint that has since been deleted.":
			return "TEMPORARY BREAKPOINT"
		if line.startswith("It stopped at breakpoint "):
			return "BREAKPOINT"
		if line == "It stopped after being stepped.":
			return "SINGLE STEP"
	return "STOPPED"

# defines paths
def path_math():
	global prev_location
	global shared_mem
	res = reason()
	if(res == 'SIGSEGV'):
		closer(res)
		return;
	# get the current position through the pointer counter
	try:
		register = gdb.execute("i r pc",to_string=True)
	# the end of the current program was reached
	except BaseException:
		reso = reason()
		closer(reso)
		return;
	else:
		# find the pc
		temp = re.findall("(pc).+(0x[A-Fa-f0-9]{3,16})",register)
		pc = temp[0][1]

		# derived from afl-fuzz to create map
		cur_location = int(pc,0)
		print(cur_location)
		shared_mem[(cur_location ^ prev_location)%(64000)] += 1
		prev_location = cur_location >> 1  

		# continue to next break
		gdb.execute("continue")
		path_math()
		return;

# determines if a path is unique
def path_unique():
	global shared_mem
	global mem_map
	global tup_str
	unique = True
	paths = mem_map
	cur_path = tup_str
	
	# compare our current path and all paths
	for path in mem_map:
		if(cur_path == path):
			unique = False
	return unique;

def mutate(arg_file,bit,mute):
	global all_bytes;
	print("new mutation!")
    
	# Open file and extract bits
	with open(arg_file, mode='rb') as file:
		all_bytes = bytearray(file.read())
    
	# Use AFL-FUZZ flip bit method 	
	def flip_bit(byte_arr, bit_loc):
		byte_arr[bit_loc >> 3] ^= (128 >> ((bit_loc) & 7))
	
	# SINGLE BIT FLIP
	if(mute == 0):
		flip_bit(all_bytes, bit)
	# ADDITION
	if(mute == 1):
		for adj in range(0, len(all_bytes)*35):
			position = int(adj / 35)
			all_bytes[position] = (all_bytes[position] + (adj % 35))%255 
	# SUBTRACTION
	if(mute == 2):
		for adj in range(0, len(all_bytes)*35):
                        position = int(adj / 35)
                        all_bytes[position] = (all_bytes[position] - (adj % 35))%255

	# Output mutated program with new name
	output_name = arg_file + str(time.time())
	with open(output_name, 'wb') as file:
		file.write(all_bytes)
	return output_name;

# loops program
def program_looper():
	global in_loc
	global cur_file
	print("LOOPER STARTING...")
	queue = deque(os.listdir('queue'))
	while(len(queue)>0):
		cur_file = "queue/" + queue.popleft()

		# get bytes of file
		cur_bytes = []
		with open(cur_file, 'rb') as file:
			cur_bytes = bytearray(file.read())
		for mute in range(0,2):
			# go through each byte
			for bit in range(0, len(cur_bytes)*8):
				# mutate file
				mutated_file = mutate(cur_file,bit,mute)
				
				#trace effects
				opener(mutated_file)
				unique = path_unique()		
				if(unique):
					print("-----------------UNIQUE------------------")
					queue.append(mutated_file)
				else:
					print("+++++++++++++++++DELETED+++++++++++++++++")
					os.remove(mutated_file)
				
	return;

program_looper()
		
