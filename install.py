#!/bin/env python
# scripted Workbench install, with example content
# prereqs:
#     - web server to serve static content and web app, with TLS
#     - ssh account to run commands on the remote cluster, either
#       password in build.properties or passwordless ssh pub key
#     - set up an SQL server (mysql worked for me), with database
#       and read-write user of that database
#     - cp config.py.example to config.py and edit
#     - cp build.properties.nopasswords to build.properties and edit
#     - create directories for remote workspace and remote scripts

import subprocess
import os
import shutil
import argparse
import os.path
import sys
import urllib

def runandcheck(arglist=[]):
    if arglist == []:
        return(0)
    else:
        try:
            subprocess.check_call(arglist)
        except subprocess.CalledProcessError as error:
            print("command (%s) failed with returncode (%s)!" % (arglist, error.returncode))
            #print("output (%s)" % (error.output,))
            sys.exit(error.returncode)

def makedirs(dirlist=(), override=False):
    for dirname in dirlist:
        if not os.path.exists(dirname):
            os.makedirs(dirname,0755)
        elif override:
            sys.stderr.write("{} already exists with --override option, using existing directory!\n".format(dirname,))
        else:
            sys.stderr.write("{} already exists, no --override option, exiting!\n".format(dirname,))
            sys.exit(1)
    

continue_var = raw_input('Has config.py been created? Y/N ')
if not continue_var == 'Y':
    print("copy config.py.example to config.py, then edit and rerun install.py")
    sys.exit(0)
import config
SVNREPO = 'https://svn.sdsc.edu/repo/scigap/trunk'
RESTUSERSREPO = 'https://svn.sdsc.edu/repo/NGBW/cipres-config/trunk'
THISDIR = os.getcwd()

parser = argparse.ArgumentParser()
parser.add_argument('--override', action='store_true')
arg_dict = vars(parser.parse_args())

# make the parent dir for the svn checkout
makedirs((config.CIPRESDIR,),override=arg_dict['override'])

os.chdir(config.CIPRESDIR)
continue_var = raw_input('svn checkout workbench repo? (Y/N) ')
if continue_var == 'Y':
    runandcheck(['svn', 'checkout', SVNREPO, 'source'])
else:
    print("Not svn checking out workbench repo.")

# create mysql database using source/sdk/scripts/database/cipres.sql
print('Create the mysql database using source/sdk/scripts/database/cipres.sql')
print('For example: mysql --verbose --host=mysql2.example.org --port=3316 -u dbadmin -p dbname < /home/john/gatewaybuild/cipres/source/sdk/scripts/database/cipres.sql')
continue_var = raw_input('hit Enter when done ')

nsgdatalist = (config.NSGDATADIR,
               config.NSGDATADIR + '/' + 'disabled_resources',
               config.NSGDATADIR + '/' + 'scripts',
               config.NSGDATADIR + '/' + 'logs',
               config.NSGDATADIR + '/' + 'workspace',
               config.NSGDATADIR + '/' + 'db_documents',
  )
makedirs(nsgdatalist, override=arg_dict['override'])

# These might need to go into .bashrc also
os.environ['PATH'] = config.JAVA_HOME + '/bin:' + os.environ['PATH'] + ':' + config.NSGDATADIR + '/scripts'
os.environ['SDK_VERSIONS'] = config.NSGDATADIR + '/scripts'
os.environ['ANT_HOME'] = config.ANTDIR
os.environ['JAVA_HOME'] = config.JAVA_HOME

os.chdir(config.CIPRESDIR + '/source')
if not os.path.exists('my_config'):
    shutil.copytree('example','my_config')
else:
    sys.stderr.write('my_config already exists, not copying!\n')
continue_var = raw_input('Overwrite properties and xml files? (Y/N) ')
if continue_var == 'Y':
    shutil.copy2('sdk/scripts/airavata-client.properties.template', THISDIR + '/airavata-client.properties')
    continue_var = raw_input('In ' + THISDIR + ', edit ssl.properties, tool-registry.cfg.xml, somexsedetool.xml, build.properties, airavata-client.properties hit Enter when done ')
    shutil.copy2(THISDIR + '/ssl.properties','my_config/sdk/src/main/resources/')
    shutil.copy2(THISDIR + '/tool-registry.cfg.xml','my_config/sdk/src/main/resources/tool/')
    shutil.copy2(THISDIR + '/somexsedetool.xml','my_config/sdk/src/main/resources/pisexml/')
    shutil.copy2(THISDIR + '/build.properties','my_config/')
    if not os.path.exists('my_config/sdk/scripts/'):
        makedirs(('my_config/sdk/scripts/',),override=arg_dict['override'])
    shutil.copy2(THISDIR + '/airavata-client.properties','my_config/sdk/scripts/')
