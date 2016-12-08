# worbench-install-example

Example install script and support files for creating a working Workbench Gateway

Some pre-requisites for installing a working gateway:

  - web server to serve static content and web app, with TLS
  - ssh account to run commands on the remote cluster, either password in build.properties or passwordless ssh pub key
  - set up an SQL server (mysql worked for me), with database and read-write user of that database
  - cp config.py.example to config.py and edit
  - cp build.properties.nopasswords to build.properties and edit
  - create directories for remote workspace and remote scripts

cd to the directory containing install.py run install.py: ./install.py

You will be prompted to edit files and confirm copying actions.
