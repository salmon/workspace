#!/usr/bin/env python
import os, subprocess, sys
import re, time

def command_wrapper(cmd, filehandler):
	timeout = 4
	is_timeout = 0
	filehandler.write("COMMAND %s :\n" % cmd)
	filehandler.flush()
	#p = subprocess.Popen(cmd, stdout=filehandler, shell=True) 
	p = subprocess.Popen(cmd, stdout=filehandler, shell=True) 
	t_beginning = time.time()
	seconds_passed = 0
	while True:
		if p.poll() is not None:
			break;
		seconds_passed = time.time() - t_beginning
		if timeout and seconds_passed > timeout:
			p.terminate()
			is_timeout = 1
		time.sleep(0.1)

	retval = p.returncode
	#retval = r.wait()

	filehandler.flush()
	if retval == 0:
		filehandler.write("\nRESULT: CMD %s SUCCESS ret: %d\n" % (cmd, retval))
	else:
		filehandler.write("\nRESULT: CMD %s FAILED. ret: %d\n" % (cmd, retval))

	filehandler.flush()
	return retval

# All: docker flannel
# Master: etcd apiserver controller-manager scheduler
# Node: kubelet proxy
def service_runing_state(filehandler):
	generic_service_list = ["docker", "flannel"]
	master_services_list = ["etcd", "apiserver", "controller-manager", "scheduler"]
	node_services_list = ["kubelet", "proxy"]

	for service_name in generic_service_list:
		cmd = "systemctl status %s" % service_name
		command_wrapper(cmd, filehandler)

	# "master":
	for service_name in master_services_list:
		cmd = "systemctl status %s" % service_name
		command_wrapper(cmd, filehandler)

	# "slave":
	for service_name in node_services_list:
		cmd = "systemctl status %s" % service_name
		command_wrapper(cmd, filehandler)

# ALL: 
# check if docker0 == /var/run/flannel/subnet.env
# docker version
def check_generic_services(filehandler):
	filehandler.write("CHECK Docker version:\n")
	cmd = "docker version"
	command_wrapper(cmd, filehandler)

	filehandler.write("CHECK IP config:\n")
	cmd = "cat /var/run/flannel/subnet.env"
	command_wrapper(cmd, filehandler)
	cmd = "ip addr"
	command_wrapper(cmd, filehandler)

# Master Check
# check etcd: {{ k8s_dir }}/etcdctl --peers ETCD_IP ls --recursive
# check log dir: /var/log/kubernetes is exist
# check apiserver: curl http://127.0.0.1:8080
# check schedule: ?
# check controller-manager: ?
# print log files : /var/log/kubernetes/*.INFO
def check_master_services(filehandler):
	dirname = "/var/log/kubernetes/"
	if not os.path.isdir(dirname):
		filehandler.write("CHECK log dir Failed: %s\n" % dirname)
	else:
		filehandler.write("CHECK log dir Success: %s\n" % dirname)

	filehandler.write("CHECK apiserver:\n")
	cmd = "curl http://127.0.0.1:8080/"
	command_wrapper(cmd, filehandler)
	cmd = "curl http://127.0.0.1:8080/healthz"
	command_wrapper(cmd, filehandler)

	cmd = "/opt/kubernetes/bin/etcdctl --peers=http://172.17.8.100:4001 ls --recursive"
	command_wrapper(cmd, filehandler)

# Node Check
# check kubelet: curl 127.0.0.1:4194
# check proxy: curl 10.10.10.1:80; curl -k https://10.10.10.2:443
def check_node_services(filehandler):
	filehandler.write("CHECK Kubelet:\n")
	cmd = "curl 127.0.0.1:4194/healthz"
	command_wrapper(cmd, filehandler)

	filehandler.write("CHECK proxy:\n")
	cmd = "curl http://10.10.10.1:80"
	command_wrapper(cmd, filehandler)
	cmd = "curl http://10.10.10.1:80/healthz"
	command_wrapper(cmd, filehandler)
	cmd = "curl -k https://10.10.10.2:443"
	command_wrapper(cmd, filehandler)
	cmd = "curl -k https://10.10.10.2:443/healthz"
	command_wrapper(cmd, filehandler)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.stderr.write('%s: %s <dirname>' % sys.argv[0], sys.argv[0])
	dirname = sys.argv[1]
	if len(sys.argv) > 3:
		print sys.argv[2]
	if os.path.isdir(dirname):
		pass
	else:
		os.mkdir(dirname)
	# print sys.argv[2]
	with open("%s/result.txt" % dirname, 'a') as f:
		# f.write("argv2: %s\n" % sys.argv[2]
		service_runing_state(f)
		check_generic_services(f)
		check_master_services(f)
		check_node_services(f)
