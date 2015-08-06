ConCoCt
=======

Description
-----------
ConCoCt is a web application to automatically compile and test simple programs
written in the C programming language.


Deployment
----------
1) Create an web2py directory to be used by your web server.

2) Clone ConCoCt repository from Github [1] to web2py/applications/.

3) Change database and mail configuration in ConCoCt/private/appconfig.ini.

4) Clone libConCoCt repository from Github [2] and add symbolic links for files
   (celery_tasks.py and libConCoct directory) to ConCoct/modules.

5) Deploy celery worker via supervisord.
    - Create a system user for running Celery worker via supervisord.
          adduser celery_worker
          usermod -aG docker celery_worker
    - Set read access for user "celery_worker" for all data directories.
    - Adjust and copy file celeryd.conf to supervisor configuration.
          cp celeryd.conf /etc/supervisor/conf.d/
    - Reread configuration files and update.
          supervisorctl reread
          supervisorctl update
    - Start Celery worker via supervisord.
          supervisorctl start celery

6) Create VM running Linux (64bit). [Only if test should be executed in VM
   instead of a Docker container]
    - Create and install a new VM as user "celery_worker" so that the Celery
      worker instance can start/control/stop the VM.
    - Install SSH server inside VM.
    - Add new user "testrunner" inside VM.
            adduser testrunner
    - Change PAM limits in /etc/security/limits.conf inside VM:
            testrunner	hard    nproc       10
            testrunner	hard    nofile      200
            testrunner  hard    core        500000
            testrunner  hard    data        500000
            testrunner  hard    fsize       500000
            testrunner  hard    stack       500000
            testrunner  hard    cpu         5
            testrunner  hard    as          500000
            testrunner  hard    nice        20
            testrunner	hard    maxlogins   1
    - Adjust settings for connecting to VM via SSH in libConCoct.py file on host.

7) Start web2py web server or integrated web2py into Apache/Nginx/etc.

8) Go to http://[server address]/admin and reload routes.

9) Go to http://[server address]/ConCoct and log in as null@null.com with the
   admin password "1234".

10) Change the name, password and email address of the administrator account.

11) Create new accounts for teachers and students under /ConCoCt/appadmin.

12) Import example tasks from directory ConCoCt/private/examples.

[1] https://github.com/wichmann/ConCoCt.git
[2] https://github.com/wichmann/libConCoCt.git


Security
--------
To prevent fork bombs, change limit of processes for single user in file
/etc/security/limits.conf (logout and login after the change!):

    celery_worker hard nproc 10

The network access for all tested solutions inside the VM (when using VM to run
unit tests) should be prohibited. This can be achieved by setting a user-specific
iptables rule:

    iptables -A OUTPUT -m owner --uid-owner testrunner -j DROP

If using the VM backend of libConCoct, the maximum disk space for the user
"testrunner" inside of the VM has to be set by a quota.

1) First you have to mount your filesystem with quota support:

    UUID=[snip]     /       ext4        defaults,usrquota       0       1

2) Install and configure the quota software:

    modprobe quota_v2
    echo 'quota_v2' >> /etc/modules
    
    apt-get install quota quotatool
    
    quotacheck -acvum
    service quota stop
    chmod 600 /aquota.user
    service quota start

    repquota /  

3) Configure the hard limit for user "testrunner":

    edquota -u testrunner

Launching docker daemon with devicemapper backend with particular block devices
for data and metadata:

    docker -d -s=devicemapper --storage-opt dm.basesize=10M


License
-------
ConCoCt is released under the MIT License.


Translations
------------
Translations were provided by:
* German translation by Christian Wichmann


Requirements
------------
ConCoct runs with web2py 2.11.2 under Python 2.7.9.


Problems
--------
Please go to http://github.com/wichmann/ConCoct to submit bug reports, request
new features, etc.


Third party software
--------------------
ConCoct includes parts of or links with the following software packages and
programs, so give the developers lots of thanks sometime!

* web2py - Best Python Web Framework (http://www.web2py.com/)
* SQLite (http://sqlite.org/) is a software library that implements a self-
  contained, serverless, zero-configuration, transactional SQL database engine.
  SQLite is in the public domain. No claim of ownership is made to any part of
  the code.
* Ace - The High Performance Code Editor for the Web. http://ace.c9.io/.
  Released under the BSD license.
* Paramiko - A Python implementation of the SSHv2 protocol. Licensed under the
  GNU LGPL license.
* Celery and RabbitMQ - An open source asynchronous task queue (Celery) based on
  distributed message passing (RabbitMQ). Licensed under the BSD License and the
  Mozilla Public License respectively.
* Oracle VirtualBox - A virtualization solution for x86 and AMD64/Intel64.
  Available under the terms of the GNU General Public License (GPL) version 2.
* Docker - An open platform for building, shipping and running distributed
  applications. Licensed under the Apache 2.0 license.
* Bootstrap - A collection of tools for creating websites and web applications.
  Licensed under the MIT license.
* JQuery - A cross-platform JavaScript library. MIT license.
* Some cliparts from opencliparts.org:
   - https://openclipart.org/detail/212046/emblem-gear
