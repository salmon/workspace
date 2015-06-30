from __future__ import absolute_import, print_function, with_statement

import os, sys, argparse, time, re
import json, optparse, codecs

from mod_utils import command_shell
from mod_utils import sort_and_diff
from mod_utils import textutil
from mod_utils import junit

class TranswarpTest(object):
    def __init__(self):
        self.conf = dict()
        self.dir_rule = [
            "00_data_init",
            "01_hyperbase_ddl",
            "02_inceptor_ddl",
            "03_inceptor_insert",
            "04_query",
            "05_answer"
        ]
        self.shell_cmd = [
            "initialize_data.sh",
            "initialize_hyperbase.sh",
            "initialize_inceptor.sh",
            "initialize_inceptor_insert.sh"
        ]

        self.hostname = "localhost"
        self.database = "default"

    def load_config(self):
        with open("conf.json") as f:
            self.conf = json.load(f)
        print(self.conf)
        if self.conf.has_key("hostname"):
            self.hostname = self.conf["hostname"]
        if self.conf.has_key("database"):
            self.database = self.conf["database"]

    def generate_reports(self, suite, cases):
        report = junit.JUnitReporter(suite)
        for testcase in cases:
            report.add_caseresult(testcase)
        report.generate_reporter(suite)

    def prepare_data(self, top_suite_name):
        for i in range(0, 3):
            cases = list()
            path = top_suite_name + '/' + self.dir_rule[i]
            start_time = time.time()
            if not os.path.isfile(path + '/' + self.shell_cmd[i]):
                print("case %s skipped." % self.shell_cmd[i])
                case = junit.TestCase(self.shell_cmd[i].split('.')[0])
            else:
                print(os.getcwd(), path)
                command = "bash %s" % self.shell_cmd[i]
                (cmd_result, timedelta) = command_shell.Command.run(command, cwd=path)
                print("command %s.\ntime %s. result %s" % (self.shell_cmd[i], timedelta, cmd_result.returncode))
                status = "failed"
                if cmd_result.returncode == 0:
                    status = "success"
                cmd_result.show(False)
                case = junit.TestCase(self.shell_cmd[i].split('.')[0], status, timedelta, cmd_result.stdout, cmd_result.stderr)
            end_time = time.time()
            test_suites = junit.TestSuites(top_suite_name, self.dir_rule[i], end_time - start_time)
            cases.append(case)
            self.generate_reports(test_suites, cases)

    def do_all_tests(self):
        if not self.conf.has_key("transwarp_suites"):
            return 0
        for top_suite_name in self.conf["transwarp_suites"]:
            self.prepare_data(top_suite_name)
            path = top_suite_name + "/" + self.dir_rule[4]
            if not os.path.isdir(path):
                continue

            self._do_transwarp_test(path, top_suite_name)

    def _do_transwarp_test(self, path, suite_name):
        prefix_command = "transwarp -t -h %s -database %s -f " % (self.hostname, self.database)
        cases = list()
        start_time = time.time()
        for root, dirs, files in os.walk(path):
            for file in files:
                if not re.match(".*\.sql$", file):
                    continue
                command = prefix_command + file
                (cmd_result, timedelta) = command_shell.Command.run(command.split(), cwd=root)
                casename = file.split('.')[0]
                status = "failed"
                if cmd_result.returncode == 0:
                    status = "success"
                fileContent = None
                with open(os.path.join(root, file), 'r') as f:
                    fileContent = f.readlines()
                    print(fileContent)
                case = junit.TestCase(casename, status, timedelta, cmd_result.stdout, cmd_result.stderr, fileContent)
                cases.append(case)
                print("command %s.\ntime %s. result %s" % (command, timedelta, cmd_result.returncode))
                print("Start Compare Results %s" % command)
                #ToDo: diff with 05_ans
                sort_and_diff.SortDiff.sort_differ_buffers(cmd_result.stdout, "05_answer/%s.out" % casename)
        end_time = time.time()

        test_suites = junit.TestSuites(suite_name, "exec_sql", end_time - start_time)
        self.generate_reports(test_suites, cases)

        return cases


    #ToDo: Not Implement
    def _do_jdbc_test(self):
        pass

if __name__ == "__main__":
    usage = "usage: %prog -d workdir"
    parser = optparse.OptionParser(usage)
    parser.add_option("-d", "--dir", action="store", type="string", default="./", dest="project_dir")
    (options, args) = parser.parse_args()

    test = TranswarpTest()
    test.load_config()

    os.chdir(options.project_dir)
    test.do_all_tests()
