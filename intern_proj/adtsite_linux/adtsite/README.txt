Setup py3.5.3 virtual environment on sitelinux20:

# Create a new virtual environment
/usr/local/bin/pyvenv-3.5 /path/to/virtual/environment

# Enter the virtual environment
source /path/to/virtual/environment/bin/activate.csh

# Install required packages
pip install *** --proxy=http://proxy.micron.com:8080

<--
package list:
Django
django-bootstrap3
channels
pexpect
requests
-->

To start the web server on sitelinux20:

screen

source /path/to/virtual/environment/bin/activate.csh
# example: source /u/xiaoxiang/python3.5-env/env_Webserver/bin/activate.csh

python /path/to/webserver/adtsite/manage.py runserver 10.160.20.106:8080
# example: python /u/xiaoxiang/webserver/adtsite/manage.py runserver 10.160.20.106:8080

# When set 'Debug' in setting.py to 'False', please run server in insecure mode 
python /path/to/webserver/adtsite/manage.py runserver --insecure 10.160.20.106:8080

# Next press 'Ctrl+A' and then press 'd' to detach screen

To monitor or stop server:

# Reattach screen
screen -r

# Press 'Ctrl+C' to stop server

Note: Please schdule a crontab job for tmp_server_file(sitelinux20) and server_tmp_files(hdfsbe) cleaning