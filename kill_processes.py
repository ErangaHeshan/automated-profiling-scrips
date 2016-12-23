#!/usr/bin/env python

# Copyright 2016 Eranga Heshan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
