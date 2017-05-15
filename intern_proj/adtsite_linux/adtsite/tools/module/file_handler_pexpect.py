import pexpect
import logging
from channels import Group
import os


class FileHandler(object):

    def spawn_ssh(self):
        child = pexpect.spawn('ssh %s@%s' % (self.user, self.host), maxread=1)
        child.expect('password: ')
        child.sendline(self.pwd)
        i = child.expect([pexpect.EOF, pexpect.TIMEOUT, '[\$]'])
        if i == 0:
            logging.error('SSH EOF Error! Can\'t login')
            child.close(force=True)
        elif i == 1:
            logging.error('SSH TIMEOUT Error! Can\'t login')
            child.close(force=True)
        elif i == 2:
            logging.info('SSH Login Success!')
            child.sendline('cd ' + self.serverpath)
            child.expect('[\$]')
        return child

    def spawn_sftp(self):
        # child = pexpect.spawn('sftp %s@%s' % (self.user, self.host), encoding='utf8')
        child = pexpect.spawn('sftp %s@%s' % ('hdfsbe', self.host), encoding='utf8')
        child.expect('password: ')
        # child.sendline(self.pwd)
        child.sendline('1BEIngest')
        i = child.expect([pexpect.EOF, pexpect.TIMEOUT, 'sftp>'])
        if i == 0:
            logging.error('SFTP EOF Error! Can\'t login')
            child.close(force=True)
        elif i == 1:
            logging.error('SFTP TIMEOUT Error! Can\'t login')
            child.close(force=True)
        elif i == 2:
            logging.info('SFTP Login Success!')
            child.sendline('mkdir ' + self.serverpath)
            index = child.expect(['Failure', 'sftp>'])
            if index == 0:
                logging.warning('The current path is existing!')
            elif index == 1:
                logging.info('Generate temporary job folder successfully!')
        return child

    def __init__(self, hostname, port, user, pwd, serverpath, localpath):
        if hostname:
            self.host = hostname
        else:
            self.host = "fslhdppclient01.imfs.micron.com"
        if port:
            self.port = port
        else:
            self.port = 22
        self.user = user
        self.pwd = pwd
        self.serverpath = serverpath
        self.localpath = localpath
        self.sftp = self.spawn_sftp()
        self.ssh = self.spawn_ssh()

    def exec_command(self, cmd, job_id):
        logpath = os.path.join(self.localpath, 'mylog.txt')
        fout = open(logpath, 'wb')
        self.ssh.logfile = fout

        self.ssh.sendline(cmd)
        patt_list = [pexpect.EOF, pexpect.TIMEOUT, '\r\n',
                     'Files_generated', 'File_generation_fail', 'KruskalWallis_Error']

        def send_msg(msg):
            Group("user-%s" % job_id).send({"text": msg})

        while True:
            i = self.ssh.expect(patt_list, timeout=300)

            if i == 0:
                send_msg(bytes(self.ssh.before).decode('utf-8'))
                send_msg('Error: EOF')
                logging.info('Error: EOF')
                break
            elif i == 1:
                send_msg(bytes(self.ssh.before).decode('utf-8'))
                send_msg('Error: TIMEOUT')
                logging.info('Error: TIMEOUT')
                break
            elif i == 2:
                send_msg(bytes(self.ssh.before).decode('utf-8'))
            elif i == 3:
                send_msg(bytes(self.ssh.before).decode('utf-8'))
                send_msg('Analysis Complete!')
                logging.info('Analysis Complete!')
                break
            elif i == 4:
                send_msg(bytes(self.ssh.before).decode('utf-8'))
                send_msg('Analysis Fail!')
                logging.error('Analysis Fail!')
                break
            elif i == 5:
                send_msg(bytes(self.ssh.before).decode('utf-8'))
                send_msg('Analysis Partly Complete!')
                logging.warning('Analysis Partly Complete!')
                break

    def kinit(self):
        self.ssh.sendline('kinit %s@%s' % (self.user, 'NA.MICRON.COM'))
        self.ssh.expect('Password for %s@%s:' % (self.user, 'NA.MICRON.COM'))
        self.ssh.sendline(self.pwd)
        i = self.ssh.expect([pexpect.EOF, pexpect.TIMEOUT, 'kinit: Preauthentication failed', '[\$]'])
        if i == 0:
            logging.error('SSH EOF Error! Can\'t login')
            self.ssh.close(force=True)
        elif i == 1:
            logging.error('SSH TIMEOUT Error! Can\'t login')
            self.ssh.close(force=True)
        elif i == 2:
            logging.warning('Kinit Fail!')
        elif i == 3:
            logging.info('Kinit Success!')

    def su_hdfsbe(self):
        self.ssh.sendline('su hdfsbe')
        self.ssh.expect('Password:')
        self.ssh.sendline('1BEIngest')
        i = self.ssh.expect([pexpect.EOF, pexpect.TIMEOUT, 'su: incorrect password', '[\$]'])
        if i == 0:
            logging.error('SSH EOF Error! Can\'t login')
            self.ssh.close(force=True)
        elif i == 1:
            logging.error('SSH TIMEOUT Error! Can\'t login')
            self.ssh.close(force=True)
        elif i == 2:
            logging.warning('su hdfsbe Fail!')
        elif i == 3:
            logging.info('su hdfsbe Success!')

    def download(self, remotefilepath, localfilepath):
        self.sftp.sendline('get ' + remotefilepath + ' ' + localfilepath)

    def upload(self, remotefilepath, localfilepath):
        self.sftp.sendline('put ' + localfilepath + ' ' + remotefilepath)

    def kill(self):
        self.ssh.sendeof()
        i = self.ssh.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=3)
        if i == 0:
            # logging.info(bytes(self.ssh.before).decode('utf-8'))
            pass
        elif i == 1:
            # logging.info(bytes(self.ssh.before).decode('utf-8'))
            pass
        self.ssh.close(force=True)
        self.sftp.close(force=True)
        logging.info('SSH and SFTP connection close!')
