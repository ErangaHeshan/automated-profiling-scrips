#!/usr/bin/env python

import subprocess
import datetime
import threading
import time

list_process_ids = []
list_process_names = []
list_valid_processes = ['supervisor',
			'nimbus',
			'QuorumPeerMain']

def main():
	from subprocess import call
	global list_process_ids
	print ('================================================================================================')
	print ('Process Killer Initiated!')
	print ('================================================================================================')
	p = subprocess.Popen(['jps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	jps_out, err = p.communicate()
	kill_processes(jps_out)
	print ('================================================================================================')

def kill_processes(jps_out):
	global list_process_ids
	list_lines = (str(jps_out)).split('\n')
	print ('Number of running processes = ' + str(len(list_lines) - 1) + '\n')
	count = 0 
	for line in list_lines:
		count = count + 1
		if(count < len(list_lines)):
			call_kill_process(line)

def call_kill_process(line):
	from subprocess import call
	global list_process_ids
	global list_process_names
	global list_valid_processes
	list_elements = (str(line)).split(' ')
	count = 0	
	if(list_elements[1] in list_valid_processes):
		print ('killing ' + list_elements[0] + '\t' + list_elements[1])
		call(['kill', str(list_elements[0])])

main()
