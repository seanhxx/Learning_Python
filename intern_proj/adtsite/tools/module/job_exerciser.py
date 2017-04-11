import paramiko
import os
import re
import threading
import time
from channels import Group
import csv
import json
from .file_handler import FileHandler

# source_path = os.path.realpath('')
# logfilename = os.path.join(source_path, 'logs', 'paramiko.log')
# paramiko.util.log_to_file(logfilename)


class JobExerciser(threading.Thread):
    source_path = os.path.realpath('')

    def __init__(self, job_id, host, user, pwd, serverpath):
        threading.Thread.__init__(self)
        self.job_id = job_id
        self.host = host
        self.user = user
        self.pwd = pwd
        self.path = serverpath

    def run(self):
        time.sleep(2)
        Group("user-%s" % self.job_id).send({
            "text": "Analysis Start!"
        })
        # set SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.user, password=self.pwd)
        # execute command
        cmd_to_execute = "spark-submit " + self.path + "adhoc.py"
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
        for line in iter(lambda: ssh_stderr.readline(2048), ""):
            Group("user-%s" % self.job_id).send({
                "text": line
            })

        for line in iter(lambda: ssh_stdout.readline(2048), ""):
            # print(line)
            Group("user-%s" % self.job_id).send({
                "text": line
            })

            pattern0 = r'File generation fail'
            match = re.search(pattern0, line)
            if match:
                Group("user-%s" % self.job_id).send({
                    "text": "Analysis Fail"
                })

            pattern1 = r'Files have generated'
            match = re.search(pattern1, line)
            if match:
                fh = FileHandler(self.host, 22, self.user, self.pwd, self.path)
                fpin_rf = os.path.join(self.path, 'result_rf.csv')
                fpin_k = os.path.join(self.path, 'result_k.csv')
                fpout_rf = os.path.join(self.source_path, 'pyscript', 'tmp_' + self.job_id, 'result_rf.csv')
                fpout_k = os.path.join(self.source_path, 'pyscript', 'tmp_' + self.job_id, 'result_k.csv')
                fh.download(fpin_rf, None, fpout_rf)
                fh.download(fpin_k, None, fpout_k)

                # with open(fpout_rf, newline='') as f:
                #     reader = csv.reader(f)
                #     for row in reader:
                #         print(json.dumps(row))
                #         Group("user-%s" % self.job_id).send({
                #             "text": json.dumps(row)
                #         })
                #
                # with open(fpout_k, newline='') as f:
                #     reader = csv.reader(f)
                #     for row in reader:
                #         print(json.dumps(row))
                #         Group("user-%s" % self.job_id).send({
                #             "text": json.dumps(row)
                #         })

                Group("user-%s" % self.job_id).send({
                    "text": "Analysis Complete"
                })
