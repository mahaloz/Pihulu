#!/usr/bin/env python3
# Zion L. Basque
# 2018-01-22
# This python program attempts to trace different branches executed in an ELF
# through jmp addresses called after a iomparision.
import sys
import struct
from random import *

# Get input from command line
arg_file = sys.argv[1]

# Open file and extract bits
with open(arg_file, mode='rb') as file:
	all_bytes = bytearray(file.read())

# Use AFL-FUZZ flip bit method 
def flip_bit(byte_arr, bitn):
	byte_arr[bitn >> 3] ^= (128 >> ((bitn) & 7))

fileLen = len(all_bytes)
u_stack = 1 << (1 + randint(0,6))

# Flip random bits in the file
for i in range(u_stack):
	rand = randint(0,(fileLen << 3)-1)
	flip_bit(all_bytes, rand)

# Output mutated program
output_name = sys.argv[2]
with open(output_name, 'wb') as file:
	file.write(all_bytes)
