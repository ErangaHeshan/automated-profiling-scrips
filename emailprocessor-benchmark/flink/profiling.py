#!/usr/bin/env python

import socket
import subprocess
import signal
import sys
import os
import shutil
import datetime
import threading
import time

def set_str(string):
	if(len(str(string)) == 1):
		return '0' + str(string)
	else:
		return str(string)


list_process_ids = []
list_process_names = []
list_valid_processes = ['org.apache.flink.runtime.taskmanager.TaskManager',
			'org.apache.flink.runtime.jobmanager.JobManager']
test_time = 70
parallelism = int(sys.argv[1])
now = datetime.datetime.now()
file_name_const = str(now.year) + '-'   + set_str(now.month) + '-' + set_str(now.day) + '_' + set_str(now.hour) + '-' + set_str(now.minute) + '_'
file_path = os.path.dirname(os.path.realpath(__file__))
folder_name = 'Dec-' + set_str(now.day) + '-' + set_str(now.hour) + '-' + set_str(now.minute) + '_flink-1.1.2_on_cluster(4_nodes)_P=' + set_str(parallelism)
host_name = socket.gethostname()

def main():
	from subprocess import call
	global list_process_ids
	print ('================================================================================================')
	print ('Welcome to the automated profiling using nmon and jfr!')
	print ('================================================================================================')
	os.mkdir(file_path + '/' + folder_name, 0755)
	os.mkdir(file_path + '/' + folder_name + '/jfr', 0755)
	print('Starting profiling process...')
	call(['/home/ubuntu/eranga/software/nmon16d_x86/./nmon_x86_64_ubuntu13',
		'-f', '-s', '5', '-c', str(test_time/5), '-F', folder_name + '/' + host_name + '.nmon'])
	p = subprocess.Popen(['jcmd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	jcmd_out, err = p.communicate()
	filter_jcmd_processes(jcmd_out)
	threading.Thread(target=profile).start()
	print ('================================================================================================')

def filter_jcmd_processes(jcmd_out):
	global list_process_ids
	list_lines = (str(jcmd_out)).split('\n')
	print ('Number of running processes = ' + str(len(list_lines) - 1) + '\n')
	count = 0 
	for line in list_lines:
		count = count + 1
		if(count < len(list_lines)):
			get_process_id(line)

def get_process_id(line):
	global list_process_ids
	global list_process_names
	global list_valid_processes
	list_elements = (str(line)).split(' ')
	count = 0	
	print (list_elements[0] + '\t' + list_elements[1])
	if(list_elements[1] in list_valid_processes):
		list_process_ids.append(list_elements[0])
		list_process_names.append(list_elements[1])

def profile():
	from subprocess import call
	global list_process_ids
	global list_process_names
	global file_name_const
	for i in range(0, len(list_process_ids)):
		file_name = 'filename=' + file_path + '/' + folder_name + '/jfr/' + file_name_const + host_name + '-' + str(i + 1) + '-' + 					list_process_names[i] + '.jfr'
        	call(['jcmd', list_process_ids[i], 'VM.unlock_commercial_features'])
        	call(['jcmd', list_process_ids[i], 'JFR.start duration=' + str(test_time) + 's', file_name])
        	print (file_name)
		time.sleep(.5)


main()
