import os
import threading
import time
from channels import Group
from .file_handler_pexpect import FileHandler


class JobExerciser(threading.Thread):

    def __init__(self, job_id, host, user, pwd, remotepath, localpath):
        threading.Thread.__init__(self)
        self.job_id = job_id
        self.host = host
        self.user = user
        self.pwd = pwd
        self.remotepath = remotepath
        self.localpath = localpath

    def run(self):
        time.sleep(3.5)
        Group("user-%s" % self.job_id).send({
            "text": "Analysis Start!"
        })

        # set SSH connection
        fh = FileHandler(self.host, 22, self.user, self.pwd, self.remotepath, self.localpath)
        fh.su_hdfsbe()
        # execute command
        exepypath = os.path.join(self.remotepath, 'adhoc.py')
        # cmd_to_execute = "spark-submit --master yarn --driver-memory 4G --executor-memory 4G --num-executors 3 --queue eng_BE_MSB " + exepypath
        cmd_to_execute = "spark-submit --driver-memory 4G --queue eng_BE_MSB " + exepypath
        fh.exec_command(cmd_to_execute, self.job_id)
        # download files
        fpin_rf = os.path.join(self.remotepath, 'result_rf.csv')
        fpin_k = os.path.join(self.remotepath, 'result_k.csv')
        fpin_raw = os.path.join(self.remotepath, 'result_raw.csv')
        fpout_rf = os.path.join(self.localpath, 'result_rf.csv')
        fpout_k = os.path.join(self.localpath, 'result_k.csv')
        fpout_raw = os.path.join(self.localpath, 'result_raw.csv')
        fh.download(fpin_raw, fpout_raw)
        fh.download(fpin_rf, fpout_rf)
        fh.download(fpin_k, fpout_k)
        fh.kill()