else:
    print("Not overwriting properties and xml files...")

# Install remote scripts
continue_var = raw_input('Overwrite remote submit, check and delete scripts? (Y/N) ')
if continue_var == 'Y':
    continue_var = raw_input('In ' + THISDIR + ', edit submit.simple.py, checkjobs.py, delete.py, hit Enter when done ')
    runandcheck(['scp', '-p', THISDIR + '/submit.simple.py', config.REMOTEUSER + '@' + config.REMOTEHOST + ':' + config.REMOTESCRIPTSDIR])
    runandcheck(['scp', '-p', THISDIR + '/checkjobs.simple.py', config.REMOTEUSER + '@' + config.REMOTEHOST + ':' + config.REMOTESCRIPTSDIR])
    runandcheck(['scp', '-p', THISDIR + '/delete.simple.py', config.REMOTEUSER + '@' + config.REMOTEHOST + ':' + config.REMOTESCRIPTSDIR])
else:
    print("Not installing remote scripts...")

# Install favicon.ico and logo.gif
shutil.copy2(THISDIR + '/favicon.ico','my_config/portal/src/main/webapp/images/')
shutil.copy2(THISDIR + '/logo.gif','my_config/portal/src/main/webapp/images/')
continue_var = raw_input('Edit my_config/portal/src/main/webapp/images/ favicon.ico and logo.gif. hit Enter when done ')

continue_var = raw_input('Edit my_config/portal/src/main/webapp/pages/common/menu.jsp to point to appropriate help.html and cite.html. hit Enter when done ')

# install struts-2.0.dtd from phylo.org
# http://www.phylo.org/struts-2.0.dtd
urllib.urlretrieve('http://www.phylo.org/struts-2.0.dtd', THISDIR + '/struts-2.0.dtd')
shutil.copy2(THISDIR + '/struts-2.0.dtd','my_config/portal/src/main/webapp/')

continue_var = raw_input('run cipresAdmin and testAndDemoAccounts? (Y/N) ')
if continue_var == 'Y':
    os.chdir(config.CIPRESDIR + '/source')
    buggydirectory = 'build/portal/src/main/codeGeneration/AUTO-GENERATED'
    if os.path.exists(buggydirectory):
        print("Removing %s" % buggydirectory)
        os.rmdir(buggydirectory)
    else:
        print("%s removal not necessary..." % buggydirectory)
    # ./build.py --conf-dir=my_config --front-end=portal --front-end=rest deploy
    runandcheck(['./build.py', '--conf-dir=my_config', '--front-end=portal', '--front-end=rest', 'deploy'])
    os.chdir(config.NSGDATADIR + '/scripts')
    # make sure this matches fields in build.properties:
    # admin.username=
    # admin.password=
    ADMINUSERNAME = raw_input('Enter admin.username from build.properties: ')
    ADMINPASSWORD = raw_input('Enter admin.password from build.properties: ')
    ADMINEMAIL = raw_input('Enter admin email address: ')
    #./cipresAdmin -u <admin user> -p <admin password> -e <admin email>
    runandcheck(['./cipresAdmin', '-u', "%s" % ADMINUSERNAME, '-p', "%s" % ADMINPASSWORD, '-e', "%s" % ADMINEMAIL])
    # run testAndDemoAccounts
    #./testAndDemoAccounts -u <admin user> -p <admin password>
    runandcheck(['./testAndDemoAccounts', '-u', "%s" % ADMINUSERNAME, '-p', "%s" % ADMINPASSWORD])
else:
    print("Not running cipresAdmin nor testAndDemoAccounts...")

os.chdir(config.CIPRESDIR + '/source')
continue_var = raw_input('svn checkout restusers repo? (Y/N) ')
if continue_var == 'Y':
    runandcheck(['svn', 'checkout', RESTUSERSREPO, 'cipres-config'])
else:
    print("Not svn checking out restusers repo.")
buggydirectory = 'build/portal/src/main/codeGeneration/AUTO-GENERATED'
if os.path.exists(buggydirectory):
    print("Removing %s" % buggydirectory)
    os.rmdir(buggydirectory)
else:
    print("%s removal not necessary..." % buggydirectory)
runandcheck(['./build.py', '--conf-dir=my_config', '--front-end=portal', '--front-end=rest', '--front-end=cipres-config/restusers', 'deploy'])

# user registration url is: 
# https://gateway.example.org:8444/restusers/login.action

