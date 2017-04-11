import paramiko
import time
import logging

# source_path = os.path.realpath('')
# logfilename = os.path.join(source_path, 'logs', 'paramiko.log')
# paramiko.util.log_to_file(logfilename)


class TimeLimitExceeded(Exception):
    pass


def _timer():
    timelimit = 10
    start_time = time.time()
    elapsed_time = time.time()-start_time
    if elapsed_time > timelimit:
        raise TimeLimitExceeded


class FileHandler(object):

    def __init__(self, host, port, username, password, serverpath):
        if host:
            self.host = host
        else:
            self.host = "fslhdppclient01"
        if port:
            self.port = port
        else:
            self.port = 22
        self.user = username
        self.pwd = password
        self.serverpath = serverpath

    def upload(self, remotefilepath, localfile, localfilepath):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, username=self.user, password=self.pwd, timeout=10.0)
        sftp = ssh.open_sftp()
        try:
            sftp.mkdir(self.serverpath)
        except OSError:
            logging.warning("The current path is existing!")
        try:
            if localfile:
                sftp.putfo(localfile, remotefilepath, _timer())
            elif localfilepath:
                sftp.put(localfilepath, remotefilepath, _timer())
        except TimeLimitExceeded:
            logging.error("The operation took too much time to complete!")
        sftp.close()

    def download(self, remotefilepath, localfile, localfilepath):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, username=self.user, password=self.pwd, timeout=10.0)
        sftp = ssh.open_sftp()
        try:
            if localfile:
                sftp.getfo(remotefilepath, localfile, _timer())
            elif localfilepath:
                sftp.get(remotefilepath, localfilepath, _timer())
        except TimeLimitExceeded:
            logging.error("The operation took too much time to complete!")
        sftp.close()

    def kinit(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.user, password=self.pwd)

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("kinit " + self.user + "@NA.MICRON.COM")
        ssh_stdin.write(self.pwd + '\n')
        ssh_stdin.flush()