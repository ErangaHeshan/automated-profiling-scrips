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
list_valid_processes = ['org.wso2.siddhi.test.kafka.SiddhiNodeFilter',
			'org.wso2.siddhi.test.kafka.SiddhiNodeMetrics',
			'org.wso2.siddhi.test.kafka.SiddhiNodeModification',
			'org.wso2.siddhi.test.kafka.ConsumerNode',
			'org.wso2.siddhi.test.kafka.ProducerNode',
			'kafka.Kafka']
parallelism = int(sys.argv[1])
test_time = 180
now = datetime.datetime.now()
file_name_const = str(now.year) + '-'   + str(now.month) + '-' + str(now.day) + '_' + str(now.hour) + '-' + str(now.minute) + '_'
file_path = os.path.dirname(os.path.realpath(__file__))
folder_name = 'Dec-' + set_str(now.day) + '-' + set_str(now.hour) + '-' + set_str(now.minute) + '_kafka_2.11-0.10.0.1_on_cluster(4_nodes)_P=' + str(parallelism)
host_name = socket.gethostname()

def main():
	from subprocess import call
	global list_process_ids
	print ('================================================================================================')
	print ('Welcome to the automated profiling using nmon and jfr!')
	print ('================================================================================================')
	os.mkdir(file_path + '/' + folder_name, 0755)
	os.mkdir(file_path + '/' + folder_name + '/jfr', 0755)
	remove_logs()
	if int(sys.argv[2]) == 0:
		start_zookeeper()
		start_kafka_server()
	print('Starting profiling process...')
	call(['/home/ubuntu/eranga/software/nmon16d_x86/./nmon_x86_64_ubuntu13',
		'-f', '-s', '5', '-c', str(test_time/5), '-F', folder_name + '/' + host_name + '.nmon'])
	if host_name == "zoo1":
		subprocess.Popen('./consumer.sh')
		subprocess.Popen('./producer.sh')		
	else:
		for i in range(parallelism):
			if host_name == "zoo2":
				subprocess.Popen('./siddhi-filter.sh')
			elif host_name == "zoo3":
				subprocess.Popen('./siddhi-metrics.sh')
			elif host_name == "zoo4":
				subprocess.Popen('./siddhi-modify.sh')		
	begin()
	time.sleep(test_time + 5)
	stop_zookeeper()
	for pid in list_process_ids:
		try:
			call(['kill', '-9', str(pid)])
		except Exception: 
	  		pass
	print("Finished profiling!")
	remove_logs()
	

def begin():
	global list_process_ids
	global list_process_names
	p = subprocess.Popen(['jcmd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	jcmd_out, err = p.communicate()
	filter_jcmd_processes(jcmd_out)
	if(('org.wso2.siddhi.test.kafka.ConsumerNode' not in list_process_names) and
		('org.wso2.siddhi.test.kafka.SiddhiNodeFilter' not in list_process_names) and
		('org.wso2.siddhi.test.kafka.SiddhiNodeMetrics' not in list_process_names) and
		('org.wso2.siddhi.test.kafka.SiddhiNodeModification' not in list_process_names) and
		('org.wso2.siddhi.test.kafka.ProducerNode' not in list_process_names)):
		print ("Kafka process is not yet started! Retrying 'jcmd' command")
		list_process_ids = []
		list_process_names = []
		time.sleep(.5)
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
	print("Deleting any excisting kafka log files...")
	if host_name == "zoo1":
		try:
			shutil.rmtree('/tmp/kafka-logs-0')			
		except Exception:
			pass
		try:
			shutil.rmtree('/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/logs')			
		except Exception:
			pass
		try:
			shutil.rmtree('/var/zookeeper/version-2')			
		except Exception:
			pass
		try:
			os.remove('/var/zookeeper/zookeeper_server.pid')			
		except Exception:
			pass
	elif host_name == "zoo2":
		try:
			shutil.rmtree('/tmp/kafka-logs-1')			
		except Exception:
			pass
		try:
			shutil.rmtree('/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/logs')			
		except Exception:
			pass
	elif host_name == "zoo3":
		try:
			shutil.rmtree('/tmp/kafka-logs-2')			
		except Exception:
			pass
		try:
			shutil.rmtree('/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/logs')			
		except Exception:
			pass
	elif host_name == "zoo4":
		try:
			shutil.rmtree('/tmp/kafka-logs-3')			
		except Exception:
			pass
		try:
			shutil.rmtree('/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/logs')			
		except Exception:
			pass

def start_kafka_server():
	from subprocess import call
	print("Starting kafka server...")
	if host_name == "zoo1":
		subprocess.Popen(['/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/bin/kafka-server-start.sh', '/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/config/server-1.properties'])
	elif host_name == "zoo2":
		subprocess.Popen(['/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/bin/kafka-server-start.sh', '/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/config/server-2.properties'])
	elif host_name == "zoo3":
		subprocess.Popen(['/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/bin/kafka-server-start.sh', '/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/config/server-3.properties'])
	elif host_name == "zoo4":
		subprocess.Popen(['/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/bin/kafka-server-start.sh', '/home/ubuntu/eranga/software/kafka_2.11-0.10.0.1/config/server-4.properties'])
	

def start_zookeeper():
	from subprocess import call
	print("Starting zookeeper server...")
	if host_name == "zoo1":
		call(['zkServer.sh', 'start'])
	else:
		time.sleep(1)


def stop_zookeeper():
	from subprocess import call
	print("Stopping zookeeper server...")
	if host_name == "zoo1":
		call(['zkServer.sh', 'stop'])


main()
