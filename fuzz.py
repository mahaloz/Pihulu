#!/usr/bin/env python3
# Zion L. Basque
# 2018-01-22
# This python program attempts to trace different branches executed in an ELF
# through jmp addresses called after a iomparision.

import sys
import subprocess

if(len(sys.argv) != 6):
	print("Error: incorrect sytanx")
	print("Example: fuzz /target/binary -i /test/seeds -o /test/out")


