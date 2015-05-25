#/usr/bin/env python
import os, sys
import re, time

def get_ipaddr():
	pass

def print_content(filehandler, prefix):
	line = filehandler.readline()
	while line:
		if re.match("^RESULT", line):
			#print line,
			break
		else:
			print "%s%s" % (prefix, line),
		line = filehandler.readline()

def callback_func(check_name):
	re.match()

def analyze_resfile(path_name):
	print "analyze result file"
	with open(path_name, 'r') as f:
		while True:
			line = f.readline()
			if not line:
				break
			if re.match("^RESULT: CMD systemctl", line):
				print line,
			# docker version
			if re.match("^COMMAND docker version", line):
				#print line,
				print_content(f, "DOCKER Content:  ")
			# check if subnet.env == docker0

			# CHECK log dir
			if re.match("^CHECK log dir", line):
				print line,

			# check apiserver http://127.0.0.1:8080/healthz
			if re.match("^COMMAND curl http://127.0.0.1:8080/healthz", line):
				#print line,
				print_content(f, "ApiServer Health:  ")

			# etcdctl show
			if re.match("^COMMAND /opt/kubernetes/bin/etcdctl", line):
				#print line,
				print_content(f, "Etcd Content:  ")

			# check kubelet
			if re.match("^COMMAND curl 127.0.0.1:4194/healthz", line):
				print_content(f, "Kubelet Health:  ")

			# check proxy: http://10.10.10.1:80/healthz https://10.10.10.2:443/healthz
			if re.match("^COMMAND curl http://10.10.10.1:80/healthz", line):
				print_content(f, "KubeProxy Http Health:  ")
			if re.match("^COMMAND curl -k https://10.10.10.2:443/healthz", line):
				print_content(f, "KubeProxy Https Health:  ")

	# print "analyze end"

def print_errlog(path_name):
	with open(path_name, 'r') as f:
		while True:
			line = f.readline()
			if not line:
				break
			print line,

def analyze(log_dir):
	dir_list = os.listdir(log_dir)
	for dirname in dir_list:
		if re.match(r'\d+$', dirname):
			path_name = log_dir + dirname
			if os.path.isdir(path_name):
				role_list = os.listdir(path_name)
				for role_name in role_list:
					print "----- Role Name: %s -----" % role_name
					print "----- Exec Time: %s -----" % \
						time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(dirname)))
					resfile_path = path_name + '/' + role_name + '/result.txt'
					errfile_path = path_name + '/' + role_name + '/error.txt'
					if os.path.isfile(resfile_path):
						analyze_resfile(resfile_path)
					elif os.path.isfile(errfile_path):
						print_errlog(errfile_path)
					else:
						print "Can't Find Result Files."
					print "----- ----- END ----- -----\n"

if __name__ == '__main__':
	log_dir = "./ansible_log/"
	analyze(log_dir)
