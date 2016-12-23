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
list_valid_processes = ['org.apache.storm.ui.core',
			'org.apache.storm.daemon.nimbus',
			'org.apache.storm.daemon.worker',
			'backtype.storm.daemon.supervisor',
			'org.apache.storm.LogWriter',			
			'org.apache.storm.daemon.logviewer',
			'org.apache.zookeeper.server.quorum.QuorumPeerMain',
			'kafka.Kafka',
			'clojure.main']
parallelism = int(sys.argv[1])
test_time = 240
now = datetime.datetime.now()
file_name_const = str(now.year) + '-'   + set_str(now.month) + '-' + set_str(now.day) + '_' + set_str(now.hour) + '-' + set_str(now.minute) + '_'
file_path = os.path.dirname(os.path.realpath(__file__))
folder_name = 'Dec-' + set_str(now.day) + '-' + set_str(now.hour) + '-' + set_str(now.minute) + '_storm-1.0.2_on_cluster(4_nodes)_P=' + str(parallelism)
host_name = socket.gethostname()

def main():
	from subprocess import call
	global list_process_ids
	print ('================================================================================================')
	print ('Welcome to the automated profiling using nmon and jfr!')
	print ('================================================================================================')
	if int(sys.argv[2]) == 0:
		remove_logs()
		if host_name == "zoo5":			
			start_zookeeper()
			start_storm_supervisor()
			start_storm_ui()
			start_storm_nimbus()
		else:
			start_storm_supervisor()
		time.sleep(30)			
	os.mkdir(file_path + '/' + folder_name, 0755)
	os.mkdir(file_path + '/' + folder_name + '/jfr', 0755)
	print('Starting profiling process...')
	call(['/home/ubuntu/eranga/software/nmon16d_x86/./nmon_x86_64_ubuntu13',
		'-f', '-s', '5', '-c', str(test_time/5), '-F', folder_name + '/' + host_name + '.nmon'])
	if host_name == "zoo5":
		subprocess.Popen('./submitStorm.sh')
	begin()
	time.sleep(test_time + 15)
	subprocess.Popen(['storm', 'kill', 'Microbenchmark', '-w', '0'])
	print("Finished profiling!")

def begin():
	global list_process_ids
	global list_process_names
	p = subprocess.Popen(['jcmd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	jcmd_out, err = p.communicate()
	filter_jcmd_processes(jcmd_out)
	if('org.apache.storm.daemon.worker' not in list_process_names):
		print ("Storm worker is not yet started! Retrying 'jcmd' command")
		list_process_ids = []
		list_process_names = []
		time.sleep(2)
		begin()
	else:
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

def remove_logs():
	print("Deleting any excisting storm logs or storm-data files...")
	if host_name == "zoo5":
		try:
			shutil.rmtree('/var/zookeeper/version-2')			
		except Exception:
			pass
		try:
			os.remove('/var/zookeeper/zookeeper_server.pid')			
		except Exception:
			pass
	try:
		shutil.rmtree('/home/ubuntu/eranga/storm-data')			
	except Exception:
		pass
	try:
		shutil.rmtree('/home/ubuntu/eranga/software/apache-storm-1.0.2/logs')			
	except Exception:
		pass


def start_storm_supervisor():
	from subprocess import call
	print("Starting storm supervisor...")
	subprocess.Popen(['storm', 'supervisor'])


def start_storm_ui():
	from subprocess import call
	print("Starting storm ui...")
	if host_name == "zoo5":
		subprocess.Popen(['storm', 'ui'])
	else:
		time.sleep(1)


def start_storm_nimbus():
	from subprocess import call
	print("Starting storm nimbus...")
	if host_name == "zoo5":
		subprocess.Popen(['storm', 'nimbus'])
	else:
		time.sleep(1)


def start_zookeeper():
	from subprocess import call
	print("Starting zookeeper server...")
	if host_name == "zoo5":
		subprocess.Popen(['zkServer.sh', 'start'])
	else:
		time.sleep(1)


def stop_zookeeper():
	from subprocess import call
	print("Stopping zookeeper server...")
	if host_name == "zoo5":
		subprocess.Popen(['zkServer.sh', 'stop'])


main()
